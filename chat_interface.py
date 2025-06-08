from typing import Dict, List, Optional, Callable
import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import threading
import time
from datetime import datetime
from conversation_manager import ConversationManager, Message
from services.azure_openai_service import AzureOpenAIService
import asyncio
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import wave
import os
from PIL import Image, ImageTk

class VoiceRecorder:
    def __init__(self):
        self.recording = False
        self.frames = []
        self.sample_rate = 44100
        
    def start_recording(self):
        self.recording = True
        self.frames = []
        
        def callback(indata, frames, time, status):
            if self.recording:
                self.frames.append(indata.copy())
                
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            callback=callback
        )
        self.stream.start()
        
    def stop_recording(self):
        self.recording = False
        self.stream.stop()
        self.stream.close()
        
        if not os.path.exists('recordings'):
            os.makedirs('recordings')
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recordings/recording_{timestamp}.wav"
        
        if self.frames:
            audio_data = np.concatenate(self.frames, axis=0)
            write(filename, self.sample_rate, audio_data)
            return filename
        return None

class ChatInterface:
    def __init__(self, root):
        """Initialize chat interface"""
        self.root = root
        self.root.title("Legal Assistant Chat")
        self.conversation_manager = ConversationManager()
        self.openai_service = AzureOpenAIService()
        self.conversation_history = []
        self.voice_recorder = VoiceRecorder()
        
        # Configure root window
        self.root.geometry("1200x800")  # Increased window size
        self.setup_ui()
        
        # Initialize state
        self.is_typing = False
        self.is_recording = False
        self.typing_thread = None
        self.current_view = "chat"  # Track current view
        
        # Configure text tags
        self.configure_tags()

    def configure_tags(self):
        """Configure text tags for message styling"""
        self.chat_display.tag_configure("user_name", foreground="blue", font=("Arial", 10, "bold"))
        self.chat_display.tag_configure("user_message", font=("Arial", 10))
        self.chat_display.tag_configure("system_name", foreground="green", font=("Arial", 10, "bold"))
        self.chat_display.tag_configure("system_message", font=("Arial", 10))
        self.chat_display.tag_configure("error_message", foreground="red", font=("Arial", 10))
        self.chat_display.tag_configure("typing_indicator", foreground="gray", font=("Arial", 10, "italic"))

    def setup_ui(self):
        """Setup the user interface"""
        # Create main container with padding
        self.main_container = ttk.Frame(self.root, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        self.main_container.grid_columnconfigure(1, weight=1)  # Changed to 1 to account for sidebar
        self.main_container.grid_rowconfigure(0, weight=1)

        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.content_container = ttk.Frame(self.main_container)
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Configure content container grid weights
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        # Create chat area
        self.create_chat_area()
        
        # Create input area
        self.create_input_area()
        
        # Create progress bar
        self.create_progress_bar()
        
        # Create quick reply area
        self.create_quick_reply_area()
        
        # Apply styles
        self.apply_styles()
        
        # Start conversation
        self.start_conversation()

    def create_sidebar(self):
        """Create the sidebar navigation"""
        # Sidebar container
        self.sidebar = ttk.Frame(self.main_container, style="Sidebar.TFrame")
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        
        # Add logo or title
        title_label = ttk.Label(
            self.sidebar,
            text="Legal Assistant",
            style="SidebarTitle.TLabel"
        )
        title_label.pack(pady=(0, 20), padx=10)
        
        # Navigation buttons
        nav_buttons = [
            ("💬 Chat", lambda: self.switch_view("chat")),
            ("📋 History", lambda: self.switch_view("history")),
            ("⚙️ Settings", lambda: self.switch_view("settings")),
            ("❓ Help", lambda: self.switch_view("help"))
        ]
        
        for text, command in nav_buttons:
            btn = ttk.Button(
                self.sidebar,
                text=text,
                command=command,
                style="Sidebar.TButton",
                width=20
            )
            btn.pack(pady=5, padx=10)

    def create_chat_area(self):
        """Create the chat message area"""
        # Chat container with border
        chat_frame = ttk.Frame(self.content_container, style="ChatFrame.TFrame")
        chat_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        # Configure grid weights
        chat_frame.grid_columnconfigure(0, weight=1)
        chat_frame.grid_rowconfigure(0, weight=1)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Arial", 11),  # Increased font size
            padx=15,
            pady=15,
            height=25,
            background="#ffffff",
            borderwidth=0
        )
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.chat_display.config(state=tk.DISABLED)
        
        # Bind scroll event
        self.chat_display.bind("<MouseWheel>", self.on_mousewheel)

    def create_input_area(self):
        """Create the message input area"""
        # Input container with border
        input_frame = ttk.Frame(self.content_container, style="InputFrame.TFrame")
        input_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Configure grid weights
        input_frame.grid_columnconfigure(1, weight=1)
        
        # Voice input button
        self.voice_button = ttk.Button(
            input_frame,
            text="🎤",
            command=self.toggle_recording,
            style="Round.TButton",
            width=3
        )
        self.voice_button.grid(row=0, column=0, padx=(10, 10), pady=10)
        
        # Message input with placeholder
        self.message_input = ttk.Entry(
            input_frame,
            font=("Arial", 11),
            style="Chat.TEntry"
        )
        self.message_input.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=10)
        self.set_input_placeholder()
        
        # Send button
        self.send_button = ttk.Button(
            input_frame,
            text="Send",
            command=lambda: self.send_message(),
            style="Primary.TButton",
            width=10
        )
        self.send_button.grid(row=0, column=2, padx=(0, 10), pady=10)
        
        # Bind enter key
        self.message_input.bind("<Return>", lambda e: self.send_message())
        
        # Bind focus events for placeholder text
        self.message_input.bind("<FocusIn>", self.on_entry_click)
        self.message_input.bind("<FocusOut>", self.on_focus_out)

    def set_input_placeholder(self):
        """Set placeholder text for input field"""
        self.message_input.insert(0, "Type your message here...")
        self.message_input.config(foreground="gray")

    def on_entry_click(self, event):
        """Handle input field click"""
        if self.message_input.get() == "Type your message here...":
            self.message_input.delete(0, tk.END)
            self.message_input.config(foreground="black")

    def on_focus_out(self, event):
        """Handle input field focus out"""
        if self.message_input.get() == "":
            self.set_input_placeholder()

    def switch_view(self, view_name):
        """Switch between different views"""
        self.current_view = view_name
        
        # Update UI based on selected view
        if view_name == "chat":
            self.content_container.tkraise()
        elif view_name == "history":
            self.show_history_view()
        elif view_name == "settings":
            self.show_settings_view()
        elif view_name == "help":
            self.show_help_view()

    def show_history_view(self):
        """Show conversation history view"""
        # Create history window
        history_window = tk.Toplevel(self.root)
        history_window.title("Conversation History")
        history_window.geometry("600x400")
        
        # Add history content
        history_text = scrolledtext.ScrolledText(
            history_window,
            wrap=tk.WORD,
            font=("Arial", 11),
            padx=15,
            pady=15
        )
        history_text.pack(fill=tk.BOTH, expand=True)
        
        # Add conversation history
        for message in self.conversation_history:
            timestamp = datetime.fromisoformat(message.timestamp).strftime("%Y-%m-%d %H:%M")
            sender = "You" if message.sender == "user" else "Assistant"
            history_text.insert(tk.END, f"{timestamp} - {sender}:\n{message.content}\n\n")
        
        history_text.config(state=tk.DISABLED)

    def show_settings_view(self):
        """Show settings view"""
        # Create settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        
        # Add settings options
        ttk.Label(settings_window, text="Settings", font=("Arial", 16, "bold")).pack(pady=20)
        
        # Theme selection
        ttk.Label(settings_window, text="Theme:").pack(pady=5)
        theme_var = tk.StringVar(value="light")
        ttk.Radiobutton(settings_window, text="Light", variable=theme_var, value="light").pack()
        ttk.Radiobutton(settings_window, text="Dark", variable=theme_var, value="dark").pack()
        
        # Font size selection
        ttk.Label(settings_window, text="Font Size:").pack(pady=5)
        font_size_var = tk.StringVar(value="medium")
        ttk.Radiobutton(settings_window, text="Small", variable=font_size_var, value="small").pack()
        ttk.Radiobutton(settings_window, text="Medium", variable=font_size_var, value="medium").pack()
        ttk.Radiobutton(settings_window, text="Large", variable=font_size_var, value="large").pack()

    def show_help_view(self):
        """Show help view"""
        # Create help window
        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("600x400")
        
        # Add help content
        help_text = scrolledtext.ScrolledText(
            help_window,
            wrap=tk.WORD,
            font=("Arial", 11),
            padx=15,
            pady=15
        )
        help_text.pack(fill=tk.BOTH, expand=True)
        
        # Add help content
        help_content = """
Legal Assistant Help

Getting Started:
1. Type your legal question in the chat box
2. Use the voice input button (🎤) to speak your question
3. Click Send or press Enter to submit

Features:
- Text and voice input
- Multi-language support
- Legal document assistance
- Form filling help

Tips:
- Be specific with your questions
- Use clear language
- Provide relevant details
- Check the conversation history for previous answers

For more help, visit our documentation or contact support.
"""
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)

    def apply_styles(self):
        """Apply custom styles to the interface"""
        style = ttk.Style()
        
        # Configure frame styles
        style.configure(
            "Sidebar.TFrame",
            background="#f0f0f0",
            relief="flat"
        )
        
        style.configure(
            "ChatFrame.TFrame",
            background="#ffffff",
            relief="solid",
            borderwidth=1
        )
        
        style.configure(
            "InputFrame.TFrame",
            background="#ffffff",
            relief="solid",
            borderwidth=1
        )
        
        # Configure button styles
        style.configure(
            "Sidebar.TButton",
            padding=10,
            font=("Arial", 11),
            background="#f0f0f0",
            relief="flat"
        )
        
        style.configure(
            "Primary.TButton",
            padding=10,
            font=("Arial", 11),
            background="#007bff",
            foreground="#ffffff"
        )
        
        style.configure(
            "Round.TButton",
            padding=5,
            font=("Arial", 11),
            relief="flat"
        )
        
        # Configure label styles
        style.configure(
            "SidebarTitle.TLabel",
            font=("Arial", 16, "bold"),
            background="#f0f0f0",
            padding=(0, 20)
        )
        
        # Configure entry style
        style.configure(
            "Chat.TEntry",
            padding=10,
            relief="flat"
        )

    def show_typing_indicator(self):
        """Show typing indicator"""
        if not self.is_typing:
            self.is_typing = True
            self.update_typing_indicator()

    def hide_typing_indicator(self):
        """Hide typing indicator"""
        self.is_typing = False
        self.chat_display.config(state=tk.NORMAL)
        # Remove typing indicator if present
        last_line_start = self.chat_display.index("end-2c linestart")
        last_line = self.chat_display.get(last_line_start, "end-1c")
        if "Typing" in last_line:
            self.chat_display.delete(last_line_start, "end-1c")
        self.chat_display.config(state=tk.DISABLED)

    def update_typing_indicator(self):
        """Update typing indicator animation"""
        if not self.is_typing:
            return
            
        self.chat_display.config(state=tk.NORMAL)
        last_line_start = self.chat_display.index("end-2c linestart")
        last_line = self.chat_display.get(last_line_start, "end-1c")
        
        if "Typing" in last_line:
            self.chat_display.delete(last_line_start, "end-1c")
        
        self.chat_display.insert(tk.END, "\nTyping...", "typing_indicator")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        if self.is_typing:
            self.root.after(500, self.update_typing_indicator)

    def add_message(self, message: Message):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Format timestamp
        timestamp = datetime.fromisoformat(message.timestamp).strftime("%H:%M")
        
        # Add message with appropriate styling
        if message.sender == "user":
            self.chat_display.insert(tk.END, f"\nYou ({timestamp}):\n", "user_name")
            self.chat_display.insert(tk.END, f"{message.content}\n", "user_message")
        else:
            self.chat_display.insert(tk.END, f"\nAssistant ({timestamp}):\n", "system_name")
            self.chat_display.insert(tk.END, f"{message.content}\n", "system_message")
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def update_quick_replies(self, quick_replies: List[str]):
        """Update quick reply buttons"""
        # Clear existing quick replies
        for widget in self.quick_reply_container.winfo_children():
            widget.destroy()
            
        # Add new quick reply buttons
        for reply in quick_replies:
            btn = ttk.Button(
                self.quick_reply_container,
                text=reply,
                style="Quick.TButton",
                command=lambda r=reply: self.handle_quick_reply(r)
            )
            btn.pack(side=tk.LEFT, padx=(0, 5))

    def update_progress(self, percentage: float):
        """Update progress bar and label"""
        self.progress_bar["value"] = percentage
        self.progress_label.config(text=f"Progress: {percentage:.1f}%")

    def send_message(self, event=None):
        """Send a message"""
        message = self.message_input.get().strip()
        if message:
            # Clear input field
            self.message_input.delete(0, tk.END)
            
            # Add user message to chat
            user_message = self.conversation_manager.add_message(
                content=message,
                sender="user"
            )
            self.add_message(user_message)
            
            # Disable input temporarily
            self.message_input.config(state=tk.DISABLED)
            self.send_button.config(state=tk.DISABLED)
            
            # Show typing indicator
            self.show_typing_indicator()
            
            # Process the message in a separate thread
            threading.Thread(
                target=self.process_message,
                args=(message,),
                daemon=True
            ).start()

    async def send_async_message(self, message):
        """Send a message asynchronously"""
        try:
            response = await self.openai_service.get_legal_response(self.conversation_history, message)
            return {
                "status": "success",
                "response": response
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def process_user_input(self, user_input):
        self.conversation_history.append(user_input)
        
        try:
            response = await self.openai_service.get_legal_response(
                self.conversation_history, 
                user_input
            )
            self.conversation_history.append(response)
            return response
        except Exception as e:
            self.logger.error(f"Error getting response from Azure OpenAI: {str(e)}")
            return "I apologize, but I encountered an error processing your request."

    def process_message(self, message: str):
        """Process a message and handle the response"""
        try:
            # Create and run event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Get response
            response = loop.run_until_complete(self.send_async_message(message))
            
            # Close the loop
            loop.close()
            
            # Handle the response
            if response["status"] == "success":
                # Add assistant message to chat
                assistant_message = self.conversation_manager.add_message(
                    content=response["response"],
                    sender="assistant"
                )
                
                # Hide typing indicator and enable input
                self.hide_typing_indicator()
                self.message_input.config(state=tk.NORMAL)
                self.send_button.config(state=tk.NORMAL)
                
                # Add message to display
                self.add_message(assistant_message)
                
                # Update conversation history
                self.conversation_history.extend([message, response["response"]])
            else:
                # Handle error
                error_msg = f"Error: {response['error']}"
                error_message = self.conversation_manager.add_message(
                    content=error_msg,
                    sender="assistant",
                    message_type="error"
                )
                
                # Hide typing indicator and enable input
                self.hide_typing_indicator()
                self.message_input.config(state=tk.NORMAL)
                self.send_button.config(state=tk.NORMAL)
                
                # Add error message to display
                self.add_message(error_message)
                
        except Exception as e:
            # Handle unexpected errors
            error_msg = f"Unexpected error: {str(e)}"
            error_message = self.conversation_manager.add_message(
                content=error_msg,
                sender="assistant",
                message_type="error"
            )
            
            # Hide typing indicator and enable input
            self.hide_typing_indicator()
            self.message_input.config(state=tk.NORMAL)
            self.send_button.config(state=tk.NORMAL)
            
            # Add error message to display
            self.add_message(error_message)

    def handle_response(self, result: Dict):
        """Handle the response from message processing"""
        self.hide_typing_indicator()
        
        if result["status"] == "error":
            # Show validation errors
            error_message = "\n".join(result["errors"])
            system_message = self.conversation_manager.add_message(
                content=f"Error: {error_message}",
                sender="system",
                message_type="error"
            )
            self.add_message(system_message)
            
        elif result["status"] == "success":
            # Show next question
            next_question = result["next_question"]
            system_message = self.conversation_manager.add_message(
                content=next_question["text"],
                sender="system"
            )
            self.add_message(system_message)
            
            # Update quick replies if available
            if "quick_replies" in next_question:
                self.update_quick_replies(next_question["quick_replies"])
            else:
                self.update_quick_replies([])
                
        elif result["status"] == "completed":
            # Show completion message
            system_message = self.conversation_manager.add_message(
                content="Thank you! I have all the information I need.",
                sender="system"
            )
            self.add_message(system_message)
            
        # Update progress
        self.update_progress(result["completion_percentage"])

    def handle_quick_reply(self, reply: str):
        """Handle quick reply button click"""
        self.message_input.insert(0, reply)
        self.send_message()

    def start_conversation(self):
        """Start the conversation"""
        # Show welcome message
        welcome_message = self.conversation_manager.add_message(
            content="Hello! I'm your legal assistant. I'll help you collect information about your case.",
            sender="system"
        )
        self.add_message(welcome_message)
        
        # Get first question
        first_question = self.conversation_manager.get_next_question()
        if first_question:
            question_message = self.conversation_manager.add_message(
                content=first_question["text"],
                sender="system"
            )
            self.add_message(question_message)
            
            # Update quick replies if available
            if "quick_replies" in first_question:
                self.update_quick_replies(first_question["quick_replies"])

    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.chat_display.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def toggle_recording(self):
        """Toggle voice recording on/off"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start voice recording"""
        self.is_recording = True
        self.voice_button.configure(text="⏺")
        self.voice_recorder.start_recording()
        
        # Add recording indicator to chat
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "\nRecording audio...\n", "system_message")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def stop_recording(self):
        """Stop voice recording and process the audio"""
        self.is_recording = False
        self.voice_button.configure(text="🎤")
        
        # Stop recording and get the filename
        audio_file = self.voice_recorder.stop_recording()
        
        if audio_file:
            # Add processing indicator to chat
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, "Processing audio...\n", "system_message")
            self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)
            
            # Process the audio file (you'll need to implement this based on your speech-to-text service)
            self.process_audio_file(audio_file)

    def process_audio_file(self, audio_file):
        """Process the recorded audio file using speech-to-text"""
        try:
            # Here you would typically send the audio file to a speech-to-text service
            # For now, we'll just add a placeholder message
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, f"Audio file saved: {audio_file}\n", "system_message")
            self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)
            
            # TODO: Implement actual speech-to-text processing
            # You can use Azure Speech Services, Google Speech-to-Text, or other services
            
        except Exception as e:
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, f"Error processing audio: {str(e)}\n", "error_message")
            self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)