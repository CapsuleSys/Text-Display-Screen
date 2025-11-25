import random
import os
import time
from typing import List, Optional, Callable
from config.settings import Settings

class TransitionManager:
    def __init__(self, screen_displayer, settings: Optional[Settings] = None):
        self.displayer = screen_displayer
        self.frame_count = 0
        
        # Store settings reference, create default if none provided
        self.settings = settings if settings is not None else Settings.create_default()
        
        # Transition scheduling
        self.text_change_interval = 1500  # frames between text changes (25 seconds at 60fps)
        self.current_text_block = 0
        
        # Text order management for shuffling
        self.text_order_indices = []  # List of indices for text blocks
        self.current_order_position = 0  # Current position in the order list
        self._last_shuffle_setting = self.settings.transition.shuffle_text_order  # Track shuffle setting changes
        self.shuffle_check_interval = 180  # Check shuffle setting every 180 frames (3 seconds)
        
        # Blank transition state
        self.is_in_blank_period = False
        self.blank_period_start_frame = 0
        self.blank_time_between_transitions = self.settings.transition.blank_time_between_transitions
        
        # File monitoring
        self.text_file_path = None
        self.last_file_mtime = 0
        self.file_check_interval = self.settings.file_monitoring.file_check_interval
        
        # Settings file monitoring
        self.settings_file_path = "config/user_settings.json"
        self.last_settings_mtime = 0
        if os.path.exists(self.settings_file_path):
            self.last_settings_mtime = os.path.getmtime(self.settings_file_path)
        
        # Text file selection monitoring
        self.text_file_selection_path = "config/current_text_file.txt"
        self.last_text_selection_mtime = 0
        if os.path.exists(self.text_file_selection_path):
            self.last_text_selection_mtime = os.path.getmtime(self.text_file_selection_path)
        
        # Callbacks for custom behavior
        self.on_text_change: Optional[Callable[[int], None]] = None
        
        print("TransitionManager initialized")
    
    def _initialize_text_order(self) -> None:
        """Initialize or regenerate the text order based on current settings"""
        if not self.displayer.text_content:
            self.text_order_indices = []
            return
            
        # Create list of all text block indices
        self.text_order_indices = list(range(len(self.displayer.text_content)))
        
        # Apply ordering based on shuffle setting
        if self.settings.transition.shuffle_text_order:
            # Only shuffle if we're turning shuffle ON (not every time settings reload)
            random.shuffle(self.text_order_indices)
            print(f"Text order shuffled: {self.text_order_indices[:10]}{'...' if len(self.text_order_indices) > 10 else ''}")
        else:
            # Keep sequential order when shuffle is OFF
            print(f"Text order sequential: 0 to {len(self.text_order_indices)-1}")
            
        self.current_order_position = 0
    
    def _update_text_order_for_shuffle_change(self, new_shuffle_setting: bool) -> None:
        """Update text order when shuffle setting changes via GUI"""
        if not self.displayer.text_content:
            return
            
        old_shuffle_setting = getattr(self, '_last_shuffle_setting', False)
        
        # Only change order if the shuffle setting actually changed
        if new_shuffle_setting != old_shuffle_setting:
            if new_shuffle_setting:
                # Turning shuffle ON - create new shuffled order
                self.text_order_indices = list(range(len(self.displayer.text_content)))
                random.shuffle(self.text_order_indices)
                print(f"Shuffle enabled - new order: {self.text_order_indices[:10]}{'...' if len(self.text_order_indices) > 10 else ''}")
            else:
                # Turning shuffle OFF - return to sequential order
                self.text_order_indices = list(range(len(self.displayer.text_content)))
                print(f"Shuffle disabled - returning to sequential order: 0 to {len(self.text_order_indices)-1}")
            
            # Reset position to start of new order
            self.current_order_position = 0
            
        self._last_shuffle_setting = new_shuffle_setting
    
    def _check_shuffle_setting_changes(self) -> None:
        """Check if shuffle setting has changed and update text order accordingly"""
        # Only check if settings file has been modified since last check
        if os.path.exists(self.settings_file_path):
            try:
                current_settings_mtime = os.path.getmtime(self.settings_file_path)
                if current_settings_mtime > self.last_settings_mtime:
                    # File was modified, load and check shuffle setting
                    current_settings = Settings.load_from_file(self.settings_file_path)
                    current_shuffle = current_settings.transition.shuffle_text_order
                    
                    # Check if shuffle setting changed
                    if current_shuffle != self._last_shuffle_setting:
                        print(f"[SHUFFLE] Setting changed: {self._last_shuffle_setting} -> {current_shuffle}")
                        
                        # Update our settings reference
                        self.settings.transition.shuffle_text_order = current_shuffle
                        
                        # Update text order based on new setting
                        self._update_text_order_for_shuffle_change(current_shuffle)
                        
            except Exception as e:
                print(f"Error checking shuffle setting changes: {e}")
    
    def _get_next_text_block(self) -> int:
        """Get the next text block index according to current ordering (shuffled or sequential)"""
        if not self.text_order_indices:
            self._initialize_text_order()
            
        if not self.text_order_indices:
            return 0  # Fallback if no text content
            
        # Get next index from order
        next_block = self.text_order_indices[self.current_order_position]
        
        # Advance position and wrap around
        self.current_order_position = (self.current_order_position + 1) % len(self.text_order_indices)
        
        # If we've wrapped around and shuffle is enabled, reshuffle for next cycle
        # If shuffle is disabled, sequential order will naturally repeat (0,1,2,3,0,1,2,3...)
        if self.current_order_position == 0 and self.settings.transition.shuffle_text_order:
            random.shuffle(self.text_order_indices)
            print(f"Reshuffled text order for new cycle: {self.text_order_indices[:10]}{'...' if len(self.text_order_indices) > 10 else ''}")
        elif self.current_order_position == 0 and not self.settings.transition.shuffle_text_order:
            print("Sequential order cycle completed, continuing with: 0, 1, 2, 3...")
        
        # Update current_text_block for compatibility
        self.current_text_block = next_block
        return next_block
    
    def set_text_change_interval(self, frames: int) -> None:
        """Set how many frames between text changes"""
        self.text_change_interval = frames
    
    def set_text_file_monitoring(self, file_path: str) -> None:
        """Enable monitoring of a text file for changes"""
        self.text_file_path = file_path
        if os.path.exists(file_path):
            self.last_file_mtime = os.path.getmtime(file_path)
            print(f"File monitoring enabled for: {file_path}")
    
    def _check_file_changes(self) -> None:
        """Check if the monitored text file and settings file have been modified"""
        # Check text file changes
        if self.text_file_path and os.path.exists(self.text_file_path):
            current_mtime = os.path.getmtime(self.text_file_path)
            if current_mtime > self.last_file_mtime:
                print(f"Text file {self.text_file_path} was modified. Reloading...")
                try:
                    self.displayer.load_text_file(self.text_file_path)
                    self.last_file_mtime = current_mtime
                    print(f"Successfully reloaded {len(self.displayer.text_content)} text blocks")
                    
                    # Reinitialize text order with new content
                    self._initialize_text_order()
                    
                except Exception as e:
                    print(f"Error reloading text file: {e}")
        
        # Check settings file changes
        if os.path.exists(self.settings_file_path):
            current_settings_mtime = os.path.getmtime(self.settings_file_path)
            if current_settings_mtime > self.last_settings_mtime:
                print(f"Settings file {self.settings_file_path} was modified. Reloading...")
                try:
                    new_settings = Settings.load_from_file(self.settings_file_path)
                    self.settings = new_settings
                    
                    # Apply new settings to displayer
                    self.settings.apply_to_displayer(self.displayer)
                    self.settings.apply_to_transition_manager(self)
                    
                    # Update blank time setting
                    self.blank_time_between_transitions = self.settings.transition.blank_time_between_transitions
                    
                    self.last_settings_mtime = current_settings_mtime
                    print("Successfully reloaded and applied settings")
                    
                    # Update text order based on shuffle setting change
                    self._update_text_order_for_shuffle_change(self.settings.transition.shuffle_text_order)
                    
                except Exception as e:
                    print(f"Error reloading settings file: {e}")
        
        # Check text file selection changes
        if os.path.exists(self.text_file_selection_path):
            current_text_selection_mtime = os.path.getmtime(self.text_file_selection_path)
            if current_text_selection_mtime > self.last_text_selection_mtime:
                print(f"Text file selection {self.text_file_selection_path} was modified. Switching text file...")
                try:
                    with open(self.text_file_selection_path, 'r', encoding='utf-8') as f:
                        new_text_file = f.read().strip()
                    
                    if os.path.exists(new_text_file) and new_text_file != self.text_file_path:
                        # Update monitored text file
                        self.text_file_path = new_text_file
                        self.last_file_mtime = os.path.getmtime(new_text_file)
                        
                        # Load new text file
                        self.displayer.load_text_file(new_text_file)
                        
                        # Reinitialize text order with new file content
                        self._initialize_text_order()
                        
                        # Start with first text block in the order
                        first_block = self.text_order_indices[0] if self.text_order_indices else 0
                        self.current_text_block = first_block
                        self.displayer.display_text(first_block)
                        
                        print(f"Successfully switched to text file: {new_text_file}")
                        print(f"New file contains {len(self.displayer.text_content)} text blocks")
                    
                    self.last_text_selection_mtime = current_text_selection_mtime
                    
                except Exception as e:
                    print(f"Error switching text file: {e}")
    
    def update(self) -> None:
        """Update the transition manager - call this every frame"""
        self.frame_count += 1
        
        # Check for file changes periodically
        if self.frame_count % self.file_check_interval == 0:
            self._check_file_changes()
        
        # Check for shuffle setting changes more frequently
        if self.frame_count % self.shuffle_check_interval == 0:
            self._check_shuffle_setting_changes()
        
        # Update the screen displayer's transition first
        self.displayer.update_transition()
        
        # Only make changes when not currently transitioning
        if self.displayer.is_transitioning:
            return
        
        # Check if we're in a blank period and if it should end
        if self.is_in_blank_period:
            self._check_blank_period_completion()
            return  # Don't process text changes while in blank period
        
        # Check if it's time for a text change
        text_change_due = self.frame_count % self.text_change_interval == 0
        if text_change_due:
            print(f"[TIMING] Frame {self.frame_count}: Text change due! Starting text change process")
            self._handle_text_change()
    
    def _handle_text_change(self):
        """Handle automatic text changes"""
        if not self.displayer.text_content:
            return
        
        # If blank time is configured, start blank period
        if self.blank_time_between_transitions > 0:
            current_time = time.time()
            self.is_in_blank_period = True
            self.blank_period_start_frame = self.frame_count
            self.blank_period_start_time = current_time
            
            # Transition to empty/blank display
            print(f"[TIMING] Frame {self.frame_count}: Starting blank transition (target: {self.blank_time_between_transitions} frames)")
            print(f"[DEBUG] blank_time_between_transitions = {self.blank_time_between_transitions}")
            print(f"[DEBUG] Settings blank_time = {self.settings.transition.blank_time_between_transitions}")
            self.displayer.start_transition_to_blank()
            return
            
        # No blank time - transition directly to next text
        next_block = self._get_next_text_block()
        print(f"[TIMING] Frame {self.frame_count}: Starting text transition to block {next_block}")
        self.displayer.display_text(next_block)
        
        # Call callback if set
        if self.on_text_change:
            self.on_text_change(next_block)
    
    def _check_blank_period_completion(self) -> None:
        """Check if the current blank period should end"""
        if not self.is_in_blank_period:
            return
            
        current_time = time.time()
        frames_elapsed = self.frame_count - self.blank_period_start_frame
        time_elapsed = current_time - self.blank_period_start_time
        
        print(f"[TIMING] Frame {self.frame_count}: Checking blank period - {frames_elapsed}/{self.blank_time_between_transitions} frames ({time_elapsed:.2f}s)")
        
        if frames_elapsed >= self.blank_time_between_transitions:
            self.is_in_blank_period = False
            print(f"[TIMING] Frame {self.frame_count}: Blank period complete after {frames_elapsed} frames ({time_elapsed:.2f}s), transitioning to next text")
            
            # Immediately transition to next text
            next_block = self._get_next_text_block()
            print(f"[TIMING] Frame {self.frame_count}: Starting text transition to block {next_block}")
            self.displayer.display_text(next_block)
            
            # Call callback if set
            if self.on_text_change:
                self.on_text_change(next_block)
    
    def manual_text_change(self, block_index: int) -> None:
        """Manually trigger a text change"""
        if not self.displayer.is_transitioning and block_index < len(self.displayer.text_content):
            self.current_text_block = block_index
            self.displayer.display_text(block_index)
            if self.on_text_change:
                self.on_text_change(block_index)
    
    def start_initial_display(self) -> None:
        """Start the initial display with first text block"""
        if self.displayer.text_content:
            # Initialize text order first
            self._initialize_text_order()
            
            # Set initial state (empty grid)
            for row in range(self.displayer.grid_height):
                for col in range(self.displayer.grid_width):
                    self.displayer.current_grid[row][col] = False
            
            # Start transition to first text block in order
            first_block = self.text_order_indices[0] if self.text_order_indices else 0
            self.displayer.display_text(first_block)
            self.current_text_block = first_block
            
            print("Initial display started")
    
    def get_status(self) -> dict:
        """Get current status information"""
        return {
            'frame_count': self.frame_count,
            'current_text_block': self.current_text_block,
            'is_transitioning': self.displayer.is_transitioning
        }
        self.current_text_block = (self.current_text_block + 1) % len(self.displayer.text_content)
        self.displayer.display_text(self.current_text_block)
        
        # Call callback if set
        if self.on_text_change:
            self.on_text_change(self.current_text_block)
        
        print(f"Text changed to block: {self.current_text_block}")
