"""
Factory functions for creating preset settings configurations.

This module provides convenience functions for creating Settings instances
with commonly used configurations optimised for different use cases.
"""

from config.enums import ColourScheme, TransitionMode


def create_transgender_pride_settings():
    """Create settings optimised for showing transgender pride colours.
    
    Returns:
        Settings instance with transgender pride configuration
    """
    # Import here to avoid circular import
    from config.settings.dataclasses import Settings
    
    settings = Settings.create_default()
    settings.overlay.colour_scheme = ColourScheme.TRANSGENDER
    settings.overlay.colour_transition_mode = TransitionMode.SPREAD_HORIZONTAL
    settings.overlay.ghost_chance = 0.15
    settings.overlay.ghost_decay = 0.985
    return settings


def create_performance_settings():
    """Create settings optimised for performance (minimal effects).
    
    Returns:
        Settings instance with performance-optimised configuration
    """
    # Import here to avoid circular import
    from config.settings.dataclasses import Settings
    
    settings = Settings.create_default()
    settings.overlay.overlay_enabled = False
    settings.overlay.ghost_chance = 0.0
    settings.overlay.flicker_chance = 0.0
    settings.transition.transition_speed = 20.0  # Faster transitions
    return settings


def create_demo_settings():
    """Create settings optimised for demonstrations (high visual impact).
    
    Returns:
        Settings instance with demo-optimised configuration
    """
    # Import here to avoid circular import
    from config.settings.dataclasses import Settings
    
    settings = Settings.create_default()
    settings.overlay.colour_scheme = ColourScheme.RAINBOW
    settings.overlay.colour_transition_mode = TransitionMode.SMOOTH
    settings.overlay.ghost_chance = 0.3
    settings.overlay.ghost_decay = 0.99
    settings.overlay.flicker_chance = 0.05
    settings.transition.transition_speed = 5.0  # Slower for visual appeal
    return settings
