# Speaking Practice App🗣️

<div align="center">
  <img src="https://github.com/user-attachments/assets/3479f836-e82d-426e-aaf6-f722504f5d03" width="100%" alt="Development Journey Banner">
</div>

## Overview
The Speaking Practice App is a tool designed to help users practice their English speaking skills, specifically for the IELTS speaking test. The application features a chat interface with an AI English expert and allows users to record and transcribe their responses, as well as receive instant feedback and corrections. The app provides functionality for managing chat history, saving conversations, and tracking time.

## Features
- **Chat Interface**: Users engage in a conversation with an AI-powered English teacher.
- **Audio Recording**: Record your spoken responses for review.
- **Transcription**: Transcribe your spoken words into text using WhisperModel for detailed feedback.
- **Timer**: Keep track of the time spent during each conversation.
- **Save Chat**: Save the chat history to a file for future reference.
- **Reset Chat History**: Reset the chat history at any time during the conversation.
- **Speech Synthesis**: Get your AI assistant's response read out loud via text-to-speech.

## Requirements

### Python Libraries
- `tkinter`: For building the graphical user interface (GUI).
- `pyttsx3`: For text-to-speech functionality.
- `pyaudio`: For audio recording.
- `numpy`: For audio data manipulation.
- `wavio`: For handling WAV file format audio recordings.
- `whisper`: For speech-to-text transcription.
- `dotenv`: For loading environment variables from `.env` files.
- `langchain_groq`: For managing AI chat interactions.
- `notion_api`: For interacting with Notion API.
- `groq_api`: For making requests to the Groq API.

### Environment Variables
Make sure the following environment variables are defined in a `.env` file:
- `GROQ_API_KEY`: Your Groq API key.
- `NOTION_API_TOKEN`: Your Notion API token.
- `PAGE_ID_PART1`: The Notion page ID for part 1.
- `PAGE_ID_PART2`: The Notion page ID for part 2.
- `PAGE_ID_PART3`: The Notion page ID for part 3.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/rahulsamant37/english-speaking-practice-app.git
    cd english-speaking-practice-app
    ```

2. Create a virtual environment:
    ```bash
    python3 -m venv venv
    ```

3. Activate the virtual environment:
    - On Windows:
      ```bash
      venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      source venv/bin/activate
      ```

4. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

5. Create a `.env` file and populate it with your environment variables:
    ```bash
    GROQ_API_KEY=your_groq_api_key
    NOTION_API_TOKEN=your_notion_api_token
    PAGE_ID_PART1=your_notion_page_id_part1
    PAGE_ID_PART2=your_notion_page_id_part2
    PAGE_ID_PART3=your_notion_page_id_part3
    ```

## Usage

1. Run the application:
    ```bash
    python main.py
    ```

2. The GUI will appear, where you can interact with the AI English teacher. The AI will ask you questions related to IELTS speaking topics, and you can record your responses.

3. Use the following controls:
   - **Start**: Start the conversation and begin recording.
   - **Pause/Resume**: Pause or resume the conversation.
   - **Stop**: Stop the conversation and recording.
   - **Restart**: Restart the conversation.
   - **Save Chat**: Save the current chat history to a file.
   - **Reset Chat**: Reset the chat history.
   - **Send**: Send your input to the AI and get a response.

4. To quit the app, click the **Quit** button. You can also choose to save the chat history before quitting.

## Chat History
The chat history is stored during the session, and you can save the conversation to a file. The file will contain the entire conversation between you and the AI, including timestamps and roles (e.g., user, assistant).

## AI Assistant
The AI assistant is designed to:
- Ask you IELTS speaking questions.
- Correct your grammar and word choices.
- Provide a score based on the IELTS 9.0 scale after the conversation ends.

## Dependencies
The app requires the following Python libraries:
- `tkinter`
- `pyttsx3`
- `pyaudio`
- `numpy`
- `wavio`
- `whisper`
- `dotenv`
- `groq_api`
- `langchain_groq`
- `notion_api`

You can install them by running:
```bash
pip install tkinter pyttsx3 pyaudio numpy wavio whisper dotenv groq_api langchain_groq notion_api
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributions
Contributions are welcome! Please feel free to submit issues, fork the project, and create pull requests to improve the functionality.

---

This README provides an overview of the app, installation instructions, and usage details. Adjust the repository and app-specific details (such as GitHub repository links or filenames) as needed for your project.
