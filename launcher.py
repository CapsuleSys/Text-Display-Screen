"""
Stream Tools Launcher

GUI launcher for Twitch stream management tools. Provides menu-based access
to various stream utilities including text display, chat tools, and more.
"""

import subprocess
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, Scrollbar, Canvas
from pathlib import Path
from typing import NamedTuple, Callable


class StreamTool(NamedTuple):
    """Definition for a launchable stream tool."""
    name: str
    description: str
    launch_function: Callable[[], None]
    settings_function: Callable[[], None]


class StreamToolsLauncher:
    """Main launcher window for stream management tools."""
    
    def __init__(self) -> None:
        """Initialise the launcher GUI."""
        self.root = tk.Tk()
        self.root.title("Stream Tools Launcher")
        self.root.geometry("700x400")
        self.root.resizable(True, True)
        
        # Ensure config directory exists
        config_dir = Path(__file__).parent / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Use venv Python if available
        venv_python = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
        self.python_exe = str(venv_python) if venv_python.exists() else sys.executable
        
        # Define available tools
        self.tools = [
            StreamTool(
                name="Screen Display",
                description=(
                    "Launches the text display window (shows text with visual effects and "
                    "colour schemes) alongside the settings GUI (configure display size, effects, "
                    "transitions, and colour schemes). Both windows work together - changes in "
                    "settings automatically update the display.\n\n"
                    "Perfect for: BRB screens, Welcome screens, Stream's Over screens, and "
                    "custom backgrounds."
                ),
                launch_function=self.launch_text_display,
                settings_function=self.open_screen_display_settings
            ),
            StreamTool(
                name="Chat Tools",
                description=(
                    "Tools for managing Twitch chat including moderation, custom commands, "
                    "and chat interactions.\n\n"
                    "(Coming soon)"
                ),
                launch_function=self.launch_chat_tools,
                settings_function=self.open_chat_tools_settings
            ),
        ]
        
        self._create_ui()
    
    def _create_ui(self) -> None:
        """Create the launcher UI components."""
        # Title label
        title_label = tk.Label(
            self.root,
            text="Stream Tools Launcher",
            font=("Arial", 16, "bold"),
            pady=15
        )
        title_label.pack()
        
        # Create scrollable frame for tools list
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas with scrollbar
        canvas = Canvas(canvas_frame, highlightthickness=0)
        scrollbar = Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create tool rows
        for tool in self.tools:
            self._create_tool_row(scrollable_frame, tool)
        
        # Exit button at bottom
        exit_btn = tk.Button(
            self.root,
            text="Exit",
            command=self.root.quit,
            width=15,
            height=1,
            font=("Arial", 10)
        )
        exit_btn.pack(pady=10)
    
    def _create_tool_row(self, parent: tk.Frame, tool: StreamTool) -> None:
        """Create a row for a single tool with launch and help buttons."""
        row_frame = tk.Frame(parent, relief=tk.RAISED, borderwidth=1, pady=8, padx=10)
        row_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Tool name label
        name_label = tk.Label(
            row_frame,
            text=tool.name,
            font=("Arial", 11),
            anchor="w"
        )
        name_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Help button
        help_btn = tk.Button(
            row_frame,
            text="?",
            command=lambda: self._show_tool_help(tool),
            width=3,
            height=1,
            font=("Arial", 10, "bold")
        )
        help_btn.pack(side=tk.RIGHT, padx=5)
        
        # Launch button
        launch_btn = tk.Button(
            row_frame,
            text="LAUNCH",
            command=tool.launch_function,
            width=10,
            height=1,
            font=("Arial", 10, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049"
        )
        launch_btn.pack(side=tk.RIGHT, padx=5)
        
        # Settings button
        settings_btn = tk.Button(
            row_frame,
            text="SETTINGS",
            command=tool.settings_function,
            width=10,
            height=1,
            font=("Arial", 10, "bold"),
            bg="#2196F3",
            fg="white",
            activebackground="#0b7dda"
        )
        settings_btn.pack(side=tk.RIGHT, padx=5)
    
    def _show_tool_help(self, tool: StreamTool) -> None:
        """Display help dialog for a tool."""
        messagebox.showinfo(
            f"About: {tool.name}",
            tool.description
        )
    
    def launch_text_display(self) -> None:
        """Launch text display application only."""
        # Launch in separate thread to avoid blocking GUI
        thread = threading.Thread(target=self._launch_text_display_thread)
        thread.daemon = True
        thread.start()
    
    def _launch_text_display_thread(self) -> None:
        """Thread worker for launching text display window."""
        main_app_path = Path(__file__).parent / "example_usage.py"
        
        try:
            # Launch main display application
            subprocess.Popen([
                self.python_exe,
                str(main_app_path)
            ], cwd=str(Path(__file__).parent))
            
            print("Screen Display launched successfully")
            
        except Exception as e:
            print(f"Failed to launch screen display: {e}")
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Launch Error",
                    f"Failed to launch Screen Display:\n{e}"
                )
            )
    
    def open_screen_display_settings(self) -> None:
        """Open settings GUI for screen display."""
        # Launch in separate thread to avoid blocking GUI
        thread = threading.Thread(target=self._open_screen_display_settings_thread)
        thread.daemon = True
        thread.start()
    
    def _open_screen_display_settings_thread(self) -> None:
        """Thread worker for launching settings GUI."""
        settings_gui_path = Path(__file__).parent / "settings_gui.py"
        
        try:
            # Launch settings GUI
            subprocess.Popen([
                self.python_exe,
                str(settings_gui_path)
            ], cwd=str(Path(__file__).parent))
            
            print("Screen Display Settings launched successfully")
            
        except Exception as e:
            print(f"Failed to launch settings: {e}")
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Launch Error",
                    f"Failed to launch Settings:\n{e}"
                )
            )
    
    def launch_chat_tools(self) -> None:
        """Launch chat tools application."""
        # Launch in separate thread to avoid blocking GUI
        thread = threading.Thread(target=self._launch_chat_tools_thread)
        thread.daemon = True
        thread.start()
    
    def _launch_chat_tools_thread(self) -> None:
        """Thread worker for launching chat tools."""
        chat_tools_path = Path(__file__).parent / "chat_tools.py"
        
        try:
            # Launch chat tools application
            subprocess.Popen([
                self.python_exe,
                str(chat_tools_path)
            ], cwd=str(Path(__file__).parent))
            
            print("Chat Tools launched successfully")
            
        except Exception as e:
            print(f"Failed to launch chat tools: {e}")
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Launch Error",
                    f"Failed to launch Chat Tools:\n{e}"
                )
            )
    
    def open_chat_tools_settings(self) -> None:
        """Open configuration for chat tools."""
        # Launch in separate thread to avoid blocking GUI
        thread = threading.Thread(target=self._open_chat_tools_settings_thread)
        thread.daemon = True
        thread.start()
    
    def _open_chat_tools_settings_thread(self) -> None:
        """Thread worker for launching chat tools settings."""
        settings_path = Path(__file__).parent / "chat_tools_settings.py"
        
        try:
            # Launch chat tools settings
            subprocess.Popen([
                self.python_exe,
                str(settings_path)
            ], cwd=str(Path(__file__).parent))
            
            print("Chat Tools Settings launched successfully")
            
        except Exception as e:
            print(f"Failed to launch chat tools settings: {e}")
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Launch Error",
                    f"Failed to launch Chat Tools Settings:\n{e}"
                )
            )
    
    def run(self) -> None:
        """Start the launcher GUI main loop."""
        self.root.mainloop()


def main() -> None:
    """Main entry point for stream tools launcher."""
    try:
        launcher = StreamToolsLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\nLauncher interrupted by user.")
    except Exception as e:
        print(f"Error starting launcher: {e}")


if __name__ == "__main__":
    main()