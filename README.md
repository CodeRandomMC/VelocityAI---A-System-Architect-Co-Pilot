# VelocityAI - A Systems Architect Toolset 🏗️🤖

## The Story Behind This Tool

I built this because I think differently about systems. I've always had a high-velocity thinking pattern for large-scale systems - I can see the big picture, identify bottlenecks, and understand complex interconnections quickly. But I didn't have the formal education opportunities to learn all the professional architectural lingo and frameworks that traditional system architects use.

What I realized is that **speed of iteration beats perfection of process**. While traditional architecture reviews can take weeks or months, I wanted to compress that down to hours using AI-augmented tools that could match my thinking velocity.

## The Problem I Solved

**Traditional Architecture Reviews:**

- Take weeks/months of back-and-forth
- Require scheduling multiple senior architects
- Often get bogged down in corporate process
- Miss critical issues until it's expensive to fix

**My AI-Augmented Approach:**

- Get comprehensive feedback in minutes
- Iterate rapidly on designs
- Catch issues early when they're cheap to fix
- Scale expertise without scaling headcount

**Why I Built This Specific Tool:**

I needed something that could analyze architecture plans at the speed of my thinking. Traditional tools were too slow, too complex, or required too much setup. So I built a **single Python file** that:

- Launches instantly with `python main.py`
- Provides immediate feedback through a clean web interface
- Works with both cloud and local AI models
- Requires minimal dependencies and setup
- Focuses purely on architectural analysis, not project management

## How It Works

### 1. The Custom Feedback AI

I started with a specialized system prompt that embodies 20+ years of senior principal architect experience. This isn't just a generic AI - it's trained to analyze systems across 7 critical dimensions:

- **Scalability**: Can it handle growth?
- **Reliability**: What breaks and when?
- **Security**: Where are the vulnerabilities?
- **Performance**: Will it be fast enough?
- **Maintainability**: Can future developers work with it?
- **Cost Efficiency**: Are we burning money?
- **Observability**: Can we debug it when it breaks?

### 2. Local LLM Support for Security

I added local LLM support through LM Studio because sending architecture plans to public APIs creates security and privacy concerns. This also allows for:

- **Privacy**: Keep sensitive system designs internal
- **Custom Models**: Use specialized architecture-trained models
- **No API Costs**: Run inference locally
- **Offline Capability**: Work without internet
- **Flexible Deployment**: Connect to LM Studio on any host/port

#### New: Dynamic Host Configuration

The latest version includes dynamic LM Studio host configuration:

- **Custom Host Support**: Connect to LM Studio running on any host:port (not just localhost:1234)
- **Connection Testing**: Built-in connection testing with real-time status feedback
- **Dynamic Model Loading**: Automatically detects and loads available models from your LM Studio instance
- **Model Refresh**: Refresh the model list without restarting the application
- **Error Handling**: Clear error messages for connection issues and timeouts

### 3. Structured JSON Output

The AI returns analysis in a consistent JSON format that gets beautifully rendered:

```json
{
  "planSummary": "What the system does",
  "strengths": [{ "point": "...", "reason": "..." }],
  "areasForImprovement": [
    {
      "area": "Database Design",
      "concern": "Single point of failure",
      "suggestion": "Add read replicas",
      "severity": "HIGH"
    }
  ],
  "actionableKeyPoints": ["Next steps to take"]
}
```

## Technical Architecture

### Frontend: Gradio Web Interface

- Clean, responsive design
- Real-time analysis feedback
- Markdown input/output
- Model selection interface

### Backend: Dual-Provider Support

- **Google GenAI**: Gemini Flash/Pro for cloud inference
- **LM Studio**: Local model support with flexible host configuration
- Automatic model detection and refresh
- Real-time connection testing
- Graceful fallback handling

### Core Components

## 🏗️ Architecture Overview


```
SystemArchticectToolset/
├── main.py              # Main application entry point
├── config.py            # Configuration constants and settings
├── core_logic.py        # Core analysis logic and prompt engineering
├── llm_clients.py       # LLM client abstractions (Google GenAI, LM Studio)
├── ui_components.py     # Gradio UI components and styling
├── test_refactored.py   # Test script to verify refactored modules
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Architecture of This Tool

This tool is built as a **single-file Python application** that demonstrates the power of rapid prototyping:

- **Single Entry Point**: `feedback.py` contains the entire application
- **Dual AI Providers**: Seamlessly switch between cloud (Google) and local (LM Studio) inference
- **Real-time UI**: Gradio provides instant feedback and responsive interface
- **Structured Analysis**: Consistent JSON output parsed into beautiful markdown
- **Zero Configuration**: Works out of the box with minimal setup

## 🔄 Refactored Modular Architecture

**NEW**: The application has been refactored into a clean, modular structure for better maintainability and extensibility. You can now choose between:

### Option 1: Single-File Version (Original)

- **File**: `_alpha.py` {Could be behind a few versions compared to the modular version}
- **Best for**: Quick prototyping, simple deployment, minimal setup
- **Philosophy**: Single file = single purpose, zero configuration

### Option 2: Modular Version (Refactored)

- **Entry Point**: `main.py`
- **Best for**: Development, testing, extending functionality
- **Philosophy**: Separation of concerns, maintainable architecture

#### Modular Structure Overview:

```
├── main.py              # Main application orchestration
├── config.py            # Configuration constants and settings
├── core_logic.py        # Core analysis logic and prompt engineering
├── llm_clients.py       # LLM client abstractions (Google GenAI, LM Studio)
├── ui_components.py     # Gradio UI components and styling
├── test_refactored.py   # Comprehensive test suite
└── README_REFACTORED.md # Detailed refactored architecture documentation
```

#### Key Benefits of Refactored Version:

- **Separation of Concerns**: Each module has a single responsibility
- **Maintainability**: Easy to modify individual components
- **Testability**: Comprehensive test coverage with `test_refactored.py`
- **Extensibility**: Simple to add new LLM providers or UI components
- **Type Safety**: Full type annotations and error handling

#### Usage:

```bash
# Run the refactored version
python main.py

# Test the refactored modules
python test_refactored.py
```

Both versions provide identical functionality - choose based on your needs!

## Why This Approach Is Different

Most system architects I know are either:

1. **Highly experienced but slow** - They know everything but take forever
2. **Fast but inexperienced** - They move quickly but miss critical issues

I'm building tools that combine **high-velocity thinking with deep expertise** through AI augmentation. This isn't about replacing human architects - it's about amplifying their capabilities.

### The Philosophy: Speed + Simplicity

This tool embodies my core beliefs:

- **Single File = Single Purpose**: One Python file, one clear function
- **Instant Feedback**: No waiting, no complicated setup
- **Choice of AI**: Use cloud or local models based on your needs
- **Structured Output**: Consistent, actionable analysis every time
- **Zero Lock-in**: It's just Python - modify it however you want

### The Multiplier Effect

With this tool, I can:

- Review 10x more architecture plans in the same time
- Catch issues I might miss in manual reviews
- Provide consistent, structured feedback
- Iterate on designs at the speed of thought
- Share the tool with others instantly (just share the Python file)

## Getting Started

### Prerequisites

```bash
pip install -r requirements.txt
```

**What gets installed:**

- `gradio` - Web interface framework
- `google-genai` - Google Gemini API client
- `requests` - HTTP client for LM Studio
- `python-dotenv` - Environment variable management
- `typing` - Type hints support

### Quick Start (Cloud)

1. Get a Google AI Studio API key from [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Create a `.env` file: `GOOGLE_API_KEY=your_api_key_here`
3. Choose your version:
   - **Modular**: `python main.py`
   - **Single-file**: `python _alpha_.py`
4. Open your browser to `http://localhost:7860`
5. Start analyzing architecture plans immediately!

### For LM Studio (Local)

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Load a model (recommend 7B+ parameter models for better analysis)
3. Start the local server in LM Studio (Server tab → Start Server)
4. Run: `python main.py`
5. Select "LM Studio (Local)" as your provider
6. Configure your LM Studio host (default: localhost:1234)
7. Test the connection to verify it's working
8. Select from available models automatically detected

#### LM Studio Configuration Options

- **Default Setup**: LM Studio running on `localhost:1234`
- **Custom Host**: Enter any host:port combination (e.g., `192.168.1.100:1234`)
- **Remote LM Studio**: Connect to LM Studio running on another machine
- **Different Port**: If you're running LM Studio on a different port

#### Using the LM Studio Interface

1. **Select Provider**: Choose "LM Studio (Local)" from the provider dropdown
2. **Configure Host**: Enter your LM Studio host:port in the configuration section
3. **Test Connection**: Click "Test Connection" to verify LM Studio is accessible
4. **Select Model**: Choose from dynamically loaded models from your LM Studio instance
5. **Refresh Models**: Use the refresh button if you load new models in LM Studio

### Testing Local Setup

**Single-file version:**

```bash
python _alpha.py
```

**Modular version:**

```bash
python main.py
```

## Usage Example

**Input**: Paste a system architecture plan in Markdown (example below):

```markdown
# Real-time Analytics Dashboard

## Components

- Frontend: React SPA
- API: Node.js monolith on single EC2
- Database: PostgreSQL on same instance
- WebSocket for real-time updates

## Data Flow

1. User clicks → POST /event
2. API writes to PostgreSQL
3. WebSocket pushes to all clients
```

**Output**: Get instant AI-powered analysis with:

- ✅ **Strengths**: Real-time capability, simple architecture
- 🔍 **Issues**: Single point of failure, no caching layer
- 🚀 **Next Steps**: Add load balancer, implement Redis

_Note: The above is an example of what you would input to analyze - not the components of this tool itself._

## What This Tool Actually Is

This is a **Python-based web application** built with:

- **Gradio**: For the interactive web interface
- **Google GenAI SDK**: For cloud-based Gemini model access
- **Requests**: For LM Studio local API communication
- **Python-dotenv**: For environment variable management

The tool itself analyzes architecture plans written in Markdown and provides structured feedback through either Google's Gemini models or local LLMs via LM Studio. It's designed to be a **fast, iterative architecture review companion** that matches high-velocity thinking patterns.

## Future Vision

I believe this approach could be extended with:

- **Specialized Models**: Custom-trained architecture review models
- **Integration**: Connect with existing architecture tools
- **Collaboration**: Team-based architecture reviews
- **Templates**: Common pattern libraries
- **Metrics**: Track architecture quality over time

## The Bigger Picture

This isn't just about architecture reviews. It's about **democratizing expertise** and **accelerating innovation**. I'm building tools that let anyone with good ideas move at the speed of their thinking, not the speed of bureaucracy.

Traditional gatekeepers say you need decades of experience and formal education. I say you need **good tools, fast iteration, and the courage to build**.

---

---

## Changelog

### Latest Updates (July 2025)

#### � Modular Architecture Refactoring

**Major Update: Dual Architecture Support**

The application now supports both single-file and modular architectures:

**New Modular Structure:**

- **`main.py`**: Main application orchestration and entry point
- **`config.py`**: Centralized configuration management
- **`core_logic.py`**: Core analysis logic and prompt engineering
- **`llm_clients.py`**: LLM client abstractions with factory pattern
- **`ui_components.py`**: Gradio UI components and styling
- **`test_refactored.py`**: Comprehensive test suite

**Benefits:**

- **Separation of Concerns**: Each module has a single responsibility
- **Maintainability**: Easy to modify individual components without affecting others
- **Testability**: Comprehensive test coverage with automated validation
- **Extensibility**: Simple to add new LLM providers, UI components, or analysis types
- **Type Safety**: Full type annotations and robust error handling

**Usage:**

```bash
# Run modular version
python main.py

# Test modular architecture
python test_refactored.py
```

**Documentation:** See `README_REFACTORED.md` for detailed architecture documentation.

#### �🚀 Enhanced LM Studio Integration

**New Features:**

- **Dynamic Host Configuration**: Configure LM Studio host from the UI instead of hardcoded localhost:1234
- **Real-time Connection Testing**: Test your LM Studio connection with instant feedback
- **Automatic Model Discovery**: Dynamically load available models from your LM Studio instance
- **Model Refresh**: Refresh the model list without restarting the application
- **Remote LM Studio Support**: Connect to LM Studio running on different machines or ports

**Technical Improvements:**

- Improved error handling for connection timeouts and failures
- Better UI feedback for connection status
- Automatic model list updates when host configuration changes
- Enhanced security with local-only inference options

**User Experience:**

- Cleaner interface with collapsible LM Studio configuration section
- Visual indicators for connection status (✅ Connected, ❌ Failed)
- Model count display when successfully connected
- Intuitive host configuration with validation

_Built with high-velocity thinking and AI augmentation_ 🚀

## Contributing

This tool reflects my thinking patterns and workflow. If you have similar high-velocity thinking or want to contribute to AI-augmented architecture tools, I'd love to collaborate.

## License

MIT License - Build whatever you want with this.
