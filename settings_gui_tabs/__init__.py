"""Settings GUI tab modules.

This package contains the individual tab classes for the settings GUI,
extracted from the monolithic settings_gui.py file as part of Phase 2
refactoring to reduce god class complexity.

Each tab is independent and uses callbacks to interact with the main
settings GUI coordinator, maintaining loose coupling.
"""

from settings_gui_tabs.text_files_tab import TextFilesTab
from settings_gui_tabs.visual_effects_tab import VisualEffectsTab
from settings_gui_tabs.transitions_tab import TransitionsTab
from settings_gui_tabs.advanced_tab import AdvancedTab

__all__ = [
    'TextFilesTab',
    'VisualEffectsTab',
    'TransitionsTab',
    'AdvancedTab',
]
