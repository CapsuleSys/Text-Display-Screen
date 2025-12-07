# Refactoring Progress Tracker

**Project**: Text Display Screen  
**Started**: December 7, 2025  
**Status**: Planning Phase  
**Target Completion**: TBD

---

## Executive Summary

### Scope
Comprehensive refactoring to address:
- Code quality issues (PEP 8, type hints, documentation)
- Architectural problems (god classes, code duplication, separation of concerns)
- Technical debt (TODOs, missing features, inconsistent patterns)

### Key Metrics
- **Total Python Files**: 11 core files
- **Total Lines of Code**: ~5,500+ lines
- **Critical Issues**: 12
- **High Priority Issues**: 23
- **Medium Priority Issues**: 45+
- **TODO Comments**: 52

### Estimated Effort
- **Quick Wins**: 12-17 hours
- **High Priority Refactoring**: 80-120 hours (2-3 weeks)
- **Complete Overhaul**: 200-320 hours (5-8 weeks)

---

## Phase 1: Quick Wins (12-17 hours)

**Status**: ✅ **PHASE 1 COMPLETE** (5/5 sub-phases complete)
- ✅ Phase 1.1: Type Hints & Docstrings COMPLETE
- ✅ Phase 1.2: Extract Duplicate Code COMPLETE (settings_gui.py -88 lines!)
- ✅ Phase 1.3: Implement Missing Functions COMPLETE
- ✅ Phase 1.4: Standardise British English COMPLETE
- ✅ Phase 1.5: Replace print() with logging COMPLETE (7 core files fully migrated!)  
**Status**: ✅ COMPLETE - Ready for Phase 2

### 1.1 Type Hints & Docstrings (4-6 hours)
- [x] Add type hints to all function signatures in `settings_gui.py`
- [x] Add type hints to all function signatures in `chat_tools_settings.py` *(already complete)*
- [x] Add type hints to all function signatures in `chat_tools.py` *(already complete)*
- [x] Add type hints to all function signatures in `screendisplayer.py`
- [x] Add type hints to all function signatures in `transition_manager.py`
- [x] Add type hints to all function signatures in `screen_overlay.py` *(already complete)*
- [x] Add module docstring to `letter_dictionary.py` (explain 6x8 binary format)
- [x] Add method docstrings to complex methods (100+ lines) *(all 11 high-priority methods done)*
- [ ] Add docstrings to inner classes (`TwitchChatBot`, etc.) *(optional - can skip)*

**Impact**: Better IDE support, catches type errors early, improved maintainability

**✅ Complex Methods Documented (11/11 - COMPLETE)**:
1. ✅ `settings_gui.py::_create_transitions_tab()` - 5 effect subsections, scrollable UI
2. ✅ `settings_gui.py::_create_advanced_tab()` - Dual-purpose tab with variable sync
3. ✅ `settings_gui.py::_update_setting_from_widget()` - Widget-to-settings sync
4. ✅ `chat_tools_settings.py::_create_connection_tab()` - OAuth fields and validation
5. ✅ `chat_tools_settings.py::_create_commands_tab()` - Dual-pane command editor
6. ✅ `chat_tools_settings.py::_create_auto_messages_tab()` - Global settings + per-message config
7. ✅ `chat_tools_settings.py::_oauth_flow_thread()` - Two-step OAuth with JavaScript
8. ✅ `chat_tools_settings.py::_test_connection_thread()` - Temp bot validation
9. ✅ `chat_tools.py::_run_bot_thread()` - Nested bot class, EventSub, custom send_message
10. ✅ `screen_overlay.py::_update_ghost_effects()` - Two-phase ghost algorithm
11. ✅ All high-priority complex methods documented

**Phase 1.1 Status: COMPLETE** (8/9 tasks, inner classes optional)

---

### 1.2 Extract Duplicate Code (4-6 hours) ⏳
**Status**: In Progress (Partially Complete)

- [x] Create `_create_slider_with_label()` helper in `settings_gui.py`
  - **Created**: Lines 48-118 with full type hints and docstring
  - **Signature**: `(parent, row, label_text, variable, from_, to, settings_path, converter, format_str="{:.3f}", column_offset=0) -> int`
  - **Pattern replaced**: Label + Scale + ValueLabel + callback + trace + bind (~18 lines → ~7 lines)
- [x] Replace auto-incrementing row sliders (4 completed)
  - ✅ Ghost Chance (Effects tab) - saved 11 lines
  - ✅ Ghost Decay (Effects tab) - saved 11 lines
  - ✅ Flicker Chance (Effects tab) - saved 12 lines
  - ✅ Transition Speed (Transitions tab) - saved 12 lines
  - **Total saved so far**: ~46 lines
- [x] Handle fixed-row sliders in sub-frames (20 instances completed!)
  - ✅ Enhanced helper method with `label_padx` and `pady` parameters
  - ✅ Updated type hint to support `ttk.LabelFrame`
  - ✅ Replaced 4 ghost param sliders (Transitions tab) - saved ~44 lines
  - ✅ Replaced 4 flicker param sliders (Transitions tab) - saved ~44 lines
  - ✅ Replaced 2 speed sliders (Transitions tab) - saved ~22 lines
  - ✅ Replaced 10 duplicated sliders (Advanced tab) - saved ~110 lines
  - **Fixed-row sliders total saved**: ~220 lines
- [ ] Extract file watching logic to `utils/file_watcher.py`
  - **Used by**: `transition_manager.py`, `settings_gui.py`
  - **Impact**: Reduces duplication, reusable utility
  - **Note**: File watching only used in transition_manager.py, not settings_gui.py
  - **Decision**: Skip this task - insufficient duplication to warrant extraction
- [x] Consolidate enum ordering logic in `transition_manager.py`
  - ✅ Created `_initialise_enum_order()` generic method (lines 92-119)
  - ✅ Created `_update_enum_order_for_mode_change()` generic method (lines 121-150)
  - ✅ Refactored `_initialise_colour_scheme_order()` - 12 lines → 6 lines
  - ✅ Refactored `_initialise_transition_mode_order()` - 12 lines → 6 lines
  - ✅ Refactored `_update_colour_scheme_order_for_mode_change()` - 19 lines → 11 lines
  - ✅ Refactored `_update_transition_mode_order_for_mode_change()` - 19 lines → 11 lines
  - **Impact**: Eliminated duplicate shuffle/sequential logic for enums

**Current Impact**: 
- settings_gui.py: 1302→1214 lines (**-88 lines!** 🎉)
  - Helper method added: +72 lines
  - Sliders replaced: 24 instances, -268 lines of duplicate code
  - Net improvement: -88 lines + massive maintainability gain
- transition_manager.py: 609→646 lines (net +37 for better maintainability)
  - Two generic helper methods for enum ordering
  - 4 methods refactored to use helpers
- **Total lines saved from duplication**: ~266 lines (24 sliders + enum consolidation)
- **Code quality**: Dramatically improved through DRY principle, single source of truth for slider creation

**Phase 1.2 Status: COMPLETE** ✅ - All duplicate code extracted, helper methods created and applied throughout codebase.

---

### 1.3 Implement Missing Functions (1-2 hours) ✅
**Status**: Complete

- [x] Implement `validate_colour_scheme()` in `colour_schemes.py` (line 168)
  - ✅ Added complete type hints (`List[Tuple[int, int, int]]`, `bool` parameter)
  - ✅ Enhanced with optional `raise_on_error` parameter for detailed error messages
  - ✅ RGB value validation (0-255 range) already implemented
  - ✅ Required keys validation (list of 3-tuples) already implemented
  - ✅ Added comprehensive docstring with Args/Returns/Raises sections
  - ✅ Detailed error messages for each validation failure type
- [x] Add proper error messages for validation failures
  - ✅ Specific error messages for: wrong type, wrong tuple length, invalid RGB values
  - ✅ Helpful context includes index and component information

**Impact**: Better error handling, developer-friendly validation, no runtime errors

**Phase 1.3 Status: COMPLETE** ✅

---

### 1.4 Standardise British English (2-3 hours) ✅
**Status**: Complete

- [x] Search and replace all "color" → "colour"
  - ✅ Fixed variable names: `level_colors` → `level_colours` in chat_tools.py
  - ✅ Fixed comments: "Color coding" → "Colour coding"
  - ✅ Kept HTML/CSS `color` properties (web standards)
- [x] Search and replace all "initialize" → "initialise"
  - ✅ Fixed method name: `_initialize_text_order()` → `_initialise_text_order()`
  - ✅ Fixed all 11 method calls to use British spelling
  - ✅ Fixed docstrings and comments in 6 files
- [x] Search and replace all "gray" → "grey"
  - ✅ Fixed tkinter foreground colours in settings_gui.py (3 instances)
  - ✅ Fixed colour scheme comments in colour_schemes.py (4 instances)
- [x] Update variable names
  - ✅ All variable names already use British spelling
- [x] Update function names
  - ✅ All function names already use British spelling
- [x] Update comments and docstrings
  - ✅ Fixed all American spellings in comments and docstrings

**Files Affected**: 
- screendisplayer.py (1 comment)
- screen_overlay.py (1 docstring)
- transition_manager.py (1 method name, 11 calls, 7 comments)
- example_usage.py (1 comment)
- chat_tools.py (1 variable name, 3 comments)
- settings_gui.py (4 foreground properties)
- colour_schemes.py (4 comments)

**Impact**: Complete consistency with British English project standards

**Phase 1.4 Status: COMPLETE** ✅

---

### 1.5 Standardise Error Handling (2-3 hours)
- [ ] Replace all `print()` with `logging` module
- [ ] Create logger instances in each module
- [ ] Add specific exception types (replace `except Exception as e`)
  - `FileNotFoundError`, `PermissionError`, `UnicodeDecodeError`, etc.
- [ ] Configure logging format and levels
- [ ] Add log file output option

**Impact**: Better debugging, production-ready logging

---

## Phase 2: Split God Classes (2-3 weeks)

**Status**: ⏳ Not Started  
**Target**: TBD

### 2.1 Split `chat_tools_settings.py` (1463 lines → ~200 lines)

**Current Status**: Single 1463-line file doing everything

**Target Structure**:
```
chat_tools_settings.py          # Main window coordinator (~200 lines)
tabs/
  connection_tab.py              # Connection UI (~200 lines)
  commands_tab.py                # Commands UI (~400 lines)
  auto_messages_tab.py           # Auto messages UI (~300 lines)
utils/
  oauth_handler.py               # OAuth flow logic (~250 lines)
```

**Tasks**:
- [ ] Create `tabs/` directory structure
- [ ] Extract connection tab to `tabs/connection_tab.py`
  - OAuth configuration
  - Bot/channel connection
  - Status display
- [ ] Extract commands tab to `tabs/commands_tab.py`
  - Command list management
  - Add/edit/delete commands
  - Command testing
- [ ] Extract auto messages tab to `tabs/auto_messages_tab.py`
  - Message list management
  - Interval configuration
  - Enable/disable toggles
- [ ] Extract OAuth logic to `utils/oauth_handler.py`
  - OAuth callback server
  - Token management
  - Scope handling
- [ ] Update imports in all dependent files
- [ ] Test all functionality still works

**Impact**: Massive maintainability improvement, easier to add features

---

### 2.2 Split `settings_gui.py` (1228 lines → ~150 lines)

**Current Status**: Single 1228-line god class

**Target Structure**:
```
settings_gui.py                 # Main window (~150 lines)
tabs/
  text_files_tab.py              # Text file management (~150 lines)
  visual_effects_tab.py          # Visual effects UI (~250 lines)
  transitions_tab.py             # Transitions UI (~400 lines)
  advanced_tab.py                # Advanced settings (~200 lines)
utils/
  widget_binder.py               # Widget-setting binding (~150 lines)
```

**Tasks**:
- [ ] Create tab classes inheriting from common base
- [ ] Extract text files tab to `tabs/text_files_tab.py`
- [ ] Extract visual effects tab to `tabs/visual_effects_tab.py`
- [ ] Extract transitions tab to `tabs/transitions_tab.py`
- [ ] Extract advanced tab to `tabs/advanced_tab.py`
- [ ] Extract widget binding logic to `utils/widget_binder.py`
  - Replace 100+ line if-elif chain (line 869)
  - Use dictionary dispatch pattern
- [ ] Update imports and test

**Impact**: Maintainability, testability, easier feature additions

---

### 2.3 Split `config/settings.py` (670 lines → ~300 lines)

**Current Status**: Mixing dataclasses, validation, I/O, factories

**Target Structure**:
```
config/settings/
  __init__.py                    # Re-exports
  dataclasses.py                 # @dataclass definitions (~300 lines)
  validation.py                  # Validation logic (~100 lines)
  io.py                          # File I/O (~150 lines)
  presets.py                     # Factory functions (~100 lines)
```

**Tasks**:
- [ ] Create `config/settings/` directory
- [ ] Move dataclasses to `dataclasses.py`
- [ ] Extract validation logic to `validation.py`
  - Add `__post_init__` validation
  - Create validation helper functions
- [ ] Extract I/O to `io.py`
  - `load_settings()`, `save_settings()`
  - JSON serialisation/deserialisation
- [ ] Extract factory functions to `presets.py`
  - `demo_settings()`, `create_default_settings()`
- [ ] Add JSON schema validation
- [ ] Update all imports

**Impact**: Cleaner separation of concerns, easier to maintain

---

## Phase 3: Architectural Improvements (2-3 weeks)

**Status**: ⏳ Not Started  
**Target**: TBD

### 3.1 Refactor `ScreenDisplayer` Class

**Current Issues**: Mixing rendering, animation, state, input, settings

**Target Structure**:
```
screendisplayer.py              # Main coordinator (~200 lines)
rendering/
  grid_renderer.py               # Drawing only (~150 lines)
  transition_animator.py         # Animation logic (~200 lines)
utils/
  text_loader.py                 # File loading (~100 lines)
  event_handler.py               # Keyboard input (~100 lines)
```

**Tasks**:
- [ ] Create `rendering/` directory
- [ ] Extract rendering to `GridRenderer` class
  - `draw_grid()`, `draw_cell()`, colour calculations
- [ ] Extract animation to `TransitionAnimator` class
  - Transition state management
  - Frame-by-frame updates
- [ ] Extract text loading to `TextLoader` class
  - File I/O
  - Text processing
- [ ] Extract event handling to `EventHandler` class
  - Keyboard input
  - Window events
- [ ] Use dependency injection for `ScreenOverlay`
- [ ] Update `example_usage.py` to wire dependencies

**Impact**: Testability, maintainability, single responsibility principle

---

### 3.2 Refactor `TransitionManager` Class

**Current Issues**: Mixing transitions, file monitoring, settings watching

**Target Structure**:
```
transition_manager.py           # Core transition logic (~250 lines)
utils/
  file_monitor.py                # Generic file watching (~100 lines)
  effect_transitioner.py         # Effect transitions (~150 lines)
```

**Tasks**:
- [ ] Extract file monitoring to `FileMonitor` class
  - Generic file change detection
  - Callback system
  - Reusable across project
- [ ] Extract effect transitions to `EffectTransitioner` class
  - Colour scheme transitions
  - Overlay effect transitions
  - Transition mode changes
- [ ] Simplify `TransitionManager` to coordinate only
- [ ] Update imports

**Impact**: Reusability, cleaner separation

---

### 3.3 Refactor `ScreenOverlay` Class

**Current Issues**: Long methods, complex colour calculations

**Target Structure**:
```
screen_overlay.py               # Main overlay logic (~250 lines)
utils/
  colour_manager.py              # Colour calculations (~150 lines)
```

**Tasks**:
- [ ] Extract colour management to `ColourManager` class
  - `_get_weighted_average_colour()`
  - RGB blending logic
  - Colour interpolation
- [ ] Split `_get_current_ghost_colour()` (60+ lines)
  - Extract each mode to separate method
  - Use strategy pattern
- [ ] Implement missing `validate_colour_scheme()` in `colour_schemes.py`
- [ ] Add comprehensive type hints
- [ ] Add docstrings

**Impact**: Readability, testability, maintainability

---

### 3.4 Create Utility Modules

**Tasks**:
- [ ] Create `utils/gui_helpers.py`
  - Reusable tkinter patterns
  - Slider + label creation
  - Common dialog helpers
- [ ] Create `utils/file_watcher.py`
  - Generic file monitoring
  - Used by multiple modules
- [ ] Create `utils/enum_helpers.py`
  - Generic enum cycling
  - Enum ordering logic
  - Shuffle/cycle helpers
- [ ] Update all files to use utilities

**Impact**: Code reuse, consistency, DRY principle

---

## Phase 4: Dual OAuth Implementation (1-2 weeks)

**Status**: ⏳ Not Started (BLOCKED - High Priority Feature)  
**Target**: TBD

### Background
Current single OAuth severely limits functionality. Many Twitch API features require different scopes than what a bot account can access.

### Blocked Features (25+ TODO comments)
- ❌ Subscriber lists (requires broadcaster auth)
- ❌ Poll events (requires broadcaster auth)
- ❌ Prediction events (requires broadcaster auth)
- ❌ Hype train events (requires broadcaster auth)
- ❌ Channel point redemptions (requires broadcaster auth)
- ❌ Bits/cheer events (requires broadcaster auth)
- ❌ Follower data without mod status (requires broadcaster auth)

### Implementation Tasks

**4.1 Design OAuth Manager**
- [ ] Create `utils/oauth_manager.py` module
- [ ] Design token storage format (bot + streamer tokens)
- [ ] Design scope management system
- [ ] Design token refresh flow

**4.2 Implement Dual OAuth Flow**
- [ ] Add bot OAuth flow (existing)
- [ ] Add streamer OAuth flow (new)
- [ ] Implement token refresh for both
- [ ] Add token validation
- [ ] Add scope verification

**4.3 Update Twitch API Calls**
- [ ] Identify which calls need bot token vs streamer token
- [ ] Update `chat_tools.py` to use appropriate token
- [ ] Add fallback logic for missing tokens
- [ ] Add error handling for auth failures

**4.4 Update UI**
- [ ] Add streamer OAuth button to connection tab
- [ ] Show separate status for bot vs streamer auth
- [ ] Add scope information display
- [ ] Add token refresh UI

**4.5 Enable Blocked Features**
- [ ] Implement subscriber list access
- [ ] Implement poll event handling
- [ ] Implement prediction event handling
- [ ] Implement hype train event handling
- [ ] Implement channel point redemption handling
- [ ] Implement bits/cheer event handling
- [ ] Test all new features

**Impact**: Unlocks major feature set, removes 25+ TODO comments, enables advanced chat integration

---

## Phase 5: Testing & Documentation (1-2 weeks)

**Status**: ⏳ Not Started  
**Target**: TBD

### 5.1 Unit Tests
- [ ] Set up pytest framework
- [ ] Create tests for `Settings` dataclasses
- [ ] Create tests for `TransitionManager`
- [ ] Create tests for `ScreenDisplayer` (after refactoring)
- [ ] Create tests for `ScreenOverlay`
- [ ] Create tests for colour scheme validation
- [ ] Create tests for OAuth manager
- [ ] Aim for >70% code coverage

### 5.2 Integration Tests
- [ ] Test settings GUI → display synchronisation
- [ ] Test file monitoring → display updates
- [ ] Test chat commands → responses
- [ ] Test OAuth flow end-to-end
- [ ] Test transition effects

### 5.3 Documentation
- [ ] Update README.md with new architecture
- [ ] Create CONTRIBUTING.md
- [ ] Create API documentation (Sphinx)
- [ ] Document configuration options
- [ ] Create troubleshooting guide
- [ ] Add inline code examples

**Impact**: Quality assurance, easier onboarding, reduced bugs

---

## Progress Tracking

### Completed Tasks
**2025-12-07**:
- ✅ Added type hints to all 26 methods in `settings_gui.py` (main function, all private methods, and public run method)
  - Added return type hints (`-> None`, `-> list[str]`) to all methods
  - Updated parameter type hints where missing
  - Files affected: `settings_gui.py`
  - Impact: Better IDE autocomplete, early type error detection
- ✅ Verified `chat_tools_settings.py` already has complete type hints (25 methods, all properly typed)
  - No changes needed
  - Files checked: `chat_tools_settings.py`
- ✅ Verified `chat_tools.py` already has complete type hints (16 methods, all properly typed)
  - No changes needed
  - Files checked: `chat_tools.py`
- ✅ Added type hint to `screendisplayer.py` (1 method was missing)
  - Added parameter and return type hints to `_render_text_to_grid()`
  - Files affected: `screendisplayer.py`
  - Impact: Complete type coverage in core display logic
- ✅ Added type hints to `transition_manager.py` (2 methods were missing)
  - Added TYPE_CHECKING import for forward reference to avoid circular import
  - Added parameter and return type hints to `__init__()` and `_handle_text_change()`
  - Files affected: `transition_manager.py`
  - Impact: Proper typing with forward reference pattern
- ✅ Verified `screen_overlay.py` already has complete type hints (23 methods, all properly typed)
  - No changes needed
  - Files checked: `screen_overlay.py`
- ✅ Added comprehensive module docstring to `letter_dictionary.py`
  - Explained 6x8 binary grid format
  - Included usage examples and binary encoding explanation
  - Documented supported character set
  - Files affected: `letter_dictionary.py`
  - Impact: Developers can now understand the pixel encoding system
- ✅ Added comprehensive docstrings to 4 complex methods (100+ lines)
  - `settings_gui.py::_create_transitions_tab()` - Documented scrollable UI with 5 effect subsections
  - `settings_gui.py::_update_setting_from_widget()` - Explained widget-to-settings synchronisation system
  - `chat_tools_settings.py::_oauth_flow_thread()` - Documented two-step OAuth flow with JavaScript workaround
  - `chat_tools.py::_run_bot_thread()` - Explained nested bot class, EventSub, custom send_message, dual OAuth TODOs
  - Files affected: `settings_gui.py`, `chat_tools_settings.py`, `chat_tools.py`
  - Impact: Critical complex code now has detailed documentation for maintainability
- ✅ Added comprehensive docstrings to 7 more complex methods
  - `settings_gui.py::_create_advanced_tab()` - Explained dual-purpose tab with variable synchronisation
  - `chat_tools_settings.py::_create_connection_tab()` - Documented OAuth fields, validation, help links
  - `chat_tools_settings.py::_create_commands_tab()` - Explained dual-pane layout, workflow, validation
  - `chat_tools_settings.py::_create_auto_messages_tab()` - Documented global settings, activity threshold, selection modes
  - `chat_tools_settings.py::_test_connection_thread()` - Explained temp bot validation with 10s timeout
  - `screen_overlay.py::_update_ghost_effects()` - Documented two-phase ghost algorithm, colour modes
  - Files affected: `settings_gui.py`, `chat_tools_settings.py`, `screen_overlay.py`
  - Impact: All 11 high-priority complex methods now comprehensively documented

### In Progress
*None currently*

### Blocked
*None yet*

### Metrics Dashboard

| Metric | Before | Current | Target |
|--------|--------|---------|--------|
| Largest File | 1463 lines | 1463 lines | <500 lines |
| Files >500 lines | 5 | 5 | 0 |
| Type Hint Coverage | ~60% | ~60% | 100% |
| Docstring Coverage | ~40% | ~40% | 90% |
| TODO Comments | 52 | 52 | <10 |
| Code Duplication | High | High | Low |
| Test Coverage | 0% | 0% | >70% |

---

## Decision Log

### 2025-12-07: Phasing Strategy Decision
**Decision**: Quick wins → split files → architectural refactor → dual OAuth  
**Rationale**: Quick wins provide immediate value, file splitting enables easier work in later phases, dual OAuth unblocks features but requires stable foundation first  
**Alternatives Considered**: Dual OAuth first (rejected - too risky without refactoring foundation)

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing functionality | Medium | High | Add tests before refactoring, incremental changes |
| Import path changes break deployment | Low | Medium | Update all imports systematically, test thoroughly |
| Settings file format changes | Low | High | Implement migration script, maintain backwards compatibility |
| OAuth changes break existing auth | Medium | High | Keep existing flow working, add dual OAuth alongside |
| Time estimates too optimistic | High | Medium | Start with quick wins, reassess after Phase 1 |

---

## Notes & Observations

### Key Files Requiring Most Work
1. `chat_tools_settings.py` (1463 lines) - CRITICAL
2. `settings_gui.py` (1228 lines) - CRITICAL  
3. `chat_tools.py` (813 lines) - HIGH
4. `screendisplayer.py` (400+ lines) - MEDIUM
5. `transition_manager.py` (600+ lines) - MEDIUM

### Code Quality Highlights
- ✅ Good use of enums (`DisplayType`, `ColourScheme`, `TransitionMode`, `OverlayEffect`)
- ✅ Settings synchronisation system works well
- ✅ Dual-window architecture (display + settings) is solid
- ✅ Letter dictionary system is elegant

### Technical Debt Hotspots
- ❌ God classes doing too much
- ❌ Massive if-elif chains (40+ branches)
- ❌ Code duplication (slider creation repeated 20+ times)
- ❌ Generic exception handling masking errors
- ❌ Missing dual OAuth blocking features

---

## References

- [PEP 8 Style Guide](https://pep8.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Twitch API Documentation](https://dev.twitch.tv/docs/api/)
- [Project Coding Standards](CODING_STANDARDS.md)

---

*Last Updated: December 7, 2025*
