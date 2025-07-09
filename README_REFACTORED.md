# VelocityAI Architecture Reviewer - Refactored

A modular architecture analysis tool that uses AI to review system design plans for scalability, reliability, security, and more.

## 🏗️ Architecture Overview

The application has been refactored into a clean, modular structure:

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

## 📦 Module Structure

### `main.py`

- **Purpose**: Main application entry point and orchestration
- **Key Components**:
  - `ArchitectureAnalyzer` class: Main application logic
  - Event handlers for UI interactions
  - Application launch configuration

### `config.py`

- **Purpose**: Centralized configuration management
- **Key Components**:
  - Model constants (Gemini Flash, Pro)
  - API configurations
  - Default settings

### `core_logic.py`

- **Purpose**: Core business logic and prompt engineering
- **Key Components**:
  - `ARCHITECT_SYSTEM_PROMPT`: Specialized prompt for architecture analysis
  - `format_analysis_response()`: Formats AI responses into readable markdown
  - `parse_analysis_response()`: Parses and validates AI responses
  - `validate_input()`: Input validation logic
  - `EXAMPLE_PLAN`: Sample architecture plan for demonstration

### `llm_clients.py`

- **Purpose**: Abstraction layer for different LLM providers
- **Key Components**:
  - `GoogleGenAIClient`: Google GenAI API client
  - `LMStudioClient`: LM Studio local API client
  - `LLMClientFactory`: Factory for creating client instances
  - `LLMClientError`: Custom exception for client errors

### `ui_components.py`

- **Purpose**: Gradio UI components and styling
- **Key Components**:
  - `UIComponents`: Container for UI elements and handlers
  - `CUSTOM_CSS`: Application styling
  - Component creation methods for different UI sections

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Google GenAI API key (optional, for cloud inference)
- LM Studio (optional, for local inference)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   # Create a .env file with:
   GOOGLE_API_KEY=your_google_api_key_here
   ```

### Running the Application

```bash
python main.py
```

The application will start on `http://localhost:7860`

### Testing the Refactored Code

```bash
python test_refactored.py
```

## 🔧 Configuration

### Google GenAI Setup

1. Get an API key from Google AI Studio
2. Set the `GOOGLE_API_KEY` environment variable
3. Select "Google GenAI" as the provider in the UI

### LM Studio Setup

1. Install and run LM Studio
2. Load a model in LM Studio
3. Select "LM Studio (Local)" as the provider in the UI
4. Configure the host/port if different from default

## 🏛️ Architecture Benefits

### Separation of Concerns

- **UI Logic**: Isolated in `ui_components.py`
- **Business Logic**: Centralized in `core_logic.py`
- **API Clients**: Abstracted in `llm_clients.py`
- **Configuration**: Centralized in `config.py`

### Maintainability

- Each module has a single responsibility
- Easy to modify individual components
- Clear interfaces between modules

### Testability

- Modular structure enables unit testing
- Dependency injection through factory pattern
- Clear separation of concerns

### Extensibility

- Easy to add new LLM providers
- UI components can be easily modified
- Configuration changes don't affect core logic

## 🛠️ Development

### Adding a New LLM Provider

1. Create a new client class in `llm_clients.py`
2. Implement the required methods (`generate_analysis`, `test_connection`, etc.)
3. Update the `LLMClientFactory`
4. Add UI components for the new provider

### Modifying the UI

1. Update `ui_components.py` for new UI elements
2. Modify `main.py` for new event handlers
3. Update `CUSTOM_CSS` for styling changes

### Changing Analysis Logic

1. Update `core_logic.py` for prompt or formatting changes
2. Modify `ARCHITECT_SYSTEM_PROMPT` for different analysis criteria
3. Update `format_analysis_response()` for different output formats

## 📋 Error Handling

The refactored application includes comprehensive error handling:

- Custom exceptions for LLM client errors
- Input validation
- Connection testing for local services
- Graceful error messages in the UI

## 🎯 Future Enhancements

The modular structure makes it easy to add:

- New LLM providers (OpenAI, Anthropic, etc.)
- Different analysis types (security-focused, performance-focused)
- Export functionality (PDF, Word, etc.)
- Batch processing capabilities
- API endpoints for programmatic access

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes in the appropriate module
4. Test with `python test_refactored.py`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.
