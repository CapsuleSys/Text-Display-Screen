"""
Button factory for creating styled tkinter buttons.

Provides reusable button creation functions with consistent styling across
the application's GUI components.
"""

import tkinter as tk
from typing import Callable, Optional


def create_primary_button(
    parent: tk.Widget,
    text: str,
    command: Callable,
    width: int = 20,
    font: tuple = ("Arial", 10, "bold")
) -> tk.Button:
    """Create a primary action button (green, for save/confirm actions).
    
    Args:
        parent: Parent widget
        text: Button text
        command: Button click callback
        width: Button width in characters
        font: Font tuple (family, size, weight)
        
    Returns:
        Configured button widget
    """
    return tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        font=font,
        bg="#4CAF50",
        fg="white"
    )


def create_danger_button(
    parent: tk.Widget,
    text: str,
    command: Callable,
    width: int = 20,
    font: tuple = ("Arial", 9)
) -> tk.Button:
    """Create a danger action button (red, for delete/remove actions).
    
    Args:
        parent: Parent widget
        text: Button text
        command: Button click callback
        width: Button width in characters
        font: Font tuple (family, size, weight)
        
    Returns:
        Configured button widget
    """
    return tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        font=font,
        bg="#F44336",
        fg="white"
    )


def create_warning_button(
    parent: tk.Widget,
    text: str,
    command: Callable,
    width: int = 15,
    font: tuple = ("Arial", 10)
) -> tk.Button:
    """Create a warning action button (orange, for test/caution actions).
    
    Args:
        parent: Parent widget
        text: Button text
        command: Button click callback
        width: Button width in characters
        font: Font tuple (family, size, weight)
        
    Returns:
        Configured button widget
    """
    return tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        font=font,
        bg="#FFA500",
        fg="white"
    )


def create_info_button(
    parent: tk.Widget,
    text: str,
    command: Callable,
    width: int = 20,
    font: tuple = ("Arial", 10, "bold")
) -> tk.Button:
    """Create an info action button (blue, for edit/modify actions).
    
    Args:
        parent: Parent widget
        text: Button text
        command: Button click callback
        width: Button width in characters
        font: Font tuple (family, size, weight)
        
    Returns:
        Configured button widget
    """
    return tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        font=font,
        bg="#2196F3",
        fg="white"
    )


def create_neutral_button(
    parent: tk.Widget,
    text: str,
    command: Callable,
    width: int = 15,
    font: tuple = ("Arial", 10)
) -> tk.Button:
    """Create a neutral action button (default styling).
    
    Args:
        parent: Parent widget
        text: Button text
        command: Button click callback
        width: Button width in characters
        font: Font tuple (family, size, weight)
        
    Returns:
        Configured button widget
    """
    return tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        font=font
    )


def create_link_label(
    parent: tk.Widget,
    text: str,
    url: str,
    row: int,
    column: int,
    font: tuple = ("Arial", 8, "underline"),
    **grid_kwargs
) -> tk.Label:
    """Create a clickable hyperlink label.
    
    Args:
        parent: Parent widget
        text: Link text
        url: URL to open when clicked
        row: Grid row position
        column: Grid column position
        font: Font tuple (family, size, style)
        **grid_kwargs: Additional grid() parameters
        
    Returns:
        Configured label widget
    """
    import webbrowser
    
    label = tk.Label(
        parent,
        text=text,
        font=font,
        fg="blue",
        cursor="hand2"
    )
    label.grid(row=row, column=column, **grid_kwargs)
    label.bind("<Button-1>", lambda e: webbrowser.open(url))
    return label
