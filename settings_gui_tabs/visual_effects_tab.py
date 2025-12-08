"""
Visual Effects tab for Settings GUI.

Handles overlay effects, colour schemes, ghost and flicker parameters.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable
from config.enums import ColourScheme, TransitionMode


class VisualEffectsTab:
    """Visual effects tab content and logic."""
    
    def __init__(
        self,
        parent_frame: ttk.Frame,
        settings,
        create_slider_callback: Callable,
        bind_widget_callback: Callable
    ):
        """Initialise the visual effects tab.
        
        Args:
            parent_frame: Parent ttk.Frame to contain tab content
            settings: Settings instance
            create_slider_callback: Callback for creating sliders
            bind_widget_callback: Callback for binding widgets to settings
        """
        self.frame = parent_frame
        self.settings = settings
        self._create_slider = create_slider_callback
        self._bind_widget = bind_widget_callback
        
        self.overlay_enabled_var = None
        self.colour_scheme_var = None
        self.transition_mode_var = None
        self.ghost_chance_var = None
        self.ghost_decay_var = None
        self.flicker_chance_var = None
        self.enable_colour_averaging_var = None
        self.colour_averaging_interval_var = None
        
        self._create_content()
    
    def _create_content(self) -> None:
        """Create the tab content."""
        row = 0
        
        # Overlay Enabled
        self.overlay_enabled_var = tk.BooleanVar(
            value=self.settings.overlay.overlay_enabled
        )
        overlay_check = ttk.Checkbutton(
            self.frame,
            text="Enable Overlay Effects",
            variable=self.overlay_enabled_var
        )
        overlay_check.grid(row=row, column=0, columnspan=2, 
                          sticky="w", padx=5, pady=5)
        self._bind_widget(overlay_check, "overlay.overlay_enabled", bool)
        row += 1
        
        # Colour Scheme
        ttk.Label(self.frame, text="Colour Scheme:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5)
        self.colour_scheme_var = tk.StringVar(
            value=self.settings.overlay.colour_scheme.value
        )
        colour_schemes = ColourScheme.list_names()
        colour_combo = ttk.Combobox(
            self.frame,
            textvariable=self.colour_scheme_var,
            values=colour_schemes,
            width=20,
            state="readonly"
        )
        colour_combo.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        self._bind_widget(colour_combo, "overlay.colour_scheme", 
                         ColourScheme.from_string)
        row += 1
        
        # Transition Mode
        ttk.Label(self.frame, text="Transition Mode:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5)
        self.transition_mode_var = tk.StringVar(
            value=self.settings.overlay.colour_transition_mode.value
        )
        transition_modes = TransitionMode.list_names()
        transition_combo = ttk.Combobox(
            self.frame,
            textvariable=self.transition_mode_var,
            values=transition_modes,
            width=20,
            state="readonly"
        )
        transition_combo.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        self._bind_widget(transition_combo, "overlay.colour_transition_mode",
                         TransitionMode.from_string)
        row += 1
        
        # Ghost Parameters Section
        ttk.Separator(self.frame, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=10)
        row += 1
        ttk.Label(self.frame, text="Ghost Effect Parameters",
                 font=("TkDefaultFont", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        row += 1
        
        # Ghost Chance
        self.ghost_chance_var = tk.DoubleVar(
            value=self.settings.overlay.ghost_chance
        )
        row = self._create_slider(
            self.frame, row, "Ghost Chance:",
            self.ghost_chance_var, 0.0, 1.0,
            "overlay.ghost_chance", float
        )
        
        # Ghost Decay
        self.ghost_decay_var = tk.DoubleVar(
            value=self.settings.overlay.ghost_decay
        )
        row = self._create_slider(
            self.frame, row, "Ghost Decay:",
            self.ghost_decay_var, 0.9, 1.0,
            "overlay.ghost_decay", float
        )
        
        # Flicker Parameters Section
        ttk.Separator(self.frame, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=10)
        row += 1
        ttk.Label(self.frame, text="Flicker Effect Parameters",
                 font=("TkDefaultFont", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        row += 1
        
        # Flicker Chance
        self.flicker_chance_var = tk.DoubleVar(
            value=self.settings.overlay.flicker_chance
        )
        row = self._create_slider(
            self.frame, row, "Flicker Chance:",
            self.flicker_chance_var, 0.0, 0.2,
            "overlay.flicker_chance", float
        )
        
        # Colour Averaging Section
        ttk.Separator(self.frame, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=10)
        row += 1
        ttk.Label(self.frame,
                 text="Colour Averaging (works with all transition modes)",
                 font=("TkDefaultFont", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        row += 1
        
        # Enable Colour Averaging
        self.enable_colour_averaging_var = tk.BooleanVar(
            value=self.settings.overlay.enable_colour_averaging
        )
        colour_averaging_check = ttk.Checkbutton(
            self.frame,
            text="Enable colour averaging (ghosts blend with neighbours)",
            variable=self.enable_colour_averaging_var
        )
        colour_averaging_check.grid(row=row, column=0, columnspan=2,
                                   sticky="w", padx=5, pady=5)
        self._bind_widget(colour_averaging_check,
                         "overlay.enable_colour_averaging", bool)
        row += 1
        
        # Colour Averaging Interval
        ttk.Label(self.frame, text="Averaging Interval (frames):").grid(
            row=row, column=0, sticky="w", padx=5, pady=5)
        self.colour_averaging_interval_var = tk.IntVar(
            value=self.settings.overlay.colour_averaging_interval
        )
        colour_averaging_scale = ttk.Scale(
            self.frame,
            from_=10,
            to=180,
            orient="horizontal",
            variable=self.colour_averaging_interval_var,
            length=200
        )
        colour_averaging_scale.grid(row=row, column=1, 
                                   sticky="w", padx=5, pady=5)
        colour_averaging_label = ttk.Label(self.frame, text="")
        colour_averaging_label.grid(row=row, column=2, sticky="w", padx=5)
        
        def update_colour_averaging_label(*args):
            try:
                frames = self.colour_averaging_interval_var.get()
                seconds = frames / 60  # Assuming 60 FPS
                colour_averaging_label.config(
                    text=f"{frames} ({seconds:.2f}s @ 60fps)"
                )
            except (tk.TclError, ValueError):
                colour_averaging_label.config(text="30 (0.50s @ 60fps)")
        
        self.colour_averaging_interval_var.trace_add(
            'write', update_colour_averaging_label
        )
        update_colour_averaging_label()
        
        self._bind_widget(colour_averaging_scale,
                         "overlay.colour_averaging_interval", int)
        row += 1
        
        ttk.Label(
            self.frame,
            text="Ghost colours periodically update to match average of 5x5 neighbours",
            font=("TkDefaultFont", 8),
            foreground="grey"
        ).grid(row=row, column=0, columnspan=3, sticky="w", padx=5, pady=(0, 5))
        row += 1
