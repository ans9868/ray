"""Test AxClient directly to demonstrate the exception behavior."""

print("=" * 70)
print("Testing AxClient directly to see what exception it raises")
print("=" * 70)
print()

try:
    from ax.service.ax_client import AxClient
    print("✓ AxClient imported successfully")
    
    # Check Ax version
    try:
        import ax
        try:
            ax_version = ax.__version__
            print(f"✓ Ax version: {ax_version}")
        except:
            print("✓ Ax imported (version unknown)")
    except:
        print("⚠ Could not determine Ax version")
    
    print("\n" + "-" * 70)
    print("Creating AxClient...")
    client = AxClient()
    print("✓ AxClient created")
    
    print("\n" + "-" * 70)
    print("Testing: Accessing client.experiment BEFORE creating experiment...")
    print("(This is what causes the bug in the old code)")
    print("-" * 70)
    
    try:
        exp = client.experiment
        print("✓ Experiment accessible (unexpected - experiment already exists?)")
    except ValueError as e:
        print(f"✓ Caught ValueError (older Ax behavior): {type(e).__name__}")
        print(f"  Message: {str(e)[:100]}")
        print("\n" + "=" * 70)
        print("RESULT: Older Ax version (< 1.0.0)")
        print("  - Raises ValueError when experiment not set")
        print("  - Old Ray code (only catching ValueError) would work")
        print("=" * 70)
    except AssertionError as e:
        print(f"✓ Caught AssertionError (newer Ax behavior): {type(e).__name__}")
        print(f"  Message: {str(e)[:100]}")
        print("\n" + "=" * 70)
        print("RESULT: Newer Ax version (>= 1.0.0)")
        print("  - Raises AssertionError when experiment not set")
        print("  - Old Ray code (only catching ValueError) would FAIL")
        print("  - This is the bug we're fixing!")
        print("=" * 70)
    except Exception as e:
        print(f"✗ Unexpected exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "-" * 70)
    print("Now creating experiment and testing again...")
    print("-" * 70)
    
    client.create_experiment(
        parameters=[
            {"name": "x1", "type": "range", "bounds": [0.0, 1.0]},
            {"name": "x2", "type": "range", "bounds": [0.0, 1.0]},
        ],
        objective_name="score",
        minimize=False,
    )
    print("✓ Experiment created")
    
    try:
        exp = client.experiment
        print("✓ Experiment accessible after creation")
        print(f"  Parameters: {len(exp.parameters)}")
    except Exception as e:
        print(f"✗ Unexpected error after creation: {type(e).__name__}: {e}")

except ImportError as e:
    print(f"✗ Failed to import AxClient: {e}")
    print("\nTo install Ax:")
    print("  pip install ax-platform")
    print("\nFor newer Ax (1.0.0+):")
    print("  pip install 'ax-platform>=1.0.0'")
except Exception as e:
    print(f"✗ Unexpected error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

