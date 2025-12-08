"""
I/O operations for settings persistence.

This module handles loading and saving settings to/from JSON files.
"""

from typing import Dict, Any
import json
import os
from logger_setup import setup_logger
from config.enums import DisplayType, ColourScheme, TransitionMode, OverlayEffect

logger = setup_logger(__name__)


def settings_to_dict(settings) -> Dict[str, Any]:
    """Convert Settings instance to a dictionary for serialisation.
    
    Args:
        settings: Settings instance to convert
        
    Returns:
        Dictionary representation of settings
    """
    return {
        'display': {
            'display_type': settings.display.display_type.name.lower(),
            'grid_width': settings.display.grid_width,
            'grid_height': settings.display.grid_height,
            'square_size': settings.display.square_size,
            'display_scale': settings.display.display_scale,
            'fps': settings.display.fps
        },
        'transition': {
            'transition_speed': settings.transition.transition_speed,
            'text_change_interval': settings.transition.text_change_interval,
            'blank_time_between_transitions': settings.transition.blank_time_between_transitions,
            'shuffle_text_order': settings.transition.shuffle_text_order,
            # Effect transition enable flags
            'transition_colour_scheme': settings.transition.transition_colour_scheme,
            'transition_colour_mode': settings.transition.transition_colour_mode,
            'transition_ghost_params': settings.transition.transition_ghost_params,
            'transition_flicker_params': settings.transition.transition_flicker_params,
            'transition_speed_variation': settings.transition.transition_speed_variation,
            # Effect transition order modes
            'colour_scheme_order': settings.transition.colour_scheme_order,
            'colour_mode_order': settings.transition.colour_mode_order,
            'ghost_params_order': settings.transition.ghost_params_order,
            'flicker_params_order': settings.transition.flicker_params_order,
            'speed_order': settings.transition.speed_order,
            # Speed variation ranges
            'speed_min': settings.transition.speed_min,
            'speed_max': settings.transition.speed_max,
            # Ghost parameter ranges
            'ghost_chance_min': settings.transition.ghost_chance_min,
            'ghost_chance_max': settings.transition.ghost_chance_max,
            'ghost_decay_min': settings.transition.ghost_decay_min,
            'ghost_decay_max': settings.transition.ghost_decay_max,
            # Flicker parameter ranges
            'flicker_chance_min': settings.transition.flicker_chance_min,
            'flicker_chance_max': settings.transition.flicker_chance_max,
            'flicker_intensity_min': settings.transition.flicker_intensity_min,
            'flicker_intensity_max': settings.transition.flicker_intensity_max
        },
        'overlay': {
            'overlay_enabled': settings.overlay.overlay_enabled,
            'overlay_effect': settings.overlay.overlay_effect.name.lower(),
            'ghost_chance': settings.overlay.ghost_chance,
            'ghost_decay': settings.overlay.ghost_decay,
            'ghost_min_intensity': settings.overlay.ghost_min_intensity,
            'ghost_spawn_chance': settings.overlay.ghost_spawn_chance,
            'flicker_chance': settings.overlay.flicker_chance,
            'flicker_intensity': settings.overlay.flicker_intensity,
            'colour_scheme': settings.overlay.colour_scheme.value,
            'colour_transition_mode': settings.overlay.colour_transition_mode.value,
            'colour_shift_speed': settings.overlay.colour_shift_speed,
            'snap_duration': settings.overlay.snap_duration,
            'enable_colour_averaging': settings.overlay.enable_colour_averaging,
            'colour_averaging_interval': settings.overlay.colour_averaging_interval
        },
        'text_rendering': {
            'char_width': settings.text_rendering.char_width,
            'char_height': settings.text_rendering.char_height,
            'spacing_x': settings.text_rendering.spacing_x,
            'spacing_y': settings.text_rendering.spacing_y
        },
        'file_monitoring': {
            'file_check_interval': settings.file_monitoring.file_check_interval
        },
        'debug': {
            'debug_output_interval': settings.debug.debug_output_interval
        },
        'ghost_tuning': {
            'spawn_intensity_base': settings.ghost_tuning.spawn_intensity_base,
            'spawn_intensity_multiplier': settings.ghost_tuning.spawn_intensity_multiplier,
            'accumulation_intensity': settings.ghost_tuning.accumulation_intensity,
            'max_ghost_intensity': settings.ghost_tuning.max_ghost_intensity
        }
    }


def dict_to_settings(data: Dict[str, Any]):
    """Create a Settings instance from a dictionary.
    
    Args:
        data: Dictionary containing settings data
        
    Returns:
        Settings instance populated with data from dictionary
    """
    # Import here to avoid circular import
    from config.settings.dataclasses import Settings
    
    settings = Settings()
    
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


def save_settings(settings, filepath: str) -> bool:
    """Save settings to a JSON file.
    
    Args:
        settings: Settings instance to save
        filepath: Path to save the settings file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        data = settings_to_dict(settings)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Settings saved to: {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving settings to {filepath}: {e}")
        return False


def load_settings(filepath: str):
    """Load settings from a JSON file.
    
    Args:
        filepath: Path to load settings from
        
    Returns:
        Settings instance loaded from file, or default settings if file doesn't exist or is invalid
    """
    # Import here to avoid circular import
    from config.settings.dataclasses import Settings
    
    if not os.path.exists(filepath):
        logger.warning(f"Settings file {filepath} not found. Using defaults.")
        return Settings.create_default()
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        settings = dict_to_settings(data)
        if settings.validate():
            logger.info(f"Settings loaded from: {filepath}")
            return settings
        else:
            logger.warning(f"Invalid settings in {filepath}. Using defaults.")
            return Settings.create_default()
    except Exception as e:
        logger.error(f"Error loading settings from {filepath}: {e}. Using defaults.")
        return Settings.create_default()
