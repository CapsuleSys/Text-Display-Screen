"""
Colour schemes for ghost overlay effects.
Each scheme contains a list of RGB colour tuples that can be used for ghost pixels.

When using 'snap' transition mode, colours will be displayed in sequence for the specified duration.
When using 'smooth' transition mode, colours will blend smoothly between each other.
"""

from typing import List, Tuple, Union
from config.enums import ColourScheme

COLOUR_SCHEMES = {
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
        (163, 163, 163),  # Grey
        (255, 255, 255),  # White
        (128, 0, 128),    # Purple
    ],
    
    'aromantic': [
        (61, 165, 66),    # Green
        (167, 211, 121),  # Light green
        (255, 255, 255),  # White
        (169, 169, 169),  # Grey
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
        (130, 130, 130),  # Medium grey
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

def get_colour_scheme(scheme: Union[ColourScheme, str]) -> List[Tuple[int, int, int]]:
    """Get a colour scheme by ColourScheme enum or string name. Returns classic scheme if not found."""
    if isinstance(scheme, ColourScheme):
        scheme_name = scheme.value
    else:
        scheme_name = str(scheme).lower()
    
    return COLOUR_SCHEMES.get(scheme_name, COLOUR_SCHEMES['classic'])


def get_colour_scheme_by_enum(scheme: ColourScheme) -> List[Tuple[int, int, int]]:
    """Get a colour scheme by ColourScheme enum. Type-safe version."""
    return COLOUR_SCHEMES.get(scheme.value, COLOUR_SCHEMES['classic'])

def list_colour_schemes() -> List[str]:
    """Return a list of available colour scheme names."""
    return list(COLOUR_SCHEMES.keys())


def list_colour_scheme_enums() -> List[ColourScheme]:
    """Return a list of available ColourScheme enums."""
    return list(ColourScheme)


def validate_colour_scheme(
    colours: List[Tuple[int, int, int]],
    raise_on_error: bool = False
) -> bool:
    """Validate that a colour scheme is properly formatted.
    
    Args:
        colours: List of RGB colour tuples to validate
        raise_on_error: If True, raise ValueError with details instead of returning False
        
    Returns:
        True if colour scheme is valid, False otherwise
        
    Raises:
        ValueError: If raise_on_error=True and validation fails
    """
    # Check if colours is a list
    if not isinstance(colours, list):
        if raise_on_error:
            raise ValueError(f"Colour scheme must be list, got {type(colours).__name__}")
        return False
    
    # Check each colour tuple
    for i, colour in enumerate(colours):
        # Check if tuple
        if not isinstance(colour, tuple):
            if raise_on_error:
                raise ValueError(f"Colour {i} must be tuple, got {type(colour).__name__}")
            return False
        
        # Check tuple length
        if len(colour) != 3:
            if raise_on_error:
                raise ValueError(f"Colour {i} must have 3 values (RGB), got {len(colour)}")
            return False
        
        # Check RGB values
        for j, component in enumerate(colour):
            if not isinstance(component, int):
                if raise_on_error:
                    raise ValueError(f"Colour {i} component {j} must be int, got {type(component).__name__}")
                return False
            
            if not (0 <= component <= 255):
                if raise_on_error:
                    raise ValueError(f"Colour {i} component {j} must be 0-255, got {component}")
                return False
    
    return True


def validate_colour_scheme_name(scheme: Union[ColourScheme, str]) -> bool:
    """Validate that a colour scheme name or enum is valid."""
    if isinstance(scheme, ColourScheme):
        return scheme.value in COLOUR_SCHEMES
    else:
        return str(scheme).lower() in COLOUR_SCHEMES
