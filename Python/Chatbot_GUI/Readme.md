ChatPy - Intelligent Assistant 🤖

ChatPy is a versatile intelligent assistant that provides both command-line (CLI) and graphical (GUI) interfaces for natural conversations, information retrieval, and entertainment.

Features ✨
    
    🤖 Intelligent Conversations

    Context-aware responses using Microsoft's DialoGPT model

    Natural language processing capabilities

    Memory of conversation history and user preferences

🎨 Dual Interface

    CLI Mode: Fast, text-based interface with colorful output

    GUI Mode: Beautiful graphical interface with theme support

💬 Conversation Capabilities

    Personal name recognition and memory

    Sentiment analysis and mood tracking

    Jokes, fun facts, and entertainment

    Weather information and time/date queries

    Contextual responses based on conversation history

🎯 User Experience

    Dark/Light theme toggle

    Typing indicators

    Conversation history

    Clean, modern interface

    Responsive design

Installation 📦
Prerequisites

    Python 3.7 or higher

    pip package manager

Step-by-Step Installation

    Clone or download the project files
    bash

# If using git
git clone <repository-url>
cd chatpy

Install required dependencies
bash

pip install transformers torch tkinter pillow pyfiglet requests

Note: On some systems, you might need to install tkinter separately:
bash

# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS (with Homebrew)
brew install python-tk

File Structure
Ensure you have these files in your project directory:
```
chatpy/
├── main.py
├── responses.py
└── assets/
    └── icon.png (optional)
```
Usage 🚀

Starting ChatPy

Run the main script:
```
python main.py
```
Interface Selection

You'll be prompted to choose your preferred interface:
text

Choose interface:
1. 💻 Command Line (CLI)
2. 🖥️  Graphical (GUI)
Enter choice (1/2):

CLI Mode Features

    Color-coded messages

    ASCII art welcome banner

    Quick keyboard shortcuts

    Lightweight and fast

GUI Mode Features

    Modern chat interface

    Theme switching (Dark/Light)

    Scrollable conversation history

    Visual typing indicators

    One-click clear chat function

Commands and Capabilities 🗣️
Basic Interactions

    Greetings: "hi", "hello", "hey"

    Personal info: "my name is [name]", "what's my name?"

    Feelings: "I'm sad/happy", "how are you?"

    Gratitude: "thank you", "thanks"

Information

    Time/Date: "what time is it?", "what's today's date?"

    Weather: "weather in [city]", "what's the weather?"

    Facts: "tell me a fun fact", "interesting fact"

Entertainment

    Jokes: "tell me a joke", "make me laugh"

    Conversation: Ask anything and get intelligent responses

Utilities

    Help: "help" - shows available commands

    Exit: "exit", "quit", "bye" - ends the session

    Clear: GUI button to clear conversation history

Technical Details 🔧
AI Backend

    Uses Microsoft DialoGPT-medium model

    Local processing (no API keys required)

    Fallback responses for reliability

    Context-aware conversation tracking

Data Management

    Stores conversation history (last 50 messages)

    Remembers user name and preferences

    Local processing only - no data sent to external servers

Customization

    Easy to extend response patterns in responses.py

    Customizable theme colors

    Modular design for adding new features

Troubleshooting 🔍
Common Issues

    Model loading errors

        Ensure stable internet connection for first-time model download

        Check available disk space (models can be several GB)

    GUI not opening

        Verify tkinter installation: python -m tkinter (should open a test window)

        On Linux, install tkinter: sudo apt-get install python3-tk

    Slow responses

        First-time model inference may be slow

        Ensure adequate system resources

        Consider using CPU-optimized models for low-resource systems

    Missing dependencies

# Reinstall all dependencies
pip install --upgrade transformers torch pillow pyfiglet requests

Performance Tips

    GUI mode uses more resources than CLI

    First run will download AI models (~500MB)

    Subsequent runs will be faster using cached models

Development 🛠️
Extending Functionality

Add new response patterns in responses.py:
python

# Add new pattern
if "your pattern" in text:
    return "Your custom response"

Adding New Features

    Modify get_responses() function in responses.py

    Update help text to include new commands

    Test both CLI and GUI interfaces

License 📄

This project is open source and available under the MIT License.
Support 💫

If you encounter any issues:

    Check the troubleshooting section above

    Ensure all dependencies are properly installed

    Verify Python version compatibility (3.7+)

Enjoy chatting with ChatPy! 🎉
