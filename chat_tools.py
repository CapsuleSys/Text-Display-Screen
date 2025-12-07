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
import asyncio
import threading


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
        
        # Bot instance
        self.bot: Optional[any] = None
        self.bot_thread: Optional[threading.Thread] = None
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        
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
            level: Log level (INFO, WARNING, ERROR, CHAT, SUCCESS, etc.)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding based on level
        level_colors = {
            "ERROR": "red",
            "WARNING": "orange",
            "SUCCESS": "green",
            "CHAT": "black",
            "INFO": "blue"
        }
        color = level_colors.get(level, "black")
        
        formatted_message = f"[{timestamp}] [{level}] {message}\n"
        
        # Enable text widget, insert message with color, disable again
        self.log_text.config(state=tk.NORMAL)
        
        # Insert with tag for coloring
        start_pos = self.log_text.index(tk.END)
        self.log_text.insert(tk.END, formatted_message)
        end_pos = self.log_text.index(tk.END)
        
        # Apply color tag to the line
        self.log_text.tag_add(level, start_pos, end_pos)
        self.log_text.tag_config(level, foreground=color)
        
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
        if not self.config:
            messagebox.showerror(
                "Configuration Missing",
                "No configuration found. Please configure settings first."
            )
            self.open_settings()
            return
        
        # Validate config has all required fields
        required_fields = ['username', 'oauth_token', 'client_id', 'client_secret', 'bot_id', 'channel']
        missing = [f for f in required_fields if not self.config.get(f)]
        if missing:
            messagebox.showerror(
                "Incomplete Configuration",
                f"Missing configuration fields: {', '.join(missing)}\n\n"
                "Please complete settings."
            )
            self.open_settings()
            return
        
        self.log_message("Attempting to connect to Twitch...", "INFO")
        
        # Start bot in separate thread
        self.bot_thread = threading.Thread(target=self._run_bot_thread)
        self.bot_thread.daemon = True
        self.bot_thread.start()
    
    def _run_bot_thread(self) -> None:
        """Thread worker for running Twitch bot."""
        try:
            from twitchio.ext import commands
            from twitchio import eventsub, ChatMessage
            
            # Create new event loop for this thread
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            
            # Create bot instance
            chat_tools_instance = self
            
            class TwitchChatBot(commands.Bot):
                def __init__(self):
                    super().__init__(
                        client_id=chat_tools_instance.config['client_id'],
                        client_secret=chat_tools_instance.config['client_secret'],
                        bot_id=chat_tools_instance.config['bot_id'],
                        prefix='!'
                    )
                    self.oauth_token = chat_tools_instance.config['oauth_token']
                    print(f"[DEBUG] Bot initialized for channel: {chat_tools_instance.config['channel']}")
                
                async def setup_hook(self):
                    """Called before connecting - subscribe to chat messages via EventSub WebSocket"""
                    print(f"[DEBUG] setup_hook called")
                    
                    # Get the channel user to subscribe to their chat
                    channel_name = chat_tools_instance.config['channel']
                    print(f"[DEBUG] Fetching channel info for: {channel_name}")
                    
                    try:
                        users = await self.fetch_users(logins=[channel_name])
                        if users:
                            broadcaster = users[0]
                            print(f"[DEBUG] Found broadcaster: {broadcaster.name} (ID: {broadcaster.id})")
                            
                            # Create subscription payload for chat messages
                            payload = eventsub.ChatMessageSubscription(
                                broadcaster_user_id=broadcaster.id,
                                user_id=chat_tools_instance.config['bot_id']
                            )
                            
                            # Subscribe to channel.chat.message events via WebSocket
                            await self.subscribe_websocket(
                                payload=payload,
                                as_bot=True
                            )
                            print(f"[DEBUG] Successfully subscribed to chat messages")
                        else:
                            print(f"[ERROR] Could not find channel: {channel_name}")
                    except Exception as e:
                        print(f"[ERROR] Failed to subscribe to chat: {e}")
                        import traceback
                        traceback.print_exc()
                
                async def event_ready(self):
                    print(f"[INFO] Bot ready event triggered")
                    chat_tools_instance.is_connected = True
                    chat_tools_instance.root.after(0, chat_tools_instance._update_connection_status)
                    chat_tools_instance.root.after(
                        0,
                        lambda: chat_tools_instance.log_message(
                            f"Connected to Twitch, monitoring #{chat_tools_instance.config['channel']}",
                            "SUCCESS"
                        )
                    )
                    print(f"[INFO] Bot ready and subscribed to channel")
                
                async def event_message(self, message: ChatMessage):
                    """Handle incoming chat messages from EventSub"""
                    print(f"[DEBUG] Message event received!")
                    print(f"[DEBUG] Message type: {type(message)}")
                    
                    try:
                        # ChatMessage has .chatter (Chatter object) and .text
                        username = message.chatter.name
                        content = message.text
                        print(f"[DEBUG] Chat: {username}: {content}")
                        
                        # Log to UI
                        chat_tools_instance.root.after(
                            0,
                            lambda u=username, c=content: chat_tools_instance.log_message(
                                f"{u}: {c}",
                                "CHAT"
                            )
                        )
                    except Exception as e:
                        print(f"[ERROR] Failed to process message: {e}")
                        import traceback
                        traceback.print_exc()
                
                async def event_error(self, payload):
                    """Handle errors from twitchio"""
                    if hasattr(payload, 'error'):
                        actual_error = payload.error
                        print(f"[ERROR] Actual error: {actual_error}")
                        error_msg = str(actual_error)
                    else:
                        error_msg = str(payload)
                        print(f"[ERROR] Bot error: {payload}")
                    
                    if hasattr(payload, 'listener'):
                        print(f"[ERROR] Failed listener: {payload.listener}")
                    
                    chat_tools_instance.root.after(
                        0,
                        lambda e=error_msg: chat_tools_instance.log_message(
                            f"Bot error: {e}",
                            "ERROR"
                        )
                    )
            
            # Store bot instance and run it
            self.bot = TwitchChatBot()
            self.log_message(f"Bot created, connecting to Twitch...", "INFO")
            
            # Run bot with the OAuth token
            self.event_loop.run_until_complete(
                self.bot.start(token=self.config['oauth_token'])
            )
            
        except ImportError:
            self.root.after(
                0,
                lambda: self.log_message(
                    "twitchio library not installed. Install with: pip install twitchio",
                    "ERROR"
                )
            )
            self.is_connected = False
            self.root.after(0, self._update_connection_status)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(
                0,
                lambda msg=error_msg: self.log_message(
                    f"Connection failed: {msg}",
                    "ERROR"
                )
            )
            self.is_connected = False
            self.root.after(0, self._update_connection_status)
            
            import traceback
            traceback.print_exc()
    
    def disconnect_from_twitch(self) -> None:
        """Disconnect from Twitch IRC."""
        self.log_message("Disconnecting from Twitch...", "INFO")
        
        if self.bot and self.event_loop:
            try:
                # Stop the bot
                future = asyncio.run_coroutine_threadsafe(
                    self.bot.close(),
                    self.event_loop
                )
                future.result(timeout=5.0)
            except Exception as e:
                self.log_message(f"Error during disconnect: {e}", "WARNING")
        
        self.is_connected = False
        self.bot = None
        self.event_loop = None
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
        import subprocess
        import sys
        
        settings_path = Path(__file__).parent / "chat_tools_settings.py"
        
        try:
            subprocess.Popen([
                sys.executable,
                str(settings_path)
            ], cwd=str(Path(__file__).parent))
            
            self.log_message("Settings window opened", "INFO")
            
            # Reload config after a delay (user might save new settings)
            self.root.after(1000, self._load_config)
            
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
