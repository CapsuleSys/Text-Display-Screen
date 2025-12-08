"""
Dual-pane layout helper for list+editor interfaces.

Provides a reusable pattern for creating interfaces with a list on the left
and an editor pane on the right, commonly used in commands and auto messages tabs.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class DualPaneLayout:
    """Creates a dual-pane layout with list on left and editor on right."""
    
    def __init__(
        self,
        parent: tk.Widget,
        list_title: str,
        list_width: int = 25,
        list_height: int = 20,
        add_button_text: str = "Add Item",
        remove_button_text: str = "Remove Selected",
        on_add: Optional[Callable] = None,
        on_remove: Optional[Callable] = None,
        on_select: Optional[Callable] = None
    ):
        """Initialise the dual-pane layout.
        
        Args:
            parent: Parent widget to contain the layout
            list_title: Title text above the list
            list_width: Width of the listbox in characters
            list_height: Height of the listbox in lines
            add_button_text: Text for add button
            remove_button_text: Text for remove button
            on_add: Callback when add button clicked
            on_remove: Callback when remove button clicked
            on_select: Callback when list item selected
        """
        self.parent = parent
        self.on_add = on_add
        self.on_remove = on_remove
        self.on_select = on_select
        
        # Main container
        self.container = tk.Frame(parent, padx=10, pady=10)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Left pane - list
        self.left_pane = tk.Frame(self.container)
        self.left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        # List title
        tk.Label(
            self.left_pane,
            text=list_title,
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        # Listbox with scrollbar
        list_frame = tk.Frame(self.left_pane)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(
            list_frame,
            width=list_width,
            height=list_height,
            font=("Arial", 10),
            yscrollcommand=scrollbar.set
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Bind selection event
        if on_select:
            self.listbox.bind("<<ListboxSelect>>", lambda e: on_select())
        
        # List control buttons
        button_frame = tk.Frame(self.left_pane)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Import button factory here to avoid circular imports
        from gui_utils.button_factory import create_primary_button, create_danger_button
        
        if on_add:
            create_primary_button(
                button_frame,
                text=add_button_text,
                command=on_add,
                width=0,  # Auto width
                font=("Arial", 9)
            ).pack(fill=tk.X, pady=(0, 5))
        
        if on_remove:
            create_danger_button(
                button_frame,
                text=remove_button_text,
                command=on_remove,
                width=0,  # Auto width
                font=("Arial", 9)
            ).pack(fill=tk.X)
        
        # Right pane - editor (to be populated by caller)
        self.right_pane = tk.Frame(self.container)
        self.right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    def get_selected_index(self) -> Optional[int]:
        """Get the index of the currently selected item.
        
        Returns:
            Selected index or None if no selection
        """
        selection = self.listbox.curselection()
        return selection[0] if selection else None
    
    def insert_item(self, text: str, index: Optional[int] = None) -> None:
        """Insert an item into the list.
        
        Args:
            text: Text to display for the item
            index: Position to insert at (None = end)
        """
        if index is None:
            self.listbox.insert(tk.END, text)
        else:
            self.listbox.insert(index, text)
    
    def remove_item(self, index: int) -> None:
        """Remove an item from the list.
        
        Args:
            index: Index of item to remove
        """
        self.listbox.delete(index)
    
    def update_item(self, index: int, text: str) -> None:
        """Update the text of an item.
        
        Args:
            index: Index of item to update
            text: New text for the item
        """
        self.listbox.delete(index)
        self.listbox.insert(index, text)
    
    def clear_items(self) -> None:
        """Remove all items from the list."""
        self.listbox.delete(0, tk.END)
    
    def select_item(self, index: int) -> None:
        """Select an item in the list.
        
        Args:
            index: Index of item to select
        """
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(index)
        self.listbox.see(index)
    
    def get_item_count(self) -> int:
        """Get the number of items in the list.
        
        Returns:
            Item count
        """
        return self.listbox.size()
