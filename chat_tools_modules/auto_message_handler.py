"""
Auto Message Handler Module

Handles automatic message posting with:
- Interval-based posting
- Chat activity thresholds
- Random or sequential message selection
- Enable/disable toggling
"""

import asyncio
import time
import random
from typing import Optional, Callable, Any
from logger_setup import setup_logger

logger = setup_logger(__name__)


class AutoMessageHandler:
    """Manages automatic message posting to Twitch chat.
    
    Handles:
    - Timed message posting based on configured interval
    - Activity threshold checking (minimum messages in window)
    - Random or sequential message selection
    - Live config reloading
    """
    
    def __init__(
        self,
        config_getter: Callable[[], Optional[dict]],
        send_message_callback: Callable[[str], Any],
        activity_tracker: list[float],
        log_callback: Optional[Callable[[str], None]] = None
    ):
        """Initialize the auto-message handler.
        
        Args:
            config_getter: Function that returns current config dict (for live reload)
            send_message_callback: Async function to send messages
            activity_tracker: List of timestamps tracking recent chat activity
            log_callback: Optional function to log auto-message sends
        """
        self.config_getter = config_getter
        self.send_message_callback = send_message_callback
        self.activity_tracker = activity_tracker
        self.log_callback = log_callback
        
        # Track message index for sequential mode
        self.message_index: int = 0
        
        # Task reference for cancellation
        self.task: Optional[asyncio.Task] = None
    
    def start(self) -> None:
        """Start the auto-message loop as an asyncio task."""
        if self.task and not self.task.done():
            logger.warning("Auto-message loop already running")
            return
        
        self.task = asyncio.create_task(self._auto_message_loop())
        logger.info("Auto-message loop started")
    
    def stop(self) -> None:
        """Stop the auto-message loop."""
        if self.task and not self.task.done():
            self.task.cancel()
            logger.info("Auto-message loop stopped")
    
    async def _auto_message_loop(self) -> None:
        """Background task for posting auto messages at intervals.
        
        Continuously runs while connected, checking config each iteration
        for live updates. Posts messages when:
        - Auto-messages are enabled
        - Interval has elapsed
        - Chat activity threshold is met
        - There are enabled messages to send
        
        TODO: Add schedule-based messages (time of day restrictions)
        TODO: Add viewer count thresholds
        TODO: Add integration with stream events
        """
        while True:
            try:
                config = self.config_getter()
                if not config:
                    await asyncio.sleep(60)
                    continue
                
                # Get fresh auto-message config
                auto_msg_config = config.get("auto_messages", {})
                
                # Check if enabled
                if not auto_msg_config.get("enabled", True):
                    await asyncio.sleep(60)  # Check again in 1 minute
                    continue
                
                # Get configuration
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
                if not self._check_activity(min_activity, activity_window_minutes):
                    continue
                
                # Select and send message
                await self._send_auto_message(enabled_messages, random_order)
            
            except asyncio.CancelledError:
                logger.info("Auto-message task cancelled")
                break
            
            except Exception as e:
                logger.error(f"Auto-message loop error: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(60)  # Wait before retrying
    
    def _check_activity(self, min_activity: int, activity_window_minutes: int) -> bool:
        """Check if chat activity meets threshold.
        
        Counts recent messages in activity window and cleans old timestamps.
        
        Args:
            min_activity: Minimum number of messages required
            activity_window_minutes: Time window to check
            
        Returns:
            True if activity threshold met, False otherwise
        """
        now = time.time()
        activity_window_seconds = activity_window_minutes * 60
        
        # Count messages in activity window
        recent_messages = [
            ts for ts in self.activity_tracker
            if now - ts <= activity_window_seconds
        ]
        
        # Clean old timestamps (mutate in place)
        self.activity_tracker.clear()
        self.activity_tracker.extend(recent_messages)
        
        if len(recent_messages) < min_activity:
            logger.debug(
                f"Skipping auto-message: insufficient activity "
                f"({len(recent_messages)}/{min_activity})"
            )
            return False
        
        return True
    
    async def _send_auto_message(self, enabled_messages: list[dict], random_order: bool) -> None:
        """Select and send an auto-message.
        
        Args:
            enabled_messages: List of enabled message dicts with 'text'
            random_order: If True, select randomly; if False, select sequentially
        """
        # Select message
        if random_order:
            message = random.choice(enabled_messages)
        else:
            # Sequential mode
            message = enabled_messages[self.message_index % len(enabled_messages)]
            self.message_index += 1
        
        # Send message
        text = message.get("text", "")
        if not text:
            return
        
        try:
            await self.send_message_callback(text)
            
            # Log to UI
            if self.log_callback:
                self.log_callback(f"[AUTO] {text}")
            
            logger.info(f"Auto-message sent: {text[:50]}...")
        
        except Exception as e:
            logger.error(f"Failed to send auto-message: {e}")
            import traceback
            traceback.print_exc()
