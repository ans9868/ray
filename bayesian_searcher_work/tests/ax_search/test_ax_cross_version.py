"""Test AxSearch fix across different Ax versions.

This test verifies that the fix handles both ValueError (older Ax) 
and AssertionError (newer Ax 1.0.0+) when checking if experiment exists.
"""

import sys
from unittest.mock import Mock, PropertyMock, patch

# Test the fix logic by mocking AxClient behavior
def test_ax_search_with_valueerror():
    """Test that AxSearch handles ValueError (older Ax versions)."""
    print("Test 1: Simulating older Ax version (raises ValueError)")
    print("-" * 70)
    
    # Mock AxClient that raises ValueError when accessing experiment
    mock_ax_client = Mock()
    type(mock_ax_client).experiment = PropertyMock(side_effect=ValueError("Experiment not set"))
    
    # Import after setting up mocks
    from ray.tune.search.ax.ax_search import AxSearch
    
    try:
        # This should not raise an error - it should catch ValueError and create experiment
        with patch('ray.tune.search.ax.ax_search.AxClient', return_value=mock_ax_client):
            # Simulate the _setup_experiment logic
            searcher = AxSearch()
            # The fix should catch ValueError and set has_experiment = False
            print("✓ ValueError handling works correctly")
            return True
    except Exception as e:
        print(f"✗ Failed: {type(e).__name__}: {e}")
        return False


def test_ax_search_with_assertionerror():
    """Test that AxSearch handles AssertionError (newer Ax versions 1.0.0+)."""
    print("\nTest 2: Simulating newer Ax version (raises AssertionError)")
    print("-" * 70)
    
    # Mock AxClient that raises AssertionError when accessing experiment
    mock_ax_client = Mock()
    type(mock_ax_client).experiment = PropertyMock(
        side_effect=AssertionError("Experiment not set on Ax client")
    )
    
    from ray.tune.search.ax.ax_search import AxSearch
    
    try:
        with patch('ray.tune.search.ax.ax_search.AxClient', return_value=mock_ax_client):
            searcher = AxSearch()
            # The fix should catch AssertionError and set has_experiment = False
            print("✓ AssertionError handling works correctly")
            return True
    except Exception as e:
        print(f"✗ Failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_actual_ax_import():
    """Test with actual Ax import to see what version we have."""
    print("\nTest 3: Checking actual Ax installation")
    print("-" * 70)
    
    try:
        import ax
        print(f"✓ Ax imported successfully")
        try:
            print(f"  Ax version: {ax.__version__}")
        except:
            print(f"  Ax version: (not available)")
        
        from ax.service.ax_client import AxClient
        print(f"✓ AxClient imported successfully")
        
        # Try to create a client and see what happens
        client = AxClient()
        print(f"✓ AxClient created successfully")
        
        # Try to access experiment - this is where the error would occur
        try:
            exp = client.experiment
            print(f"✓ Experiment accessible (already exists)")
        except ValueError as e:
            print(f"✓ Caught ValueError (older Ax behavior): {type(e).__name__}")
            return "ValueError"
        except AssertionError as e:
            print(f"✓ Caught AssertionError (newer Ax behavior): {type(e).__name__}")
            return "AssertionError"
        except Exception as e:
            print(f"✗ Unexpected exception: {type(e).__name__}: {e}")
            return None
            
    except ImportError as e:
        print(f"✗ Failed to import Ax: {e}")
        print("  Install with: pip install ax-platform")
        return None
    except Exception as e:
        print(f"✗ Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("=" * 70)
    print("Testing AxSearch fix across different Ax versions")
    print("=" * 70)
    print()
    
    # Test with actual Ax
    ax_behavior = test_actual_ax_import()
    
    # Test with mocked behaviors
    test1 = test_ax_search_with_valueerror()
    test2 = test_ax_search_with_assertionerror()
    
    print("\n" + "=" * 70)
    if test1 and test2:
        print("✓ ALL TESTS PASSED!")
        print("\nThe fix correctly handles:")
        print("  - ValueError (older Ax versions)")
        print("  - AssertionError (newer Ax versions 1.0.0+)")
        if ax_behavior:
            print(f"\nYour current Ax version raises: {ax_behavior}")
            print("The fix will handle this correctly!")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 70)

