# 🚀 LangGraph Tutorial

Progressive learning path for mastering LangGraph agent development.

## 🎓 Learning Methodology

**❗️ Important: This is a hands-on learning tutorial where YOU implement the code.**

**🤖 AI Assistant Role:**
- **Concept explanation**: Core principles and theory
- **Architecture guidance**: Class/function structure and design patterns
- **Code snippets**: Key implementation examples (NOT full solutions)
- **Debugging help**: Support when you're stuck
- **Code review**: Feedback on your implementations

**👨‍💻 Your Role as Learner:**
- **Write the code**: Implement based on guidance and examples
- **Test thoroughly**: Verify your implementations work correctly
- **Debug independently**: Solve issues and understand error messages
- **Ask questions**: When concepts are unclear or you need direction

**💡 Progress Tip**: Move slowly through each phase. Fully understand and implement each concept before advancing!

## 📁 Structure

Each numbered file represents a complete phase of learning:

- `01_basic_chatbot.py` - Basic StateGraph and chatbot node
- `02_tool_chatbot.py` - Tool integration and conditional routing  
- `03_memory_chatbot.py` - Persistent memory with checkpointer
- `04_human_loop_chatbot.py` - Human-in-the-loop workflows
- `05_react_agent.py` - ReAct reasoning and acting agent
- `06_multi_agent.py` - Multi-agent collaboration system

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run Phase 1
python 01_basic_chatbot.py

# Run Phase 2 (after setting up Tavily API key)
python 02_tool_chatbot.py
```

## 🔑 API Keys

Add your API keys to `.env`:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
TAVILY_API_KEY=tvly-your-key-here
```

## 📚 Learning Path

Follow the roadmap in `LEARNING_ROADMAP.md` for guided step-by-step learning.

Each phase builds upon the previous one, introducing new concepts progressively.
