"""
Test script to verify enum transition mode cycling works correctly.
Run this to check if the M key cycling functionality is working with enums.
"""

from config.enums import TransitionMode, ColourScheme
from screen_overlay import ScreenOverlay

def test_transition_mode_cycling():
    """Test that transition mode cycling works with enums."""
    print("=== Testing Transition Mode Cycling ===\n")
    
    # Create a simple overlay to test with
    overlay = ScreenOverlay(10, 10, 10, 1.0)
    
    # Test the cycling logic that matches the screendisplayer.py event handler
    modes_to_test = [
        TransitionMode.SMOOTH,
        TransitionMode.SNAP, 
        TransitionMode.MIXED,
        TransitionMode.SPREAD_HORIZONTAL,
        TransitionMode.SPREAD_VERTICAL
    ]
    
    print("Testing mode cycling sequence:")
    current_mode = TransitionMode.SMOOTH
    
    for i in range(6):  # Test one full cycle plus one
        print(f"Step {i+1}: Current mode = {current_mode.value}")
        
        # Apply the same cycling logic as in screendisplayer.py
        if current_mode == TransitionMode.SMOOTH:
            new_mode = TransitionMode.SNAP
        elif current_mode == TransitionMode.SNAP:
            new_mode = TransitionMode.MIXED
        elif current_mode == TransitionMode.MIXED:
            new_mode = TransitionMode.SPREAD_HORIZONTAL
        elif current_mode == TransitionMode.SPREAD_HORIZONTAL:
            new_mode = TransitionMode.SPREAD_VERTICAL
        else:  # SPREAD_VERTICAL
            new_mode = TransitionMode.SMOOTH
            
        # Set the mode on the overlay
        success = overlay.set_colour_transition_mode(new_mode)
        print(f"         -> Setting to {new_mode.value}: {'Success' if success else 'Failed'}")
        
        # Verify it was actually set
        actual_mode = overlay.colour_transition_mode
        print(f"         -> Actual mode after setting: {actual_mode.value}")
        print(f"         -> Match: {'✓' if actual_mode == new_mode else '✗'}")
        
        current_mode = new_mode
        print()


def test_colour_scheme_cycling():
    """Test that colour scheme cycling works with enums."""
    print("=== Testing Colour Scheme Cycling ===")
    
    overlay = ScreenOverlay(10, 10, 10, 1.0)
    
    # Test cycling through first few colour schemes
    all_schemes = list(ColourScheme)
    print(f"Available schemes ({len(all_schemes)} total):")
    for i, scheme in enumerate(all_schemes[:5]):  # Show first 5
        print(f"  {i+1}. {scheme.value}")
    
    print("\nTesting scheme cycling:")
    
    # Start with transgender scheme
    current_scheme = ColourScheme.TRANSGENDER
    overlay.set_colour_scheme(current_scheme)
    
    for i in range(3):  # Test a few cycles
        print(f"Step {i+1}: Current scheme = {current_scheme.value}")
        
        # Find next scheme (same logic as in screendisplayer.py)
        try:
            current_index = all_schemes.index(current_scheme)
            next_index = (current_index + 1) % len(all_schemes)
        except ValueError:
            next_index = 0
        
        next_scheme = all_schemes[next_index]
        
        # Set the scheme
        success = overlay.set_colour_scheme(next_scheme)
        print(f"         -> Setting to {next_scheme.value}: {'Success' if success else 'Failed'}")
        
        # Verify it was set
        actual_name = overlay.colour_scheme_name
        print(f"         -> Actual scheme after setting: {actual_name}")
        print(f"         -> Match: {'✓' if actual_name == next_scheme.value else '✗'}")
        
        current_scheme = next_scheme
        print()


if __name__ == "__main__":
    test_transition_mode_cycling()
    test_colour_scheme_cycling()
    
    print("=== Test Summary ===")
    print("If all steps show '✓ Match', then the enum cycling is working correctly!")
    print("The M key should now properly cycle through transition modes.")
    print("The T key should now properly cycle through colour schemes.")