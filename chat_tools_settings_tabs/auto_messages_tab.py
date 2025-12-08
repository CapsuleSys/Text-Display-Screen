"""Auto Messages Tab for Chat Tools Settings GUI.

Configure automated messages that post at regular intervals.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, Any, Optional


class AutoMessagesTab:
    """Auto messages configuration tab.
    
    Provides UI for creating/editing automated messages that post at intervals.
    Includes global settings and per-message configuration.
    """
    
    def __init__(
        self,
        parent_frame: ttk.Notebook,
        on_message_selected_callback: Callable[[Any], None],
        add_message_callback: Callable[[], None],
        remove_message_callback: Callable[[], None],
        save_message_callback: Callable[[], None]
    ) -> None:
        """Initialize the auto messages tab.
        
        Args:
            parent_frame: The notebook widget to add this tab to
            on_message_selected_callback: Called when a message is selected from list
            add_message_callback: Called when Add Message button is clicked
            remove_message_callback: Called when Remove Selected button is clicked
            save_message_callback: Called when Save Message button is clicked
        """
        self.frame = tk.Frame(parent_frame)
        parent_frame.add(self.frame, text="Auto Messages")
        
        self.on_message_selected_callback = on_message_selected_callback
        self.add_message_callback = add_message_callback
        self.remove_message_callback = remove_message_callback
        self.save_message_callback = save_message_callback
        
        # Global settings variables
        self.auto_msg_master_enabled_var: Optional[tk.BooleanVar] = None
        self.auto_msg_interval_var: Optional[tk.IntVar] = None
        self.auto_msg_min_activity_var: Optional[tk.IntVar] = None
        self.auto_msg_activity_window_var: Optional[tk.IntVar] = None
        self.auto_msg_random_var: Optional[tk.BooleanVar] = None
        
        # Per-message settings variables
        self.msg_enabled_var: Optional[tk.BooleanVar] = None
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create all widgets for the auto messages tab."""
        # Main container with dual pane layout
        main_container = tk.Frame(self.frame, padx=10, pady=10)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left pane - messages list
        left_pane = tk.Frame(main_container)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        tk.Label(
            left_pane,
            text="Auto Messages",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        # Messages listbox with scrollbar
        list_frame = tk.Frame(left_pane)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.messages_listbox = tk.Listbox(
            list_frame,
            width=25,
            height=12,
            font=("Arial", 10),
            yscrollcommand=scrollbar.set
        )
        self.messages_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.messages_listbox.yview)
        
        self.messages_listbox.bind("<<ListboxSelect>>", self.on_message_selected_callback)
        
        # List control buttons
        list_btn_frame = tk.Frame(left_pane)
        list_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            list_btn_frame,
            text="Add Message",
            command=self.add_message_callback,
            font=("Arial", 9),
            bg="#4CAF50",
            fg="white"
        ).pack(fill=tk.X, pady=(0, 5))
        
        tk.Button(
            list_btn_frame,
            text="Remove Selected",
            command=self.remove_message_callback,
            font=("Arial", 9),
            bg="#F44336",
            fg="white"
        ).pack(fill=tk.X)
        
        # Right pane - message editor + global settings
        right_pane = tk.Frame(main_container)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Global settings section
        global_frame = tk.LabelFrame(
            right_pane,
            text="Global Settings",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=10
        )
        global_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Master enable
        self.auto_msg_master_enabled_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(
            global_frame,
            text="Enable Auto Messages",
            variable=self.auto_msg_master_enabled_var,
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Post interval
        interval_frame = tk.Frame(global_frame)
        interval_frame.pack(anchor="w", pady=(0, 10))
        
        tk.Label(
            interval_frame,
            text="Post Interval:",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.auto_msg_interval_var = tk.IntVar(value=20)
        
        tk.Spinbox(
            interval_frame,
            from_=1,
            to=180,
            textvariable=self.auto_msg_interval_var,
            font=("Arial", 10),
            width=8
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Label(
            interval_frame,
            text="minutes",
            font=("Arial", 9)
        ).pack(side=tk.LEFT)
        
        tk.Label(
            global_frame,
            text="(How often to post an auto-message)",
            font=("Arial", 8),
            fg="grey"
        ).pack(anchor="w", pady=(0, 10))
        
        # Activity threshold
        activity_frame = tk.Frame(global_frame)
        activity_frame.pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            activity_frame,
            text="Minimum Chat Activity:",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.auto_msg_min_activity_var = tk.IntVar(value=5)
        
        tk.Spinbox(
            activity_frame,
            from_=0,
            to=100,
            textvariable=self.auto_msg_min_activity_var,
            font=("Arial", 10),
            width=8
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Label(
            activity_frame,
            text="messages",
            font=("Arial", 9)
        ).pack(side=tk.LEFT)
        
        # Activity window
        window_frame = tk.Frame(global_frame)
        window_frame.pack(anchor="w", pady=(0, 5))
        
        tk.Label(
            window_frame,
            text="Activity Window:",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.auto_msg_activity_window_var = tk.IntVar(value=5)
        
        tk.Spinbox(
            window_frame,
            from_=1,
            to=60,
            textvariable=self.auto_msg_activity_window_var,
            font=("Arial", 10),
            width=8
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Label(
            window_frame,
            text="minutes",
            font=("Arial", 9)
        ).pack(side=tk.LEFT)
        
        tk.Label(
            global_frame,
            text="(Skip auto-message if fewer than X messages in last Y minutes)",
            font=("Arial", 8),
            fg="grey"
        ).pack(anchor="w", pady=(0, 10))
        
        # Selection mode
        tk.Label(
            global_frame,
            text="Selection Mode:",
            font=("Arial", 10)
        ).pack(anchor="w", pady=(5, 2))
        
        self.auto_msg_random_var = tk.BooleanVar(value=True)
        
        mode_frame = tk.Frame(global_frame)
        mode_frame.pack(anchor="w", pady=(0, 5))
        
        tk.Radiobutton(
            mode_frame,
            text="Random",
            variable=self.auto_msg_random_var,
            value=True,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Radiobutton(
            mode_frame,
            text="Sequential",
            variable=self.auto_msg_random_var,
            value=False,
            font=("Arial", 9)
        ).pack(side=tk.LEFT)
        
        # Message editor section
        editor_frame = tk.LabelFrame(
            right_pane,
            text="Message Editor",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=10
        )
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Message text
        tk.Label(
            editor_frame,
            text="Message Text:",
            font=("Arial", 10)
        ).pack(anchor="w", pady=(0, 2))
        
        self.msg_text = scrolledtext.ScrolledText(
            editor_frame,
            font=("Arial", 10),
            height=6,
            wrap=tk.WORD
        )
        self.msg_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Enabled checkbox
        self.msg_enabled_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(
            editor_frame,
            text="Enabled",
            variable=self.msg_enabled_var,
            font=("Arial", 10)
        ).pack(anchor="w", pady=(5, 15))
        
        # Save message button
        tk.Button(
            editor_frame,
            text="Save Message",
            command=self.save_message_callback,
            font=("Arial", 10, "bold"),
            bg="#2196F3",
            fg="white",
            width=20
        ).pack(anchor="w")
