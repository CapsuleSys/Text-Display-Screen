"""
Centralized settings configuration for Text Display Screen.

This module provides a Settings class that manages all configurable aspects of the
display system using type-safe enums and validation. It serves as the single source
of truth for all display and overlay settings configuration.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any, Union
from config.enums import DisplayType, ColourScheme, TransitionMode, OverlayEffect, RGB, DEFAULT_DISPLAY_TYPE, DEFAULT_COLOUR_SCHEME, DEFAULT_TRANSITION_MODE, DEFAULT_OVERLAY_EFFECT
import json
import os
from logger_setup import setup_logger

logger = setup_logger(__name__)


@dataclass
class DisplaySettings:
    """Settings for the main display configuration."""
    display_type: DisplayType = DEFAULT_DISPLAY_TYPE
    grid_width: int = 120
    grid_height: int = 68
    square_size: int = 16
    display_scale: float = 0.5
    fps: int = 60
    
    def validate(self) -> bool:
        """Validate display settings."""
        if self.grid_width <= 0 or self.grid_height <= 0:
            return False
        if self.square_size <= 0:
            return False
        if self.display_scale <= 0:
            return False
        if self.fps <= 0:
            return False
        return True


@dataclass 
class TransitionSettings:
    """Settings for text transition animations."""
    transition_speed: float = 10.0  # pixels per frame
    text_change_interval: int = 1500  # frames between text changes
    blank_time_between_transitions: int = 0  # frames to show blank screen between transitions
    shuffle_text_order: bool = False  # whether to process text blocks in random order
    
    # Effect transition enable flags
    transition_colour_scheme: bool = False  # whether to change colour scheme on text change
    transition_colour_mode: bool = False  # whether to change transition mode on text change
    transition_ghost_params: bool = False  # whether to change ghost parameters on text change
    transition_flicker_params: bool = False  # whether to change flicker parameters on text change
    transition_speed_variation: bool = False  # whether to vary transition speed on text change
    
    # Effect transition order modes ("random" or "sequential")
    colour_scheme_order: str = "random"
    colour_mode_order: str = "random"
    ghost_params_order: str = "random"
    flicker_params_order: str = "random"
    speed_order: str = "random"
    
    # Speed variation ranges
    speed_min: float = 1.0
    speed_max: float = 15.0
    
    # Ghost parameter ranges
    ghost_chance_min: float = 0.05
    ghost_chance_max: float = 0.3
    ghost_decay_min: float = 0.985
    ghost_decay_max: float = 0.998
    
    # Flicker parameter ranges
    flicker_chance_min: float = 0.0
    flicker_chance_max: float = 0.1
    flicker_intensity_min: float = 0.1
    flicker_intensity_max: float = 0.3
    
    def validate(self) -> bool:
        """Validate transition settings."""
        if self.transition_speed < 0.1:
            return False
        if self.text_change_interval <= 0:
            return False
        
        # Validate order mode strings
        valid_orders = ["random", "sequential"]
        if self.colour_scheme_order not in valid_orders:
            return False
        if self.colour_mode_order not in valid_orders:
            return False
        if self.ghost_params_order not in valid_orders:
            return False
        if self.flicker_params_order not in valid_orders:
            return False
        if self.speed_order not in valid_orders:
            return False
        
        # Validate min/max ranges
        if self.speed_min >= self.speed_max:
            return False
        if self.speed_min < 0.1 or self.speed_max > 50.0:
            return False
        
        if self.ghost_chance_min >= self.ghost_chance_max:
            return False
        if not (0.0 <= self.ghost_chance_min <= 1.0) or not (0.0 <= self.ghost_chance_max <= 1.0):
            return False
        
        if self.ghost_decay_min >= self.ghost_decay_max:
            return False
        if not (0.0 <= self.ghost_decay_min <= 1.0) or not (0.0 <= self.ghost_decay_max <= 1.0):
            return False
        
        if self.flicker_chance_min >= self.flicker_chance_max:
            return False
        if not (0.0 <= self.flicker_chance_min <= 1.0) or not (0.0 <= self.flicker_chance_max <= 1.0):
            return False
        
        if self.flicker_intensity_min >= self.flicker_intensity_max:
            return False
        if not (0.0 <= self.flicker_intensity_min <= 1.0) or not (0.0 <= self.flicker_intensity_max <= 1.0):
            return False
        
        return True


@dataclass
class TextRenderingSettings:
    """Settings for text character rendering."""
    char_width: int = 6          # Character width in pixels
    char_height: int = 8         # Character height in pixels  
    spacing_x: int = 1           # Horizontal spacing between characters
    spacing_y: int = 1           # Vertical spacing between lines
    
    def validate(self) -> bool:
        """Validate text rendering settings."""
        if self.char_width <= 0 or self.char_height <= 0:
            return False
        if self.spacing_x < 0 or self.spacing_y < 0:
            return False
        return True


@dataclass  
class FileMonitoringSettings:
    """Settings for file change monitoring."""
    file_check_interval: int = 60  # Frames between file modification checks
    
    def validate(self) -> bool:
        """Validate file monitoring settings."""
        if self.file_check_interval <= 0:
            return False
        return True


@dataclass
class DebugSettings:
    """Settings for debug output and logging."""
    debug_output_interval: int = 300  # Frames between debug messages (5 sec at 60fps)
    
    def validate(self) -> bool:
        """Validate debug settings."""
        if self.debug_output_interval <= 0:
            return False
        return True


@dataclass
class GhostEffectTuning:
    """Fine-tuning parameters for ghost effects."""
    spawn_intensity_base: float = 0.9        # Maximum spawn intensity
    spawn_intensity_multiplier: float = 1.0   # Multiplier for spawn intensity  
    accumulation_intensity: float = 0.8       # How much intensity to add when accumulating
    max_ghost_intensity: float = 1.0          # Maximum possible ghost intensity
    
    def validate(self) -> bool:
        """Validate ghost effect tuning settings."""
        if not (0.0 <= self.spawn_intensity_base <= 1.0):
            return False
        if self.spawn_intensity_multiplier < 0:
            return False
        if not (0.0 <= self.accumulation_intensity <= 1.0):
            return False
        if not (0.0 <= self.max_ghost_intensity <= 1.0):
            return False
        return True


@dataclass
class OverlaySettings:
    """Settings for ghost overlay effects."""
    overlay_enabled: bool = True
    overlay_effect: OverlayEffect = DEFAULT_OVERLAY_EFFECT
    
    # Ghost effect parameters
    ghost_chance: float = 0.15
    ghost_decay: float = 0.985
    ghost_min_intensity: float = 0.1
    ghost_spawn_chance: float = 0.05
    
    # Flicker effect parameters
    flicker_chance: float = 0.0
    flicker_intensity: float = 0.2
    
    # Colour settings
    colour_scheme: ColourScheme = DEFAULT_COLOUR_SCHEME
    colour_transition_mode: TransitionMode = DEFAULT_TRANSITION_MODE
    colour_shift_speed: float = 0.005
    snap_duration: int = 120  # frames
    
    # Colour averaging settings
    enable_colour_averaging: bool = False  # Whether to periodically average ghost colours with neighbours
    colour_averaging_interval: int = 30  # Frames between colour averaging updates
    
    def validate(self) -> bool:
        """Validate overlay settings."""
        if not (0.0 <= self.ghost_chance <= 1.0):
            return False
        if not (0.0 <= self.ghost_decay <= 1.0):
            return False
        if not (0.0 <= self.ghost_min_intensity <= 1.0):
            return False
        if not (0.0 <= self.ghost_spawn_chance <= 1.0):
            return False
        if not (0.0 <= self.flicker_chance <= 1.0):
            return False
        if not (0.0 <= self.flicker_intensity <= 1.0):
            return False
        if self.colour_shift_speed < 0:
            return False
        if self.snap_duration <= 0:
            return False
        if self.colour_averaging_interval <= 0:
            return False
        return True


@dataclass
class Settings:
    """Main settings container for the Text Display Screen application."""
    display: DisplaySettings = field(default_factory=DisplaySettings)
    transition: TransitionSettings = field(default_factory=TransitionSettings)
    overlay: OverlaySettings = field(default_factory=OverlaySettings)
    text_rendering: TextRenderingSettings = field(default_factory=TextRenderingSettings)
    file_monitoring: FileMonitoringSettings = field(default_factory=FileMonitoringSettings)
    debug: DebugSettings = field(default_factory=DebugSettings)
    ghost_tuning: GhostEffectTuning = field(default_factory=GhostEffectTuning)
    
    @classmethod
    def create_default(cls) -> 'Settings':
        """Create a Settings instance with all default values."""
        return cls()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        """Create a Settings instance from a dictionary."""
        settings = cls()
        
        # Load display settings
        if 'display' in data:
            display_data = data['display']
            if 'display_type' in display_data:
                settings.display.display_type = DisplayType.from_string(display_data['display_type'])
            if 'grid_width' in display_data:
                settings.display.grid_width = display_data['grid_width']
            if 'grid_height' in display_data:
                settings.display.grid_height = display_data['grid_height']
            if 'square_size' in display_data:
                settings.display.square_size = display_data['square_size']
            if 'display_scale' in display_data:
                settings.display.display_scale = display_data['display_scale']
            if 'fps' in display_data:
                settings.display.fps = display_data['fps']
        
        # Load transition settings
        if 'transition' in data:
            transition_data = data['transition']
            if 'transition_speed' in transition_data:
                settings.transition.transition_speed = transition_data['transition_speed']
            if 'text_change_interval' in transition_data:
                settings.transition.text_change_interval = transition_data['text_change_interval']
            if 'blank_time_between_transitions' in transition_data:
                settings.transition.blank_time_between_transitions = transition_data['blank_time_between_transitions']
            if 'shuffle_text_order' in transition_data:
                settings.transition.shuffle_text_order = transition_data['shuffle_text_order']
            
            # Load effect transition enable flags
            if 'transition_colour_scheme' in transition_data:
                settings.transition.transition_colour_scheme = transition_data['transition_colour_scheme']
            if 'transition_colour_mode' in transition_data:
                settings.transition.transition_colour_mode = transition_data['transition_colour_mode']
            if 'transition_ghost_params' in transition_data:
                settings.transition.transition_ghost_params = transition_data['transition_ghost_params']
            if 'transition_flicker_params' in transition_data:
                settings.transition.transition_flicker_params = transition_data['transition_flicker_params']
            if 'transition_speed_variation' in transition_data:
                settings.transition.transition_speed_variation = transition_data['transition_speed_variation']
            
            # Load effect transition order modes
            if 'colour_scheme_order' in transition_data:
                settings.transition.colour_scheme_order = transition_data['colour_scheme_order']
            if 'colour_mode_order' in transition_data:
                settings.transition.colour_mode_order = transition_data['colour_mode_order']
            if 'ghost_params_order' in transition_data:
                settings.transition.ghost_params_order = transition_data['ghost_params_order']
            if 'flicker_params_order' in transition_data:
                settings.transition.flicker_params_order = transition_data['flicker_params_order']
            if 'speed_order' in transition_data:
                settings.transition.speed_order = transition_data['speed_order']
            
            # Load speed variation ranges
            if 'speed_min' in transition_data:
                settings.transition.speed_min = transition_data['speed_min']
            if 'speed_max' in transition_data:
                settings.transition.speed_max = transition_data['speed_max']
            
            # Load ghost parameter ranges
            if 'ghost_chance_min' in transition_data:
                settings.transition.ghost_chance_min = transition_data['ghost_chance_min']
            if 'ghost_chance_max' in transition_data:
                settings.transition.ghost_chance_max = transition_data['ghost_chance_max']
            if 'ghost_decay_min' in transition_data:
                settings.transition.ghost_decay_min = transition_data['ghost_decay_min']
            if 'ghost_decay_max' in transition_data:
                settings.transition.ghost_decay_max = transition_data['ghost_decay_max']
            
            # Load flicker parameter ranges
            if 'flicker_chance_min' in transition_data:
                settings.transition.flicker_chance_min = transition_data['flicker_chance_min']
            if 'flicker_chance_max' in transition_data:
                settings.transition.flicker_chance_max = transition_data['flicker_chance_max']
            if 'flicker_intensity_min' in transition_data:
                settings.transition.flicker_intensity_min = transition_data['flicker_intensity_min']
            if 'flicker_intensity_max' in transition_data:
                settings.transition.flicker_intensity_max = transition_data['flicker_intensity_max']
        
        # Load overlay settings
        if 'overlay' in data:
            overlay_data = data['overlay']
            if 'overlay_enabled' in overlay_data:
                settings.overlay.overlay_enabled = overlay_data['overlay_enabled']
            if 'overlay_effect' in overlay_data:
                settings.overlay.overlay_effect = OverlayEffect.from_string(overlay_data['overlay_effect'])
            if 'ghost_chance' in overlay_data:
                settings.overlay.ghost_chance = overlay_data['ghost_chance']
            if 'ghost_decay' in overlay_data:
                settings.overlay.ghost_decay = overlay_data['ghost_decay']
            if 'ghost_min_intensity' in overlay_data:
                settings.overlay.ghost_min_intensity = overlay_data['ghost_min_intensity']
            if 'ghost_spawn_chance' in overlay_data:
                settings.overlay.ghost_spawn_chance = overlay_data['ghost_spawn_chance']
            if 'flicker_chance' in overlay_data:
                settings.overlay.flicker_chance = overlay_data['flicker_chance']
            if 'flicker_intensity' in overlay_data:
                settings.overlay.flicker_intensity = overlay_data['flicker_intensity']
            if 'colour_scheme' in overlay_data:
                settings.overlay.colour_scheme = ColourScheme.from_string(overlay_data['colour_scheme'])
            if 'colour_transition_mode' in overlay_data:
                settings.overlay.colour_transition_mode = TransitionMode.from_string(overlay_data['colour_transition_mode'])
            if 'colour_shift_speed' in overlay_data:
                settings.overlay.colour_shift_speed = overlay_data['colour_shift_speed']
            if 'snap_duration' in overlay_data:
                settings.overlay.snap_duration = overlay_data['snap_duration']
            if 'enable_colour_averaging' in overlay_data:
                settings.overlay.enable_colour_averaging = overlay_data['enable_colour_averaging']
            if 'colour_averaging_interval' in overlay_data:
                settings.overlay.colour_averaging_interval = overlay_data['colour_averaging_interval']
        
        # Load text rendering settings
        if 'text_rendering' in data:
            text_data = data['text_rendering']
            if 'char_width' in text_data:
                settings.text_rendering.char_width = text_data['char_width']
            if 'char_height' in text_data:
                settings.text_rendering.char_height = text_data['char_height']
            if 'spacing_x' in text_data:
                settings.text_rendering.spacing_x = text_data['spacing_x']
            if 'spacing_y' in text_data:
                settings.text_rendering.spacing_y = text_data['spacing_y']
        
        # Load file monitoring settings
        if 'file_monitoring' in data:
            file_data = data['file_monitoring']
            if 'file_check_interval' in file_data:
                settings.file_monitoring.file_check_interval = file_data['file_check_interval']
        
        # Load debug settings
        if 'debug' in data:
            debug_data = data['debug']
            if 'debug_output_interval' in debug_data:
                settings.debug.debug_output_interval = debug_data['debug_output_interval']
        
        # Load ghost tuning settings
        if 'ghost_tuning' in data:
            ghost_data = data['ghost_tuning']
            if 'spawn_intensity_base' in ghost_data:
                settings.ghost_tuning.spawn_intensity_base = ghost_data['spawn_intensity_base']
            if 'spawn_intensity_multiplier' in ghost_data:
                settings.ghost_tuning.spawn_intensity_multiplier = ghost_data['spawn_intensity_multiplier']
            if 'accumulation_intensity' in ghost_data:
                settings.ghost_tuning.accumulation_intensity = ghost_data['accumulation_intensity']
            if 'max_ghost_intensity' in ghost_data:
                settings.ghost_tuning.max_ghost_intensity = ghost_data['max_ghost_intensity']
        
        return settings
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Settings to a dictionary for serialization."""
        return {
            'display': {
                'display_type': self.display.display_type.name.lower(),
                'grid_width': self.display.grid_width,
                'grid_height': self.display.grid_height,
                'square_size': self.display.square_size,
                'display_scale': self.display.display_scale,
                'fps': self.display.fps
            },
            'transition': {
                'transition_speed': self.transition.transition_speed,
                'text_change_interval': self.transition.text_change_interval,
                'blank_time_between_transitions': self.transition.blank_time_between_transitions,
                'shuffle_text_order': self.transition.shuffle_text_order,
                # Effect transition enable flags
                'transition_colour_scheme': self.transition.transition_colour_scheme,
                'transition_colour_mode': self.transition.transition_colour_mode,
                'transition_ghost_params': self.transition.transition_ghost_params,
                'transition_flicker_params': self.transition.transition_flicker_params,
                'transition_speed_variation': self.transition.transition_speed_variation,
                # Effect transition order modes
                'colour_scheme_order': self.transition.colour_scheme_order,
                'colour_mode_order': self.transition.colour_mode_order,
                'ghost_params_order': self.transition.ghost_params_order,
                'flicker_params_order': self.transition.flicker_params_order,
                'speed_order': self.transition.speed_order,
                # Speed variation ranges
                'speed_min': self.transition.speed_min,
                'speed_max': self.transition.speed_max,
                # Ghost parameter ranges
                'ghost_chance_min': self.transition.ghost_chance_min,
                'ghost_chance_max': self.transition.ghost_chance_max,
                'ghost_decay_min': self.transition.ghost_decay_min,
                'ghost_decay_max': self.transition.ghost_decay_max,
                # Flicker parameter ranges
                'flicker_chance_min': self.transition.flicker_chance_min,
                'flicker_chance_max': self.transition.flicker_chance_max,
                'flicker_intensity_min': self.transition.flicker_intensity_min,
                'flicker_intensity_max': self.transition.flicker_intensity_max
            },
            'overlay': {
                'overlay_enabled': self.overlay.overlay_enabled,
                'overlay_effect': self.overlay.overlay_effect.name.lower(),
                'ghost_chance': self.overlay.ghost_chance,
                'ghost_decay': self.overlay.ghost_decay,
                'ghost_min_intensity': self.overlay.ghost_min_intensity,
                'ghost_spawn_chance': self.overlay.ghost_spawn_chance,
                'flicker_chance': self.overlay.flicker_chance,
                'flicker_intensity': self.overlay.flicker_intensity,
                'colour_scheme': self.overlay.colour_scheme.value,
                'colour_transition_mode': self.overlay.colour_transition_mode.value,
                'colour_shift_speed': self.overlay.colour_shift_speed,
                'snap_duration': self.overlay.snap_duration,
                'enable_colour_averaging': self.overlay.enable_colour_averaging,
                'colour_averaging_interval': self.overlay.colour_averaging_interval
            },
            'text_rendering': {
                'char_width': self.text_rendering.char_width,
                'char_height': self.text_rendering.char_height,
                'spacing_x': self.text_rendering.spacing_x,
                'spacing_y': self.text_rendering.spacing_y
            },
            'file_monitoring': {
                'file_check_interval': self.file_monitoring.file_check_interval
            },
            'debug': {
                'debug_output_interval': self.debug.debug_output_interval
            },
            'ghost_tuning': {
                'spawn_intensity_base': self.ghost_tuning.spawn_intensity_base,
                'spawn_intensity_multiplier': self.ghost_tuning.spawn_intensity_multiplier,
                'accumulation_intensity': self.ghost_tuning.accumulation_intensity,
                'max_ghost_intensity': self.ghost_tuning.max_ghost_intensity
            }
        }
    
    def validate(self) -> bool:
        """Validate all settings."""
        return (self.display.validate() and 
                self.transition.validate() and 
                self.overlay.validate() and
                self.text_rendering.validate() and
                self.file_monitoring.validate() and
                self.debug.validate() and
                self.ghost_tuning.validate())
    
    def save_to_file(self, filepath: str) -> bool:
        """Save settings to a JSON file."""
        try:
            data = self.to_dict()
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Settings saved to: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving settings to {filepath}: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'Settings':
        """Load settings from a JSON file. Returns default settings if file doesn't exist or is invalid."""
        if not os.path.exists(filepath):
            logger.warning(f"Settings file {filepath} not found. Using defaults.")
            return cls.create_default()
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            settings = cls.from_dict(data)
            if settings.validate():
                logger.info(f"Settings loaded from: {filepath}")
                return settings
            else:
                logger.warning(f"Invalid settings in {filepath}. Using defaults.")
                return cls.create_default()
        except Exception as e:
            logger.error(f"Error loading settings from {filepath}: {e}. Using defaults.")
            return cls.create_default()
    
    def apply_to_displayer(self, displayer) -> None:
        """Apply these settings to a ScreenDisplayer instance."""
        # Set transition speed
        displayer.set_transition_speed(self.transition.transition_speed)
        
        # Configure overlay effects
        displayer.configure_overlay_effects(
            ghost_chance=self.overlay.ghost_chance,
            ghost_decay=self.overlay.ghost_decay,
            flicker_chance=self.overlay.flicker_chance,
            flicker_intensity=self.overlay.flicker_intensity,
            colour_scheme=self.overlay.colour_scheme,
            colour_transition_mode=self.overlay.colour_transition_mode,
            snap_duration=self.overlay.snap_duration,
            enable_colour_averaging=self.overlay.enable_colour_averaging,
            colour_averaging_interval=self.overlay.colour_averaging_interval
        )
        
        # Set display type
        displayer.set_display_type(self.display.display_type)
        
        logger.debug("Settings applied to ScreenDisplayer")
    
    def apply_to_transition_manager(self, transition_manager) -> None:
        """Apply settings to a TransitionManager instance."""
        transition_manager.set_text_change_interval(self.transition.text_change_interval)
        transition_manager.blank_time_between_transitions = self.transition.blank_time_between_transitions
        logger.debug("Settings applied to TransitionManager")
    
    def get_summary(self) -> str:
        """Get a human-readable summary of current settings."""
        return f"""Text Display Screen Settings:
Display:
  - Type: {self.display.display_type.name}
  - Grid: {self.display.grid_width}x{self.display.grid_height}
  - Square Size: {self.display.square_size}px
  - Scale: {self.display.display_scale}x
  - FPS: {self.display.fps}

Transitions:
  - Speed: {self.transition.transition_speed} pixels/frame
  - Change Interval: {self.transition.text_change_interval} frames

Overlay Effects:
  - Enabled: {self.overlay.overlay_enabled}
  - Effect Type: {self.overlay.overlay_effect.name}
  - Colour Scheme: {self.overlay.colour_scheme.value}
  - Transition Mode: {self.overlay.colour_transition_mode.value}
  - Ghost Chance: {self.overlay.ghost_chance}
  - Ghost Decay: {self.overlay.ghost_decay}
  - Flicker Chance: {self.overlay.flicker_chance}"""


# Convenience functions for common use cases
def create_transgender_pride_settings() -> Settings:
    """Create settings optimised for showing transgender pride colours."""
    settings = Settings.create_default()
    settings.overlay.colour_scheme = ColourScheme.TRANSGENDER
    settings.overlay.colour_transition_mode = TransitionMode.SPREAD_HORIZONTAL
    settings.overlay.ghost_chance = 0.15
    settings.overlay.ghost_decay = 0.985
    return settings


def create_performance_settings() -> Settings:
    """Create settings optimised for performance (minimal effects)."""
    settings = Settings.create_default()
    settings.overlay.overlay_enabled = False
    settings.overlay.ghost_chance = 0.0
    settings.overlay.flicker_chance = 0.0
    settings.transition.transition_speed = 20.0  # Faster transitions
    return settings


def create_demo_settings() -> Settings:
    """Create settings optimised for demonstrations (high visual impact)."""
    settings = Settings.create_default()
    settings.overlay.colour_scheme = ColourScheme.RAINBOW
    settings.overlay.colour_transition_mode = TransitionMode.SMOOTH
    settings.overlay.ghost_chance = 0.3
    settings.overlay.ghost_decay = 0.99
    settings.overlay.flicker_chance = 0.05
    settings.transition.transition_speed = 5.0  # Slower for visual appeal
    return settings