import pygame
from screendisplayer import ScreenDisplayer
from transition_manager import TransitionManager
from config.settings import Settings, create_transgender_pride_settings, create_demo_settings
from config.enums import DisplayType, ColorScheme, TransitionMode
import os

def animate_example():
    try:
        # Initialize pygame first
        pygame.init()
        print("Pygame initialized successfully")
        
        # Create settings using enum-based configuration
        print("Creating settings with enum-based configuration...")
        
        # Try to load settings from file first (from settings GUI), fallback to transgender pride theme
        settings_file = "config/user_settings.json"
        if os.path.exists(settings_file):
            print(f"Loading settings from {settings_file}...")
            settings = Settings.load_from_file(settings_file)
        else:
            print("No settings file found, using transgender pride theme...")
            settings = create_transgender_pride_settings()  # Use transgender pride theme
        
        # You can also create custom settings:
        # settings = Settings.create_default()
        # settings.display.display_type = DisplayType.PIXEL_GRID
        # settings.overlay.color_scheme = ColorScheme.RAINBOW
        # settings.overlay.color_transition_mode = TransitionMode.SPREAD_HORIZONTAL
        # settings.transition.transition_speed = 8.0
        
        print(f"Settings summary:\n{settings.get_summary()}")
        
        # Create display with enum-based settings
        print("Creating ScreenDisplayer...")
        displayer = ScreenDisplayer(
            grid_width=settings.display.grid_width,
            grid_height=settings.display.grid_height,
            square_size=settings.display.square_size,
            display_scale=settings.display.display_scale,
            display_type=settings.display.display_type,
            settings=settings
        )
        print("ScreenDisplayer created successfully")

        # Load text content - check for selected file first
        selected_text_file_path = "config/current_text_file.txt"
        text_file = "TextInputFiles/webcam_background.txt"  # Default fallback
        
        # Try to load selected text file
        if os.path.exists(selected_text_file_path):
            try:
                with open(selected_text_file_path, 'r', encoding='utf-8') as f:
                    selected_file = f.read().strip()
                if os.path.exists(selected_file):
                    text_file = selected_file
                    print(f"Using selected text file: {text_file}")
            except Exception as e:
                print(f"Error reading text file selection: {e}, using default")
        
        if os.path.exists(text_file):
            print(f"Loading text file: {text_file}")
            displayer.load_text_file(text_file)
            print(f"Text content loaded: {len(displayer.text_content)} blocks")
        else:
            print(f"Warning: {text_file} not found. Creating sample text...")
            displayer.text_content = [
                "Hello\nWorld!",
                "This is\na test\nof the\nsystem",
                "Text\nDisplay\nWorking!",
                "Transition\nManager\nRocks!"
            ]
            print("Sample text created")
        
        # Create and configure transition manager
        print("Setting up TransitionManager...")
        transition_manager = TransitionManager(displayer, settings)
        
        # Enable file monitoring
        transition_manager.set_text_file_monitoring(text_file)
        
        # Set up callback for logging
        def on_text_change(block_index):
            status = transition_manager.get_status()
            print(f"Text changed to block {block_index} at frame {status['frame_count']}")
        
        transition_manager.on_text_change = on_text_change
        
        # Start initial display
        transition_manager.start_initial_display()
        
        # Apply enum-based settings to displayer and transition manager
        print("Applying settings...")
        settings.apply_to_displayer(displayer)
        settings.apply_to_transition_manager(transition_manager)
        
        # Optional: Save settings to file for future use
        settings.save_to_file("config/user_settings.json")
        
        # You can also demonstrate different color schemes and transition modes:
        print("\nDemonstrating enum-based color scheme changes:")
        print(f"Available color schemes: {', '.join(ColorScheme.list_names())}")
        print(f"Available transition modes: {', '.join(TransitionMode.list_names())}")
        
        print("Starting main loop...")
        print("Controls:")
        print("  ESC - Exit")
        print("  O - Toggle overlay effects")
        print("  C - Clear overlay effects")
        print("  T - Cycle through color schemes (enum-based)")
        print("  M - Cycle color transition modes (enum-based)")
        print("  S - Save current settings to file")
        print("  L - Load settings from file")
        print("\nNote: All settings now use type-safe enums instead of strings!")
        
        # Run the display with transition manager using settings-based FPS
        displayer.run(fps=settings.display.fps, transition_manager=transition_manager)
            
    except Exception as e:
        print(f"Error in animate_example: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__ == "__main__":
    animate_example()
