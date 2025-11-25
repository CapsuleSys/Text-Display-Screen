"""
Color schemes for ghost overlay effects.
Each scheme contains a list of RGB color tuples that can be used for ghost pixels.

When using 'snap' transition mode, colors will be displayed in sequence for the specified duration.
When using 'smooth' transition mode, colors will blend smoothly between each other.
"""

from typing import List, Tuple, Union
from config.enums import ColorScheme

COLOR_SCHEMES = {
    'transgender': [
        (91, 206, 250),   # Baby blue
        (245, 169, 184),  # Pink
        (255, 255, 255),  # White
        (245, 169, 184),  # Pink
        (91, 206, 250),   # Baby blue
    ],
    
    'rainbow': [
        (255, 0, 0),      # Red
        (255, 127, 0),    # Orange
        (255, 255, 0),    # Yellow
        (0, 255, 0),      # Green
        (0, 0, 255),      # Blue
        (75, 0, 130),     # Indigo
        (148, 0, 211),    # Violet
    ],
    
    'lesbian': [
        (213, 45, 0),     # Dark orange
        (255, 154, 86),   # Orange
        (255, 255, 255),  # White
        (211, 98, 164),   # Pink
        (163, 2, 98),     # Dark pink
    ],
    
    'bisexual': [
        (214, 2, 112),    # Magenta
        (155, 79, 150),   # Purple
        (0, 56, 168),     # Blue
    ],
    
    'nonbinary': [
        (255, 244, 48),   # Yellow
        (255, 255, 255),  # White
        (156, 89, 209),   # Purple
        (44, 44, 44),     # Black
    ],
    
    'pansexual': [
        (255, 33, 140),   # Pink
        (255, 216, 0),    # Yellow
        (33, 177, 255),   # Blue
    ],
    
    'asexual': [
        (0, 0, 0),        # Black
        (163, 163, 163),  # Gray
        (255, 255, 255),  # White
        (128, 0, 128),    # Purple
    ],
    
    'aromantic': [
        (61, 165, 66),    # Green
        (167, 211, 121),  # Light green
        (255, 255, 255),  # White
        (169, 169, 169),  # Gray
        (0, 0, 0),        # Black
    ],
    
    'fire': [
        (255, 0, 0),      # Red
        (255, 69, 0),     # Red-orange
        (255, 140, 0),    # Dark orange
        (255, 165, 0),    # Orange
        (255, 215, 0),    # Gold
    ],
    
    'ice': [
        (173, 216, 230),  # Light blue
        (135, 206, 235),  # Sky blue
        (70, 130, 180),   # Steel blue
        (100, 149, 237),  # Cornflower blue
        (255, 255, 255),  # White
    ],
    
    'forest': [
        (34, 139, 34),    # Forest green
        (50, 205, 50),    # Lime green
        (124, 252, 0),    # Lawn green
        (173, 255, 47),   # Green-yellow
        (154, 205, 50),   # Yellow-green
    ],
    
    'sunset': [
        (255, 94, 77),    # Coral
        (255, 154, 0),    # Orange
        (255, 206, 84),   # Yellow
        (237, 117, 95),   # Salmon
        (148, 0, 211),    # Purple
    ],
    
    'ocean': [
        (0, 119, 190),    # Ocean blue
        (0, 180, 216),    # Cyan
        (144, 224, 239),  # Light blue
        (0, 119, 140),    # Teal
        (3, 4, 94),       # Navy
    ],
    
    'retro': [
        (255, 20, 147),   # Deep pink
        (0, 255, 255),    # Cyan
        (255, 255, 0),    # Yellow
        (255, 0, 255),    # Magenta
        (0, 255, 0),      # Lime
    ],
    
    'pastel': [
        (255, 182, 193),  # Light pink
        (173, 216, 230),  # Light blue
        (144, 238, 144),  # Light green
        (255, 160, 122),  # Light salmon
        (221, 160, 221),  # Plum
    ],
    
    'neon': [
        (57, 255, 20),    # Neon green
        (255, 20, 147),   # Neon pink
        (0, 255, 255),    # Neon cyan
        (255, 255, 0),    # Neon yellow
        (191, 0, 255),    # Neon purple
    ],
    
    'classic': [
        (255, 0, 0),      # Red
        (0, 255, 0),      # Green
        (0, 0, 255),      # Blue
        (255, 255, 0),    # Yellow
        (255, 0, 255),    # Magenta
        (0, 255, 255),    # Cyan
        (255, 255, 255),  # White
    ],
    'gloomy': [
        (130, 130, 130),  # Medium gray
        (0, 0, 0),        # Black
        (0, 0, 0),        # Black
        (0, 0, 0),        # Black
        (130, 130, 130),  # Medium gray
    ],
    "yellowbeam": [
        (45, 45, 45),
        (0,0,0),
        (255, 255, 0),    # Yellow
        (0,0,0),
        (45, 45, 45),
    ],
    "redbeam": [
        (45, 45, 45),
        (0,0,0),
        (255, 0, 0),    # Red
        (0,0,0),
        (45, 45, 45),
    ],
    "bluebeam": [
        (45, 45, 45),
        (0,0,0),
        (0, 0, 255),    # Blue
        (0,0,0),
        (45, 45, 45),
    ],
}

def get_color_scheme(scheme: Union[ColorScheme, str]) -> List[Tuple[int, int, int]]:
    """Get a color scheme by ColorScheme enum or string name. Returns classic scheme if not found."""
    if isinstance(scheme, ColorScheme):
        scheme_name = scheme.value
    else:
        scheme_name = str(scheme).lower()
    
    return COLOR_SCHEMES.get(scheme_name, COLOR_SCHEMES['classic'])


def get_color_scheme_by_enum(scheme: ColorScheme) -> List[Tuple[int, int, int]]:
    """Get a color scheme by ColorScheme enum. Type-safe version."""
    return COLOR_SCHEMES.get(scheme.value, COLOR_SCHEMES['classic'])

def list_color_schemes() -> List[str]:
    """Return a list of available color scheme names."""
    return list(COLOR_SCHEMES.keys())


def list_color_scheme_enums() -> List[ColorScheme]:
    """Return a list of available ColorScheme enums."""
    return list(ColorScheme)


def validate_color_scheme(colors) -> bool:
    """Validate that a color scheme is properly formatted."""
    if not isinstance(colors, list):
        return False
    
    for color in colors:
        if not isinstance(color, tuple) or len(color) != 3:
            return False
        if not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
            return False
    
    return True


def validate_color_scheme_name(scheme: Union[ColorScheme, str]) -> bool:
    """Validate that a color scheme name or enum is valid."""
    if isinstance(scheme, ColorScheme):
        return scheme.value in COLOR_SCHEMES
    else:
        return str(scheme).lower() in COLOR_SCHEMES
