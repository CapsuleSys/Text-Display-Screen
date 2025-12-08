"""
Dataclass definitions for Text Display Screen settings.

This module contains all the settings dataclasses that define the configuration
structure for the display system. Each dataclass represents a logical group of
related settings with validation methods.
"""

from dataclasses import dataclass, field
from config.enums import (
    DisplayType, 
    ColourScheme, 
    TransitionMode, 
    OverlayEffect,
    DEFAULT_DISPLAY_TYPE,
    DEFAULT_COLOUR_SCHEME,
    DEFAULT_TRANSITION_MODE,
    DEFAULT_OVERLAY_EFFECT
)


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
    
    def validate(self) -> bool:
        """Validate all settings."""
        return (self.display.validate() and 
                self.transition.validate() and 
                self.overlay.validate() and
                self.text_rendering.validate() and
                self.file_monitoring.validate() and
                self.debug.validate() and
                self.ghost_tuning.validate())
    
    def to_dict(self):
        """Convert Settings to a dictionary for serialisation."""
        from config.settings.io import settings_to_dict
        return settings_to_dict(self)
    
    @classmethod
    def from_dict(cls, data):
        """Create a Settings instance from a dictionary."""
        from config.settings.io import dict_to_settings
        return dict_to_settings(data)
    
    def save_to_file(self, filepath: str) -> bool:
        """Save settings to a JSON file."""
        from config.settings.io import save_settings
        return save_settings(self, filepath)
    
    @classmethod
    def load_from_file(cls, filepath: str):
        """Load settings from a JSON file."""
        from config.settings.io import load_settings
        return load_settings(filepath)
    
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
    
    def apply_to_transition_manager(self, transition_manager) -> None:
        """Apply settings to a TransitionManager instance."""
        transition_manager.set_text_change_interval(self.transition.text_change_interval)
        transition_manager.blank_time_between_transitions = self.transition.blank_time_between_transitions
