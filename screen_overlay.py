import random
import pygame
import math
from typing import List, Tuple, Dict, Optional, Union, Any
from color_schemes import get_color_scheme, validate_color_scheme
from config.enums import TransitionMode, ColorScheme
from config.settings import Settings

class ScreenOverlay:
    def __init__(self, grid_width: int, grid_height: int, square_size: int, display_scale: float = 1.0, 
                 settings: Optional[Settings] = None):
        """Initialize the screen overlay system"""
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.square_size = square_size
        self.display_scale = display_scale
        
        # Store settings reference, create default if none provided
        self.settings = settings if settings is not None else Settings.create_default()
        
        # Effect layers - now store (intensity, color, timer) tuples for ghosts
        self.ghost_layer = [[(0.0, (255, 0, 0), 0) for _ in range(grid_width)] for _ in range(grid_height)]
        self.flicker_layer = [[0.0 for _ in range(grid_width)] for _ in range(grid_height)]
        
        # Effect parameters
        self.ghost_chance = 0.5  # Increased chance for better outline effect
        self.ghost_decay = 0.99   # How quickly ghost pixels fade
        self.ghost_min_intensity = 0.1  # Minimum intensity before ghost disappears
        self.ghost_spawn_chance = 0.05  # Increased spawn chance for outline effect
        self.flicker_chance = 0.0  # Chance for pixel to flicker
        self.flicker_intensity = 0.2  # Intensity of flicker effect
        
        # Color settings - now supports color schemes
        self.current_color_scheme = get_color_scheme('classic')
        self.color_scheme_name = 'classic'
        self.color_shift_speed = 0.005  # How fast colors shift (radians per frame) - 4x slower
        self.color_time = 0.0  # Internal timer for color shifting
        self.flicker_color = (255, 200, 100)  # Warm flicker color
        
        # Color transition mode
        self.color_transition_mode = TransitionMode.SMOOTH
        self.snap_duration = 120  # frames to hold each color in snap mode (2 seconds at 60fps)
        
        # Text boundary tracking for spread modes
        self.text_bounds = {
            'min_col': 0,
            'max_col': grid_width - 1,
            'min_row': 0,
            'max_row': grid_height - 1
        }
        
        # Color averaging settings
        self.enable_color_averaging = False
        self.color_averaging_interval = 30  # frames
        
        print(f"ScreenOverlay initialized: {grid_width}x{grid_height}")
    
    def update_effects(self, current_grid: List[List[bool]]) -> None:
        """Update all overlay effects based on current screen state"""
        # Update color shift timer
        self.color_time += self.color_shift_speed
        
        # Update text boundaries for spread modes
        self._update_text_bounds(current_grid)
        
        self._update_ghost_effects(current_grid)
        self._update_flicker_effects(current_grid)
        
        # Apply color averaging if enabled (checks individual pixel timers)
        if self.enable_color_averaging:
            self._apply_color_averaging()
    
    def set_color_scheme(self, scheme: Union[ColorScheme, str]) -> bool:
        """Set the color scheme for ghost effects. Accepts ColorScheme enum or string. Returns True if successful."""
        try:
            new_scheme = get_color_scheme(scheme)
            if validate_color_scheme(new_scheme):
                self.current_color_scheme = new_scheme
                if isinstance(scheme, ColorScheme):
                    self.color_scheme_name = scheme.value
                else:
                    self.color_scheme_name = str(scheme).lower()
                print(f"Color scheme changed to: {self.color_scheme_name}")
                return True
            else:
                print(f"Invalid color scheme format: {scheme}")
                return False
        except Exception as e:
            print(f"Error setting color scheme {scheme}: {e}")
            return False
    
    def set_custom_color_scheme(self, colors: List[Tuple[int, int, int]]) -> bool:
        """Set a custom color scheme. Returns True if successful."""
        if validate_color_scheme(colors):
            self.current_color_scheme = colors
            self.color_scheme_name = 'custom'
            print(f"Custom color scheme set with {len(colors)} colors")
            return True
        else:
            print("Invalid custom color scheme format")
            return False
    
    def set_color_transition_mode(self, mode: Union[TransitionMode, str], snap_duration: Optional[int] = None) -> bool:
        """Set the color transition mode. Accepts TransitionMode enum or string. Returns True if successful."""
        try:
            if isinstance(mode, TransitionMode):
                self.color_transition_mode = mode
                mode_name = mode.value
            else:
                mode_lower = str(mode).lower()
                self.color_transition_mode = TransitionMode.from_string(mode_lower)
                mode_name = mode_lower
            
            if snap_duration is not None:
                self.snap_duration = max(1, snap_duration)
            
            print(f"Color transition mode set to: {mode_name}")
            if self.color_transition_mode == TransitionMode.SNAP:
                print(f"Snap duration: {self.snap_duration} frames")
            elif self.color_transition_mode == TransitionMode.MIXED:
                print("Mixed mode: each ghost gets a random color from the scheme")
            elif self.color_transition_mode == TransitionMode.SPREAD_HORIZONTAL:
                print("Horizontal spread mode: colors spread horizontally across screen")
            elif self.color_transition_mode == TransitionMode.SPREAD_VERTICAL:
                print("Vertical spread mode: colors spread vertically across screen")
            
            return True
        except Exception as e:
            print(f"Error setting color transition mode: {e}")
            print(f"Valid modes: {', '.join(TransitionMode.list_names())}")
            return False
    
    def _get_current_ghost_color(self) -> Tuple[int, int, int]:
        """Get the current ghost color based on time and color scheme"""
        if not self.current_color_scheme:
            return (255, 0, 0)  # Fallback red
        
        # For single color schemes, just return that color
        if len(self.current_color_scheme) == 1:
            return self.current_color_scheme[0]
        
        # For multi-color schemes, choose behavior based on transition mode
        scheme_length = len(self.current_color_scheme)
        
        if self.color_transition_mode == TransitionMode.SNAP:
            # Snap mode: hold each color for a specific duration
            total_cycle_time = self.snap_duration * scheme_length
            frame_in_cycle = int(self.color_time / self.color_shift_speed) % total_cycle_time
            color_index = frame_in_cycle // self.snap_duration
            return self.current_color_scheme[color_index % scheme_length]
        elif self.color_transition_mode in [TransitionMode.SPREAD_HORIZONTAL, TransitionMode.SPREAD_VERTICAL]:
            # Spread modes: calculate color based on position (use center position as default)
            center_row = self.grid_height // 2
            center_col = self.grid_width // 2
            if self.color_transition_mode == TransitionMode.SPREAD_HORIZONTAL:
                return self._get_horizontal_spread_color(center_row, center_col)
            else:
                return self._get_vertical_spread_color(center_row, center_col)
        else:
            # Smooth mode: smoothly transition between colors
            color_position = (math.sin(self.color_time) + 1) / 2  # 0 to 1
            color_index = color_position * (scheme_length - 1)
            
            # Get the two adjacent colors to interpolate between
            lower_index = int(color_index)
            upper_index = min(lower_index + 1, scheme_length - 1)
            blend_factor = color_index - lower_index
            
            # Interpolate between the two colors
            color1 = self.current_color_scheme[lower_index]
            color2 = self.current_color_scheme[upper_index]
            
            r = int(color1[0] * (1 - blend_factor) + color2[0] * blend_factor)
            g = int(color1[1] * (1 - blend_factor) + color2[1] * blend_factor)
            b = int(color1[2] * (1 - blend_factor) + color2[2] * blend_factor)
            
            return (r, g, b)
    
    def _get_random_scheme_color(self) -> Tuple[int, int, int]:
        """Get a random color from the current color scheme"""
        if not self.current_color_scheme:
            return (255, 0, 0)  # Fallback red
        
        return random.choice(self.current_color_scheme)
    
    def _get_horizontal_spread_color(self, row: int, col: int) -> Tuple[int, int, int]:
        """Get color based on horizontal position for horizontal spread mode"""
        if not self.current_color_scheme or len(self.current_color_scheme) < 2:
            return self.current_color_scheme[0] if self.current_color_scheme else (255, 0, 0)
        
        # Calculate horizontal position ratio based on text boundaries
        text_width = self.text_bounds['max_col'] - self.text_bounds['min_col']
        if text_width <= 0:
            horizontal_ratio = 0.0
        else:
            # Clamp the column to text boundaries
            clamped_col = max(self.text_bounds['min_col'], min(self.text_bounds['max_col'], col))
            horizontal_ratio = (clamped_col - self.text_bounds['min_col']) / text_width
        
        # Map the ratio to color scheme
        scheme_length = len(self.current_color_scheme)
        color_position = horizontal_ratio * (scheme_length - 1)
        
        # Get the two adjacent colors to interpolate between
        lower_index = int(color_position)
        upper_index = min(lower_index + 1, scheme_length - 1)
        blend_factor = color_position - lower_index
        
        # Interpolate between the two colors
        color1 = self.current_color_scheme[lower_index]
        color2 = self.current_color_scheme[upper_index]
        
        r = int(color1[0] * (1 - blend_factor) + color2[0] * blend_factor)
        g = int(color1[1] * (1 - blend_factor) + color2[1] * blend_factor)
        b = int(color1[2] * (1 - blend_factor) + color2[2] * blend_factor)
        
        return (r, g, b)
    
    def _get_vertical_spread_color(self, row: int, col: int) -> Tuple[int, int, int]:
        """Get color based on vertical position for vertical spread mode"""
        if not self.current_color_scheme or len(self.current_color_scheme) < 2:
            return self.current_color_scheme[0] if self.current_color_scheme else (255, 0, 0)
        
        # Calculate vertical position ratio based on text boundaries
        text_height = self.text_bounds['max_row'] - self.text_bounds['min_row']
        if text_height <= 0:
            vertical_ratio = 0.0
        else:
            # Clamp the row to text boundaries
            clamped_row = max(self.text_bounds['min_row'], min(self.text_bounds['max_row'], row))
            vertical_ratio = (clamped_row - self.text_bounds['min_row']) / text_height
        
        # Map the ratio to color scheme
        scheme_length = len(self.current_color_scheme)
        color_position = vertical_ratio * (scheme_length - 1)
        
        # Get the two adjacent colors to interpolate between
        lower_index = int(color_position)
        upper_index = min(lower_index + 1, scheme_length - 1)
        blend_factor = color_position - lower_index
        
        # Interpolate between the two colors
        color1 = self.current_color_scheme[lower_index]
        color2 = self.current_color_scheme[upper_index]
        
        r = int(color1[0] * (1 - blend_factor) + color2[0] * blend_factor)
        g = int(color1[1] * (1 - blend_factor) + color2[1] * blend_factor)
        b = int(color1[2] * (1 - blend_factor) + color2[2] * blend_factor)
        
        return (r, g, b)
    
    def _get_weighted_average_color(self, row: int, col: int) -> Tuple[int, int, int]:
        """Get average color of ghost pixels in a 5x5 area around the given position"""
        total_r, total_g, total_b = 0.0, 0.0, 0.0
        total_intensity = 0.0
        
        # Check 5x5 area centered on position
        for dr in range(-2, 3):  # -2, -1, 0, 1, 2
            for dc in range(-2, 3):
                check_row = row + dr
                check_col = col + dc
                
                # Skip if out of bounds
                if not (0 <= check_row < self.grid_height and 0 <= check_col < self.grid_width):
                    continue
                
                intensity, color, timer = self.ghost_layer[check_row][check_col]
                if intensity > 0:
                    # Weight each color component by its intensity
                    total_r += color[0] * intensity
                    total_g += color[1] * intensity
                    total_b += color[2] * intensity
                    total_intensity += intensity
        
        # If no ghosts found in area, return a random color from scheme
        if total_intensity == 0:
            return self._get_random_scheme_color()
        
        # Calculate weighted average
        avg_r = int(total_r / total_intensity)
        avg_g = int(total_g / total_intensity)
        avg_b = int(total_b / total_intensity)
        
        return (avg_r, avg_g, avg_b)
    
    def _apply_color_averaging(self) -> None:
        """Apply color averaging to ghost pixels based on their individual timers"""
        # Create a new layer to store updated colors (avoid modifying while iterating)
        new_colors = []
        
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                intensity, current_color, timer = self.ghost_layer[row][col]
                
                # Only update ghosts that exist and have reached their interval
                if intensity > 0 and timer >= self.color_averaging_interval:
                    # Calculate average color from neighbors
                    new_color = self._get_weighted_average_color(row, col)
                    # Reset timer for this ghost
                    new_colors.append((row, col, intensity, new_color, 0))
        
        # Apply all color updates
        for row, col, intensity, new_color, new_timer in new_colors:
            self.ghost_layer[row][col] = (intensity, new_color, new_timer)
    
    def _update_ghost_effects(self, current_grid: List[List[bool]]) -> None:
        """Update ghost pixel effects"""
        # Store new ghost pixels to add after processing existing ones
        new_ghosts = []
        current_color = self._get_current_ghost_color()
        
        # Decay existing ghost pixels and check for spawning
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                intensity, color, timer = self.ghost_layer[row][col]
                if intensity > 0:
                    # Remove ghost if text pixel becomes active at this location
                    if current_grid[row][col]:
                        self.ghost_layer[row][col] = (0.0, color, 0)
                        continue
                    
                    # Decay the ghost while preserving its original color and incrementing timer
                    new_intensity = intensity * self.ghost_decay
                    new_timer = timer + 1
                    if new_intensity < self.ghost_min_intensity:
                        self.ghost_layer[row][col] = (0.0, color, 0)
                    else:
                        self.ghost_layer[row][col] = (new_intensity, color, new_timer)
                        
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
                                        # Use parent ghost's color (color averaging happens separately if enabled)
                                        spawn_color = color
                                        # New ghost starts with timer at 0
                                        new_ghosts.append((ghost_row, ghost_col, spawn_intensity, spawn_color, 0))
        
        # Add new ghost pixels spawned by existing ghosts
        for row, col, intensity, color, timer in new_ghosts:
            self.ghost_layer[row][col] = (intensity, color, timer)
        
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
                            
                            # Choose color based on transition mode
                            if self.color_transition_mode == TransitionMode.MIXED:
                                # In mixed mode, pick a random color from the scheme for text-spawned ghosts
                                ghost_color = self._get_random_scheme_color()
                            elif self.color_transition_mode == TransitionMode.SPREAD_HORIZONTAL:
                                # In horizontal spread mode, use horizontal position-based color
                                ghost_color = self._get_horizontal_spread_color(ghost_row, ghost_col)
                            elif self.color_transition_mode == TransitionMode.SPREAD_VERTICAL:
                                # In vertical spread mode, use vertical position-based color
                                ghost_color = self._get_vertical_spread_color(ghost_row, ghost_col)
                            else:
                                # In smooth/snap modes, use the current cycling color
                                ghost_color = current_color
                            
                            # Reset timer when creating new ghost or refreshing existing one
                            new_timer = 0 if existing_intensity == 0 else existing_timer
                            # Always apply since we're adding to existing intensity (making it stronger)
                            self.ghost_layer[ghost_row][ghost_col] = (new_intensity, ghost_color, new_timer)
    
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
    
    def render_overlay(self, screen: pygame.Surface, base_color: Tuple[int, int, int]) -> None:
        """Render overlay effects on top of the base screen"""
        # Render ghost pixels with their individual colors
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                intensity, color, timer = self.ghost_layer[row][col]
                if intensity > 0:
                    self._draw_effect_pixel(screen, row, col, color, intensity)
                
                if self.flicker_layer[row][col] > 0:
                    self._draw_effect_pixel(screen, row, col, self.flicker_color, 
                                          self.flicker_layer[row][col])
    
    def _draw_effect_pixel(self, screen: pygame.Surface, row: int, col: int, 
                          color: Tuple[int, int, int], intensity: float) -> None:
        """Draw a single effect pixel with given intensity"""
        x = int(col * self.square_size * self.display_scale)
        y = int(row * self.square_size * self.display_scale)
        width = int(self.square_size * self.display_scale)
        height = int(self.square_size * self.display_scale)
        
        # Apply intensity to color
        effect_color = tuple(int(c * intensity) for c in color)
        
        # Create a surface for alpha blending
        effect_surface = pygame.Surface((width, height))
        effect_surface.set_alpha(int(255 * intensity))
        effect_surface.fill(effect_color)
        
        screen.blit(effect_surface, (x, y))
    
    def set_ghost_parameters(self, chance: Optional[float] = None, decay: Optional[float] = None, 
                           min_intensity: Optional[float] = None, spawn_chance: Optional[float] = None,
                           color_shift_speed: Optional[float] = None) -> None:
        """Configure ghost effect parameters"""
        if chance is not None:
            self.ghost_chance = max(0.0, min(1.0, chance))
        if decay is not None:
            self.ghost_decay = max(0.0, min(1.0, decay))
        if min_intensity is not None:
            self.ghost_min_intensity = max(0.0, min(1.0, min_intensity))
        if spawn_chance is not None:
            self.ghost_spawn_chance = max(0.0, min(1.0, spawn_chance))
        if color_shift_speed is not None:
            self.color_shift_speed = max(0.0, color_shift_speed)
    
    def set_flicker_parameters(self, chance: Optional[float] = None, intensity: Optional[float] = None) -> None:
        """Configure flicker effect parameters"""
        if chance is not None:
            self.flicker_chance = max(0.0, min(1.0, chance))
        if intensity is not None:
            self.flicker_intensity = max(0.0, min(1.0, intensity))
    
    def set_color_averaging_parameters(self, enabled: Optional[bool] = None, interval: Optional[int] = None) -> None:
        """Configure color averaging parameters"""
        if enabled is not None:
            self.enable_color_averaging = enabled
            print(f"Color averaging {'enabled' if enabled else 'disabled'}")
        if interval is not None:
            self.color_averaging_interval = max(1, interval)
            print(f"Color averaging interval set to {self.color_averaging_interval} frames")
    
    def clear_effects(self) -> None:
        """Clear all overlay effects"""
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                self.ghost_layer[row][col] = (0.0, (255, 0, 0), 0)  # Default red color, timer at 0
                self.flicker_layer[row][col] = 0.0
    
    def get_effect_stats(self) -> Dict[str, int]:
        """Get statistics about current effects"""
        ghost_count = sum(1 for row in self.ghost_layer for intensity, color, timer in row if intensity > 0)
        flicker_count = sum(1 for row in self.flicker_layer for val in row if val > 0)
        
        return {
            'ghost_pixels': ghost_count,
            'flicker_pixels': flicker_count
        }
    
    def get_color_scheme_info(self) -> Dict[str, Any]:
        """Get information about the current color scheme"""
        return {
            'name': self.color_scheme_name,
            'colors': self.current_color_scheme,
            'color_count': len(self.current_color_scheme),
            'transition_mode': self.color_transition_mode.value if isinstance(self.color_transition_mode, TransitionMode) else self.color_transition_mode,
            'snap_duration': self.snap_duration if self.color_transition_mode == TransitionMode.SNAP else None
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
