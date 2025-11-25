"""
Dual Launch System for Text Display Screen

Launches both the main display application and the settings GUI simultaneously
as independent windows. Provides coordinated startup and settings synchronization.
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path


def launch_settings_gui():
    """Launch the settings GUI application."""
    settings_gui_path = Path(__file__).parent / "settings_gui.py"
    
    try:
        # Launch settings GUI as separate process
        subprocess.Popen([
            sys.executable, 
            str(settings_gui_path)
        ], cwd=str(Path(__file__).parent))
        print("Settings GUI launched successfully")
        return True
    except Exception as e:
        print(f"Failed to launch settings GUI: {e}")
        return False


def launch_main_application():
    """Launch the main display application."""
    main_app_path = Path(__file__).parent / "example_usage.py"
    
    try:
        # Small delay to let settings GUI start first
        time.sleep(1)
        
        # Launch main application as separate process
        subprocess.Popen([
            sys.executable,
            str(main_app_path)
        ], cwd=str(Path(__file__).parent))
        print("Main application launched successfully")
        return True
    except Exception as e:
        print(f"Failed to launch main application: {e}")
        return False


def launch_both_applications():
    """Launch both applications simultaneously."""
    print("Starting Text Display Screen with Settings GUI...")
    
    # Ensure config directory exists
    config_dir = Path(__file__).parent / "config"
    config_dir.mkdir(exist_ok=True)
    
    # Launch settings GUI first (it will create default settings if needed)
    settings_success = launch_settings_gui()
    
    if settings_success:
        # Launch main application in a separate thread with delay
        main_thread = threading.Thread(target=launch_main_application)
        main_thread.daemon = True  # Will exit when main program exits
        main_thread.start()
        
        print("\nBoth applications starting...")
        print("- Settings GUI: Configure display settings, effects, and parameters")
        print("- Main Display: Shows text with visual effects")
        print("\nBoth windows are independent - you can minimize, resize, or close them separately.")
        print("Settings changes are automatically saved and will be applied to the main display.")
        
        # Keep this script running briefly to show messages
        time.sleep(3)
        print("Dual launch completed. Applications are now running independently.")
        
    else:
        print("Failed to start applications. Please check for errors above.")


def main():
    """Main entry point for dual launch."""
    try:
        launch_both_applications()
    except KeyboardInterrupt:
        print("\nLaunch interrupted by user.")
    except Exception as e:
        print(f"Error during dual launch: {e}")


if __name__ == "__main__":
    main()