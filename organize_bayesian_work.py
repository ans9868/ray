#!/usr/bin/env python3
"""Organize Bayesian searcher documentation and test files into a structured directory."""

import os
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent
WORK_DIR = BASE_DIR / "bayesian_searcher_work"

# File mappings: (source_file, destination_subdirectory)
FILE_MAPPINGS = {
    # Documentation - Reports
    "BAYESIAN_SEARCHER_AUDIT_REPORT.md": "docs/reports/",
    "BAYESIAN_SEARCHER_BUG_REPORT.md": "docs/reports/",
    "audit_bayesian_20260126.md": "docs/reports/",
    "SESSION_SUMMARY.md": "docs/reports/",
    
    # Documentation - AxSearch
    "AX_SEARCH_FIX_SUMMARY.md": "docs/ax_search/",
    "AX_SEARCH_FIX_COMPARISON.md": "docs/ax_search/",
    "AX_SEARCH_TEST_MATRIX.md": "docs/ax_search/",
    
    # Documentation - Verification
    "VERIFICATION_RESULTS.md": "docs/verification/",
    "test_before_fix_verification.md": "docs/verification/",
    
    # Tests - AxSearch
    "test_ax_doc_example.py": "tests/ax_search/",
    "test_ax_fix.py": "tests/ax_search/",
    "test_ax_tutorial_matrix.py": "tests/ax_search/",
    "test_ax_init_only.py": "tests/ax_search/",
    "test_ax_cross_version.py": "tests/ax_search/",
    "test_ax_client_direct.py": "tests/ax_search/",
    
    # Tests - BayesOpt
    "test_bayesopt_doc_example.py": "tests/bayesopt/",
    
    # Audits - Scripts
    "audit_bayesian.py": "audits/scripts/",
    "audit_bayesian_enhanced.py": "audits/scripts/",
    
    # Audits - Output
    "audit_bayesian_20260126.txt": "audits/output/",
}

def create_directory_structure():
    """Create the directory structure."""
    directories = [
        "docs/reports",
        "docs/ax_search",
        "docs/verification",
        "tests/ax_search",
        "tests/bayesopt",
        "audits/scripts",
        "audits/output",
    ]
    
    for directory in directories:
        dir_path = WORK_DIR / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")

def move_files():
    """Move files to their new locations."""
    moved = []
    not_found = []
    
    for source_file, dest_subdir in FILE_MAPPINGS.items():
        source_path = BASE_DIR / source_file
        dest_dir = WORK_DIR / dest_subdir
        dest_path = dest_dir / source_file
        
        if source_path.exists():
            shutil.move(str(source_path), str(dest_path))
            moved.append(source_file)
            print(f"Moved: {source_file} -> {dest_path}")
        else:
            not_found.append(source_file)
            print(f"Warning: {source_file} not found, skipping...")
    
    return moved, not_found

def create_readme():
    """Create a README explaining the organization."""
    readme_content = """# Bayesian Searcher Work

This directory contains all documentation, tests, and audit materials related to the Bayesian searcher investigation and fixes.

## Directory Structure

```
bayesian_searcher_work/
├── docs/
│   ├── reports/          # Audit reports and bug reports
│   ├── ax_search/        # AxSearch-specific documentation
│   └── verification/     # Verification and testing documentation
├── tests/
│   ├── ax_search/        # AxSearch test scripts
│   └── bayesopt/         # BayesOptSearch test scripts
├── audits/
│   ├── scripts/          # Audit scripts
│   └── output/           # Audit output files
└── README.md             # This file
```

## Contents

### Documentation (`docs/`)

#### Reports (`docs/reports/`)
- `BAYESIAN_SEARCHER_AUDIT_REPORT.md` - Initial audit report (2025-12-18)
- `BAYESIAN_SEARCHER_BUG_REPORT.md` - Comprehensive bug report
- `audit_bayesian_20260126.md` - Updated audit report (2026-01-26)
- `SESSION_SUMMARY.md` - Complete session summary

#### AxSearch (`docs/ax_search/`)
- `AX_SEARCH_FIX_SUMMARY.md` - Summary of AxSearch fix
- `AX_SEARCH_FIX_COMPARISON.md` - Before/after code comparison
- `AX_SEARCH_TEST_MATRIX.md` - Test results matrix

#### Verification (`docs/verification/`)
- `VERIFICATION_RESULTS.md` - Verification of bug existence
- `test_before_fix_verification.md` - Pre-fix verification

### Tests (`tests/`)

#### AxSearch Tests (`tests/ax_search/`)
- `test_ax_doc_example.py` - Tests tutorial examples
- `test_ax_fix.py` - Tests for the fix
- `test_ax_tutorial_matrix.py` - Comprehensive test matrix
- `test_ax_init_only.py` - Initialization tests
- `test_ax_cross_version.py` - Cross-version compatibility tests
- `test_ax_client_direct.py` - Direct AxClient tests

#### BayesOpt Tests (`tests/bayesopt/`)
- `test_bayesopt_doc_example.py` - Documentation example test (reproduces 11/20 issue)

### Audits (`audits/`)

#### Scripts (`audits/scripts/`)
- `audit_bayesian.py` - Basic audit script
- `audit_bayesian_enhanced.py` - Enhanced audit with issue detection

#### Output (`audits/output/`)
- `audit_bayesian_20260126.txt` - Raw audit output from 2026-01-26

## Key Findings

### AxSearch
- **Issue**: AssertionError with Ax >= 1.0.0 (fixed by catching both ValueError and AssertionError)
- **New Issue**: TypeError with `objective_name` parameter in newer Ax versions (needs fix)

### BayesOptSearch
- **Issue**: Silent duplicate filtering causing premature stop (11/20 trials completed)
- **Root Cause**: GP suggests same point repeatedly, code silently skips duplicates

### OptunaSearch
- **Status**: Working correctly (no issues found in recent audit)

### HyperOptSearch
- **Status**: Working correctly (minor deprecation warnings from third-party library)

## Related Files

The actual source code fixes are in:
- `python/ray/tune/search/ax/ax_search.py` - AxSearch implementation
- `python/ray/tune/search/bayesopt/bayesopt_search.py` - BayesOptSearch implementation

## Organization Date

Files organized on: 2026-01-26
"""
    
    readme_path = WORK_DIR / "README.md"
    readme_path.write_text(readme_content)
    print(f"Created README: {readme_path}")

def main():
    """Main organization function."""
    print("=" * 60)
    print("Organizing Bayesian Searcher Work Files")
    print("=" * 60)
    print()
    
    # Create directory structure
    print("Creating directory structure...")
    create_directory_structure()
    print()
    
    # Move files
    print("Moving files...")
    moved, not_found = move_files()
    print()
    
    # Create README
    print("Creating README...")
    create_readme()
    print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Files moved: {len(moved)}")
    print(f"Files not found: {len(not_found)}")
    if not_found:
        print(f"\nFiles not found (may have been moved already or don't exist):")
        for f in not_found:
            print(f"  - {f}")
    print()
    print(f"All files organized in: {WORK_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
