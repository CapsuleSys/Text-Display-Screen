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


class ChatToolsSettings:
    """Settings GUI for configuring Twitch chat connection."""
    
    def __init__(self) -> None:
        """Initialise the chat tools settings GUI."""
        self.root = tk.Tk()
        self.root.title("Chat Tools - Settings")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.config_path = Path(__file__).parent / "config" / "chat_tools_config.json"
        
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
        
        # OAuth token field
        tk.Label(
            form_frame,
            text="OAuth Token:",
            font=("Arial", 11)
        ).grid(row=1, column=0, sticky="w", pady=10)
        
        self.oauth_entry = tk.Entry(
            form_frame,
            width=30,
            font=("Arial", 11),
            show="*"
        )
        self.oauth_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Help text for OAuth
        oauth_help = tk.Label(
            form_frame,
            text="Get your token at: https://twitchapps.com/tmi/",
            font=("Arial", 8),
            fg="grey"
        )
        oauth_help.grid(row=2, column=1, sticky="w", padx=10)
        
        # Channel field
        tk.Label(
            form_frame,
            text="Channel to Join:",
            font=("Arial", 11)
        ).grid(row=3, column=0, sticky="w", pady=10)
        
        self.channel_entry = tk.Entry(form_frame, width=30, font=("Arial", 11))
        self.channel_entry.grid(row=3, column=1, pady=10, padx=10)
        
        # Channel help text
        channel_help = tk.Label(
            form_frame,
            text="Enter channel name without #",
            font=("Arial", 8),
            fg="grey"
        )
        channel_help.grid(row=4, column=1, sticky="w", padx=10)
        
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
            self.oauth_entry.insert(0, config.get("oauth_token", ""))
            self.channel_entry.insert(0, config.get("channel", ""))
            
        except Exception as e:
            print(f"Failed to load existing config: {e}")
    
    def test_connection(self) -> None:
        """Test connection to Twitch with provided credentials."""
        # TODO: Implement Twitch connection test using twitchio
        # TODO: Validate username format
        # TODO: Validate OAuth token format (should start with oauth:)
        # TODO: Validate channel name
        # TODO: Attempt connection and show success/failure message
        
        username = self.username_entry.get().strip()
        oauth_token = self.oauth_entry.get().strip()
        channel = self.channel_entry.get().strip()
        
        # Basic validation
        if not username or not oauth_token or not channel:
            messagebox.showerror(
                "Validation Error",
                "All fields are required to test connection."
            )
            return
        
        # Placeholder for actual connection test
        messagebox.showinfo(
            "Test Connection",
            "Connection test not yet implemented.\n\n"
            "This will attempt to connect to Twitch IRC and verify credentials."
        )
    
    def save_settings(self) -> None:
        """Save Twitch configuration to file."""
        username = self.username_entry.get().strip()
        oauth_token = self.oauth_entry.get().strip()
        channel = self.channel_entry.get().strip()
        
        # Validate fields
        if not username or not oauth_token or not channel:
            messagebox.showerror(
                "Validation Error",
                "All fields are required. Please fill in all fields."
            )
            return
        
        # TODO: Add OAuth token format validation
        # TODO: Add username format validation
        # TODO: Add channel name format validation
        
        # Create configuration dictionary
        config = {
            "username": username,
            "oauth_token": oauth_token,
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
