"""
Demonstration of the new enum-based settings system.

This script shows how to use the type-safe enum system to configure
display settings, color schemes, and transition modes.
"""

from config.enums import DisplayType, ColorScheme, TransitionMode, OverlayEffect
from config.settings import Settings, create_transgender_pride_settings, create_demo_settings, create_performance_settings


def demo_enum_usage():
    """Demonstrate basic enum usage."""
    print("=== Enum System Demonstration ===\n")
    
    # Display types
    print("Available Display Types:")
    for display_type in DisplayType:
        print(f"  - {display_type.name}: {display_type}")
    
    # Color schemes
    print(f"\nAvailable Color Schemes ({len(ColorScheme)} total):")
    for i, scheme in enumerate(ColorScheme):
        print(f"  {i+1:2d}. {scheme.value}")
    
    # Transition modes
    print(f"\nAvailable Transition Modes ({len(TransitionMode)} total):")
    for mode in TransitionMode:
        print(f"  - {mode.value}")
    
    # Overlay effects
    print(f"\nAvailable Overlay Effects ({len(OverlayEffect)} total):")
    for effect in OverlayEffect:
        print(f"  - {effect.name}")


def demo_settings_creation():
    """Demonstrate different ways to create settings."""
    print("\n=== Settings Creation Demonstration ===\n")
    
    # Method 1: Default settings
    print("1. Default Settings:")
    default_settings = Settings.create_default()
    print(f"   Display Type: {default_settings.display.display_type.name}")
    print(f"   Color Scheme: {default_settings.overlay.color_scheme.value}")
    print(f"   Transition Mode: {default_settings.overlay.color_transition_mode.value}")
    
    # Method 2: Preset transgender pride settings
    print("\n2. Transgender Pride Settings:")
    trans_settings = create_transgender_pride_settings()
    print(f"   Display Type: {trans_settings.display.display_type.name}")
    print(f"   Color Scheme: {trans_settings.overlay.color_scheme.value}")
    print(f"   Transition Mode: {trans_settings.overlay.color_transition_mode.value}")
    print(f"   Ghost Chance: {trans_settings.overlay.ghost_chance}")
    
    # Method 3: Demo settings for visual impact
    print("\n3. Demo Settings (High Visual Impact):")
    demo_settings = create_demo_settings()
    print(f"   Display Type: {demo_settings.display.display_type.name}")
    print(f"   Color Scheme: {demo_settings.overlay.color_scheme.value}")
    print(f"   Transition Mode: {demo_settings.overlay.color_transition_mode.value}")
    print(f"   Ghost Chance: {demo_settings.overlay.ghost_chance}")
    print(f"   Flicker Chance: {demo_settings.overlay.flicker_chance}")
    
    # Method 4: Performance settings (minimal effects)
    print("\n4. Performance Settings (Minimal Effects):")
    perf_settings = create_performance_settings()
    print(f"   Display Type: {perf_settings.display.display_type.name}")
    print(f"   Overlay Enabled: {perf_settings.overlay.overlay_enabled}")
    print(f"   Transition Speed: {perf_settings.transition.transition_speed} pixels/frame")


def demo_custom_settings():
    """Demonstrate creating custom settings with enums."""
    print("\n=== Custom Settings Creation ===\n")
    
    # Create custom settings
    custom = Settings.create_default()
    
    # Modify settings using enums (type-safe!)
    custom.display.display_type = DisplayType.PIXEL_GRID
    custom.display.grid_width = 80
    custom.display.grid_height = 40
    custom.display.fps = 30
    
    custom.overlay.color_scheme = ColorScheme.RAINBOW
    custom.overlay.color_transition_mode = TransitionMode.SNAP
    custom.overlay.ghost_chance = 0.25
    custom.overlay.snap_duration = 60  # 1 second at 60fps
    
    custom.transition.transition_speed = 15.0
    custom.transition.text_change_interval = 900  # 15 seconds at 60fps
    
    print("Custom Settings Created:")
    print(f"   Grid Size: {custom.display.grid_width}x{custom.display.grid_height}")
    print(f"   FPS: {custom.display.fps}")
    print(f"   Color Scheme: {custom.overlay.color_scheme.value}")
    print(f"   Transition Mode: {custom.overlay.color_transition_mode.value}")
    print(f"   Snap Duration: {custom.overlay.snap_duration} frames")
    print(f"   Transition Speed: {custom.transition.transition_speed} pixels/frame")
    
    # Validate settings
    is_valid = custom.validate()
    print(f"   Settings Valid: {is_valid}")
    
    return custom


def demo_enum_string_conversion():
    """Demonstrate string conversion features."""
    print("\n=== String Conversion Demonstration ===\n")
    
    # Converting from strings (backward compatibility)
    print("Converting from strings:")
    color_from_string = ColorScheme.from_string("transgender")
    print(f"   'transgender' -> {color_from_string.value}")
    
    mode_from_string = TransitionMode.from_string("spread_horizontal")
    print(f"   'spread_horizontal' -> {mode_from_string.value}")
    
    # Invalid string handling
    invalid_color = ColorScheme.from_string("invalid_scheme")
    print(f"   'invalid_scheme' -> {invalid_color.value} (fallback to default)")
    
    # Converting to strings
    print("\nConverting to strings:")
    rainbow_scheme = ColorScheme.RAINBOW
    print(f"   {rainbow_scheme} -> '{rainbow_scheme.value}'")
    
    smooth_mode = TransitionMode.SMOOTH
    print(f"   {smooth_mode} -> '{smooth_mode.value}'")


def demo_file_operations():
    """Demonstrate saving and loading settings from files."""
    print("\n=== File Operations Demonstration ===\n")
    
    # Create some custom settings
    custom = Settings.create_default()
    custom.overlay.color_scheme = ColorScheme.BISEXUAL
    custom.overlay.color_transition_mode = TransitionMode.SPREAD_VERTICAL
    custom.display.fps = 45
    
    # Save to file
    filename = "config/demo_settings.json"
    success = custom.save_to_file(filename)
    print(f"Save operation: {'Success' if success else 'Failed'}")
    
    # Load from file
    if success:
        loaded_settings = Settings.load_from_file(filename)
        print("Loaded settings:")
        print(f"   Color Scheme: {loaded_settings.overlay.color_scheme.value}")
        print(f"   Transition Mode: {loaded_settings.overlay.color_transition_mode.value}")
        print(f"   FPS: {loaded_settings.display.fps}")
        
        # Verify they match
        schemes_match = loaded_settings.overlay.color_scheme == custom.overlay.color_scheme
        modes_match = loaded_settings.overlay.color_transition_mode == custom.overlay.color_transition_mode
        fps_match = loaded_settings.display.fps == custom.display.fps
        
        print(f"   Settings match original: {schemes_match and modes_match and fps_match}")


if __name__ == "__main__":
    # Run all demonstrations
    demo_enum_usage()
    demo_settings_creation()
    custom_settings = demo_custom_settings()
    demo_enum_string_conversion()
    demo_file_operations()
    
    print("\n=== Summary ===")
    print("The enum system provides:")
    print("  ✓ Type safety - no more typos in string names")
    print("  ✓ IDE autocompletion for all settings")
    print("  ✓ Validation and fallback for invalid values")
    print("  ✓ Centralized configuration management")
    print("  ✓ File-based settings persistence")
    print("  ✓ Backward compatibility with string-based code")
    print("\nYour display settings are now fully type-safe and organized!")