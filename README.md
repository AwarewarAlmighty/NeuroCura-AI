Neurocura AI System
A Windows-based AI assistant specializing in neurological and cognitive health information. Neurocura provides evidence-based guidance for both healthcare professionals and general users seeking to understand brain health, cognitive wellness, and neurological conditions.
Features
Interactive Chat Interface: Communicate with a specialized AI focused on neurological topics
Message Editing: Right-click to edit your messages and view edit history
Information Hub: Access detailed documentation about Neurocura's capabilities
Context Menus: Right-click messages for additional options
Error Handling: Comprehensive error reporting for API communication
Multi-tab Interface: Switch between chat and information views
Responsive Design: Optimized for Windows environments
Installation
Prerequisites
Python 3.6+
PyQt6 installed
Google Generative AI API key
Setup Instructions
Clone the repository:
bash
Copy
git clone https://github.com/yourusername/neurocura-ai.git
cd neurocura-ai
Create a virtual environment (recommended):
bash
Copy
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:
bash
Copy
pip install pyqt6 google-generativeai
Set up your API key:
bash
Copy
export API_KEY="your_google_generative_ai_api_key"  # On Windows: set API_KEY=your_key
Run the application:
bash
Copy
python main.py
Usage
Chat Interface:
Type your question in the text box
Click "Send Message" or press Enter
Wait for Neurocura's response (status shown in the bottom bar)
Message Editing:
Right-click any user message to edit
View edit history through the context menu
Edits automatically regenerate AI responses
Information Tab:
Review Neurocura's capabilities
Learn about usage guidelines
Understand message editing features
Clear Chat:
Use the "Clear Chat" button to reset the conversation
System Requirements
Windows 10/11
Python 3.6+
At least 4GB RAM
Internet connection for API communication
Disclaimer
Neurocura AI is an educational tool and should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical decisions.
Future Improvements
Integration with medical databases
Multilingual support
Expanded neurological condition database
Voice-to-text functionality
Customizable response styles
User authentication for personalized experiences
License
This project is licensed under the MIT License - see the LICENSE file for details.
