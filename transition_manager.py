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
        
        # Effect transition cycling state
        self.colour_scheme_order_indices = []
        self.current_colour_scheme_position = 0
        self._last_colour_scheme_setting = self.settings.transition.transition_colour_scheme
        self._last_colour_scheme_order = self.settings.transition.colour_scheme_order
        
        self.transition_mode_order_indices = []
        self.current_transition_mode_position = 0
        self._last_transition_mode_setting = self.settings.transition.transition_colour_mode
        self._last_transition_mode_order = self.settings.transition.colour_mode_order
        
        # Initialize effect order lists
        self._initialise_colour_scheme_order()
        self._initialise_transition_mode_order()
        
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
    
    def _initialise_colour_scheme_order(self) -> None:
        """Initialise the colour scheme order based on current settings"""
        from config.enums import ColourScheme
        
        # Create list of all colour scheme enum values
        self.colour_scheme_order_indices = list(ColourScheme)
        
        # Apply ordering based on order mode
        if self.settings.transition.colour_scheme_order == "random":
            random.shuffle(self.colour_scheme_order_indices)
            print(f"Colour scheme order shuffled: {[s.value for s in self.colour_scheme_order_indices[:5]]}...")
        else:
            print(f"Colour scheme order sequential: {len(self.colour_scheme_order_indices)} schemes")
        
        self.current_colour_scheme_position = 0
    
    def _initialise_transition_mode_order(self) -> None:
        """Initialise the transition mode order based on current settings"""
        from config.enums import TransitionMode
        
        # Create list of all transition mode enum values
        self.transition_mode_order_indices = list(TransitionMode)
        
        # Apply ordering based on order mode
        if self.settings.transition.colour_mode_order == "random":
            random.shuffle(self.transition_mode_order_indices)
            print(f"Transition mode order shuffled: {[m.value for m in self.transition_mode_order_indices]}")
        else:
            print(f"Transition mode order sequential: {len(self.transition_mode_order_indices)} modes")
        
        self.current_transition_mode_position = 0
    
    def _update_colour_scheme_order_for_mode_change(self, new_order_mode: str) -> None:
        """Update colour scheme order when order mode changes via GUI"""
        from config.enums import ColourScheme
        
        old_order_mode = self._last_colour_scheme_order
        
        # Only change order if the mode actually changed
        if new_order_mode != old_order_mode:
            self.colour_scheme_order_indices = list(ColourScheme)
            
            if new_order_mode == "random":
                random.shuffle(self.colour_scheme_order_indices)
                print(f"Colour scheme order changed to random: {[s.value for s in self.colour_scheme_order_indices[:5]]}...")
            else:
                print(f"Colour scheme order changed to sequential")
            
            # Reset position to start
            self.current_colour_scheme_position = 0
        
        self._last_colour_scheme_order = new_order_mode
    
    def _update_transition_mode_order_for_mode_change(self, new_order_mode: str) -> None:
        """Update transition mode order when order mode changes via GUI"""
        from config.enums import TransitionMode
        
        old_order_mode = self._last_transition_mode_order
        
        # Only change order if the mode actually changed
        if new_order_mode != old_order_mode:
            self.transition_mode_order_indices = list(TransitionMode)
            
            if new_order_mode == "random":
                random.shuffle(self.transition_mode_order_indices)
                print(f"Transition mode order changed to random: {[m.value for m in self.transition_mode_order_indices]}")
            else:
                print(f"Transition mode order changed to sequential")
            
            # Reset position to start
            self.current_transition_mode_position = 0
        
        self._last_transition_mode_order = new_order_mode
    
    def _check_effect_transition_setting_changes(self) -> None:
        """Check if effect transition settings have changed and update accordingly"""
        if not os.path.exists(self.settings_file_path):
            return
        
        try:
            current_settings_mtime = os.path.getmtime(self.settings_file_path)
            if current_settings_mtime > self.last_settings_mtime:
                # File was modified, load and check effect transition settings
                current_settings = Settings.load_from_file(self.settings_file_path)
                
                # Check Colour scheme transition setting changes
                current_color_scheme_enabled = current_settings.transition.transition_colour_scheme
                current_color_scheme_order = current_settings.transition.colour_scheme_order
                
                if current_color_scheme_enabled != self._last_colour_scheme_setting:
                    print(f"[EFFECT] Colour scheme transition: {self._last_colour_scheme_setting} -> {current_color_scheme_enabled}")
                    self.settings.transition.transition_colour_scheme = current_color_scheme_enabled
                    self._last_colour_scheme_setting = current_color_scheme_enabled
                    
                    # Initialize order list if just enabled
                    if current_color_scheme_enabled:
                        self._initialise_colour_scheme_order()
                
                if current_color_scheme_order != self._last_colour_scheme_order:
                    print(f"[EFFECT] Colour scheme order: {self._last_colour_scheme_order} -> {current_color_scheme_order}")
                    self.settings.transition.colour_scheme_order = current_color_scheme_order
                    self._update_colour_scheme_order_for_mode_change(current_color_scheme_order)
                
                # Check transition mode setting changes
                current_transition_mode_enabled = current_settings.transition.transition_colour_mode
                current_transition_mode_order = current_settings.transition.colour_mode_order
                
                if current_transition_mode_enabled != self._last_transition_mode_setting:
                    print(f"[EFFECT] Transition mode transition: {self._last_transition_mode_setting} -> {current_transition_mode_enabled}")
                    self.settings.transition.transition_colour_mode = current_transition_mode_enabled
                    self._last_transition_mode_setting = current_transition_mode_enabled
                    
                    # Initialize order list if just enabled
                    if current_transition_mode_enabled:
                        self._initialise_transition_mode_order()
                
                if current_transition_mode_order != self._last_transition_mode_order:
                    print(f"[EFFECT] Transition mode order: {self._last_transition_mode_order} -> {current_transition_mode_order}")
                    self.settings.transition.colour_mode_order = current_transition_mode_order
                    self._update_transition_mode_order_for_mode_change(current_transition_mode_order)
                
        except Exception as e:
            print(f"Error checking effect transition setting changes: {e}")
    
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
            self._check_effect_transition_setting_changes()
        
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
    
    def _apply_effect_transitions(self) -> None:
        """Apply effect transitions before text changes (if enabled)"""
        
        # 1. Colour scheme TRANSITION
        if self.settings.transition.transition_colour_scheme:
            if self.settings.transition.colour_scheme_order == "sequential":
                # Get next Colour scheme from order list
                if not self.colour_scheme_order_indices:
                    self._initialise_colour_scheme_order()
                
                next_scheme = self.colour_scheme_order_indices[self.current_colour_scheme_position]
                self.current_colour_scheme_position = (self.current_colour_scheme_position + 1) % len(self.colour_scheme_order_indices)
                
                # Reshuffle on cycle completion if in random mode
                if self.current_colour_scheme_position == 0 and self.settings.transition.colour_scheme_order == "random":
                    random.shuffle(self.colour_scheme_order_indices)
                    print(f"[EFFECT] Reshuffled Colour scheme order for new cycle")
                
                print(f"[EFFECT] Sequential Colour scheme: {next_scheme.value}")
            else:  # random
                # Pick random Colour scheme
                from config.enums import ColourScheme
                next_scheme = random.choice(list(ColourScheme))
                print(f"[EFFECT] Random Colour scheme: {next_scheme.value}")
            
            # Apply to displayer
            self.displayer.set_ghost_colour_scheme(next_scheme)
        
        # 2. TRANSITION MODE TRANSITION
        if self.settings.transition.transition_colour_mode:
            if self.settings.transition.colour_mode_order == "sequential":
                # Get next transition mode from order list
                if not self.transition_mode_order_indices:
                    self._initialise_transition_mode_order()
                
                next_mode = self.transition_mode_order_indices[self.current_transition_mode_position]
                self.current_transition_mode_position = (self.current_transition_mode_position + 1) % len(self.transition_mode_order_indices)
                
                # Reshuffle on cycle completion if in random mode
                if self.current_transition_mode_position == 0 and self.settings.transition.colour_mode_order == "random":
                    random.shuffle(self.transition_mode_order_indices)
                    print(f"[EFFECT] Reshuffled transition mode order for new cycle")
                
                print(f"[EFFECT] Sequential transition mode: {next_mode.value}")
            else:  # random
                # Pick random transition mode
                from config.enums import TransitionMode
                next_mode = random.choice(list(TransitionMode))
                print(f"[EFFECT] Random transition mode: {next_mode.value}")
            
            # Apply to displayer
            self.displayer.set_colour_transition_mode(next_mode)
        
        # 3. GHOST PARAMETERS TRANSITION
        if self.settings.transition.transition_ghost_params:
            # Generate random values within configured ranges
            ghost_chance = random.uniform(
                self.settings.transition.ghost_chance_min,
                self.settings.transition.ghost_chance_max
            )
            ghost_decay = random.uniform(
                self.settings.transition.ghost_decay_min,
                self.settings.transition.ghost_decay_max
            )
            
            print(f"[EFFECT] Ghost params: chance={ghost_chance:.3f}, decay={ghost_decay:.4f}")
            
            # Apply to displayer
            self.displayer.configure_overlay_effects(
                ghost_chance=ghost_chance,
                ghost_decay=ghost_decay
            )
        
        # 4. FLICKER PARAMETERS TRANSITION
        if self.settings.transition.transition_flicker_params:
            # Generate random values within configured ranges
            flicker_chance = random.uniform(
                self.settings.transition.flicker_chance_min,
                self.settings.transition.flicker_chance_max
            )
            flicker_intensity = random.uniform(
                self.settings.transition.flicker_intensity_min,
                self.settings.transition.flicker_intensity_max
            )
            
            print(f"[EFFECT] Flicker params: chance={flicker_chance:.3f}, intensity={flicker_intensity:.3f}")
            
            # Apply to displayer
            self.displayer.configure_overlay_effects(
                flicker_chance=flicker_chance,
                flicker_intensity=flicker_intensity
            )
        
        # 5. SPEED VARIATION
        if self.settings.transition.transition_speed_variation:
            # Generate random speed within configured range
            speed = random.uniform(
                self.settings.transition.speed_min,
                self.settings.transition.speed_max
            )
            
            print(f"[EFFECT] Speed variation: {speed:.1f} px/frame")
            
            # Apply to displayer
            self.displayer.set_transition_speed(speed)
    
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
            
        # No blank time - apply effect transitions then transition directly to next text
        self._apply_effect_transitions()
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
            
            # Apply effect transitions now that blank period is complete
            self._apply_effect_transitions()
            
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
