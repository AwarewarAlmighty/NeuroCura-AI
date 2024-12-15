import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QTextEdit, QPushButton, QLabel, QTabWidget,
                            QScrollArea, QMessageBox, QHBoxLayout, QListWidget,
                            QListWidgetItem, QInputDialog, QMenu)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction
import google.generativeai as genai

class Message:
    def __init__(self, text, is_user=True):
        self.text = text
        self.is_user = is_user
        self.original_text = text  # Store original text for edit history

class AIWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, prompt, api_key):
        super().__init__()
        self.prompt = prompt
        self.api_key = api_key

    def run(self):
        try:
            genai.configure(api_key=self.api_key)
            
            generation_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                system_instruction="""Neurocura AI System 
You are Neurocura, a supportive AI assistant specializing in neurological and cognitive health information. Your purpose is to help both healthcare professionals and general users better understand and navigate topics related to brain health, cognitive wellness, and neurological conditions.
Core Capabilities:

Health Information Support
Explain neurological and cognitive health topics in clear, understandable language
Share evidence-based information about brain health and cognitive wellness
Help interpret general neurological terms and medical concepts
Provide educational resources about common neurological conditions


Wellness Guidance
Suggest science-backed strategies for maintaining brain health
Share cognitive enhancement techniques for daily life
Offer general lifestyle recommendations for neurological wellness
Provide stress management and mental wellness tips


Educational Support
Break down complex neurological concepts into simple terms
Share relevant research findings in accessible language
Explain common diagnostic tests and procedures
Provide resources for further learning about brain health


Communication Bridge
Help users prepare questions for their healthcare providers
Explain medical terminology in simple language
Assist in understanding health information materials
Support better communication about neurological health

Interaction Guidelines:
Use clear, friendly, and accessible language for all users
Adjust explanation complexity based on the user's background
Always emphasize the importance of consulting healthcare providers
Include practical, everyday examples when explaining concepts
Maintain a supportive and encouraging tone
Respect privacy and confidentiality
Share information from reputable sources when appropriate

Important Notes:
For All Users
Neurocura is an educational tool, not a medical diagnostic system
Always consult healthcare providers for personal medical advice
Information provided is for educational purposes only
Emergency situations require immediate medical attention


For Healthcare Professionals
Can provide technical information and research references
Assists in educational material preparation
Supports evidence-based practice discussions
Helps with patient education planning


For General Users
Focuses on general understanding and wellness
Provides practical, everyday brain health tips
Helps prepare for medical appointments
Supports better health literacy

Limitations:
Cannot diagnose conditions or prescribe treatments
Does not provide personalized medical advice
Cannot access or interpret individual medical records
Knowledge is based on training data, not real-time updates

Remember: Neurocura aims to support both general understanding and professional knowledge of neurological health while maintaining appropriate boundaries. The goal is to enhance health literacy and support better brain health decisions for all users, while always encouraging appropriate professional medical care when needed."""  # Full system prompt here
            )

            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(self.prompt)
            self.finished.emit(response.text)
        except Exception as e:
            self.error.emit(str(e))

class MessageWidget(QListWidgetItem):
    def __init__(self, message: Message):
        super().__init__()
        self.message = message
        self.update_text()

    def update_text(self):
        prefix = "You: " if self.message.is_user else "Neurocura: "
        self.setText(f"{prefix}{self.message.text}")

class NeurocuraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("API_KEY")
        self.message_history = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Neurocura AI System')
        self.setGeometry(100, 100, 1200, 800)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Chat Interface Tab
        chat_tab = QWidget()
        chat_layout = QVBoxLayout(chat_tab)

        # Header
        header_label = QLabel("Neurocura AI Assistant")
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        chat_layout.addWidget(header_label)

        # Disclaimer
        disclaimer = QLabel("This is an AI assistant and not a replacement for professional medical advice. "
                          "Please consult with healthcare professionals for medical decisions.")
        disclaimer.setWordWrap(True)
        disclaimer.setStyleSheet("color: red; font-style: italic; margin: 10px;")
        chat_layout.addWidget(disclaimer)

        # Chat display using QListWidget for better message management
        self.chat_display = QListWidget()
        self.chat_display.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.chat_display.customContextMenuRequested.connect(self.show_context_menu)
        chat_layout.addWidget(self.chat_display)

        # Input area
        self.input_box = QTextEdit()
        self.input_box.setMaximumHeight(100)
        chat_layout.addWidget(self.input_box)

        # Button layout
        button_layout = QHBoxLayout()
        
        # Send button
        send_button = QPushButton('Send Message')
        send_button.clicked.connect(self.send_message)
        button_layout.addWidget(send_button)

        # Clear button
        clear_button = QPushButton('Clear Chat')
        clear_button.clicked.connect(self.clear_chat)
        button_layout.addWidget(clear_button)

        chat_layout.addLayout(button_layout)
        tabs.addTab(chat_tab, "Chat Interface")

        # Information Tab
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        
        info_text = """
        <h2>Neurocura AI System</h2>
        <h3>Core Capabilities:</h3>
        <ul>
            <li>Neurological Analysis</li>
            <li>Diagnostic Support</li>
            <li>Treatment Recommendations</li>
            <li>Research Assistance</li>
            <li>Patient Education</li>
            <li>Cognitive Enhancement Strategies</li>
        </ul>
        <h3>Usage Guidelines:</h3>
        <ul>
            <li>Ask questions about neurological conditions and treatments</li>
            <li>Request explanations of medical concepts</li>
            <li>Seek research summaries and latest findings</li>
            <li>Get information about cognitive enhancement strategies</li>
        </ul>
        <h3>Message Editing:</h3>
        <ul>
            <li>Right-click on any of your messages to edit them</li>
            <li>You can view edit history of messages</li>
            <li>Edit feature helps correct typos and clarify questions</li>
        </ul>
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setOpenExternalLinks(True)
        info_layout.addWidget(info_label)
        
        tabs.addTab(info_tab, "Information")

        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready')

    def show_context_menu(self, position):
        item = self.chat_display.itemAt(position)
        if item and isinstance(item, MessageWidget) and item.message.is_user:
            menu = QMenu()
            
            edit_action = QAction("Edit Message", self)
            edit_action.triggered.connect(lambda: self.edit_message(item))
            menu.addAction(edit_action)

            view_history_action = QAction("View Edit History", self)
            view_history_action.triggered.connect(lambda: self.view_edit_history(item))
            menu.addAction(view_history_action)

            menu.exec(self.chat_display.mapToGlobal(position))

    def edit_message(self, item):
        text, ok = QInputDialog.getMultiLineText(
            self, 'Edit Message', 'Edit your message:',
            item.message.text
        )
        if ok and text != item.message.text:
            # Store original text in history
            if not hasattr(item.message, 'edit_history'):
                item.message.edit_history = []
            item.message.edit_history.append(item.message.text)
            
            # Update message
            item.message.text = text
            item.update_text()
            
            # Regenerate AI response
            self.regenerate_response(item)

    def view_edit_history(self, item):
        if hasattr(item.message, 'edit_history') and item.message.edit_history:
            history_text = "Edit History:\n\n"
            for i, historic_text in enumerate(item.message.edit_history, 1):
                history_text += f"Version {i}:\n{historic_text}\n\n"
            history_text += f"Current Version:\n{item.message.text}"
            
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Message Edit History")
            msg_box.setText(history_text)
            msg_box.exec()
        else:
            QMessageBox.information(self, "Edit History", "No edit history available for this message.")

    def regenerate_response(self, item):
        # Find the response item that follows the edited message
        index = self.chat_display.row(item)
        if index + 1 < self.chat_display.count():
            response_item = self.chat_display.item(index + 1)
            if isinstance(response_item, MessageWidget) and not response_item.message.is_user:
                # Remove the old response
                self.chat_display.takeItem(index + 1)
                # Generate new response
                self.worker = AIWorker(item.message.text, self.api_key)
                self.worker.finished.connect(lambda response: self.handle_regenerated_response(response, index + 1))
                self.worker.error.connect(self.handle_error)
                self.worker.start()
                self.status_bar.showMessage('Regenerating response...')

    def handle_regenerated_response(self, response, index):
        message = Message(response, is_user=False)
        self.chat_display.insertItem(index, MessageWidget(message))
        self.status_bar.showMessage('Response regenerated')

    def send_message(self):
        user_input = self.input_box.toPlainText().strip()
        if not user_input:
            return

        # Add user message
        user_message = Message(user_input, is_user=True)
        self.chat_display.addItem(MessageWidget(user_message))
        self.input_box.clear()

        # Generate AI response
        self.worker = AIWorker(user_input, self.api_key)
        self.worker.finished.connect(self.handle_response)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

        self.status_bar.showMessage('Processing...')

    def handle_response(self, response):
        message = Message(response, is_user=False)
        self.chat_display.addItem(MessageWidget(message))
        self.status_bar.showMessage('Ready')

    def handle_error(self, error_message):
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")
        self.status_bar.showMessage('Error occurred')

    def clear_chat(self):
        self.chat_display.clear()
        self.message_history.clear()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = NeurocuraApp()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()