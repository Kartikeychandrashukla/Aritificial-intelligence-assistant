# Eight - Intelligent Voice Assistant

Eight is a powerful voice-controlled AI assistant that helps you with productivity tasks, automation, and information retrieval. Built with Python, it combines speech recognition, text-to-speech, and OpenAI's GPT to create a comprehensive digital assistant.

## Features

### Core Features
- **Voice Recognition**: Natural language processing for hands-free operation
- **Text-to-Speech**: Audible responses for better interaction
- **AI Integration**: Powered by OpenAI GPT for intelligent responses

### Productivity Features

#### 1. Reminders & Alarms
Set time-based reminders that alert you after a specified duration.
```
"Remind me to call John in 30 minutes"
"Set reminder check email in 5 minutes"
```

#### 2. Note-Taking
Create and manage voice notes that are automatically saved with timestamps.
```
"Take a note buy groceries tomorrow"
"List notes"
"Show notes"
```

#### 3. Calculator
Perform mathematical calculations using voice commands.
```
"Calculate 25 plus 37"
"What is 100 divided by 4"
"Solve 15 times 8"
```

#### 4. File Operations
Manage files on your system with voice commands.
```
"List files"
"Search file config"
"Create file test.txt"
```

### Web & Application Control

#### Web Browsing
```
"Open YouTube"
"Open Google"
"Open Netflix"
```

#### Microsoft Office
```
"Open PowerPoint"
"Open Word"
"Open Excel"
```

### Information & Utilities

#### Time & Date
```
"What time is it"
"What's the date"
"What's today's date"
```

#### AI Queries
Ask any question naturally, and Eight will use AI to provide intelligent answers.
```
"What is artificial intelligence"
"Explain quantum computing"
"Write a poem about nature"
```

## Installation

### Prerequisites
- Python 3.7 or higher
- Microphone for voice input
- OpenAI API key

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/Kartikeychandrashukla/Aritificial-intelligence-assistant.git
cd Aritificial-intelligence-assistant
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API Key**
Edit `config.py` and add your OpenAI API key:
```python
apikey = "your-openai-api-key-here"
```

4. **Run the assistant**
```bash
python main.py
```

## Configuration

### OpenAI API Key
Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

### Email Configuration (Optional)
To enable email features, add to `config.py`:
```python
EMAIL = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
```

## Usage

1. Run the program: `python main.py`
2. Wait for "Hello I am Eight"
3. Speak your command clearly
4. Wait for the response
5. Say "stop" or "exit" to quit

## Command Reference

| Category | Command Example | Description |
|----------|----------------|-------------|
| **Reminders** | "remind me to [task] in [X] minutes" | Set a timed reminder |
| **Notes** | "take a note [content]" | Save a voice note |
| **Notes** | "list notes" | Show saved notes |
| **Calculator** | "calculate [expression]" | Perform calculations |
| **Files** | "list files" | List files in directory |
| **Files** | "search file [name]" | Find files by name |
| **Files** | "create file [name]" | Create new file |
| **Web** | "open [site]" | Open website |
| **Office** | "open word/excel/powerpoint" | Launch Office apps |
| **Time** | "what time is it" | Get current time |
| **Date** | "what's the date" | Get current date |
| **AI** | Any question | Ask AI anything |
| **Exit** | "stop" or "exit" | Quit the program |

## Technical Details

### Dependencies
- **pyttsx3**: Text-to-speech conversion
- **SpeechRecognition**: Voice input processing
- **openai**: AI-powered responses
- **PyAudio**: Audio input/output handling

### File Structure
```
Aritificial-intelligence-assistant/
├── main.py              # Main application
├── config.py            # Configuration (API keys)
├── requirements.txt     # Python dependencies
├── README.md           # Documentation
└── eight_notes/        # Saved notes directory (auto-created)
```

### Notes Storage
Notes are automatically saved in the `eight_notes/` directory with timestamp filenames:
- Format: `note_YYYYMMDD_HHMMSS.txt`
- Contains: Date, time, and note content

## Troubleshooting

### Microphone Not Working
- Check microphone permissions
- Verify PyAudio installation
- Test microphone in other applications

### Speech Recognition Issues
- Speak clearly and at moderate pace
- Reduce background noise
- Check internet connection (Google Speech API requires internet)

### OpenAI API Errors
- Verify API key is correct
- Check API quota/billing
- Ensure internet connection

### Office Apps Not Opening
- Update the file paths in `main.py` to match your Office installation
- Default paths are for Office 2016/365

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is open source and available for educational purposes.

## Future Enhancements

- Email sending functionality
- Weather information
- News headlines
- Music playback
- Smart home integration
- Multi-language support
- GUI interface

## Author

Kartikey Chandra Shukla

## Acknowledgments

- OpenAI for GPT API
- Google Speech Recognition
- Python Speech Recognition library
