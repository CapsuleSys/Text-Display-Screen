import random
import pygame
import math
from typing import List, Tuple, Dict, Optional, Union, Any
from colour_schemes import get_colour_scheme, validate_colour_scheme
from config.enums import TransitionMode, ColourScheme
from config.settings import Settings
from logger_setup import setup_logger

logger = setup_logger(__name__)

class ScreenOverlay:
    def __init__(self, grid_width: int, grid_height: int, square_size: int, display_scale: float = 1.0, 
                 settings: Optional[Settings] = None):
        """Initialise the screen overlay system"""
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.square_size = square_size
        self.display_scale = display_scale
        
        # Store settings reference, create default if none provided
        self.settings = settings if settings is not None else Settings.create_default()
        
        # Effect layers - now store (intensity, colour, timer) tuples for ghosts
        self.ghost_layer = [[(0.0, (255, 0, 0), 0) for _ in range(grid_width)] for _ in range(grid_height)]
        self.flicker_layer = [[0.0 for _ in range(grid_width)] for _ in range(grid_height)]
        
        # Effect parameters
        self.ghost_chance = 0.5  # Increased chance for better outline effect
        self.ghost_decay = 0.99   # How quickly ghost pixels fade
        self.ghost_min_intensity = 0.1  # Minimum intensity before ghost disappears
        self.ghost_spawn_chance = 0.05  # Increased spawn chance for outline effect
        self.flicker_chance = 0.0  # Chance for pixel to flicker
        self.flicker_intensity = 0.2  # Intensity of flicker effect
        
        # Colour settings - now supports colour schemes
        self.current_colour_scheme = get_colour_scheme('classic')
        self.colour_scheme_name = 'classic'
        self.colour_shift_speed = 0.005  # How fast colours shift (radians per frame) - 4x slower
        self.colour_time = 0.0  # Internal timer for colour shifting
        self.flicker_colour = (255, 200, 100)  # Warm flicker colour
        
        # Colour transition mode
        self.colour_transition_mode = TransitionMode.SMOOTH
        self.snap_duration = 120  # frames to hold each colour in snap mode (2 seconds at 60fps)
        
        # Text boundary tracking for spread modes
        self.text_bounds = {
            'min_col': 0,
            'max_col': grid_width - 1,
            'min_row': 0,
            'max_row': grid_height - 1
        }
        
        # Colour averaging settings
        self.enable_colour_averaging = False
        self.colour_averaging_interval = 30  # frames
        
        logger.info(f"ScreenOverlay initialized: {grid_width}x{grid_height}")
    
    def update_effects(self, current_grid: List[List[bool]]) -> None:
        """Update all overlay effects based on current screen state"""
        # Update colour shift timer
        self.colour_time += self.colour_shift_speed
        
        # Update text boundaries for spread modes
        self._update_text_bounds(current_grid)
        
        self._update_ghost_effects(current_grid)
        self._update_flicker_effects(current_grid)
        
        # Apply colour averaging if enabled (checks individual pixel timers)
        if self.enable_colour_averaging:
            self._apply_colour_averaging()
    
    def set_colour_scheme(self, scheme: Union[ColourScheme, str]) -> bool:
        """Set the colour scheme for ghost effects. Accepts ColourScheme enum or string. Returns True if successful."""
        try:
            new_scheme = get_colour_scheme(scheme)
            if validate_colour_scheme(new_scheme):
                self.current_colour_scheme = new_scheme
                if isinstance(scheme, ColourScheme):
                    self.colour_scheme_name = scheme.value
                else:
                    self.colour_scheme_name = str(scheme).lower()
                logger.info(f"Colour scheme changed to: {self.colour_scheme_name}")
                return True
            else:
                logger.warning(f"Invalid colour scheme format: {scheme}")
                return False
        except Exception as e:
            logger.error(f"Error setting colour scheme {scheme}: {e}")
            return False
    
    def set_custom_colour_scheme(self, colours: List[Tuple[int, int, int]]) -> bool:
        """Set a custom colour scheme. Returns True if successful."""
        if validate_colour_scheme(colours):
            self.current_colour_scheme = colours
            self.colour_scheme_name = 'custom'
            logger.info(f"Custom colour scheme set with {len(colours)} colours")
            return True
        else:
            logger.warning("Invalid custom colour scheme format")
            return False
    
    def set_colour_transition_mode(self, mode: Union[TransitionMode, str], snap_duration: Optional[int] = None) -> bool:
        """Set the colour transition mode. Accepts TransitionMode enum or string. Returns True if successful."""
        try:
            if isinstance(mode, TransitionMode):
                self.colour_transition_mode = mode
                mode_name = mode.value
            else:
                mode_lower = str(mode).lower()
                self.colour_transition_mode = TransitionMode.from_string(mode_lower)
                mode_name = mode_lower
            
            if snap_duration is not None:
                self.snap_duration = max(1, snap_duration)
            
            logger.info(f"Colour transition mode set to: {mode_name}")
            if self.colour_transition_mode == TransitionMode.SNAP:
                logger.info(f"Snap duration: {self.snap_duration} frames")
            elif self.colour_transition_mode == TransitionMode.MIXED:
                logger.info("Mixed mode: each ghost gets a random colour from the scheme")
            elif self.colour_transition_mode == TransitionMode.SPREAD_HORIZONTAL:
                logger.info("Horizontal spread mode: colours spread horizontally across screen")
            elif self.colour_transition_mode == TransitionMode.SPREAD_VERTICAL:
                logger.info("Vertical spread mode: colours spread vertically across screen")
            elif self.colour_transition_mode == TransitionMode.SPREAD_DIAGONALLY_DOWN:
                logger.info("Diagonal down spread mode: colours spread diagonally from top-left to bottom-right")
            elif self.colour_transition_mode == TransitionMode.SPREAD_DIAGONALLY_UP:
                logger.info("Diagonal up spread mode: colours spread diagonally from bottom-left to top-right")
            
            return True
        except Exception as e:
            logger.error(f"Error setting colour transition mode: {e}")
            logger.info(f"Valid modes: {', '.join(TransitionMode.list_names())}")
            return False
    
    def _get_current_ghost_colour(self) -> Tuple[int, int, int]:
        """Get the current ghost colour based on time and colour scheme"""
        if not self.current_colour_scheme:
            return (255, 0, 0)  # Fallback red
        
        # For single colour schemes, just return that colour
        if len(self.current_colour_scheme) == 1:
            return self.current_colour_scheme[0]
        
        # For multi-colour schemes, choose behaviour based on transition mode
        scheme_length = len(self.current_colour_scheme)
        
        if self.colour_transition_mode == TransitionMode.SNAP:
            # Snap mode: hold each colour for a specific duration
            total_cycle_time = self.snap_duration * scheme_length
            frame_in_cycle = int(self.colour_time / self.colour_shift_speed) % total_cycle_time
            colour_index = frame_in_cycle // self.snap_duration
            return self.current_colour_scheme[colour_index % scheme_length]
        elif self.colour_transition_mode in [TransitionMode.SPREAD_HORIZONTAL, TransitionMode.SPREAD_VERTICAL, TransitionMode.SPREAD_DIAGONALLY_DOWN, TransitionMode.SPREAD_DIAGONALLY_UP]:
            # Spread modes: calculate colour based on position (use centre position as default)
            center_row = self.grid_height // 2
            center_col = self.grid_width // 2
            if self.colour_transition_mode == TransitionMode.SPREAD_HORIZONTAL:
                return self._get_horizontal_spread_colour(center_row, center_col)
            elif self.colour_transition_mode == TransitionMode.SPREAD_VERTICAL:
                return self._get_vertical_spread_colour(center_row, center_col)
            elif self.colour_transition_mode == TransitionMode.SPREAD_DIAGONALLY_DOWN:
                return self._get_diagonal_down_spread_colour(center_row, center_col)
            else:
                return self._get_diagonal_up_spread_colour(center_row, center_col)
        else:
            # Smooth mode: smoothly transition between colours
            colour_position = (math.sin(self.colour_time) + 1) / 2  # 0 to 1
            colour_index = colour_position * (scheme_length - 1)
            
            # Get the two adjacent colours to interpolate between
            lower_index = int(colour_index)
            upper_index = min(lower_index + 1, scheme_length - 1)
            blend_factor = colour_index - lower_index
            
            # Interpolate between the two colours
            colour1 = self.current_colour_scheme[lower_index]
            colour2 = self.current_colour_scheme[upper_index]
            
            r = int(colour1[0] * (1 - blend_factor) + colour2[0] * blend_factor)
            g = int(colour1[1] * (1 - blend_factor) + colour2[1] * blend_factor)
            b = int(colour1[2] * (1 - blend_factor) + colour2[2] * blend_factor)
            
            return (r, g, b)
    
    def _get_random_scheme_colour(self) -> Tuple[int, int, int]:
        """Get a random colour from the current colour scheme"""
        if not self.current_colour_scheme:
            return (255, 0, 0)  # Fallback red
        
        return random.choice(self.current_colour_scheme)
    
    def _get_horizontal_spread_colour(self, row: int, col: int) -> Tuple[int, int, int]:
        """Get colour based on horizontal position for horizontal spread mode"""
        if not self.current_colour_scheme or len(self.current_colour_scheme) < 2:
            return self.current_colour_scheme[0] if self.current_colour_scheme else (255, 0, 0)
        
        # Calculate horizontal position ratio based on text boundaries
        text_width = self.text_bounds['max_col'] - self.text_bounds['min_col']
        if text_width <= 0:
            horizontal_ratio = 0.0
        else:
            # Clamp the column to text boundaries
            clamped_col = max(self.text_bounds['min_col'], min(self.text_bounds['max_col'], col))
            horizontal_ratio = (clamped_col - self.text_bounds['min_col']) / text_width
        
        # Map the ratio to colour scheme
        scheme_length = len(self.current_colour_scheme)
        colour_position = horizontal_ratio * (scheme_length - 1)
        
        # Get the two adjacent colours to interpolate between
        lower_index = int(colour_position)
        upper_index = min(lower_index + 1, scheme_length - 1)
        blend_factor = colour_position - lower_index
        
        # Interpolate between the two colours
        colour1 = self.current_colour_scheme[lower_index]
        colour2 = self.current_colour_scheme[upper_index]
        
        r = int(colour1[0] * (1 - blend_factor) + colour2[0] * blend_factor)
        g = int(colour1[1] * (1 - blend_factor) + colour2[1] * blend_factor)
        b = int(colour1[2] * (1 - blend_factor) + colour2[2] * blend_factor)
        
        return (r, g, b)
    
    def _get_vertical_spread_colour(self, row: int, col: int) -> Tuple[int, int, int]:
        """Get colour based on vertical position for vertical spread mode"""
        if not self.current_colour_scheme or len(self.current_colour_scheme) < 2:
            return self.current_colour_scheme[0] if self.current_colour_scheme else (255, 0, 0)
        
        # Calculate vertical position ratio based on text boundaries
        text_height = self.text_bounds['max_row'] - self.text_bounds['min_row']
        if text_height <= 0:
            vertical_ratio = 0.0
        else:
            # Clamp the row to text boundaries
            clamped_row = max(self.text_bounds['min_row'], min(self.text_bounds['max_row'], row))
            vertical_ratio = (clamped_row - self.text_bounds['min_row']) / text_height
        
        # Map the ratio to colour scheme
        scheme_length = len(self.current_colour_scheme)
        colour_position = vertical_ratio * (scheme_length - 1)
        
        # Get the two adjacent colours to interpolate between
        lower_index = int(colour_position)
        upper_index = min(lower_index + 1, scheme_length - 1)
        blend_factor = colour_position - lower_index
        
        # Interpolate between the two colours
        colour1 = self.current_colour_scheme[lower_index]
        colour2 = self.current_colour_scheme[upper_index]
        
        r = int(colour1[0] * (1 - blend_factor) + colour2[0] * blend_factor)
        g = int(colour1[1] * (1 - blend_factor) + colour2[1] * blend_factor)
        b = int(colour1[2] * (1 - blend_factor) + colour2[2] * blend_factor)
        
        return (r, g, b)
    
    def _get_diagonal_down_spread_colour(self, row: int, col: int) -> Tuple[int, int, int]:
        """Get colour based on diagonal position for diagonal down spread mode.
        
        Top-left corner (0, 0) gets the first colour (index 0).
        Bottom-right corner (max_row, max_col) gets the last colour.
        """
        if not self.current_colour_scheme or len(self.current_colour_scheme) < 2:
            return self.current_colour_scheme[0] if self.current_colour_scheme else (255, 0, 0)
        
        # Calculate diagonal position ratio based on text boundaries
        text_width = self.text_bounds['max_col'] - self.text_bounds['min_col']
        text_height = self.text_bounds['max_row'] - self.text_bounds['min_row']
        
        if text_width <= 0 or text_height <= 0:
            diagonal_ratio = 0.0
        else:
            # Clamp position to text boundaries
            clamped_row = max(self.text_bounds['min_row'], min(self.text_bounds['max_row'], row))
            clamped_col = max(self.text_bounds['min_col'], min(self.text_bounds['max_col'], col))
            
            # Normalise to 0-1 range within text bounds
            row_ratio = (clamped_row - self.text_bounds['min_row']) / text_height
            col_ratio = (clamped_col - self.text_bounds['min_col']) / text_width
            
            # Diagonal ratio: average of row and column ratios
            # Top-left (0, 0) gives 0.0, bottom-right (1, 1) gives 1.0
            diagonal_ratio = (row_ratio + col_ratio) / 2.0
        
        # Map the ratio to colour scheme
        scheme_length = len(self.current_colour_scheme)
        colour_position = diagonal_ratio * (scheme_length - 1)
        
        # Get the two adjacent colours to interpolate between
        lower_index = int(colour_position)
        upper_index = min(lower_index + 1, scheme_length - 1)
        blend_factor = colour_position - lower_index
        
        # Interpolate between the two colours
        colour1 = self.current_colour_scheme[lower_index]
        colour2 = self.current_colour_scheme[upper_index]
        
        r = int(colour1[0] * (1 - blend_factor) + colour2[0] * blend_factor)
        g = int(colour1[1] * (1 - blend_factor) + colour2[1] * blend_factor)
        b = int(colour1[2] * (1 - blend_factor) + colour2[2] * blend_factor)
        
        return (r, g, b)
    
    def _get_diagonal_up_spread_colour(self, row: int, col: int) -> Tuple[int, int, int]:
        """Get colour based on diagonal position for diagonal up spread mode.
        
        Bottom-left corner (max_row, 0) gets the first colour (index 0).
        Top-right corner (0, max_col) gets the last colour.
        """
        if not self.current_colour_scheme or len(self.current_colour_scheme) < 2:
            return self.current_colour_scheme[0] if self.current_colour_scheme else (255, 0, 0)
        
        # Calculate diagonal position ratio based on text boundaries
        text_width = self.text_bounds['max_col'] - self.text_bounds['min_col']
        text_height = self.text_bounds['max_row'] - self.text_bounds['min_row']
        
        if text_width <= 0 or text_height <= 0:
            diagonal_ratio = 0.0
        else:
            # Clamp position to text boundaries
            clamped_row = max(self.text_bounds['min_row'], min(self.text_bounds['max_row'], row))
            clamped_col = max(self.text_bounds['min_col'], min(self.text_bounds['max_col'], col))
            
            # Normalise to 0-1 range within text bounds
            row_ratio = (clamped_row - self.text_bounds['min_row']) / text_height
            col_ratio = (clamped_col - self.text_bounds['min_col']) / text_width
            
            # Diagonal ratio: inverted row + column ratio
            # Bottom-left (1, 0) gives 0.0, top-right (0, 1) gives 1.0
            diagonal_ratio = ((1.0 - row_ratio) + col_ratio) / 2.0
        
        # Map the ratio to colour scheme
        scheme_length = len(self.current_colour_scheme)
        colour_position = diagonal_ratio * (scheme_length - 1)
        
        # Get the two adjacent colours to interpolate between
        lower_index = int(colour_position)
        upper_index = min(lower_index + 1, scheme_length - 1)
        blend_factor = colour_position - lower_index
        
        # Interpolate between the two colours
        colour1 = self.current_colour_scheme[lower_index]
        colour2 = self.current_colour_scheme[upper_index]
        
        r = int(colour1[0] * (1 - blend_factor) + colour2[0] * blend_factor)
        g = int(colour1[1] * (1 - blend_factor) + colour2[1] * blend_factor)
        b = int(colour1[2] * (1 - blend_factor) + colour2[2] * blend_factor)
        
        return (r, g, b)
    
    def _get_weighted_average_colour(self, row: int, col: int) -> Tuple[int, int, int]:
        """Get average colour of ghost pixels in a 5x5 area around the given position"""
        total_r, total_g, total_b = 0.0, 0.0, 0.0
        total_intensity = 0.0
        
        # Check 5x5 area centred on position
        for dr in range(-2, 3):  # -2, -1, 0, 1, 2
            for dc in range(-2, 3):
                check_row = row + dr
                check_col = col + dc
                
                # Skip if out of bounds
                if not (0 <= check_row < self.grid_height and 0 <= check_col < self.grid_width):
                    continue
                
                intensity, colour, timer = self.ghost_layer[check_row][check_col]
                if intensity > 0:
                    # Weight each colour component by its intensity
                    total_r += colour[0] * intensity
                    total_g += colour[1] * intensity
                    total_b += colour[2] * intensity
                    total_intensity += intensity
        
        # If no ghosts found in area, return a random colour from scheme
        if total_intensity == 0:
            return self._get_random_scheme_colour()
        
        # Calculate weighted average
        avg_r = int(total_r / total_intensity)
        avg_g = int(total_g / total_intensity)
        avg_b = int(total_b / total_intensity)
        
        return (avg_r, avg_g, avg_b)
    
    def _apply_colour_averaging(self) -> None:
        """Apply colour averaging to ghost pixels based on their individual timers"""
        # Create a new layer to store updated colours (avoid modifying while iterating)
        new_colours = []
        
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                intensity, current_colour, timer = self.ghost_layer[row][col]
                
                # Only update ghosts that exist and have reached their interval
                if intensity > 0 and timer >= self.colour_averaging_interval:
                    # Calculate average colour from neighbours
                    new_colour = self._get_weighted_average_colour(row, col)
                    # Reset timer for this ghost
                    new_colours.append((row, col, intensity, new_colour, 0))
        
        # Apply all colour updates
        for row, col, intensity, new_colour, new_timer in new_colours:
            self.ghost_layer[row][col] = (intensity, new_colour, new_timer)
    
    def _update_ghost_effects(self, current_grid: List[List[bool]]) -> None:
        """Update ghost pixel effects.
        
        Ghost effects create trailing pixels that fade out over time when text
        changes, creating a visual echo effect. Uses two-phase algorithm to
        prevent conflicts between decay and spawning.
        
        Algorithm:
        Phase 1 - Decay Existing Ghosts:
        - Multiply each ghost's intensity by decay factor (typically 0.97-0.99)
        - Remove ghosts that overlap with new active text pixels
        - Remove ghosts below minimum intensity threshold (0.01)
        
        Phase 2 - Spawn New Ghosts:
        - Check each active text pixel for ghost spawning
        - Spawn probability controlled by ghost_chance (0.0-1.0)
        - New ghosts start at configured intensity (typically 0.5-1.0)
        - Add to separate list to avoid modifying during iteration
        
        Colour Modes (from colour_transition_mode):
        - MIXED: Each ghost gets random colour from current scheme
        - HORIZONTAL_SPREAD/VERTICAL_SPREAD: Colour varies by position
        - SMOOTH/SNAP: Single colour for all ghosts
        
        Colour Averaging Integration:
        - Updates averaging timer for smooth colour transitions
        - Applies weighted colour averaging if enabled
        - Triggers periodic colour recalculation at configured intervals
        
        Performance:
        - Two-pass algorithm prevents race conditions
        - Separate new_ghosts list for clean spawning logic
        - Intensity threshold removes invisible ghosts early
        
        Related Settings:
        - ghost_chance: Probability of spawning (0.0-1.0)
        - ghost_decay: Fade rate per frame (0.9-1.0)
        - ghost_spawn_intensity: Initial brightness (0.0-1.0)
        - colour_transition_mode: How ghost colours are determined
        """
        # Store new ghost pixels to add after processing existing ones
        new_ghosts = []
        current_colour = self._get_current_ghost_colour()
        
        # Decay existing ghost pixels and check for spawning
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                intensity, colour, timer = self.ghost_layer[row][col]
                if intensity > 0:
                    # Remove ghost if text pixel becomes active at this location
                    if current_grid[row][col]:
                        self.ghost_layer[row][col] = (0.0, colour, 0)
                        continue
                    
                    # Decay the ghost while preserving its original colour and incrementing timer
                    new_intensity = intensity * self.ghost_decay
                    new_timer = timer + 1
                    if new_intensity < self.ghost_min_intensity:
                        self.ghost_layer[row][col] = (0.0, colour, 0)
                    else:
                        self.ghost_layer[row][col] = (new_intensity, colour, new_timer)
                        
                        # Check if this ghost spawns additional ghosts
                        if random.random() < self.ghost_spawn_chance:
                            ghost_positions = self._get_adjacent_positions(row, col)
                            if ghost_positions:
                                # Filter to only positions without active pixels
                                valid_positions = [
                                    (gr, gc) for gr, gc in ghost_positions 
                                    if not current_grid[gr][gc]
                                ]
                                if valid_positions:
                                    ghost_row, ghost_col = random.choice(valid_positions)
                                    # Spawn ghost with reduced intensity
                                    spawn_intensity = min(self.settings.ghost_tuning.spawn_intensity_base, new_intensity * self.settings.ghost_tuning.spawn_intensity_multiplier)
                                    # Only spawn if no existing ghost OR if new ghost is more intense
                                    existing_intensity = self.ghost_layer[ghost_row][ghost_col][0]
                                    if existing_intensity == 0 or spawn_intensity > existing_intensity:
                                        # Use parent ghost's colour (colour averaging happens separately if enabled)
                                        spawn_colour = colour
                                        # New ghost starts with timer at 0
                                        new_ghosts.append((ghost_row, ghost_col, spawn_intensity, spawn_colour, 0))
        
        # Add new ghost pixels spawned by existing ghosts
        for row, col, intensity, colour, timer in new_ghosts:
            self.ghost_layer[row][col] = (intensity, colour, timer)
        
        # Create new ghost pixels from activated pixels (outline effect)
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                if current_grid[row][col] and random.random() < self.ghost_chance:
                    # Try to create ghost pixel in adjacent position
                    ghost_positions = self._get_adjacent_positions(row, col)
                    if ghost_positions:
                        # Filter positions to exclude active text pixels (create outline, not overlay)
                        outline_positions = [
                            (gr, gc) for gr, gc in ghost_positions 
                            if not current_grid[gr][gc]
                        ]
                        if outline_positions:
                            ghost_row, ghost_col = random.choice(outline_positions)
                            existing_intensity, existing_color, existing_timer = self.ghost_layer[ghost_row][ghost_col]
                            new_intensity = min(self.settings.ghost_tuning.max_ghost_intensity, existing_intensity + self.settings.ghost_tuning.accumulation_intensity)
                            
                            # Choose colour based on transition mode
                            if self.colour_transition_mode == TransitionMode.MIXED:
                                # In mixed mode, pick a random colour from the scheme for text-spawned ghosts
                                ghost_colour = self._get_random_scheme_colour()
                            elif self.colour_transition_mode == TransitionMode.SPREAD_HORIZONTAL:
                                # In horizontal spread mode, use horizontal position-based colour
                                ghost_colour = self._get_horizontal_spread_colour(ghost_row, ghost_col)
                            elif self.colour_transition_mode == TransitionMode.SPREAD_VERTICAL:
                                # In vertical spread mode, use vertical position-based colour
                                ghost_colour = self._get_vertical_spread_colour(ghost_row, ghost_col)
                            elif self.colour_transition_mode == TransitionMode.SPREAD_DIAGONALLY_DOWN:
                                # In diagonal down spread mode, use diagonal position-based colour
                                ghost_colour = self._get_diagonal_down_spread_colour(ghost_row, ghost_col)
                            elif self.colour_transition_mode == TransitionMode.SPREAD_DIAGONALLY_UP:
                                # In diagonal up spread mode, use diagonal position-based colour
                                ghost_colour = self._get_diagonal_up_spread_colour(ghost_row, ghost_col)
                            else:
                                # In smooth/snap modes, use the current cycling colour
                                ghost_colour = current_colour
                            
                            # Reset timer when creating new ghost or refreshing existing one
                            new_timer = 0 if existing_intensity == 0 else existing_timer
                            # Always apply since we're adding to existing intensity (making it stronger)
                            self.ghost_layer[ghost_row][ghost_col] = (new_intensity, ghost_colour, new_timer)
    
    def _update_flicker_effects(self, current_grid: List[List[bool]]) -> None:
        """Update flicker effects for activated pixels"""
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                if current_grid[row][col] and random.random() < self.flicker_chance:
                    self.flicker_layer[row][col] = self.flicker_intensity
                else:
                    self.flicker_layer[row][col] = 0.0
    
    def _get_adjacent_positions(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get valid adjacent positions for ghost pixel placement"""
        positions = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.grid_height and 0 <= new_col < self.grid_width:
                positions.append((new_row, new_col))
        
        return positions
    
    def render_overlay(self, screen: pygame.Surface, base_colour: Tuple[int, int, int]) -> None:
        """Render overlay effects on top of the base screen"""
        # Render ghost pixels with their individual colours
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                intensity, colour, timer = self.ghost_layer[row][col]
                if intensity > 0:
                    self._draw_effect_pixel(screen, row, col, colour, intensity)
                
                if self.flicker_layer[row][col] > 0:
                    self._draw_effect_pixel(screen, row, col, self.flicker_colour, 
                                          self.flicker_layer[row][col])
    
    def _draw_effect_pixel(self, screen: pygame.Surface, row: int, col: int, 
                          colour: Tuple[int, int, int], intensity: float) -> None:
        """Draw a single effect pixel with given intensity"""
        x = int(col * self.square_size * self.display_scale)
        y = int(row * self.square_size * self.display_scale)
        width = int(self.square_size * self.display_scale)
        height = int(self.square_size * self.display_scale)
        
        # Apply intensity to colour
        effect_colour = tuple(int(c * intensity) for c in colour)
        
        # Create a surface for alpha blending
        effect_surface = pygame.Surface((width, height))
        effect_surface.set_alpha(int(255 * intensity))
        effect_surface.fill(effect_colour)
        
        screen.blit(effect_surface, (x, y))
    
    def set_ghost_parameters(self, chance: Optional[float] = None, decay: Optional[float] = None, 
                           min_intensity: Optional[float] = None, spawn_chance: Optional[float] = None,
                           colour_shift_speed: Optional[float] = None) -> None:
        """Configure ghost effect parameters"""
        if chance is not None:
            self.ghost_chance = max(0.0, min(1.0, chance))
        if decay is not None:
            self.ghost_decay = max(0.0, min(1.0, decay))
        if min_intensity is not None:
            self.ghost_min_intensity = max(0.0, min(1.0, min_intensity))
        if spawn_chance is not None:
            self.ghost_spawn_chance = max(0.0, min(1.0, spawn_chance))
        if colour_shift_speed is not None:
            self.colour_shift_speed = max(0.0, colour_shift_speed)
    
    def set_flicker_parameters(self, chance: Optional[float] = None, intensity: Optional[float] = None) -> None:
        """Configure flicker effect parameters"""
        if chance is not None:
            self.flicker_chance = max(0.0, min(1.0, chance))
        if intensity is not None:
            self.flicker_intensity = max(0.0, min(1.0, intensity))
    
    def set_colour_averaging_parameters(self, enabled: Optional[bool] = None, interval: Optional[int] = None) -> None:
        """Configure colour averaging parameters"""
        if enabled is not None:
            self.enable_colour_averaging = enabled
            logger.info(f"Colour averaging {'enabled' if enabled else 'disabled'}")
        if interval is not None:
            self.colour_averaging_interval = max(1, interval)
            logger.info(f"Colour averaging interval set to {self.colour_averaging_interval} frames")
    
    def clear_effects(self) -> None:
        """Clear all overlay effects"""
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                self.ghost_layer[row][col] = (0.0, (255, 0, 0), 0)  # Default red colour, timer at 0
                self.flicker_layer[row][col] = 0.0
    
    def get_effect_stats(self) -> Dict[str, int]:
        """Get statistics about current effects"""
        ghost_count = sum(1 for row in self.ghost_layer for intensity, colour, timer in row if intensity > 0)
        flicker_count = sum(1 for row in self.flicker_layer for val in row if val > 0)
        
        return {
            'ghost_pixels': ghost_count,
            'flicker_pixels': flicker_count
        }
    
    def get_colour_scheme_info(self) -> Dict[str, Any]:
        """Get information about the current colour scheme"""
        return {
            'name': self.colour_scheme_name,
            'colours': self.current_colour_scheme,
            'colour_count': len(self.current_colour_scheme),
            'transition_mode': self.colour_transition_mode.value if isinstance(self.colour_transition_mode, TransitionMode) else self.colour_transition_mode,
            'snap_duration': self.snap_duration if self.colour_transition_mode == TransitionMode.SNAP else None
        }
    
    def _update_text_bounds(self, current_grid: List[List[bool]]) -> None:
        """Update the boundaries of the actual text for spread calculations"""
        min_col = self.grid_width
        max_col = -1
        min_row = self.grid_height
        max_row = -1
        
        # Find the actual bounds of the text
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                if current_grid[row][col]:
                    min_col = min(min_col, col)
                    max_col = max(max_col, col)
                    min_row = min(min_row, row)
                    max_row = max(max_row, row)
        
        # Only update if we found actual text
        if min_col <= max_col:
            self.text_bounds['min_col'] = min_col
            self.text_bounds['max_col'] = max_col
            self.text_bounds['min_row'] = min_row
            self.text_bounds['max_row'] = max_row
