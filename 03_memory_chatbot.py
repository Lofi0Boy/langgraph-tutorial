from typing import Annotated
import uuid
from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv
from langchain_community.tools import TavilySearchResults
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from typing import TypedDict
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

llm = ChatAnthropic(
    model = "claude-sonnet-4-20250514",
    api_key = os.getenv("ANTHROPIC_API_KEY")
)

tavily_tool = TavilySearchResults(api_key = os.getenv("TAVILY_API_KEY"))

class State(TypedDict):
    messages: Annotated[list, add_messages]


tools = [tavily_tool]
def chatbot(state:State):
    # provide tools information to the llm
    llm_with_tools = llm.bind_tools(tools)
    messages = state['messages']
    system_prompt = """
    you are a helpful assistant that can search the web for information.
    Use tools when you need to search the web for information.
    Remember our conversation history so that you always have the context of the conversation.
    """
    
    full_messages = [system_prompt] + messages
    response = llm_with_tools.invoke(full_messages)

    return {"messages": [response]}


def create_memory_search_graph():

    memory = MemorySaver()
    
    graph_builder = StateGraph(State)
    #function node
    graph_builder.add_node("chatbot", chatbot)

    #object node
    graph_builder.add_node("tools", ToolNode(tools))

    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges("chatbot", tools_condition)

    return graph_builder.compile(checkpointer = memory)
    

def test_memory_conversation():

    graph = create_memory_search_graph()

    config = {"configurable": {"thread_id": "conversation_1"}}

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Goodbye!")
            break
        if user_input.lower() in ["clear", "reset"]:
            config["configurable"]["thread_id"] = str(uuid.uuid4())
            print(f"New conversation started with thread ID: {config['configurable']['thread_id']}")
            continue
        
        response = graph.invoke({"messages": [{"role": "user", "content": user_input}]}, config = config)
        print(f"Assistant: {response['messages'][-1].content}")

if __name__ == "__main__":
    test_memory_conversation()