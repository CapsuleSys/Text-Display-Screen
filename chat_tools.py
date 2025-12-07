"""
Twitch Chat Tools

Main chat monitoring and interaction tool for Twitch streams. Connects to
Twitch IRC, displays chat messages in a log window, and provides basic
chat interaction capabilities including custom commands and auto messages.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import json
from pathlib import Path
from typing import Optional, Any
from datetime import datetime
import asyncio
import threading
import time
import random
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from logger_setup import setup_logger

logger = setup_logger(__name__)


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
        
        # Command tracking
        self.command_cooldowns: dict[str, float] = {}  # trigger -> last_used_time
        
        # Auto messages tracking
        self.auto_msg_task: Optional[asyncio.Task] = None
        self.auto_msg_index: int = 0  # For sequential mode
        self.chat_activity_timestamps: list[float] = []  # Message timestamps
        
        # File watcher for config changes
        self.config_observer: Optional[Observer] = None
        
        self._create_ui()
        self._load_config()
        self._start_config_watcher()
    
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
        
        # Colour coding based on level
        level_colours = {
            "ERROR": "red",
            "WARNING": "orange",
            "SUCCESS": "green",
            "CHAT": "black",
            "INFO": "blue"
        }
        colour = level_colours.get(level, "black")
        
        formatted_message = f"[{timestamp}] [{level}] {message}\n"
        
        # Enable text widget, insert message with colour, disable again
        self.log_text.config(state=tk.NORMAL)
        
        # Insert with tag for colouring
        start_pos = self.log_text.index(tk.END)
        self.log_text.insert(tk.END, formatted_message)
        end_pos = self.log_text.index(tk.END)
        
        # Apply colour tag to the line
        self.log_text.tag_add(level, start_pos, end_pos)
        self.log_text.tag_config(level, foreground=colour)
        
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
        """Thread worker for running Twitch bot.
        
        This method runs the Twitch chat bot in a separate thread with its own
        asyncio event loop. It creates a nested TwitchChatBot class that handles
        all Twitch interactions using the TwitchIO library.
        
        Bot Architecture:
        - Nested TwitchChatBot class inherits from commands.Bot
        - Uses custom OAuth token authentication (not standard IRC)
        - Sends messages via Helix API instead of IRC (see send_message method)
        - Subscribes to EventSub WebSocket for real-time events
        - Maintains separate event loop in this thread
        
        Event Handlers:
        - event_ready: Called when bot connects, joins channel, sets up EventSub
        - event_message: Handles incoming chat messages, processes commands/auto-messages
        - event_error: Handles bot errors and reconnection
        
        Custom send_message Method:
        - Uses Twitch Helix API (POST /helix/chat/messages)
        - Requires broadcaster_id for sending messages
        - Returns success/failure boolean
        - More reliable than IRC for programmatic messages
        
        Chat Activity Tracking:
        - Maintains recent_messages deque for auto-message activity threshold
        - Tracks timestamps to implement min_messages_in_window requirement
        - Used to prevent auto-messages when chat is inactive
        
        Current Limitations (TODO - lines 294-339):
        - Single OAuth token limits available scopes
        - Missing dual OAuth (bot + broadcaster tokens)
        - Cannot access subscriber lists, polls, predictions, hype trains
        - Cannot receive bits/cheer events without broadcaster auth
        - EventSub subscriptions are limited by token scopes
        
        Thread Safety:
        - Runs in separate thread with own event loop
        - GUI updates via root.after() to avoid tkinter issues
        - Bot stored in self.bot for external access/shutdown
        
        Error Handling:
        - Catches all exceptions in outer try-except
        - Logs errors to GUI via log_message()
        - event_error handler for bot-specific errors
        """
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
                    logger.debug(f"Bot initialized for channel: {chat_tools_instance.config['channel']}")
                    
                    # Store broadcaster ID for sending messages
                    self.broadcaster_id: Optional[str] = None
                
                async def send_message(self, message: str) -> None:
                    """Send a message to the configured channel using Twitch Helix API directly."""
                    if not self.broadcaster_id:
                        logger.error("Broadcaster ID not set")
                        return
                    
                    # Send chat message using aiohttp directly to Twitch Helix API
                    import aiohttp
                    
                    url = "https://api.twitch.tv/helix/chat/messages"
                    headers = {
                        "Authorization": f"Bearer {self.oauth_token}",
                        "Client-Id": chat_tools_instance.config['client_id'],
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "broadcaster_id": self.broadcaster_id,
                        "sender_id": chat_tools_instance.config['bot_id'],
                        "message": message
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, headers=headers, json=payload) as resp:
                            if resp.status == 200:
                                logger.debug(f"Message sent successfully")
                            else:
                                error_text = await resp.text()
                                logger.error(f"Failed to send message: {resp.status} - {error_text}")
                
                async def setup_hook(self):
                    """Called before connecting - subscribe to chat messages via EventSub WebSocket"""
                    logger.debug(f"setup_hook called")
                    
                    # TODO: Implement dual OAuth token support for bot and streamer accounts
                    # TODO: Currently using single bot account token which limits channel data access
                    # TODO: Bot token should be used for chat operations (this subscription)
                    # TODO: Streamer token should be used for channel data queries (subs, predictions, polls, etc.)
                    # TODO: When dual OAuth implemented:
                    # TODO:   - Use bot token for ChatMessageSubscription (current behavior)
                    # TODO:   - Use streamer token for ChannelSubscribeSubscription
                    # TODO:   - Use streamer token for ChannelPredictionBeginSubscription  
                    # TODO:   - Use streamer token for ChannelPollBeginSubscription
                    # TODO:   - Use streamer token for HypeTrainBeginSubscription
                    # TODO:   - Use streamer token for ChannelPointsRedemptionAddSubscription
                    # TODO:   - Use streamer token for ChannelCheerSubscription (bits)
                    # TODO: Bot must be moderator in streamer's channel for moderator:read:followers scope
                    
                    # Get the channel user to subscribe to their chat
                    channel_name = chat_tools_instance.config['channel']
                    logger.debug(f"Fetching channel info for: {channel_name}")
                    
                    try:
                        users = await self.fetch_users(logins=[channel_name])
                        if users:
                            broadcaster = users[0]
                            self.broadcaster_id = broadcaster.id  # Store for sending messages
                            logger.debug(f"Found broadcaster: {broadcaster.name} (ID: {broadcaster.id})")
                            
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
                            logger.debug(f"Successfully subscribed to chat messages")
                            
                            # TODO: Add additional EventSub subscriptions when dual OAuth implemented
                            # TODO: Subscribe to channel.subscribe (requires streamer token)
                            # TODO: Subscribe to channel.prediction.begin (requires streamer token)
                            # TODO: Subscribe to channel.poll.begin (requires streamer token)
                            # TODO: Subscribe to channel.hype_train.begin (requires streamer token)
                            # TODO: Subscribe to channel.channel_points_custom_reward_redemption.add (requires streamer token)
                            # TODO: Subscribe to channel.cheer (requires streamer token)
                            # TODO: Subscribe to channel.follow (requires moderator token, bot must be mod)
                            
                        else:
                            logger.error(f"Could not find channel: {channel_name}")
                    except Exception as e:
                        logger.error(f"Failed to subscribe to chat: {e}")
                        import traceback
                        traceback.print_exc()
                
                async def event_ready(self):
                    logger.info(f"Bot ready event triggered")
                    chat_tools_instance.is_connected = True
                    chat_tools_instance.root.after(0, chat_tools_instance._update_connection_status)
                    chat_tools_instance.root.after(
                        0,
                        lambda: chat_tools_instance.log_message(
                            f"Connected to Twitch, monitoring #{chat_tools_instance.config['channel']}",
                            "SUCCESS"
                        )
                    )
                    logger.info(f"Bot ready and subscribed to channel")
                    
                    # Start auto-message task
                    chat_tools_instance.auto_msg_task = asyncio.create_task(
                        chat_tools_instance._auto_message_loop()
                    )
                
                async def event_message(self, message: ChatMessage):
                    """Handle incoming chat messages from EventSub"""
                    logger.debug(f"Message event received!")
                    logger.debug(f"Message type: {type(message)}")
                    
                    try:
                        # ChatMessage has .chatter (Chatter object) and .text
                        username = message.chatter.name
                        content = message.text
                        logger.debug(f"Chat: {username}: {content}")
                        
                        # Track chat activity for auto-messages
                        chat_tools_instance.chat_activity_timestamps.append(time.time())
                        
                        # Log to UI
                        chat_tools_instance.root.after(
                            0,
                            lambda u=username, c=content: chat_tools_instance.log_message(
                                f"{u}: {c}",
                                "CHAT"
                            )
                        )
                        
                        # Check for commands
                        await chat_tools_instance._handle_command(message)
                        
                    except Exception as e:
                        logger.error(f"Failed to process message: {e}")
                        import traceback
                        traceback.print_exc()
                
                async def event_error(self, payload):
                    """Handle errors from twitchio"""
                    if hasattr(payload, 'error'):
                        actual_error = payload.error
                        logger.error(f"Actual error: {actual_error}")
                        error_msg = str(actual_error)
                    else:
                        error_msg = str(payload)
                        logger.error(f"Bot error: {payload}")
                    
                    if hasattr(payload, 'listener'):
                        logger.error(f"Failed listener: {payload.listener}")
                    
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
        
        # Cancel auto-message task
        if self.auto_msg_task and not self.auto_msg_task.done():
            self.auto_msg_task.cancel()
        
        if self.bot and self.event_loop:
            try:
                # Stop the bot gracefully
                future = asyncio.run_coroutine_threadsafe(
                    self.bot.close(),
                    self.event_loop
                )
                future.result(timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Bot close timed out, forcing shutdown")
            except OSError as e:
                # Suppress Windows overlapped I/O errors during shutdown
                if e.winerror != 6:  # Ignore "handle is invalid" errors
                    logger.warning(f"Error during disconnect: {e}")
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
        
        self.is_connected = False
        self.bot = None
        self.event_loop = None
        self.auto_msg_task = None
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
    
    def _start_config_watcher(self) -> None:
        """Start watching config file for changes."""
        if not self.config_path.exists():
            return
        
        chat_tools_instance = self
        
        class ConfigFileHandler(FileSystemEventHandler):
            """Handler for config file changes."""
            
            def on_modified(self, event):
                """Called when config file is modified."""
                if event.src_path == str(chat_tools_instance.config_path):
                    logger.info(f"Config file changed, reloading...")
                    # Reload in main thread with small delay to ensure file write is complete
                    chat_tools_instance.root.after(500, chat_tools_instance._reload_config)
        
        # Create observer and start watching
        event_handler = ConfigFileHandler()
        self.config_observer = Observer()
        self.config_observer.schedule(
            event_handler,
            str(self.config_path.parent),
            recursive=False
        )
        self.config_observer.start()
        logger.info("Config file watcher started")
    
    def _reload_config(self) -> None:
        """Reload configuration from file without reconnecting."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                new_config = json.load(f)
            
            # Store old config for comparison
            old_config = self.config.copy() if self.config else {}
            
            # Update config
            self.config = new_config
            
            # Detect specific changes for logging
            changes = []
            
            # Check connection settings
            connection_keys = ["username", "oauth_token", "client_id", "client_secret", "bot_id", "channel"]
            if any(old_config.get(k) != new_config.get(k) for k in connection_keys):
                changes.append("[Connection tab] connection settings")
            
            # Check commands
            if old_config.get("commands") != new_config.get("commands"):
                num_commands = len(new_config.get("commands", []))
                changes.append(f"[Commands tab] commands ({num_commands} total)")
            
            # Check auto messages config
            if old_config.get("auto_messages") != new_config.get("auto_messages"):
                changes.append("[Auto Messages tab] auto-messages")
            
            if changes:
                self.log_message(
                    f"Config reloaded: {', '.join(changes)} updated",
                    "INFO"
                )
            else:
                self.log_message("Config reloaded (no changes detected)", "INFO")
        
        except Exception as e:
            self.log_message(f"Failed to reload config: {e}", "ERROR")
    
    def _stop_config_watcher(self) -> None:
        """Stop watching config file."""
        if self.config_observer:
            try:
                self.config_observer.stop()
                self.config_observer.join(timeout=2.0)
            except Exception:
                pass  # Suppress errors during shutdown
            finally:
                self.config_observer = None
                logger.info("Config file watcher stopped")
    
    async def _handle_command(self, message: Any) -> None:
        """Handle chat command if message matches configured commands."""
        # TODO: Add command usage statistics tracking
        
        if not self.config:
            return
        
        commands = self.config.get("commands", [])
        if not commands:
            return
        
        content = message.text.strip()
        if not content:
            return
        
        # Extract first word as potential command
        parts = content.split(maxsplit=1)
        trigger = parts[0].lower()
        
        # Find matching command
        matched_command = None
        for cmd in commands:
            if not cmd.get("enabled", True):
                continue
            
            triggers = cmd.get("triggers", [])
            if trigger in [t.lower() for t in triggers]:
                matched_command = cmd
                break
        
        if not matched_command:
            return
        
        # Check cooldown
        now = time.time()
        cooldown = matched_command.get("cooldown", 0)
        
        if trigger in self.command_cooldowns:
            last_used = self.command_cooldowns[trigger]
            time_since = now - last_used
            
            if time_since < cooldown:
                remaining = int(cooldown - time_since)
                print(f"[DEBUG] Command {trigger} on cooldown ({remaining}s remaining)")
                return
        
        # Check permissions
        permission = matched_command.get("permission", "everyone")
        username = message.chatter.name.lower()
        
        # Get channel owner from config
        channel_owner = self.config.get("channel", "").lower()
        
        if permission == "streamer":
            if username != channel_owner:
                print(f"[DEBUG] {username} tried to use streamer-only command {trigger}")
                return
        
        elif permission == "mods":
            # Check if user is mod or broadcaster
            is_mod = message.chatter.is_mod if hasattr(message.chatter, 'is_mod') else False
            is_broadcaster = username == channel_owner
            
            if not (is_mod or is_broadcaster):
                print(f"[DEBUG] {username} tried to use mod-only command {trigger}")
                return
        
        # Execute command - send response
        response = matched_command.get("response", "")
        if response and self.bot:
            try:
                # Use bot's custom send_message method
                await self.bot.send_message(response)
                
                # Update cooldown
                self.command_cooldowns[trigger] = now
                
                # Log to UI
                self.root.after(
                    0,
                    lambda r=response: self.log_message(
                        f"[BOT] {r}",
                        "SUCCESS"
                    )
                )
                
                print(f"[INFO] Command {trigger} executed by {username}")
            
            except Exception as e:
                logger.error(f"Failed to send command response: {e}")
                import traceback
                traceback.print_exc()
    
    async def _auto_message_loop(self) -> None:
        """Background task for posting auto messages at intervals."""
        # TODO: Add schedule-based messages (time of day restrictions)
        # TODO: Add viewer count thresholds
        # TODO: Add integration with stream events
        
        if not self.config:
            return
        
        # Store channel reference for sending messages
        channel_ref = None
        
        while True:
            try:
                # Get fresh config each iteration to pick up changes
                auto_msg_config = self.config.get("auto_messages", {}) if self.config else {}
                
                # Check if auto messages enabled
                if not auto_msg_config.get("enabled", True):
                    await asyncio.sleep(60)  # Check again in 1 minute
                    continue
                
                # Get configuration (fresh each time)
                interval_minutes = auto_msg_config.get("post_interval_minutes", 20)
                min_activity = auto_msg_config.get("min_chat_activity", 5)
                activity_window_minutes = auto_msg_config.get("activity_window_minutes", 5)
                random_order = auto_msg_config.get("random_order", True)
                messages = auto_msg_config.get("messages", [])
                
                # Filter enabled messages
                enabled_messages = [m for m in messages if m.get("enabled", True)]
                
                if not enabled_messages:
                    await asyncio.sleep(60)
                    continue
                
                # Wait for interval
                await asyncio.sleep(interval_minutes * 60)
                
                # Check chat activity
                now = time.time()
                activity_window_seconds = activity_window_minutes * 60
                
                # Count messages in activity window
                recent_messages = [
                    ts for ts in self.chat_activity_timestamps
                    if now - ts <= activity_window_seconds
                ]
                
                # Clean old timestamps
                self.chat_activity_timestamps = recent_messages
                
                if len(recent_messages) < min_activity:
                    logger.debug(f"Skipping auto-message: insufficient activity ({len(recent_messages)}/{min_activity})")
                    continue
                
                # Select message
                if random_order:
                    message = random.choice(enabled_messages)
                else:
                    # Sequential mode
                    message = enabled_messages[self.auto_msg_index % len(enabled_messages)]
                    self.auto_msg_index += 1
                
                # Send message - use bot's custom send_message method
                text = message.get("text", "")
                if text and self.bot:
                    try:
                        await self.bot.send_message(text)
                        
                        # Log to UI
                        self.root.after(
                            0,
                            lambda t=text: self.log_message(
                                f"[AUTO] {t}",
                                "SUCCESS"
                            )
                        )
                        
                        print(f"[INFO] Auto-message sent: {text[:50]}...")
                    
                    except Exception as e:
                        logger.error(f"Failed to send auto-message: {e}")
                        import traceback
                        traceback.print_exc()
            
            except asyncio.CancelledError:
                logger.info("Auto-message task cancelled")
                break
            
            except Exception as e:
                logger.error(f"Auto-message loop error: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(60)  # Wait before retrying
    
    def run(self) -> None:
        """Start the chat tools main loop."""
        self.log_message("Chat Tools started", "INFO")
        self.log_message(
            "Click 'Open Settings' to configure Twitch connection, then 'Connect' to start monitoring chat.",
            "INFO"
        )
        try:
            self.root.mainloop()
        finally:
            # Clean up gracefully on exit
            try:
                self._stop_config_watcher()
                if self.is_connected:
                    self.disconnect_from_twitch()
            except Exception:
                pass  # Suppress errors during cleanup


def main() -> None:
    """Main entry point for chat tools."""
    try:
        chat_tools = ChatTools()
        chat_tools.run()
    except KeyboardInterrupt:
        logger.info("Chat tools interrupted by user.")
    except Exception as e:
        logger.error(f"Error starting chat tools: {e}")


if __name__ == "__main__":
    main()
