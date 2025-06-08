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

class ChatInterface:
    def __init__(self, root):
        """Initialize chat interface"""
        self.root = root
        self.root.title("Legal Assistant Chat")
        self.conversation_manager = ConversationManager()
        self.openai_service = AzureOpenAIService()
        self.conversation_history = []
        
        # Configure root window
        self.root.geometry("800x600")
        self.setup_ui()
        
        # Initialize state
        self.is_typing = False
        self.typing_thread = None
        
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
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

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

    def create_chat_area(self):
        """Create the chat message area"""
        # Chat container
        chat_container = ttk.Frame(self.main_container)
        chat_container.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        # Configure grid weights
        chat_container.grid_columnconfigure(0, weight=1)
        chat_container.grid_rowconfigure(0, weight=1)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            font=("Arial", 10),
            padx=10,
            pady=10,
            height=20
        )
        self.chat_display.grid(row=0, column=0, sticky="nsew")
        self.chat_display.config(state=tk.DISABLED)
        
        # Bind scroll event
        self.chat_display.bind("<MouseWheel>", self.on_mousewheel)

    def create_input_area(self):
        """Create the message input area"""
        # Input container
        input_container = ttk.Frame(self.main_container)
        input_container.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Configure grid weights
        input_container.grid_columnconfigure(1, weight=1)
        
        # Message input
        self.message_input = ttk.Entry(
            input_container,
            font=("Arial", 10)
        )
        self.message_input.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        # Send button
        self.send_button = ttk.Button(
            input_container,
            text="Send",
            command=lambda: self.send_message(),
            width=10
        )
        self.send_button.grid(row=0, column=2)
        
        # Bind enter key
        self.message_input.bind("<Return>", lambda e: self.send_message())

    def create_progress_bar(self):
        """Create the progress tracking bar"""
        # Progress container
        progress_container = ttk.Frame(self.main_container)
        progress_container.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        # Progress label
        self.progress_label = ttk.Label(
            progress_container,
            text="Progress: 0%"
        )
        self.progress_label.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_container,
            mode='determinate',
            length=200
        )
        self.progress_bar.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)

    def create_quick_reply_area(self):
        """Create the quick reply buttons area"""
        self.quick_reply_container = ttk.Frame(self.main_container)
        self.quick_reply_container.grid(row=3, column=0, sticky="ew")

    def apply_styles(self):
        """Apply custom styles to the interface"""
        style = ttk.Style()
        
        # Configure frame styles
        style.configure("TFrame", background="#ffffff")
        
        # Configure button styles
        style.configure(
            "TButton",
            padding=5,
            font=("Arial", 10)
        )
        
        style.configure(
            "Quick.TButton",
            padding=5,
            font=("Arial", 9)
        )
        
        # Configure label styles
        style.configure(
            "TLabel",
            font=("Arial", 10),
            background="#ffffff"
        )
        
        # Configure progress bar style
        style.configure(
            "TProgressbar",
            thickness=20,
            background="#4CAF50"
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