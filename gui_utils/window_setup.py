"""
Base window setup utilities for tkinter applications.

Provides common window configuration patterns used across GUI components.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Literal


def setup_window(
    root: tk.Tk,
    title: str,
    width: int = 600,
    height: int = 650,
    resizable: bool = True,
    topmost: bool = False
) -> None:
    """Configure a tkinter window with standard settings.
    
    Args:
        root: Root window to configure
        title: Window title
        width: Window width in pixels
        height: Window height in pixels
        resizable: Whether window can be resized
        topmost: Whether window stays on top of others
    """
    root.title(title)
    root.geometry(f"{width}x{height}")
    root.resizable(resizable, resizable)
    root.attributes('-topmost', topmost)


def create_title_label(
    parent: tk.Widget,
    text: str,
    font: tuple = ("Arial", 16, "bold"),
    pady: int = 15
) -> tk.Label:
    """Create a title label for the top of a window.
    
    Args:
        parent: Parent widget
        text: Title text
        font: Font tuple (family, size, weight)
        pady: Vertical padding
        
    Returns:
        Configured label widget
    """
    label = tk.Label(
        parent,
        text=text,
        font=font,
        pady=pady
    )
    label.pack()
    return label


def create_tabbed_notebook(
    parent: tk.Widget,
    fill: Literal['none', 'x', 'y', 'both'] = 'both',
    expand: bool = True,
    padx: int = 10,
    pady: tuple | int = (0, 10)
) -> ttk.Notebook:
    """Create a ttk Notebook for tabbed interfaces.
    
    Args:
        parent: Parent widget
        fill: Fill direction (tk.BOTH, tk.X, tk.Y, or tk.NONE)
        expand: Whether to expand to fill available space
        padx: Horizontal padding
        pady: Vertical padding (can be int or tuple)
        
    Returns:
        Configured notebook widget
    """
    notebook = ttk.Notebook(parent)
    notebook.pack(fill=fill, expand=expand, padx=padx, pady=pady)
    return notebook


def create_button_row(
    parent: tk.Widget,
    pady: int = 10
) -> tk.Frame:
    """Create a frame for holding a row of buttons.
    
    Args:
        parent: Parent widget
        pady: Vertical padding
        
    Returns:
        Frame configured for button layout
    """
    frame = tk.Frame(parent, pady=pady)
    frame.pack()
    return frame


def create_status_label(
    parent: tk.Widget,
    initial_text: str = "Ready",
    font: tuple = ("Arial", 9),
    fg: str = "grey"
) -> tk.Label:
    """Create a status label for displaying messages.
    
    Args:
        parent: Parent widget
        initial_text: Initial status text
        font: Font tuple (family, size)
        fg: Foreground colour
        
    Returns:
        Configured label widget
    """
    label = tk.Label(
        parent,
        text=initial_text,
        font=font,
        fg=fg
    )
    label.pack(pady=5)
    return label


def configure_grid_weights(
    widget: tk.Widget,
    rows: Optional[list[int]] = None,
    columns: Optional[list[int]] = None,
    row_weight: int = 1,
    column_weight: int = 1
) -> None:
    """Configure grid row and column weights for a widget.
    
    Args:
        widget: Widget to configure
        rows: List of row indices to configure (None = row 0)
        columns: List of column indices to configure (None = column 0)
        row_weight: Weight to assign to rows
        column_weight: Weight to assign to columns
    """
    if rows is None:
        rows = [0]
    if columns is None:
        columns = [0]
    
    for row in rows:
        widget.grid_rowconfigure(row, weight=row_weight)
    
    for column in columns:
        widget.grid_columnconfigure(column, weight=column_weight)
