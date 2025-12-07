"""
Twitch Chat Tools

Main chat monitoring and interaction tool for Twitch streams. Connects to
Twitch IRC, displays chat messages in a log window, and provides basic
chat interaction capabilities.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import json
from pathlib import Path
from typing import Optional
from datetime import datetime


class ChatTools:
    """Main chat tools application with Twitch integration."""
    
    def __init__(self) -> None:
        """Initialise the chat tools application."""
        self.root = tk.Tk()
        self.root.title("Chat Tools")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.config_path = Path(__file__).parent / "config" / "chat_tools_config.json"
        self.config: Optional[dict] = None
        self.is_connected: bool = False
        
        # TODO: Add twitchio bot instance variable
        # self.bot: Optional[TwitchBot] = None
        
        self._create_ui()
        self._load_config()
    
    def _create_ui(self) -> None:
        """Create the chat tools UI components."""
        # Title bar with connection status
        header_frame = tk.Frame(self.root, bg="#2C3E50", pady=10)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text="Twitch Chat Tools",
            font=("Arial", 16, "bold"),
            bg="#2C3E50",
            fg="white"
        )
        title_label.pack(side=tk.LEFT, padx=20)
        
        self.status_label = tk.Label(
            header_frame,
            text="● Disconnected",
            font=("Arial", 11),
            bg="#2C3E50",
            fg="#E74C3C"
        )
        self.status_label.pack(side=tk.RIGHT, padx=20)
        
        # Log display area
        log_frame = tk.Frame(self.root, padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            log_frame,
            text="Chat Log:",
            font=("Arial", 11, "bold")
        ).pack(anchor="w")
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 10),
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg="#F8F9FA",
            fg="#2C3E50"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Control buttons
        control_frame = tk.Frame(self.root, pady=10)
        control_frame.pack(fill=tk.X)
        
        self.connect_btn = tk.Button(
            control_frame,
            text="Connect",
            command=self.toggle_connection,
            width=15,
            font=("Arial", 10, "bold"),
            bg="#4CAF50",
            fg="white"
        )
        self.connect_btn.pack(side=tk.LEFT, padx=10)
        
        clear_btn = tk.Button(
            control_frame,
            text="Clear Log",
            command=self.clear_log,
            width=15,
            font=("Arial", 10)
        )
        clear_btn.pack(side=tk.LEFT, padx=10)
        
        settings_btn = tk.Button(
            control_frame,
            text="Open Settings",
            command=self.open_settings,
            width=15,
            font=("Arial", 10)
        )
        settings_btn.pack(side=tk.LEFT, padx=10)
    
    def _load_config(self) -> None:
        """Load Twitch configuration from file."""
        if not self.config_path.exists():
            self.log_message(
                "No configuration found. Please open settings to configure Twitch connection.",
                "WARNING"
            )
            return
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            
            self.log_message(
                f"Configuration loaded for channel: {self.config.get('channel', 'unknown')}",
                "INFO"
            )
            
        except Exception as e:
            self.log_message(f"Failed to load configuration: {e}", "ERROR")
    
    def log_message(self, message: str, level: str = "INFO") -> None:
        """Add a message to the chat log with timestamp.
        
        Args:
            message: The message to log
            level: Log level (INFO, WARNING, ERROR, CHAT, etc.)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}\n"
        
        # Enable text widget, insert message, disable again
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)  # Auto-scroll to bottom
        self.log_text.config(state=tk.DISABLED)
    
    def clear_log(self) -> None:
        """Clear the chat log display."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log_message("Log cleared", "INFO")
    
    def toggle_connection(self) -> None:
        """Toggle connection to Twitch chat."""
        if self.is_connected:
            self.disconnect_from_twitch()
        else:
            self.connect_to_twitch()
    
    def connect_to_twitch(self) -> None:
        """Connect to Twitch IRC using configured credentials."""
        # TODO: Implement Twitch IRC connection using twitchio
        # TODO: Create bot instance with credentials from config
        # TODO: Start bot in separate thread/async task
        # TODO: Register event handlers for messages
        # TODO: Update connection status on success/failure
        
        if not self.config:
            messagebox.showerror(
                "Configuration Missing",
                "No configuration found. Please configure settings first."
            )
            self.open_settings()
            return
        
        # Placeholder for actual connection
        self.log_message("Attempting to connect to Twitch...", "INFO")
        
        # Simulate connection (remove when implementing real connection)
        messagebox.showinfo(
            "Connection",
            "Twitch connection not yet implemented.\n\n"
            "This will connect to Twitch IRC using twitchio library."
        )
        
        # TODO: Remove simulation below when implementing real connection
        # self.is_connected = True
        # self._update_connection_status()
        # self.log_message(f"Connected to #{self.config['channel']}", "SUCCESS")
    
    def disconnect_from_twitch(self) -> None:
        """Disconnect from Twitch IRC."""
        # TODO: Stop bot instance
        # TODO: Close IRC connection
        # TODO: Clean up async tasks
        # TODO: Update connection status
        
        self.log_message("Disconnecting from Twitch...", "INFO")
        
        self.is_connected = False
        self._update_connection_status()
        self.log_message("Disconnected from Twitch", "INFO")
    
    def _update_connection_status(self) -> None:
        """Update the connection status indicator."""
        if self.is_connected:
            self.status_label.config(
                text="● Connected",
                fg="#2ECC71"
            )
            self.connect_btn.config(
                text="Disconnect",
                bg="#E74C3C"
            )
        else:
            self.status_label.config(
                text="● Disconnected",
                fg="#E74C3C"
            )
            self.connect_btn.config(
                text="Connect",
                bg="#4CAF50"
            )
    
    def open_settings(self) -> None:
        """Open the chat tools settings window."""
        # TODO: Launch settings GUI
        # TODO: Reload config after settings window closes
        
        import subprocess
        import sys
        
        settings_path = Path(__file__).parent / "chat_tools_settings.py"
        
        try:
            subprocess.Popen([
                sys.executable,
                str(settings_path)
            ], cwd=str(Path(__file__).parent))
            
            self.log_message("Settings window opened", "INFO")
            
        except Exception as e:
            self.log_message(f"Failed to open settings: {e}", "ERROR")
    
    # TODO: Implement event handlers for Twitch chat
    # def on_message_received(self, message) -> None:
    #     """Handle incoming Twitch chat message."""
    #     pass
    
    # def on_user_join(self, user) -> None:
    #     """Handle user joining chat."""
    #     pass
    
    # def on_user_part(self, user) -> None:
    #     """Handle user leaving chat."""
    #     pass
    
    # def send_chat_message(self, message: str) -> None:
    #     """Send a message to Twitch chat."""
    #     pass
    
    def run(self) -> None:
        """Start the chat tools main loop."""
        self.log_message("Chat Tools started", "INFO")
        self.log_message(
            "Click 'Open Settings' to configure Twitch connection, then 'Connect' to start monitoring chat.",
            "INFO"
        )
        self.root.mainloop()


def main() -> None:
    """Main entry point for chat tools."""
    try:
        chat_tools = ChatTools()
        chat_tools.run()
    except KeyboardInterrupt:
        print("\nChat tools interrupted by user.")
    except Exception as e:
        print(f"Error starting chat tools: {e}")


if __name__ == "__main__":
    main()
