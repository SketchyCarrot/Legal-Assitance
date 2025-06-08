from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.voice_endpoints import router as voice_router
from services.bhashini_service import BhashiniService
import tkinter as tk
from tkinter import ttk
from chat_interface import ChatInterface
import logging
import os
import sys
from PIL import Image, ImageTk

# Initialize FastAPI app
try:
    app = FastAPI(title="Legal Assistant API")
except Exception as e:
    logging.error(f"Failed to initialize FastAPI: {str(e)}")
    raise

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get BhashiniService instance
async def get_bhashini_service():
    async with BhashiniService() as service:
        yield service

# Update router to use the service dependency
app.include_router(
    voice_router,
    prefix="/api",
    tags=["voice"],
    dependencies=[Depends(get_bhashini_service)]
)

# Add startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logging.info("Starting up FastAPI application")

@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Shutting down FastAPI application")

# Tkinter GUI Application
class LegalAssistantApp:
    def __init__(self):
        # Setup logging
        self.setup_logging()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Legal Assistant")
        
        # Configure window
        self.setup_window()
        
        # Create chat interface
        self.app = ChatInterface(self.root)
        
        # Configure window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'app.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_window(self):
        """Configure the main window"""
        # Set window size and position
        window_width = 800
        window_height = 600
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        # Set window geometry
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Make window resizable
        self.root.minsize(600, 400)
        
        # Set window icon
        self.set_window_icon()
        
        # Configure theme
        self.configure_theme()

    def set_window_icon(self):
        """Set the window icon"""
        icon_paths = [
            "assets/icon.ico",
            "assets/icon.png",
            os.path.join(os.path.dirname(__file__), "assets/icon.ico"),
            os.path.join(os.path.dirname(__file__), "assets/icon.png")
        ]
        
        for icon_path in icon_paths:
            try:
                if icon_path.endswith('.ico'):
                    self.root.iconbitmap(icon_path)
                    break
                elif icon_path.endswith('.png'):
                    icon = Image.open(icon_path)
                    photo = ImageTk.PhotoImage(icon)
                    self.root.iconphoto(True, photo)
                    break
            except Exception:
                continue
        else:
            self.logger.warning("Could not load application icon")

    def configure_theme(self):
        """Configure custom theme"""
        style = ttk.Style()
        
        # Try to use 'clam' theme as base
        try:
            style.theme_use('clam')
        except tk.TclError:
            self.logger.warning("Could not load 'clam' theme, using default")
        
        # Configure colors
        style.configure(
            ".",
            background="#ffffff",
            foreground="#333333",
            font=("Arial", 10)
        )
        
        # Configure specific elements
        style.configure(
            "TButton",
            padding=5,
            background="#4CAF50",
            foreground="#ffffff"
        )
        
        style.map(
            "TButton",
            background=[("active", "#45a049"), ("disabled", "#cccccc")],
            foreground=[("disabled", "#666666")]
        )
        
        style.configure(
            "TEntry",
            padding=5,
            fieldbackground="#ffffff"
        )
        
        style.configure(
            "TFrame",
            background="#ffffff"
        )
        
        style.configure(
            "TProgressbar",
            thickness=20,
            background="#4CAF50"
        )

    def on_closing(self):
        """Handle window closing"""
        if self.app.conversation_manager.state.collected_data:
            # Create data directory if it doesn't exist
            data_dir = "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            # Export data before closing
            try:
                export_path = os.path.join(data_dir, "collected_data.json")
                with open(export_path, "w") as f:
                    f.write(self.app.conversation_manager.export_data())
                self.logger.info(f"Successfully exported collected data to {export_path}")
            except Exception as e:
                self.logger.error(f"Failed to export data: {str(e)}")
        
        self.root.destroy()

    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Application error: {str(e)}")
            raise

def main():
    app = LegalAssistantApp()
    app.run()

if __name__ == "__main__":
    import uvicorn
    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        # Run FastAPI server
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        # Run Tkinter app
        main()