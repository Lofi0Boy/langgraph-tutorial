"""
Phase 1: Basic LangGraph Chatbot
Simple chatbot using StateGraph with Claude
"""
import os
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Load environment variables
load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize Claude
llm = ChatAnthropic(
    model='claude-3-5-sonnet-20241022',
    api_key=os.getenv('ANTHROPIC_API_KEY')
)

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

def create_graph():
    graph_builder = StateGraph(State)
    
    # Add the chatbot node
    graph_builder.add_node("chatbot", chatbot)
    
    # Define the flow: START → chatbot → END
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    
    # Compile the graph
    return graph_builder.compile()

def test_chatbot():
    graph = create_graph()
    
    result = graph.invoke({
        "messages": [{"role": "user", "content": "Hello! What is LangGraph?"}]
    })
    
    print("User: Hello! What is LangGraph?")
    print(f"Assistant: {result['messages'][-1].content}")

if __name__ == "__main__":
    test_chatbot()
