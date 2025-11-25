"""
Enums for Text Display Screen settings.

This module provides type-safe enum definitions for all configurable display settings,
replacing string-based configurations with proper enums for better validation,
IDE support, and code maintainability.
"""

from enum import Enum, auto
from typing import List, Tuple


class DisplayType(Enum):
    """Display rendering types for text output."""
    PIXEL_GRID = auto()  # Current 6x8 character grid with pixel spacing
    # Future display types can be added here:
    # ASCII_ART = auto()
    # BRAILLE = auto() 
    # BLOCK_CHARACTERS = auto()
    
    @classmethod
    def from_string(cls, name: str) -> 'DisplayType':
        """Convert a string name to DisplayType enum. Returns PIXEL_GRID if not found."""
        name_upper = name.upper()
        for display_type in cls:
            if display_type.name == name_upper:
                return display_type
        return cls.PIXEL_GRID


class ColorScheme(Enum):
    """Available color schemes for ghost overlay effects."""
    # Pride flag schemes
    TRANSGENDER = "transgender"
    LESBIAN = "lesbian"
    BISEXUAL = "bisexual"
    NONBINARY = "nonbinary"
    PANSEXUAL = "pansexual"
    ASEXUAL = "asexual"
    AROMANTIC = "aromantic"
    
    # Themed color schemes
    RAINBOW = "rainbow"
    FIRE = "fire"
    ICE = "ice"
    FOREST = "forest"
    SUNSET = "sunset"
    OCEAN = "ocean"
    RETRO = "retro"
    PASTEL = "pastel"
    NEON = "neon"
    CLASSIC = "classic"
    GLOOMY = "gloomy"
    YELLOWBEAM = "yellowbeam"
    REDBEAM = "redbeam"
    BLUEBEAM = "bluebeam"
    
    @classmethod
    def list_names(cls) -> List[str]:
        """Return a list of all color scheme names as strings."""
        return [scheme.value for scheme in cls]
    
    @classmethod
    def from_string(cls, name: str) -> 'ColorScheme':
        """Convert a string name to ColorScheme enum. Returns CLASSIC if not found."""
        name_lower = name.lower()
        for scheme in cls:
            if scheme.value == name_lower:
                return scheme
        return cls.CLASSIC
    
    def __str__(self) -> str:
        """Return the string value of the color scheme."""
        return self.value


class TransitionMode(Enum):
    """Color transition modes for ghost overlay effects."""
    SMOOTH = "smooth"              # Smooth color blending over time
    SNAP = "snap"                  # Discrete color changes at intervals
    MIXED = "mixed"                # Random colors from scheme
    SPREAD_HORIZONTAL = "spread_horizontal"  # Horizontal color gradient
    SPREAD_VERTICAL = "spread_vertical"      # Vertical color gradient
    
    @classmethod
    def list_names(cls) -> List[str]:
        """Return a list of all transition mode names as strings."""
        return [mode.value for mode in cls]
    
    @classmethod
    def from_string(cls, name: str) -> 'TransitionMode':
        """Convert a string name to TransitionMode enum. Returns SMOOTH if not found."""
        name_lower = name.lower()
        for mode in cls:
            if mode.value == name_lower:
                return mode
        return cls.SMOOTH
    
    def __str__(self) -> str:
        """Return the string value of the transition mode."""
        return self.value


class OverlayEffect(Enum):
    """Ghost overlay effect types."""
    OUTLINE = auto()     # Ghost pixels around text edges
    GLOW = auto()        # Glowing effect around text
    FLICKER = auto()     # Random pixel flickering
    NONE = auto()        # No overlay effects
    
    @classmethod
    def from_string(cls, name: str) -> 'OverlayEffect':
        """Convert a string name to OverlayEffect enum. Returns OUTLINE if not found."""
        name_upper = name.upper()
        for effect in cls:
            if effect.name == name_upper:
                return effect
        return cls.OUTLINE


# Type aliases for commonly used types
RGB = Tuple[int, int, int]
ColorList = List[RGB]

# Default values
DEFAULT_DISPLAY_TYPE = DisplayType.PIXEL_GRID
DEFAULT_COLOR_SCHEME = ColorScheme.CLASSIC
DEFAULT_TRANSITION_MODE = TransitionMode.SMOOTH
DEFAULT_OVERLAY_EFFECT = OverlayEffect.OUTLINE