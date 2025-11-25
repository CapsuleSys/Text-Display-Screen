"""
Centralized settings configuration for Text Display Screen.

This module provides a Settings class that manages all configurable aspects of the
display system using type-safe enums and validation. It serves as the single source
of truth for all display and overlay settings configuration.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any, Union
from config.enums import DisplayType, ColorScheme, TransitionMode, OverlayEffect, RGB, DEFAULT_DISPLAY_TYPE, DEFAULT_COLOR_SCHEME, DEFAULT_TRANSITION_MODE, DEFAULT_OVERLAY_EFFECT
import json
import os


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
    
    def validate(self) -> bool:
        """Validate transition settings."""
        if self.transition_speed < 0.1:
            return False
        if self.text_change_interval <= 0:
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
    
    # Color settings
    color_scheme: ColorScheme = DEFAULT_COLOR_SCHEME
    color_transition_mode: TransitionMode = DEFAULT_TRANSITION_MODE
    color_shift_speed: float = 0.005
    snap_duration: int = 120  # frames
    
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
        if self.color_shift_speed < 0:
            return False
        if self.snap_duration <= 0:
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
            if 'color_scheme' in overlay_data:
                settings.overlay.color_scheme = ColorScheme.from_string(overlay_data['color_scheme'])
            if 'color_transition_mode' in overlay_data:
                settings.overlay.color_transition_mode = TransitionMode.from_string(overlay_data['color_transition_mode'])
            if 'color_shift_speed' in overlay_data:
                settings.overlay.color_shift_speed = overlay_data['color_shift_speed']
            if 'snap_duration' in overlay_data:
                settings.overlay.snap_duration = overlay_data['snap_duration']
        
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
                'shuffle_text_order': self.transition.shuffle_text_order
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
                'color_scheme': self.overlay.color_scheme.value,
                'color_transition_mode': self.overlay.color_transition_mode.value,
                'color_shift_speed': self.overlay.color_shift_speed,
                'snap_duration': self.overlay.snap_duration
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
            print(f"Settings saved to: {filepath}")
            return True
        except Exception as e:
            print(f"Error saving settings to {filepath}: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'Settings':
        """Load settings from a JSON file. Returns default settings if file doesn't exist or is invalid."""
        if not os.path.exists(filepath):
            print(f"Settings file {filepath} not found. Using defaults.")
            return cls.create_default()
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            settings = cls.from_dict(data)
            if settings.validate():
                print(f"Settings loaded from: {filepath}")
                return settings
            else:
                print(f"Invalid settings in {filepath}. Using defaults.")
                return cls.create_default()
        except Exception as e:
            print(f"Error loading settings from {filepath}: {e}. Using defaults.")
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
            color_scheme=self.overlay.color_scheme,
            color_transition_mode=self.overlay.color_transition_mode,
            snap_duration=self.overlay.snap_duration
        )
        
        # Set display type
        displayer.set_display_type(self.display.display_type)
        
        print("Settings applied to ScreenDisplayer")
    
    def apply_to_transition_manager(self, transition_manager) -> None:
        """Apply settings to a TransitionManager instance."""
        transition_manager.set_text_change_interval(self.transition.text_change_interval)
        transition_manager.blank_time_between_transitions = self.transition.blank_time_between_transitions
        print("Settings applied to TransitionManager")
    
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
  - Color Scheme: {self.overlay.color_scheme.value}
  - Transition Mode: {self.overlay.color_transition_mode.value}
  - Ghost Chance: {self.overlay.ghost_chance}
  - Ghost Decay: {self.overlay.ghost_decay}
  - Flicker Chance: {self.overlay.flicker_chance}"""


# Convenience functions for common use cases
def create_transgender_pride_settings() -> Settings:
    """Create settings optimized for showing transgender pride colors."""
    settings = Settings.create_default()
    settings.overlay.color_scheme = ColorScheme.TRANSGENDER
    settings.overlay.color_transition_mode = TransitionMode.SPREAD_HORIZONTAL
    settings.overlay.ghost_chance = 0.15
    settings.overlay.ghost_decay = 0.985
    return settings


def create_performance_settings() -> Settings:
    """Create settings optimized for performance (minimal effects)."""
    settings = Settings.create_default()
    settings.overlay.overlay_enabled = False
    settings.overlay.ghost_chance = 0.0
    settings.overlay.flicker_chance = 0.0
    settings.transition.transition_speed = 20.0  # Faster transitions
    return settings


def create_demo_settings() -> Settings:
    """Create settings optimized for demonstrations (high visual impact)."""
    settings = Settings.create_default()
    settings.overlay.color_scheme = ColorScheme.RAINBOW
    settings.overlay.color_transition_mode = TransitionMode.SMOOTH
    settings.overlay.ghost_chance = 0.3
    settings.overlay.ghost_decay = 0.99
    settings.overlay.flicker_chance = 0.05
    settings.transition.transition_speed = 5.0  # Slower for visual appeal
    return settings