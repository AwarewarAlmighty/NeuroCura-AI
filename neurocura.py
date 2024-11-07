import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QTextEdit, QPushButton, QLabel, QTabWidget,
                             QListWidget, QListWidgetItem, QInputDialog, QMenu, 
                             QFileDialog, QMessageBox, QHBoxLayout, QSplitter, 
                             QTreeWidget, QTreeWidgetItem, QStyle)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QColor, QPalette
import google.generativeai as genai

class ChatSession:
    def __init__(self, title=None, id=None):
        """
        Initialize a chat session.
        
        :param title: Optional title for the session
        :param id: Optional unique identifier for the session
        """
        self.id = id or str(datetime.now().timestamp())
        self.title = title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.messages = []
        self.created_at = datetime.now()

    def add_message(self, message):
        """
        Add a message to the session.
        
        :param message: Message object to add
        """
        self.messages.append(message)

    def to_dict(self):
        """
        Convert the session to a dictionary for JSON serialization.
        
        :return: Dictionary representation of the session
        """
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'messages': [
                {
                    'text': msg.text, 
                    'is_user': msg.is_user, 
                    'edit_history': msg.edit_history
                } for msg in self.messages
            ]
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a ChatSession instance from a dictionary.
        
        :param data: Dictionary containing session data
        :return: ChatSession instance
        """
        session = cls(title=data.get('title'), id=data.get('id'))
        session.created_at = datetime.fromisoformat(data.get('created_at', str(datetime.now())))
        
        # Reconstruct messages
        for msg_data in data.get('messages', []):
            message = Message(
                msg_data['text'], 
                is_user=msg_data.get('is_user', True),
                edit_history=msg_data.get('edit_history', [])
            )
            session.add_message(message)
        
        return session

class SessionManager:
    """
    Manages chat sessions, including saving, loading, and tracking sessions.
    """
    def __init__(self, sessions_dir='chat_sessions'):
        """
        Initialize SessionManager.
        
        :param sessions_dir: Directory to store session files
        """
        self.sessions_dir = sessions_dir
        
        # Ensure sessions directory exists
        os.makedirs(sessions_dir, exist_ok=True)
        
        # Load existing sessions
        self.sessions = self.load_all_sessions()

    def create_session(self, title=None):
        """
        Create a new chat session.
        
        :param title: Optional title for the session
        :return: Newly created ChatSession
        """
        session = ChatSession(title=title)
        self.sessions[session.id] = session
        self.save_session(session)
        return session

    def save_session(self, session):
        """
        Save a session to a JSON file.
        
        :param session: ChatSession to save
        """
        filename = os.path.join(self.sessions_dir, f"{session.id}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, ensure_ascii=False, indent=4)

    def load_session(self, session_id):
        """
        Load a specific session by its ID.
        
        :param session_id: Unique identifier of the session
        :return: Loaded ChatSession
        """
        filename = os.path.join(self.sessions_dir, f"{session_id}.json")
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                return ChatSession.from_dict(session_data)
        return None

    def load_all_sessions(self):
        """
        Load all existing sessions from the sessions directory.
        
        :return: Dictionary of loaded sessions
        """
        sessions = {}
        for filename in os.listdir(self.sessions_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.sessions_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                        session = ChatSession.from_dict(session_data)
                        sessions[session.id] = session
                except Exception as e:
                    print(f"Error loading session {filename}: {e}")
        return sessions

    def delete_session(self, session_id):
        """
        Delete a session by its ID.
        
        :param session_id: Unique identifier of the session to delete
        """
        filename = os.path.join(self.sessions_dir, f"{session_id}.json")
        if os.path.exists(filename):
            os.remove(filename)
            if session_id in self.sessions:
                del self.sessions[session_id]

class Message:
    def __init__(self, text, is_user=True, edit_history=None):
        self.text = text
        self.is_user = is_user
        self.edit_history = edit_history or []

class MessageWidget(QListWidgetItem):
    def __init__(self, message):
        super().__init__(message.text)
        self.message = message
        if message.is_user:
            self.setForeground(QColor(0, 0, 255))  # Blue for user messages
        else:
            self.setForeground(QColor(0, 128, 0))  # Green for AI messages
class AIWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, user_input, api_key):
        super().__init__()
        self.user_input = user_input
        self.api_key = api_key
        
    def run(self):
        try:
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Create generation config
            generation_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }
            
            # Initialize the model
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

Remember: Neurocura aims to support both general understanding and professional knowledge of neurological health while maintaining appropriate boundaries. The goal is to enhance health literacy and support better brain health decisions for all users, while always encouraging appropriate professional medical care when needed."""
            )
            
            # Start chat session
            chat_session = model.start_chat(history=[])
            
            # Get response
            response = chat_session.send_message(self.user_input)
            
            # Emit the response text
            self.finished.emit(response.text)
            
        except Exception as e:
            self.error.emit(str(e))


class NeurocuraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('API_KEY')
        self.session_manager = SessionManager()
        self.current_session = None
        self.initUI()

    def initUI(self):
        # Set Fusion style
        self.setStyle(QApplication.style())
        
        self.setWindowTitle('Neurocura AI System')
        self.setGeometry(100, 100, 1400, 800)

        # Main layout with splitter for sidebar and main content
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        
        # Sidebar for chat sessions
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(250)
        self.sidebar.itemClicked.connect(self.load_session)
        
        # Button to create new session
        new_session_button = QPushButton("New Chat")
        new_session_button.clicked.connect(self.create_new_session)
        
        # Sidebar layout
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(self.sidebar)
        sidebar_layout.addWidget(new_session_button)

        # Main chat area
        main_area = QWidget()
        main_area_layout = QVBoxLayout(main_area)

        # Header
        header_label = QLabel("Neurocura AI Assistant")
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        main_area_layout.addWidget(header_label)

        # Chat display using QListWidget
        self.chat_display = QListWidget()
        self.chat_display.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.chat_display.customContextMenuRequested.connect(self.show_context_menu)
        main_area_layout.addWidget(self.chat_display)

        # Input area
        self.input_box = QTextEdit()
        self.input_box.setMaximumHeight(100)
        main_area_layout.addWidget(self.input_box)

        # Button layout
        button_layout = QHBoxLayout()

        # Send button
        send_button = QPushButton('Send Message')
        send_button.clicked.connect(self.send_message)
        button_layout.addWidget(send_button)

        # Export button
        export_button = QPushButton("Export Conversation")
        export_button.clicked.connect(self.export_conversation)
        button_layout.addWidget(export_button)

        # Import button
        import_button = QPushButton("Import Conversation")
        import_button.clicked.connect(self.import_conversation)
        button_layout.addWidget(import_button)

        main_area_layout.addLayout(button_layout)

        # Add layouts to main layout
        main_layout.addLayout(sidebar_layout)
        main_layout.addWidget(main_area)

        self.setCentralWidget(main_widget)

        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready')

        # Populate sidebar with existing sessions
        self.populate_sidebar()
        
        # Create initial session if no sessions exist
        if not self.session_manager.sessions:
            self.create_new_session()

        # Apply fusion style colors
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.setPalette(palette)

        # Apply stylesheet for more customization
        self.setStyleSheet("""
            QWidget {
                background-color: #353535;
                color: white;
                font-size: 12px;
            }
            QListWidget, QTextEdit {
                background-color: #252525;
                border: 1px solid #1A1A1A;
                color: white;
            }
            QPushButton {
                background-color: #4A4A4A;
                color: white;
                border: 1px solid #1A1A1A;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
            }
            QLabel {
                color: white;
            }
        """)

    def show_context_menu(self, position):
        # Get the selected item
        current_item = self.chat_display.currentItem()
        if not current_item:
            return

        # Create context menu
        context_menu = QMenu(self)
        
        # Edit action
        edit_action = QAction("Edit Message", self)
        edit_action.triggered.connect(self.edit_message)
        context_menu.addAction(edit_action)
        
        # Delete action
        delete_action = QAction("Delete Message", self)
        delete_action.triggered.connect(self.delete_message)
        context_menu.addAction(delete_action)
        
        # Show the context menu
        context_menu.exec(self.chat_display.mapToGlobal(position))

    def edit_message(self):
        # Get the current selected item
        current_item = self.chat_display.currentItem()
        if not current_item:
            return

        # Open input dialog to edit the message
        text, ok = QInputDialog.getText(
            self, 
            "Edit Message", 
            "Edit your message:", 
            text=current_item.text()
        )
        
        if ok and text:
            # Update the message text
            current_item.setText(text)
            
            # Update the underlying message in the session
            for message in self.current_session.messages:
                if message.text == current_item.text():
                    message.text = text
                    break
            
            # Save the updated session
            self.session_manager.save_session(self.current_session)

    def delete_message(self):
        # Get the current selected item
        current_item = self.chat_display.currentItem()
        if not current_item:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Delete Message", 
            "Are you sure you want to delete this message?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from the session
            row = self.chat_display.row(current_item)
            del self.current_session.messages[row]
            
            # Remove from chat display
            self.chat_display.takeItem(row)
            
            # Save the updated session
            self.session_manager.save_session(self.current_session)

    def export_conversation(self):
        # Prevent export without an active session
        if not self.current_session:
            QMessageBox.warning(self, "Export Error", "No active session to export.")
            return

        # Open file dialog to choose export location
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Conversation", 
            f"{self.current_session.title}.txt", 
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    for msg in self.current_session.messages:
                        speaker = "You" if msg.is_user else "AI"
                        file.write(f"{speaker}: {msg.text}\n")
                
                QMessageBox.information(self, "Export Successful", f"Conversation exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")

    def import_conversation(self):
        # Open file dialog to choose file to import
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            "Import Conversation", 
            "", 
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                # Create a new session for import
                session = self.session_manager.create_session(f"Imported Chat {datetime.now().strftime('%Y%m%d_%H%M%S')}")
                
                # Read the file
                with open(filename, 'r', encoding='utf-8') as file:
                    for line in file:
                        line = line.strip()
                        if line:
                            # Determine if message is from user or AI
                            is_user = line.startswith("You:")
                            message_text = line.split(": ", 1)[1] if ": " in line else line
                            
                            # Create and add message
                            message = Message(message_text, is_user=is_user)
                            session.add_message(message)
                
                # Refresh sidebar and load the new session
                self.populate_sidebar()
                self.load_session_by_id(session.id)
                
                QMessageBox.information(self, "Import Successful", f"Conversation imported from {filename}")
            
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import: {str(e)}")

    def populate_sidebar(self):
        """Populate the sidebar with existing chat sessions."""
        self.sidebar.clear()
        for session_id, session in sorted(
            self.session_manager.sessions.items(),
            key=lambda x: x[1].created_at,
            reverse=True
        ):
            item = QListWidgetItem(session.title)
            item.setData(Qt.ItemDataRole.UserRole, session_id)
            self.sidebar.addItem(item)

    def load_session(self, item):
        """Load a chat session when clicked in the sidebar."""
        session_id = item.data(Qt.ItemDataRole.UserRole)
        self.load_session_by_id(session_id)

    def load_session_by_id(self, session_id):
        """Load a chat session by its ID."""
        session = self.session_manager.sessions.get(session_id)
        if session:
            self.current_session = session
            self.chat_display.clear()
            
            # Load all messages from the session
            for message in session.messages:
                message_widget = MessageWidget(message)
                self.chat_display.addItem(message_widget)
            
            # Scroll to the bottom
            self.chat_display.scrollToBottom()
            
            # Update window title
            self.setWindowTitle(f'Neurocura AI System - {session.title}')

    def create_new_session(self):
        """Create a new chat session."""
        title, ok = QInputDialog.getText(
            self,
            'New Chat Session',
            'Enter a title for the new chat:',
            text=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        if ok:
            # Create new session
            session = self.session_manager.create_session(title)
            
            # Update sidebar
            self.populate_sidebar()
            
            # Load the new session
            self.load_session_by_id(session.id)

    def send_message(self):
        """Send a message in the current chat session."""
        if not self.current_session:
            QMessageBox.warning(self, "Error", "No active chat session.")
            return

        # Get message text and clear input box
        message_text = self.input_box.toPlainText().strip()
        self.input_box.clear()

        if not message_text:
            return

        # Create and add user message
        user_message = Message(message_text, is_user=True)
        self.current_session.add_message(user_message)
        self.chat_display.addItem(MessageWidget(user_message))

        # Save session after adding message
        self.session_manager.save_session(self.current_session)

        # Create and start AI worker thread
        self.worker = AIWorker(message_text, self.api_key)
        self.worker.finished.connect(self.handle_ai_response)
        self.worker.error.connect(self.handle_ai_error)
        self.worker.start()

        # Disable input while waiting for response
        self.input_box.setEnabled(False)
        self.status_bar.showMessage('Waiting for AI response...')

    def handle_ai_response(self, response_text):
        """Handle the AI response when received."""
        # Create and add AI message
        ai_message = Message(response_text, is_user=False)
        self.current_session.add_message(ai_message)
        self.chat_display.addItem(MessageWidget(ai_message))

        # Save session after adding AI response
        self.session_manager.save_session(self.current_session)

        # Re-enable input
        self.input_box.setEnabled(True)
        self.status_bar.showMessage('Ready')
        
        # Scroll to the bottom
        self.chat_display.scrollToBottom()

    def handle_ai_error(self, error_message):
        """Handle any errors in AI response generation."""
        QMessageBox.critical(self, "AI Error", f"Error generating response: {error_message}")
        self.input_box.setEnabled(True)
        self.status_bar.showMessage('Error in AI response')

def main():
    app = QApplication(sys.argv)
    ex = NeurocuraApp()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()