"""Commands Tab for Chat Tools Settings GUI.

Dual-pane interface for creating and managing custom chat commands.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, Any, Optional


class CommandsTab:
    """Chat commands configuration tab.
    
    Provides UI for creating/editing custom commands that users can trigger in chat.
    Commands have triggers, responses, permission levels, and cooldowns.
    """
    
    def __init__(
        self,
        parent_frame: ttk.Notebook,
        on_command_selected_callback: Callable[[Any], None],
        add_command_callback: Callable[[], None],
        remove_command_callback: Callable[[], None],
        save_command_callback: Callable[[], None]
    ) -> None:
        """Initialize the commands tab.
        
        Args:
            parent_frame: The notebook widget to add this tab to
            on_command_selected_callback: Called when a command is selected from list
            add_command_callback: Called when Add Command button is clicked
            remove_command_callback: Called when Remove Selected button is clicked
            save_command_callback: Called when Save Command button is clicked
        """
        self.frame = tk.Frame(parent_frame)
        parent_frame.add(self.frame, text="Commands")
        
        self.on_command_selected_callback = on_command_selected_callback
        self.add_command_callback = add_command_callback
        self.remove_command_callback = remove_command_callback
        self.save_command_callback = save_command_callback
        
        # Editor state variables
        self.cmd_permission_var: Optional[tk.StringVar] = None
        self.cmd_cooldown_var: Optional[tk.IntVar] = None
        self.cmd_enabled_var: Optional[tk.BooleanVar] = None
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create all widgets for the commands tab."""
        # Main container with dual pane layout
        main_container = tk.Frame(self.frame, padx=10, pady=10)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left pane - commands list
        left_pane = tk.Frame(main_container)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        tk.Label(
            left_pane,
            text="Commands",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        # Commands listbox with scrollbar
        list_frame = tk.Frame(left_pane)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.commands_listbox = tk.Listbox(
            list_frame,
            width=25,
            height=20,
            font=("Arial", 10),
            yscrollcommand=scrollbar.set
        )
        self.commands_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.commands_listbox.yview)
        
        self.commands_listbox.bind("<<ListboxSelect>>", self.on_command_selected_callback)
        
        # List control buttons
        list_btn_frame = tk.Frame(left_pane)
        list_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            list_btn_frame,
            text="Add Command",
            command=self.add_command_callback,
            font=("Arial", 9),
            bg="#4CAF50",
            fg="white"
        ).pack(fill=tk.X, pady=(0, 5))
        
        tk.Button(
            list_btn_frame,
            text="Remove Selected",
            command=self.remove_command_callback,
            font=("Arial", 9),
            bg="#F44336",
            fg="white"
        ).pack(fill=tk.X)
        
        # Right pane - command editor
        right_pane = tk.Frame(main_container)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            right_pane,
            text="Command Editor",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Command name
        tk.Label(
            right_pane,
            text="Command Name:",
            font=("Arial", 10)
        ).pack(anchor="w", pady=(5, 2))
        
        self.cmd_name_entry = tk.Entry(
            right_pane,
            font=("Arial", 10),
            width=40
        )
        self.cmd_name_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Triggers
        tk.Label(
            right_pane,
            text="Triggers (space-separated, e.g., !discord !dc !server):",
            font=("Arial", 10)
        ).pack(anchor="w", pady=(5, 2))
        
        self.cmd_triggers_entry = tk.Entry(
            right_pane,
            font=("Arial", 10),
            width=40
        )
        self.cmd_triggers_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Response
        tk.Label(
            right_pane,
            text="Response:",
            font=("Arial", 10)
        ).pack(anchor="w", pady=(5, 2))
        
        self.cmd_response_text = scrolledtext.ScrolledText(
            right_pane,
            font=("Arial", 10),
            height=6,
            wrap=tk.WORD
        )
        self.cmd_response_text.pack(fill=tk.X, pady=(0, 10))
        
        # Permission level
        tk.Label(
            right_pane,
            text="Permission Level:",
            font=("Arial", 10)
        ).pack(anchor="w", pady=(5, 2))
        
        self.cmd_permission_var = tk.StringVar(value="everyone")
        
        perm_frame = tk.Frame(right_pane)
        perm_frame.pack(anchor="w", pady=(0, 10))
        
        tk.Radiobutton(
            perm_frame,
            text="Streamer Only",
            variable=self.cmd_permission_var,
            value="streamer",
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Radiobutton(
            perm_frame,
            text="Mods Only",
            variable=self.cmd_permission_var,
            value="mods",
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Radiobutton(
            perm_frame,
            text="Everyone",
            variable=self.cmd_permission_var,
            value="everyone",
            font=("Arial", 9)
        ).pack(side=tk.LEFT)
        
        # Cooldown
        cooldown_frame = tk.Frame(right_pane)
        cooldown_frame.pack(anchor="w", pady=(5, 10))
        
        tk.Label(
            cooldown_frame,
            text="Cooldown (seconds):",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.cmd_cooldown_var = tk.IntVar(value=30)
        
        tk.Spinbox(
            cooldown_frame,
            from_=0,
            to=3600,
            textvariable=self.cmd_cooldown_var,
            font=("Arial", 10),
            width=10
        ).pack(side=tk.LEFT)
        
        # Enabled checkbox
        self.cmd_enabled_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(
            right_pane,
            text="Enabled",
            variable=self.cmd_enabled_var,
            font=("Arial", 10)
        ).pack(anchor="w", pady=(5, 15))
        
        # Save command button
        tk.Button(
            right_pane,
            text="Save Command",
            command=self.save_command_callback,
            font=("Arial", 10, "bold"),
            bg="#2196F3",
            fg="white",
            width=20
        ).pack(anchor="w")
