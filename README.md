# Neurocura AI System

Neurocura AI is a Windows-based AI assistant designed to provide supportive, evidence-based information on neurological and cognitive health. The app is built using Python with PyQt6 for the graphical user interface and Google’s Generative AI for natural language responses.

## Table of Contents
•	[Overview](#overview)<br/>
•	[Features](#features)<br/>
•	[Installation](#installation)<br/>
•	[Configuration](#configuration)<br/>
•	[Usage](#usage)<br/>
•	[Steps](#steps)<br/>
•	[License](#license)<br/>
•	[Disclaimer](#disclaimer)<br/>

## Overview
Neurocura AI helps both healthcare professionals and general users:<br/>
•	Understand neurological conditions with clear explanations.<br/>
•	Get wellness guidance and cognitive enhancement strategies.<br/>
•	Prepare for medical appointments by explaining technical concepts in accessible language.<br/>
•	Generate, edit, and maintain an interactive conversation history.<br/>
The application emphasizes responsible usage by including disclaimers advising users to consult healthcare professionals for personalized medical advice.<br/>

## Features
•	Chat Interface: Interact with an AI assistant capable of answering questions about brain and neurological health.<br/>
•	Message Editing: Edit your messages and view their edit history to refine questions for better responses.<br/>
•	Dynamic Responses: Regenerates AI responses when a user edits a message.<br/>
•	User-Friendly Layout: Utilizes tabs to separate the chat interface and application information.<br/>
•	Detailed Guidance: Provides an educational interface geared toward both general users and healthcare professionals.<br/>
•	Clear Disclaimer: Prominently displays a disclaimer that the tool is for educational purposes only.<br/>

## Installation
Prerequisites<br/>
•	Python 3.7 or later<br/>
•	PyQt6<br/>
•	google-generativeai<br/>

## Steps
1. Clone the Repository<br/>
   ```
   git clone https://github.com/AwarewarAlmighty/neurocura-ai.git
   cd neurocura-ai
   ```
2. Create a Virtual Environment (optional but recommended):<br/>
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install Dependecies:<br/>
   ```
   pip install PyQt6 google-generativeai
   ```

## Configuration
The application requires an API key to access Google Generative AI services. Set your API key in your environment variables:
• On Windows:
  ```
  set API_KEY=your_api_key_here
  ```
Alternatively, you can set the API key in your IDE's run configurations or use a .env file with a package such as python-dotenv.

## Usage
To run Neurocura AI, execute the main Python file:
  ```
  python neurocura_ai.py
  ```
## Application Workflow
•	Chat Interface: Type your query into the text input area and click the "Send Message" button. The AI assistant will process your message and display a response.<br/>
•	Editing Messages: Right-click on any of your messages to edit the content. You can view previous versions by selecting "View Edit History."<br/>
•	Clear Chat: Click the "Clear Chat" button to reset the conversation history.<br/>
•	Information Tab: Learn more about the app’s capabilities, usage guidelines, and key features from the information tab.<br/>

## Code Structure
•	`neurocura_ai.py` – Main application script launching the PyQt interface.<br/>
•	`Message Class` – Handles user and AI messages including storing original text for edit history.<br/>
•	`AIWorker Class` – Runs the Google Generative AI calls in a separate thread to ensure a responsive UI.<br/>
•	`MessageWidget Class` – Manages how each message is displayed in the chat list.<br/>
•	`NeurocuraApp Class` – The main window handling UI, user interactions, and chat display features.<br/>

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Disclaimer
**Important**: Neurocura AI is designed as an educational tool and informational resource, not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare professionals with any questions you may have regarding a medical condition.
