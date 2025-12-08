"""
Settings module for Text Display Screen.

This module provides a clean interface for settings management by re-exporting
all the settings classes and functions from the submodules.

Main exports:
    - Settings: Main settings container class
    - All individual settings dataclasses (DisplaySettings, TransitionSettings, etc.)
    - I/O functions: load_settings, save_settings
    - Factory functions: create_transgender_pride_settings, create_performance_settings, create_demo_settings
"""

# Import dataclasses
from config.settings.dataclasses import (
    Settings,
    DisplaySettings,
    TransitionSettings,
    TextRenderingSettings,
    FileMonitoringSettings,
    DebugSettings,
    GhostEffectTuning,
    OverlaySettings
)

# Import I/O functions
from config.settings.io import (
    load_settings,
    save_settings,
    settings_to_dict,
    dict_to_settings
)

# Import factory functions
from config.settings.presets import (
    create_transgender_pride_settings,
    create_performance_settings,
    create_demo_settings
)


__all__ = [
    # Main class
    'Settings',
    # Individual settings classes
    'DisplaySettings',
    'TransitionSettings',
    'TextRenderingSettings',
    'FileMonitoringSettings',
    'DebugSettings',
    'GhostEffectTuning',
    'OverlaySettings',
    # I/O functions
    'load_settings',
    'save_settings',
    'settings_to_dict',
    'dict_to_settings',
    # Factory functions
    'create_transgender_pride_settings',
    'create_performance_settings',
    'create_demo_settings',
]
