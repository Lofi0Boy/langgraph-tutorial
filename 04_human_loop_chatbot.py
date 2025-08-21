from typing import Annotated

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from typing import Optional

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_name: Optional[str]
    conversation_purpose: Optional[str]


@tool
def update_user_info( tool_call_id: Annotated[str,InjectedToolCallId], name: str = None, purpose: str = None) -> Command|str:
    '''
    Use this tool to update the name of the user or purpose of the chat.
    '''
    result_parts = []
    new_state = {}
    if name:
        new_state['user_name'] = name
        result_parts.append(f"이름을 {name}으로 저장했습니다")
    if purpose:
        new_state['conversation_purpose'] = purpose
        result_parts.append(f"대화 목적을 {purpose}로 저장했습니다")
    
    if result_parts:
        # Command로 반환하면 ToolNode에서 Command를 처리한다.
        # ToolNode에서 이게 어떤 툴콜의 결과인지 알기 위해서 tool_call_id를 전달하는듯
        # tool_call_id처럼 langgraph가 자동으로 주입해주는 값은 기본값 설정 X
        new_state['messages'] = [ToolMessage(content=result_parts,tool_call_id=tool_call_id)]
        return Command(update=new_state)
    else:
        return "사용자 데이터터를 업데이트 하지 못했습니다."

# tool 로서가 아니라 Node로서 다뤄보자. Tool로서 사용하기엔 뭔가 이상한듯,
def human_assistance(state: State) -> State:
    """Request assistance from a human."""
    human_response = interrupt({"query": state["messages"][-1].content})
    return human_response["data"]

def chatbot(state: State):
    
    global current_llm, llm_with_tools
    
    # 현재 모델부터 시작해서 모든 모델을 시도
    available_models = list(chat_models.keys())
    tried_models = []
    
    # 현재 모델을 먼저 시도
    if current_llm in available_models:
        available_models.remove(current_llm)
        available_models.insert(0, current_llm)
    
    for model in available_models:
        try:
            llm_with_tools = chat_models[model].bind_tools(tools)
            message = llm_with_tools.invoke(state["messages"])
            assert len(message.tool_calls) <= 1
            current_llm = model  # 성공한 모델을 현재 모델로 설정
            return {"messages": [message]}
        except Exception as e:
            tried_models.append(model)
            print(f"Model {model} failed: {str(e)}")
            continue
    
    # 모든 모델이 실패한 경우
    error_message = AIMessage(content="Sorry. All the models are not working. Try later.")
    return {"messages": [error_message]}

tavily = TavilySearch(max_result=2)
tools = [tavily, update_user_info]

claude = init_chat_model("anthropic:claude-3-5-sonnet-latest")
openai = init_chat_model("openai:gpt-4o-mini")
gemini = init_chat_model("google_genai:gemini-2.0-flash")
chat_models = {'gemini':gemini, 'claude':claude, 'openai':openai}

current_llm = 'gemini'
llm_with_tools = chat_models[current_llm].bind_tools(tools)


memory = InMemorySaver()

tool_node = ToolNode(tools)

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")

graph = graph_builder.compile(checkpointer=memory)

def stream_graph_updates(input: str|Command, config: dict):
    if isinstance(input, Command):
        events = graph.stream(input, config, stream_mode='values')
    else:
        events = graph.stream({'messages': [HumanMessage(content=input)]}, config, stream_mode='values')


    for i,event in enumerate(events):
        print('step',i)
        if 'messages' in event and event['messages']:
            message = event['messages'][-1]
            message.pretty_print()



config = {'configurable': {'thread_id': '123'}}

while True:
    # stateSnapshot => Value, Interrupts, next 등을 가지고 있음. 
    # 또 뭘 가지고 있는지는 나중에 알게 되겠지?
    current_state = graph.get_state(config)
    if current_state.interrupts :
        for interrupt in current_state.interrupts:
            query = interrupt.value['query']
            human_response = input(f"User: {query}")
            stream_graph_updates(Command(resume={"data": human_response}),config)
            break
        continue

    user_input = input('You: ')
    if user_input.lower() in ['q', 'quit', 'exit']:
        print('👋 Bye!')
        break
        
    stream_graph_updates(user_input, config)






