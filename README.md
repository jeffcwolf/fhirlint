# FHIR Quality Inspector

Desktop application for validating and analyzing FHIR bundles against MII Kerndatensatz standards.

## Current Status

**Phase 1: COMPLETE ✓**
- Project structure created
- Bundle parser working (100% success rate on test data)
- MII profile detection implemented
- Tested on 1,651 real POLAR FHIR bundles

**In Progress: Phase 2**
- Quality checker with MII-specific rules

## Quick Start

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test validator
python test_multiple_bundles.py
```

## What It Does

- ✓ Loads FHIR Bundle JSON files
- ✓ Validates bundle structure
- ✓ Detects MII Kerndatensatz modules (Person, Fall, Diagnose, Medikation)
- ✓ Counts resources by type
- 🚧 Quality checks (in progress)
- 🚧 Visual dashboard (planned)
- 🚧 HTML/JSON reports (planned)

## Technical Stack

- **Python 3.11+**
- **fhir.resources** - FHIR parsing library
- **tkinter** - GUI (built-in)
- **matplotlib** - Charts and visualizations

## Test Data

Located in `/work/data/` - 1,651 POLAR FHIR bundles containing:
- Patient resources (MII Person module)
- Encounter resources (MII Fall module)
- Condition resources (MII Diagnose module with ICD-10-GM)
- Medication resources (MII Medikation module)
- Consent resources

All bundles validated successfully ✓
