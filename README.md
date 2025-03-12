# AI Agent

A flexible and extensible AI agent system that combines LLM capabilities with custom tools for interactive task execution. The system supports multi-tool operations, memory retention, and natural language interactions.

## Project Structure

```
ai_agent_system_from_scratch/
│
├── README.md
├── requirements.txt
├── .env
├── main.py
│
├── agent_system/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── base_tool.py
│   │   ├── memory.py
│   │   ├── llm_client.py
│   │   └── agent.py
│   │
│   └── tools/
│       ├── __init__.py
│       ├── time_tool.py
│       ├── news_tool.py
│       └── weather_tool.py

```

## Key Components

### Core Components

1. **Agent (`agent.py`)**
   - Main orchestrator of the system
   - Manages tool execution and response generation
   - Supports multi-tool operations with sequential execution
   - Maintains conversation context through memory system

2. **Memory System (`memory.py`)**
   - Stores conversation history
   - Maintains a fixed-size memory buffer
   - Provides contextual information for LLM queries

3. **LLM Client (`llm_client.py`)**
   - Handles communication with OpenAI's API
   - Manages prompt generation and response parsing
   - Supports customizable model selection

4. **Base Tool (`base_tool.py`)**
   - Abstract base class for all tools
   - Defines standard interface for tool implementation

### Available Tools

1. **Time Tool (`time_tool.py`)**
   - Provides timezone-aware time information
   - Supports all standard timezone formats
   - Example: "Get time in America/New_York"

2. **Weather Tool (`weather_tool.py`)**
   - Fetches current weather information
   - Uses OpenWeatherMap API
   - Provides temperature and weather conditions
   - Example: "Get weather in London"

3. **News Tool (`news_tool.py`)**
   - **Purpose:** Fetches news-related information and answers questions based on multiple search APIs and Groq's Llama model.
   - **Key Features:**
     - **Multi-API Fallback:** Uses Bing and Google Custom Search APIs to retrieve news data.
     - **Caching:** Implements a caching mechanism (via DiskCache) to reduce redundant API calls.
     - **Web Content Extraction:** Leverages Trafilatura to extract and include website content from search results.
     - **LLM Integration:** Generates comprehensive answers using Groq's Llama model (e.g., "llama3-8b-8192").
   - **Example Query:** "What are the latest updates on climate change policies?"

## Setup

1. Clone the repository:
```bash
git clone https://github.com/A-L-E-X-W/ai-agent.git


cd ai-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. update `.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key
RAPIDAPI_KEY=your_rapidapi_api_key
GROQ_API_KEY=your_groq_api_key
GOOGLE_CUSTOM_SEARCH_JSON_API=your_google_custom_search_api_key
GOOGLE_CX=your_google_custom_search_engine_id
SERP_API_KEY=your_serp_api_key
SERP_STACK_API_KEY=your_serp_stack_api_key


```

## Usage

1. Run the agent:
```bash
python main.py
```

2. Interact with the agent using natural language. Examples:
```
You: What's the current time in London?
You: How's the weather in New York?
You: What's the latest news on technology trends?

```

3. The agent can handle multiple operations in a single query:
```
You: Compare the weather in London and New York, and tell me the latest news on renewable energy.

```

## Adding New Tools

1. Create a new tool class in the `tools` directory
2. Inherit from `BaseTool`
3. Implement required methods:
   - `name()`
   - `description()`
   - `use()`

Example:
```python
from agent_system.core.base_tool import BaseTool

class NewTool(BaseTool):
    def name(self) -> str:
        return "New Tool"
    
    def description(self) -> str:
        return "Description of what the tool does"
    
    def use(self, *args, **kwargs):
        # Implement tool functionality
        return "Tool result"
```

## Memory System

The memory system maintains conversation context with:
- Maximum memory items (default: 10)
- Timestamp tracking
- Source attribution (user/agent)
- Formatted context generation

## Error Handling

The system includes comprehensive error handling for:
- Invalid tool requests
- API failures
- Invalid parameters
- Missing API keys

## Requirements

- Python 3.7+
- API keys for OpenAI (optional), OpenWeatherMap, Groq, Bing (RapidAPI), Google Custom Search, and SERP services.
- Required packages listed in `requirements.txt`

## Future Enhancements

Potential areas for expansion:
- Additional tools integration
- Enhanced memory management
- Tool result caching
- Conversation summarization
- Multi-turn planning
- Custom tool pipelines

