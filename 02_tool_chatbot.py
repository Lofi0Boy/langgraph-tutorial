"""
Phase 2: Tool-Enabled Chatbot
Chatbot that can search the web using Tavily
"""
import os
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Load environment variables
load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize Claude
llm = ChatAnthropic(
    model='claude-4-sonnet-latest',
    api_key=os.getenv('ANTHROPIC_API_KEY')
)

# Create search tool
tool = TavilySearchResults(
    max_results=2,
    api_key=os.getenv('TAVILY_API_KEY')
)
tools = [tool]

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    messages = state["messages"]

    system_prompt = {
        "role": "system", 
        "content":
        """
        Use tools when you find the information is not available in your knowledge base.
        If you didn't use tools, don't mention why you didn't use it unless asked.
        """
    }

    full_messages = [system_prompt] + messages
    response = llm_with_tools.invoke(full_messages)

    return {"messages": [response]}

def create_tool_graph():
    graph_builder = StateGraph(State)
    
    # Add nodes
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", ToolNode(tools=tools))
    
    # Add edges
    graph_builder.add_edge(START, "chatbot")
    
    # Conditional edge: if chatbot wants to use tools, go to tools
    # Otherwise, end the conversation
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    
    # After using tools, go back to chatbot
    graph_builder.add_edge("tools", "chatbot")
    
    return graph_builder.compile()

def test_tool_chatbot():
    graph = create_tool_graph()
    
    result = graph.invoke({
        "messages": [{"role": "user", "content": "What's the latest news about AI in 2024?"}]
    })
    
    print("User: What's the latest news about AI in 2024?")
    print(f"Assistant: {result['messages'][-1].content}")

    result = graph.invoke({
        "messages": [{"role": "user", "content": "What's the result of 2+2?"}]
    })
    
    print("User: What's the result of 2+2?")
    print(f"Assistant: {result['messages'][-1].content}")

def debug_tool_info():
    for tool in tools:
        print('-'*30)
        print(f'{tool.name=}')
        print(f'{tool.description=}')
        print(f'{tool.args=}')
        print('-'*30)
if __name__ == "__main__":
    # debug_tool_info()
    test_tool_chatbot()
