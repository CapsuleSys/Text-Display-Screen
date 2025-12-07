"""
Chat Tools Settings GUI

Configuration interface for Twitch chat integration. Allows users to input
their Twitch credentials, test connection, and save settings for the chat tools.
"""

import tkinter as tk
from tkinter import messagebox
import json
from pathlib import Path
from typing import Optional
import asyncio
import threading
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler


def create_link_label(parent: tk.Frame, text: str, url: str, row: int, column: int, **grid_kwargs) -> tk.Label:
    """Create a clickable link label."""
    label = tk.Label(
        parent,
        text=text,
        font=("Arial", 8, "underline"),
        fg="blue",
        cursor="hand2"
    )
    label.grid(row=row, column=column, **grid_kwargs)
    label.bind("<Button-1>", lambda e: webbrowser.open(url))
    return label


class ChatToolsSettings:
    """Settings GUI for configuring Twitch chat connection."""
    
    def __init__(self) -> None:
        """Initialise the chat tools settings GUI."""
        self.root = tk.Tk()
        self.root.title("Chat Tools - Settings")
        self.root.geometry("550x600")
        self.root.resizable(False, False)
        
        self.config_path = Path(__file__).parent / "config" / "chat_tools_config.json"
        
        # OAuth callback storage
        self.oauth_callback_data: Optional[dict] = None
        self.oauth_server: Optional[HTTPServer] = None
        
        # Ensure config directory exists
        self.config_path.parent.mkdir(exist_ok=True)
        
        self._create_ui()
        self._load_existing_config()
    
    def _create_ui(self) -> None:
        """Create the settings UI components."""
        # Title
        title_label = tk.Label(
            self.root,
            text="Twitch Chat Configuration",
            font=("Arial", 16, "bold"),
            pady=20
        )
        title_label.pack()
        
        # Main form frame
        form_frame = tk.Frame(self.root, padx=40, pady=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Username field
        tk.Label(
            form_frame,
            text="Twitch Username:",
            font=("Arial", 11)
        ).grid(row=0, column=0, sticky="w", pady=10)
        
        self.username_entry = tk.Entry(form_frame, width=30, font=("Arial", 11))
        self.username_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Client ID field (needed first for OAuth)
        tk.Label(
            form_frame,
            text="Client ID:",
            font=("Arial", 11)
        ).grid(row=1, column=0, sticky="w", pady=10)
        
        self.client_id_entry = tk.Entry(form_frame, width=30, font=("Arial", 11))
        self.client_id_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Client Secret field
        tk.Label(
            form_frame,
            text="Client Secret:",
            font=("Arial", 11)
        ).grid(row=2, column=0, sticky="w", pady=10)
        
        self.client_secret_entry = tk.Entry(
            form_frame,
            width=30,
            font=("Arial", 11),
            show="*"
        )
        self.client_secret_entry.grid(row=2, column=1, pady=10, padx=10)
        
        # Help text for app credentials (clickable link)
        create_link_label(
            form_frame,
            "Register app at: https://dev.twitch.tv/console/apps",
            "https://dev.twitch.tv/console/apps",
            row=3,
            column=1,
            sticky="w",
            padx=10
        )
        
        # OAuth authorize button
        oauth_btn = tk.Button(
            form_frame,
            text="🔑 Authorize with Twitch",
            command=self.start_oauth_flow,
            font=("Arial", 10, "bold"),
            bg="#9146FF",
            fg="white",
            width=28
        )
        oauth_btn.grid(row=4, column=1, pady=15, padx=10)
        
        # OAuth token field (read-only, populated by OAuth)
        tk.Label(
            form_frame,
            text="OAuth Token:",
            font=("Arial", 11)
        ).grid(row=5, column=0, sticky="w", pady=10)
        
        self.oauth_entry = tk.Entry(
            form_frame,
            width=30,
            font=("Arial", 11),
            show="*",
            state="readonly"
        )
        self.oauth_entry.grid(row=5, column=1, pady=10, padx=10)
        
        # Help text for OAuth
        oauth_help = tk.Label(
            form_frame,
            text="Use 'Authorize with Twitch' button above",
            font=("Arial", 8),
            fg="grey"
        )
        oauth_help.grid(row=6, column=1, sticky="w", padx=10)
        
        # Bot ID field
        tk.Label(
            form_frame,
            text="Bot ID:",
            font=("Arial", 11)
        ).grid(row=7, column=0, sticky="w", pady=10)
        
        self.bot_id_entry = tk.Entry(form_frame, width=30, font=("Arial", 11))
        self.bot_id_entry.grid(row=7, column=1, pady=10, padx=10)
        
        # Bot ID help text (clickable link)
        create_link_label(
            form_frame,
            "Get Bot ID: streamweasels.com/tools/convert-twitch-username-to-user-id",
            "https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/",
            row=8,
            column=1,
            sticky="w",
            padx=10,
            pady=(0, 10)
        )
        
        # Channel field
        tk.Label(
            form_frame,
            text="Channel to Join:",
            font=("Arial", 11)
        ).grid(row=9, column=0, sticky="w", pady=10)
        
        self.channel_entry = tk.Entry(form_frame, width=30, font=("Arial", 11))
        self.channel_entry.grid(row=9, column=1, pady=10, padx=10)
        
        # Channel help text
        channel_help = tk.Label(
            form_frame,
            text="Enter channel name without #",
            font=("Arial", 8),
            fg="grey"
        )
        channel_help.grid(row=10, column=1, sticky="w", padx=10)
        
        # Button frame
        button_frame = tk.Frame(self.root, pady=20)
        button_frame.pack()
        
        # Test connection button
        test_btn = tk.Button(
            button_frame,
            text="Test Connection",
            command=self.test_connection,
            width=15,
            font=("Arial", 10),
            bg="#FFA500",
            fg="white"
        )
        test_btn.pack(side=tk.LEFT, padx=10)
        
        # Save button
        save_btn = tk.Button(
            button_frame,
            text="Save Settings",
            command=self.save_settings,
            width=15,
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white"
        )
        save_btn.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.root.quit,
            width=15,
            font=("Arial", 10)
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
    
    def _load_existing_config(self) -> None:
        """Load existing configuration if available."""
        if not self.config_path.exists():
            return
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # Populate fields with existing values
            self.username_entry.insert(0, config.get("username", ""))
            
            # OAuth token is readonly, need to enable temporarily
            oauth_token = config.get("oauth_token", "")
            if oauth_token:
                self.oauth_entry.config(state="normal")
                self.oauth_entry.insert(0, oauth_token)
                self.oauth_entry.config(state="readonly")
            
            self.client_id_entry.insert(0, config.get("client_id", ""))
            self.client_secret_entry.insert(0, config.get("client_secret", ""))
            self.bot_id_entry.insert(0, config.get("bot_id", ""))
            self.channel_entry.insert(0, config.get("channel", ""))
            
        except Exception as e:
            print(f"Failed to load existing config: {e}")
    
    def start_oauth_flow(self) -> None:
        """Start OAuth2 authorization flow with Twitch."""
        client_id = self.client_id_entry.get().strip()
        
        if not client_id:
            messagebox.showerror(
                "Missing Client ID",
                "Please enter your Client ID before authorizing.\n\n"
                "Get it from: https://dev.twitch.tv/console/apps"
            )
            return
        
        # Start OAuth flow in separate thread
        thread = threading.Thread(target=self._oauth_flow_thread, args=(client_id,))
        thread.daemon = True
        thread.start()
    
    def _oauth_flow_thread(self, client_id: str) -> None:
        """Thread worker for OAuth flow."""
        try:
            # Create OAuth callback handler
            settings_instance = self
            
            class OAuthCallbackHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    # Parse the callback URL
                    print(f"[DEBUG] Callback received: {self.path}")
                    parsed = urllib.parse.urlparse(self.path)
                    params = urllib.parse.parse_qs(parsed.query)
                    
                    print(f"[DEBUG] Query params: {params}")
                    
                    # Check if this is the token callback (from JavaScript)
                    if '/callback' in self.path and 'access_token' in params:
                        token = params['access_token'][0]
                        print(f"[SUCCESS] Token received: {token[:20]}...")
                        settings_instance.oauth_callback_data = {
                            'token': token,
                            'success': True
                        }
                        
                        # Send minimal response
                        self.send_response(200)
                        self.send_header('Content-type', 'text/plain')
                        self.end_headers()
                        self.wfile.write(b'OK')
                        
                    elif 'error' in params:
                        # Error in OAuth
                        error = params['error'][0]
                        print(f"[ERROR] OAuth error: {error}")
                        settings_instance.oauth_callback_data = {
                            'success': False,
                            'error': error
                        }
                        
                        # Send error page
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(f'''
                            <html><body style="font-family: Arial; text-align: center; padding: 50px;">
                                <h1 style="color: red;">Authorization Failed</h1>
                                <p>Error: {error}</p>
                                <p>Please close this window and try again.</p>
                            </body></html>
                        '''.encode())
                        
                    else:
                        # Initial redirect from Twitch - extract fragment with JavaScript
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(b'''
                            <html>
                            <head><title>Twitch Authorization</title></head>
                            <body style="font-family: Arial; text-align: center; padding: 50px;">
                                <h1 style="color: #9146FF;">Processing Authorization...</h1>
                                <p>Please wait...</p>
                                <script>
                                    // Extract token from URL fragment
                                    const hash = window.location.hash.substring(1);
                                    const params = new URLSearchParams(hash);
                                    const token = params.get('access_token');
                                    const error = params.get('error');
                                    
                                    if (token) {
                                        // Send token to server via query string
                                        fetch('/callback?access_token=' + encodeURIComponent(token))
                                            .then(() => {
                                                document.body.innerHTML = `
                                                    <h1 style="color: #9146FF;">Authorization Successful!</h1>
                                                    <p>You can close this window and return to the application.</p>
                                                `;
                                            })
                                            .catch(err => {
                                                document.body.innerHTML = `
                                                    <h1 style="color: red;">Error</h1>
                                                    <p>Failed to send token. Please try again.</p>
                                                `;
                                            });
                                    } else if (error) {
                                        document.body.innerHTML = `
                                            <h1 style="color: red;">Authorization Failed</h1>
                                            <p>Error: ${error}</p>
                                            <p>Please close this window and try again.</p>
                                        `;
                                    } else {
                                        document.body.innerHTML = `
                                            <h1 style="color: orange;">No Token Received</h1>
                                            <p>No authorization data found. Please try again.</p>
                                        `;
                                    }
                                </script>
                            </body>
                            </html>
                        ''')
                
                def log_message(self, format, *args):
                    # Suppress server logs
                    pass
            
            # Start local server
            port = 8080
            self.oauth_server = HTTPServer(('localhost', port), OAuthCallbackHandler)
            
            # Build OAuth URL
            redirect_uri = f"http://localhost:{port}"
            # TODO: Implement dual OAuth flow for bot account and streamer account
            # TODO: Current flow only authenticates bot account, which limits access to streamer's channel data
            # TODO: Bot account needs these scopes for basic functionality:
            # TODO:   - user:read:chat (read messages via EventSub)
            # TODO:   - user:write:chat (send messages to chat)
            # TODO:   - moderator:read:followers (read followers as moderator)
            # TODO: Streamer account needs these scopes for full channel data access:
            # TODO:   - channel:read:subscriptions (read subscriber list and events)
            # TODO:   - channel:read:predictions (read prediction events)
            # TODO:   - channel:read:polls (read poll events)
            # TODO:   - channel:read:hype_train (read hype train events)
            # TODO:   - channel:read:redemptions (read channel point redemptions)
            # TODO:   - bits:read (read bits/cheer events)
            # TODO: Implementation plan for dual OAuth:
            # TODO:   1. Add separate "Authenticate Bot" and "Authenticate Streamer" buttons in settings
            # TODO:   2. Store both tokens in config (bot_oauth_token, streamer_oauth_token)
            # TODO:   3. Use bot token for chat operations (read/write messages)
            # TODO:   4. Use streamer token for channel data queries (subs, predictions, polls, etc.)
            # TODO:   5. Add validation to ensure both tokens are present before connecting
            # TODO:   6. Handle token refresh separately for both accounts
            # TODO:   7. Display which account is authenticated in settings UI
            # TODO: For now, using single bot account OAuth with moderator permissions
            # TODO: Bot must be moderator in streamer's channel for moderator:read:followers to work
            
            # Comprehensive scopes for chat, stream info, and events
            scopes = (
                "user:read:chat "
                "user:write:chat "
                "channel:read:subscriptions "
                "moderator:read:followers "
                "channel:read:predictions "
                "channel:read:polls "
                "channel:read:hype_train "
                "channel:read:redemptions "
                "bits:read"
            )
            
            auth_url = (
                f"https://id.twitch.tv/oauth2/authorize"
                f"?client_id={client_id}"
                f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
                f"&response_type=token"
                f"&scope={urllib.parse.quote(scopes)}"
            )
            
            print(f"Opening browser for OAuth authorization...")
            print(f"Auth URL: {auth_url}")
            
            # Open browser
            webbrowser.open(auth_url)
            
            # Wait for callback (with timeout)
            self.oauth_callback_data = None
            
            # Handle two requests: initial page load + token callback
            print("[DEBUG] Waiting for initial callback...")
            self.oauth_server.handle_request()  # Initial page load
            
            if not self.oauth_callback_data:
                print("[DEBUG] Waiting for token callback...")
                self.oauth_server.handle_request()  # Token callback from JavaScript
            
            # Process result
            if self.oauth_callback_data and self.oauth_callback_data.get('success'):
                token = self.oauth_callback_data['token']
                print(f"[SUCCESS] OAuth token received")
                
                # Update UI in main thread
                self.root.after(0, lambda: self._update_oauth_token(token))
            else:
                error = self.oauth_callback_data.get('error', 'Unknown error') if self.oauth_callback_data else 'Timeout'
                print(f"[ERROR] OAuth failed: {error}")
                
                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Authorization Failed",
                        f"OAuth authorization failed: {error}"
                    )
                )
            
        except Exception as e:
            print(f"[ERROR] OAuth flow error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            self.root.after(
                0,
                lambda msg=str(e): messagebox.showerror(
                    "OAuth Error",
                    f"Error during OAuth flow:\n{msg}"
                )
            )
        finally:
            if self.oauth_server:
                self.oauth_server.server_close()
    
    def _update_oauth_token(self, token: str) -> None:
        """Update OAuth token field in UI."""
        self.oauth_entry.config(state="normal")
        self.oauth_entry.delete(0, tk.END)
        self.oauth_entry.insert(0, token)
        self.oauth_entry.config(state="readonly")
        
        messagebox.showinfo(
            "Authorization Successful",
            "OAuth token received successfully!\n\n"
            "Next: Enter your Bot ID below.\n"
            "Get it from: https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/\n\n"
            "Then test the connection or save settings."
        )
    
    def test_connection(self) -> None:
        """Test connection to Twitch with provided credentials."""
        username = self.username_entry.get().strip()
        oauth_token = self.oauth_entry.get().strip()
        client_id = self.client_id_entry.get().strip()
        client_secret = self.client_secret_entry.get().strip()
        bot_id = self.bot_id_entry.get().strip()
        channel = self.channel_entry.get().strip()
        
        # Basic validation
        if not all([username, oauth_token, client_id, client_secret, bot_id, channel]):
            messagebox.showerror(
                "Validation Error",
                "All fields are required to test connection."
            )
            return
        
        # Validate bot_id is numeric
        if not bot_id.isdigit():
            messagebox.showerror(
                "Validation Error",
                f"Bot ID must be numeric (got: {bot_id}).\n\n"
                "Get your numeric Bot ID from:\n"
                "https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/"
            )
            return
        
        # OAuth2 tokens don't need oauth: prefix (that's for IRC tokens only)
        # Remove it if present
        if oauth_token.startswith("oauth:"):
            oauth_token = oauth_token[6:]
        
        # Run connection test in separate thread to avoid blocking GUI
        thread = threading.Thread(
            target=self._test_connection_thread,
            args=(username, oauth_token, client_id, client_secret, bot_id, channel)
        )
        thread.daemon = True
        thread.start()
    
    def _test_connection_thread(
        self,
        username: str,
        oauth_token: str,
        client_id: str,
        client_secret: str,
        bot_id: str,
        channel: str
    ) -> None:
        """Thread worker for testing Twitch connection."""
        try:
            # Try importing twitchio
            try:
                from twitchio.ext import commands
            except ImportError:
                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Missing Dependency",
                        "twitchio library not installed.\n\n"
                        "Install with: pip install twitchio"
                    )
                )
                return
            
            # Create temporary bot for testing
            class TestBot(commands.Bot):
                def __init__(self, test_callback):
                    super().__init__(
                        token=oauth_token,
                        prefix='!',
                        initial_channels=[channel],
                        client_id=client_id,
                        client_secret=client_secret,
                        bot_id=bot_id
                    )
                    self.test_callback = test_callback
                    self.connection_made = False
                
                async def event_ready(self):
                    # Connection successful
                    if not self.connection_made:
                        self.connection_made = True
                        self.test_callback(True, f"Successfully connected to #{channel}")
                        await self.close()
            
            # Run the test
            success = [False, "Connection timeout"]
            
            def test_callback(result: bool, message: str):
                success[0] = result
                success[1] = message
            
            # Create and run bot with timeout
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            bot = TestBot(test_callback)
            
            try:
                # Run with timeout
                loop.run_until_complete(
                    asyncio.wait_for(bot.start(), timeout=10.0)
                )
            except asyncio.TimeoutError:
                success[0] = False
                success[1] = "Connection timeout - check your credentials"
            except Exception as e:
                success[0] = False
                success[1] = f"Connection failed: {str(e)}"
            finally:
                loop.close()
            
            # Show result in GUI thread
            if success[0]:
                print(f"[SUCCESS] {success[1]}")
                self.root.after(
                    0,
                    lambda msg=success[1]: messagebox.showinfo(
                        "Connection Successful",
                        msg
                    )
                )
            else:
                print(f"[ERROR] {success[1]}")
                self.root.after(
                    0,
                    lambda msg=success[1]: messagebox.showerror(
                        "Connection Failed",
                        msg
                    )
                )
                
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] Error testing connection: {error_msg}")
            import traceback
            traceback.print_exc()
            self.root.after(
                0,
                lambda msg=error_msg: messagebox.showerror(
                    "Test Error",
                    f"Error testing connection:\n{msg}"
                )
            )
    
    def save_settings(self) -> None:
        """Save Twitch configuration to file."""
        username = self.username_entry.get().strip()
        
        # OAuth entry is readonly, need to get value differently
        self.oauth_entry.config(state="normal")
        oauth_token = self.oauth_entry.get().strip()
        self.oauth_entry.config(state="readonly")
        
        client_id = self.client_id_entry.get().strip()
        client_secret = self.client_secret_entry.get().strip()
        bot_id = self.bot_id_entry.get().strip()
        channel = self.channel_entry.get().strip()
        
        # Validate fields
        if not all([username, oauth_token, client_id, client_secret, bot_id, channel]):
            messagebox.showerror(
                "Validation Error",
                "All fields are required. Please fill in all fields.\n\n"
                "Use 'Authorize with Twitch' button to get OAuth token."
            )
            return
        
        # Validate and fix OAuth token format
        # OAuth2 tokens don't need oauth: prefix (that's for IRC tokens)
        
        # Remove # from channel name if present
        if channel.startswith("#"):
            channel = channel[1:]
        
        # Create configuration dictionary
        config = {
            "username": username,
            "oauth_token": oauth_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "bot_id": bot_id,
            "channel": channel
        }
        
        try:
            # Save to file
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            
            messagebox.showinfo(
                "Settings Saved",
                f"Chat tools configuration saved successfully to:\n{self.config_path}"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Save Error",
                f"Failed to save settings:\n{e}"
            )
    
    def run(self) -> None:
        """Start the settings GUI main loop."""
        self.root.mainloop()


def main() -> None:
    """Main entry point for chat tools settings."""
    try:
        settings_gui = ChatToolsSettings()
        settings_gui.run()
    except KeyboardInterrupt:
        print("\nSettings interrupted by user.")
    except Exception as e:
        print(f"Error starting settings: {e}")


if __name__ == "__main__":
    main()
