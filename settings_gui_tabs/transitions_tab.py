"""Transitions tab for the settings GUI.

This module contains the TransitionsTab class which handles all transition-related
settings including transition speed, text change intervals, blank time, and five
subsections for effect transitions (colour schemes, overlay effects, transition modes,
ghost parameters, and flicker parameters).
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Any


class TransitionsTab:
    """Manages the transitions settings tab.
    
    This tab contains a scrollable canvas with multiple sections:
    1. Transition Speed - Controls how fast pixel transitions occur
    2. Text Change Interval - Time between automatic text block changes
    3. Blank Time - Optional blank display period between transitions
    4. Effect Transitions - Five subsections for transitioning visual effects:
       - Colour scheme transitions (between different colour palettes)
       - Overlay effect transitions (enable/disable effects)
       - Transition mode changes (how colours change)
       - Ghost parameter variations (chance/decay ranges)
       - Flicker parameter variations (chance/intensity ranges)
    """
    
    def __init__(
        self,
        parent_frame: ttk.Frame,
        settings: Any,
        create_slider_callback: Callable,
        bind_widget_callback: Callable
    ):
        """Initialize the transitions tab.
        
        Args:
            parent_frame: The parent frame to place this tab's content in
            settings: The settings object containing all configuration
            create_slider_callback: Callback to create sliders with labels
            bind_widget_callback: Callback to bind widgets to settings
        """
        self.frame = parent_frame
        self.settings = settings
        self._create_slider = create_slider_callback
        self._bind_widget = bind_widget_callback
        
        # Store tkinter variables for widget access
        self.transition_speed_var: tk.DoubleVar
        self.text_change_interval_var: tk.IntVar
        self.blank_time_var: tk.IntVar
        self.transition_colour_scheme_var: tk.BooleanVar
        self.colour_scheme_order_var: tk.StringVar
        self.transition_colour_mode_var: tk.BooleanVar
        self.colour_mode_order_var: tk.StringVar
        self.transition_ghost_params_var: tk.BooleanVar
        self.ghost_params_order_var: tk.StringVar
        self.ghost_chance_min_var: tk.DoubleVar
        self.ghost_chance_max_var: tk.DoubleVar
        self.ghost_decay_min_var: tk.DoubleVar
        self.ghost_decay_max_var: tk.DoubleVar
        self.transition_flicker_params_var: tk.BooleanVar
        self.flicker_params_order_var: tk.StringVar
        self.flicker_chance_min_var: tk.DoubleVar
        self.flicker_chance_max_var: tk.DoubleVar
        self.flicker_intensity_min_var: tk.DoubleVar
        self.flicker_intensity_max_var: tk.DoubleVar
        self.transition_speed_variation_var: tk.BooleanVar
        self.speed_order_var: tk.StringVar
        self.speed_min_var: tk.DoubleVar
        self.speed_max_var: tk.DoubleVar
        
        self._create_content()
    
    def _create_content(self) -> None:
        """Create all the content for the transitions tab."""
        # Create a canvas with scrollbar for the transitions tab
        canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Now use scrollable_frame instead of frame for all content
        frame = scrollable_frame
        row = 0
        
        # Transition Speed
        self.transition_speed_var = tk.DoubleVar(value=self.settings.transition.transition_speed)
        row = self._create_slider(
            frame, row, "Transition Speed (px/frame):",
            self.transition_speed_var, 0.1, 50.0,
            "transition.transition_speed", float, format_str="{:.1f}"
        )
        
        # Text Change Interval
        ttk.Label(frame, text="Text Change Interval (frames):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.text_change_interval_var = tk.IntVar(value=self.settings.transition.text_change_interval)
        text_change_spin = ttk.Spinbox(frame, from_=60, to=18000, textvariable=self.text_change_interval_var, 
                                      width=15)
        text_change_spin.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        
        # Show seconds equivalent
        text_change_seconds_label = ttk.Label(frame, text="")
        text_change_seconds_label.grid(row=row, column=2, sticky="w", padx=5)
        
        def update_text_change_seconds(*args):
            try:
                frames = self.text_change_interval_var.get()
                if frames > 0:
                    seconds = frames / 60  # Assuming 60 FPS
                    text_change_seconds_label.config(text=f"({seconds:.1f}s @ 60fps)")
                else:
                    text_change_seconds_label.config(text="(0.0s @ 60fps)")
            except (tk.TclError, ValueError):
                text_change_seconds_label.config(text="(-- s @ 60fps)")
        self.text_change_interval_var.trace_add('write', update_text_change_seconds)
        update_text_change_seconds()
        
        self._bind_widget(text_change_spin, "transition.text_change_interval", int)
        row += 1
        
        # Blank Time Between Transitions
        ttk.Label(frame, text="Blank Time Between Transitions (frames):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.blank_time_var = tk.IntVar(value=self.settings.transition.blank_time_between_transitions)
        blank_time_scale = ttk.Scale(frame, from_=0, to=600, orient="horizontal",
                                    variable=self.blank_time_var, length=300)
        blank_time_scale.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        blank_time_label = ttk.Label(frame, text="")
        blank_time_label.grid(row=row, column=2, sticky="w", padx=5)
        
        def update_blank_time_label(*args):
            try:
                frames = self.blank_time_var.get()
                seconds = frames / 60  # Assuming 60 FPS
                blank_time_label.config(text=f"{frames} ({seconds:.1f}s @ 60fps)")
            except (tk.TclError, ValueError):
                blank_time_label.config(text="0 (0.0s @ 60fps)")
        self.blank_time_var.trace_add('write', update_blank_time_label)
        update_blank_time_label()
        
        self._bind_widget(blank_time_scale, "transition.blank_time_between_transitions", int)
        row += 1
        
        # Add separator before effect transitions section
        ttk.Separator(frame, orient="horizontal").grid(row=row, column=0, columnspan=3,
                                                       sticky="ew", padx=5, pady=15)
        row += 1
        
        # Effect Transitions Section Header
        ttk.Label(frame, text="Effect Transitions (change effects when text changes)", 
                 font=("TkDefaultFont", 10, "bold")).grid(
            row=row, column=0, columnspan=3, sticky="w", padx=5, pady=5)
        row += 1
        
        # 1. COLOUR SCHEME TRANSITIONS
        colour_scheme_frame = ttk.LabelFrame(frame, text="Colour Scheme Transitions", padding=10)
        colour_scheme_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        row += 1
        
        self.transition_colour_scheme_var = tk.BooleanVar(value=self.settings.transition.transition_colour_scheme)
        colour_scheme_check = ttk.Checkbutton(colour_scheme_frame, 
            text="Also transition colour scheme when text changes",
            variable=self.transition_colour_scheme_var)
        colour_scheme_check.grid(row=0, column=0, columnspan=2, sticky="w", pady=2)
        self._bind_widget(colour_scheme_check, "transition.transition_colour_scheme", bool)
        
        self.colour_scheme_order_var = tk.StringVar(value=self.settings.transition.colour_scheme_order)
        ttk.Radiobutton(colour_scheme_frame, text="Random", variable=self.colour_scheme_order_var, 
                       value="random").grid(row=1, column=0, sticky="w", padx=20)
        ttk.Radiobutton(colour_scheme_frame, text="Sequential", variable=self.colour_scheme_order_var,
                       value="sequential").grid(row=1, column=1, sticky="w")
        self._bind_widget(colour_scheme_frame, "transition.colour_scheme_order", str)
        
        ttk.Label(colour_scheme_frame, text="Cycles through all 23 available colour schemes",
                 font=("TkDefaultFont", 8)).grid(row=2, column=0, columnspan=2, sticky="w", pady=2)
        
        # 2. TRANSITION MODE TRANSITIONS
        colour_mode_frame = ttk.LabelFrame(frame, text="Transition Mode Transitions", padding=10)
        colour_mode_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        row += 1
        
        self.transition_colour_mode_var = tk.BooleanVar(value=self.settings.transition.transition_colour_mode)
        colour_mode_check = ttk.Checkbutton(colour_mode_frame,
            text="Also transition colour transition mode when text changes",
            variable=self.transition_colour_mode_var)
        colour_mode_check.grid(row=0, column=0, columnspan=2, sticky="w", pady=2)
        self._bind_widget(colour_mode_check, "transition.transition_colour_mode", bool)
        
        self.colour_mode_order_var = tk.StringVar(value=self.settings.transition.colour_mode_order)
        ttk.Radiobutton(colour_mode_frame, text="Random", variable=self.colour_mode_order_var,
                       value="random").grid(row=1, column=0, sticky="w", padx=20)
        ttk.Radiobutton(colour_mode_frame, text="Sequential", variable=self.colour_mode_order_var,
                       value="sequential").grid(row=1, column=1, sticky="w")
        self._bind_widget(colour_mode_frame, "transition.colour_mode_order", str)
        
        ttk.Label(colour_mode_frame, text="Cycles through: smooth, snap, mixed, spread_horizontal, spread_vertical",
                 font=("TkDefaultFont", 8)).grid(row=2, column=0, columnspan=2, sticky="w", pady=2)
        
        # 3. GHOST EFFECT TRANSITIONS
        ghost_frame = ttk.LabelFrame(frame, text="Ghost Effect Transitions", padding=10)
        ghost_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        row += 1
        
        self.transition_ghost_params_var = tk.BooleanVar(value=self.settings.transition.transition_ghost_params)
        ghost_check = ttk.Checkbutton(ghost_frame,
            text="Also transition ghost effects when text changes",
            variable=self.transition_ghost_params_var)
        ghost_check.grid(row=0, column=0, columnspan=3, sticky="w", pady=2)
        self._bind_widget(ghost_check, "transition.transition_ghost_params", bool)
        
        self.ghost_params_order_var = tk.StringVar(value=self.settings.transition.ghost_params_order)
        ttk.Radiobutton(ghost_frame, text="Random", variable=self.ghost_params_order_var,
                       value="random").grid(row=1, column=0, sticky="w", padx=20)
        ttk.Radiobutton(ghost_frame, text="Sequential", variable=self.ghost_params_order_var,
                       value="sequential").grid(row=1, column=1, sticky="w")
        self._bind_widget(ghost_frame, "transition.ghost_params_order", str)
        
        # Ghost Chance Min/Max
        self.ghost_chance_min_var = tk.DoubleVar(value=self.settings.transition.ghost_chance_min)
        self._create_slider(
            ghost_frame, 2, "Ghost Chance Min:",
            self.ghost_chance_min_var, 0.0, 1.0,
            "transition.ghost_chance_min", float,
            label_padx=20, pady=2
        )
        
        self.ghost_chance_max_var = tk.DoubleVar(value=self.settings.transition.ghost_chance_max)
        self._create_slider(
            ghost_frame, 3, "Ghost Chance Max:",
            self.ghost_chance_max_var, 0.0, 1.0,
            "transition.ghost_chance_max", float,
            label_padx=20, pady=2
        )
        
        # Ghost Decay Min/Max
        self.ghost_decay_min_var = tk.DoubleVar(value=self.settings.transition.ghost_decay_min)
        self._create_slider(
            ghost_frame, 4, "Ghost Decay Min:",
            self.ghost_decay_min_var, 0.9, 1.0,
            "transition.ghost_decay_min", float,
            format_str="{:.4f}", label_padx=20, pady=2
        )
        
        self.ghost_decay_max_var = tk.DoubleVar(value=self.settings.transition.ghost_decay_max)
        self._create_slider(
            ghost_frame, 5, "Ghost Decay Max:",
            self.ghost_decay_max_var, 0.9, 1.0,
            "transition.ghost_decay_max", float,
            format_str="{:.4f}", label_padx=20, pady=2
        )
        
        ttk.Label(ghost_frame, text="Randomizes ghost parameters within specified ranges",
                 font=("TkDefaultFont", 8)).grid(row=6, column=0, columnspan=3, sticky="w", pady=2)
        
        # 4. FLICKER EFFECT TRANSITIONS
        flicker_frame = ttk.LabelFrame(frame, text="Flicker Effect Transitions", padding=10)
        flicker_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        row += 1
        
        self.transition_flicker_params_var = tk.BooleanVar(value=self.settings.transition.transition_flicker_params)
        flicker_check = ttk.Checkbutton(flicker_frame,
            text="Also transition flicker effects when text changes",
            variable=self.transition_flicker_params_var)
        flicker_check.grid(row=0, column=0, columnspan=3, sticky="w", pady=2)
        self._bind_widget(flicker_check, "transition.transition_flicker_params", bool)
        
        self.flicker_params_order_var = tk.StringVar(value=self.settings.transition.flicker_params_order)
        ttk.Radiobutton(flicker_frame, text="Random", variable=self.flicker_params_order_var,
                       value="random").grid(row=1, column=0, sticky="w", padx=20)
        ttk.Radiobutton(flicker_frame, text="Sequential", variable=self.flicker_params_order_var,
                       value="sequential").grid(row=1, column=1, sticky="w")
        self._bind_widget(flicker_frame, "transition.flicker_params_order", str)
        
        # Flicker Chance Min/Max
        self.flicker_chance_min_var = tk.DoubleVar(value=self.settings.transition.flicker_chance_min)
        self._create_slider(
            flicker_frame, 2, "Flicker Chance Min:",
            self.flicker_chance_min_var, 0.0, 0.2,
            "transition.flicker_chance_min", float,
            label_padx=20, pady=2
        )
        
        self.flicker_chance_max_var = tk.DoubleVar(value=self.settings.transition.flicker_chance_max)
        self._create_slider(
            flicker_frame, 3, "Flicker Chance Max:",
            self.flicker_chance_max_var, 0.0, 0.2,
            "transition.flicker_chance_max", float,
            label_padx=20, pady=2
        )
        
        # Flicker Intensity Min/Max
        self.flicker_intensity_min_var = tk.DoubleVar(value=self.settings.transition.flicker_intensity_min)
        self._create_slider(
            flicker_frame, 4, "Flicker Intensity Min:",
            self.flicker_intensity_min_var, 0.0, 1.0,
            "transition.flicker_intensity_min", float,
            label_padx=20, pady=2
        )
        
        self.flicker_intensity_max_var = tk.DoubleVar(value=self.settings.transition.flicker_intensity_max)
        self._create_slider(
            flicker_frame, 5, "Flicker Intensity Max:",
            self.flicker_intensity_max_var, 0.0, 1.0,
            "transition.flicker_intensity_max", float,
            label_padx=20, pady=2
        )
        
        ttk.Label(flicker_frame, text="Randomizes flicker parameters within specified ranges",
                 font=("TkDefaultFont", 8)).grid(row=6, column=0, columnspan=3, sticky="w", pady=2)
        
        # 5. SPEED VARIATION
        speed_frame = ttk.LabelFrame(frame, text="Speed Variation", padding=10)
        speed_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        row += 1
        
        self.transition_speed_variation_var = tk.BooleanVar(value=self.settings.transition.transition_speed_variation)
        speed_variation_check = ttk.Checkbutton(speed_frame,
            text="Also vary transition speed when text changes",
            variable=self.transition_speed_variation_var)
        speed_variation_check.grid(row=0, column=0, columnspan=3, sticky="w", pady=2)
        self._bind_widget(speed_variation_check, "transition.transition_speed_variation", bool)
        
        self.speed_order_var = tk.StringVar(value=self.settings.transition.speed_order)
        ttk.Radiobutton(speed_frame, text="Random", variable=self.speed_order_var,
                       value="random").grid(row=1, column=0, sticky="w", padx=20)
        ttk.Radiobutton(speed_frame, text="Sequential", variable=self.speed_order_var,
                       value="sequential").grid(row=1, column=1, sticky="w")
        self._bind_widget(speed_frame, "transition.speed_order", str)
        
        # Speed Min/Max
        self.speed_min_var = tk.DoubleVar(value=self.settings.transition.speed_min)
        self._create_slider(
            speed_frame, 2, "Speed Min (px/frame):",
            self.speed_min_var, 0.1, 50.0,
            "transition.speed_min", float,
            format_str="{:.1f}", label_padx=20, pady=2
        )
        
        self.speed_max_var = tk.DoubleVar(value=self.settings.transition.speed_max)
        self._create_slider(
            speed_frame, 3, "Speed Max (px/frame):",
            self.speed_max_var, 0.1, 50.0,
            "transition.speed_max", float,
            format_str="{:.1f}", label_padx=20, pady=2
        )
        
        ttk.Label(speed_frame, text="Randomizes transition speed within specified range",
                 font=("TkDefaultFont", 8)).grid(row=4, column=0, columnspan=3, sticky="w", pady=2)
