"""
GUI utilities package for Text Display Screen.

Provides reusable GUI components and patterns for building consistent
tkinter interfaces across the application.

Main modules:
    - button_factory: Styled button creation functions
    - dual_pane_layout: List+editor interface pattern
    - window_setup: Common window configuration utilities
"""

from gui_utils.button_factory import (
    create_primary_button,
    create_danger_button,
    create_warning_button,
    create_info_button,
    create_neutral_button,
    create_link_label
)

from gui_utils.dual_pane_layout import DualPaneLayout

from gui_utils.window_setup import (
    setup_window,
    create_title_label,
    create_tabbed_notebook,
    create_button_row,
    create_status_label,
    configure_grid_weights
)

__all__ = [
    # Button factory
    'create_primary_button',
    'create_danger_button',
    'create_warning_button',
    'create_info_button',
    'create_neutral_button',
    'create_link_label',
    # Dual pane layout
    'DualPaneLayout',
    # Window setup
    'setup_window',
    'create_title_label',
    'create_tabbed_notebook',
    'create_button_row',
    'create_status_label',
    'configure_grid_weights',
]
