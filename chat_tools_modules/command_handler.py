"""
Command Handler Module

Handles Twitch chat command processing including:
- Command matching from trigger words
- Permission checking (streamer, mods, everyone)
- Cooldown management
- Response sending
"""

import time
from typing import Any, Optional, Callable
from logger_setup import setup_logger

logger = setup_logger(__name__)


class CommandHandler:
    """Handles chat command processing with permissions and cooldowns."""
    
    def __init__(
        self,
        config_getter: Callable[[], Optional[dict]],
        send_message_callback: Callable[[str], Any],
        log_callback: Optional[Callable[[str], None]] = None
    ):
        """Initialize the command handler.
        
        Args:
            config_getter: Function that returns current config dict (for live reload support)
            send_message_callback: Async function to send message responses
            log_callback: Optional function to log command execution
        """
        self.config_getter = config_getter
        self.send_message_callback = send_message_callback
        self.log_callback = log_callback
        
        # Track command cooldowns: {trigger -> last_used_timestamp}
        self.command_cooldowns: dict[str, float] = {}
    
    async def handle_command(self, message: Any) -> None:
        """Process incoming message for potential command execution.
        
        Checks if message matches any configured command triggers, validates
        permissions and cooldowns, then executes the command response.
        
        Args:
            message: ChatMessage object with .text and .chatter attributes
            
        TODO: Add command usage statistics tracking
        """
        config = self.config_getter()
        if not config:
            return
        
        commands = config.get("commands", [])
        if not commands:
            return
        
        content = message.text.strip()
        if not content:
            return
        
        # Extract first word as potential command trigger
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
        if not self._check_cooldown(trigger, matched_command):
            return
        
        # Check permissions
        if not self._check_permission(message, matched_command, config):
            return
        
        # Execute command - send response
        await self._execute_command(trigger, matched_command, message.chatter.name)
    
    def _check_cooldown(self, trigger: str, command: dict) -> bool:
        """Check if command is off cooldown.
        
        Args:
            trigger: The trigger word that was used
            command: Command configuration dict with 'cooldown' seconds
            
        Returns:
            True if command can be executed, False if still on cooldown
        """
        now = time.time()
        cooldown = command.get("cooldown", 0)
        
        if trigger in self.command_cooldowns:
            last_used = self.command_cooldowns[trigger]
            time_since = now - last_used
            
            if time_since < cooldown:
                remaining = int(cooldown - time_since)
                logger.debug(f"Command {trigger} on cooldown ({remaining}s remaining)")
                return False
        
        return True
    
    def _check_permission(self, message: Any, command: dict, config: dict) -> bool:
        """Check if user has permission to execute command.
        
        Args:
            message: ChatMessage object with .chatter attribute
            command: Command configuration dict with 'permission' level
            config: Bot configuration with 'channel' owner name
            
        Returns:
            True if user has permission, False otherwise
        """
        permission = command.get("permission", "everyone")
        username = message.chatter.name.lower()
        channel_owner = config.get("channel", "").lower()
        
        if permission == "streamer":
            if username != channel_owner:
                logger.debug(f"{username} tried to use streamer-only command")
                return False
        
        elif permission == "mods":
            # Check if user is mod or broadcaster
            is_mod = message.chatter.is_mod if hasattr(message.chatter, 'is_mod') else False
            is_broadcaster = username == channel_owner
            
            if not (is_mod or is_broadcaster):
                logger.debug(f"{username} tried to use mod-only command")
                return False
        
        # "everyone" permission - no restrictions
        return True
    
    async def _execute_command(self, trigger: str, command: dict, username: str) -> None:
        """Execute command by sending response and updating cooldown.
        
        Args:
            trigger: The trigger word that was used
            command: Command configuration dict with 'response'
            username: Username of the user who triggered the command
        """
        response = command.get("response", "")
        if not response:
            return
        
        try:
            # Send response via callback (async)
            await self.send_message_callback(response)
            
            # Update cooldown
            self.command_cooldowns[trigger] = time.time()
            
            # Log execution
            if self.log_callback:
                self.log_callback(f"[BOT] {response}")
            
            logger.info(f"Command {trigger} executed by {username}")
        
        except Exception as e:
            logger.error(f"Failed to send command response: {e}")
            import traceback
            traceback.print_exc()
