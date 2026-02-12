#!/usr/bin/env python3
"""
Create "messy" FHIR bundles with intentional quality issues
This demonstrates the validator's error detection capabilities
"""
import json
import sys
sys.path.insert(0, '/work/src')
from pathlib import Path
import random

def create_messy_bundles():
    """Create sample bundles with various quality issues"""

    output_dir = Path('/work/messy_data')
    output_dir.mkdir(exist_ok=True)

    print("Creating messy FHIR bundles for error detection demo...\n")

    # Bundle 1: Missing required fields
    bundle1 = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "fullUrl": "Patient/messy-patient-1",
                "resource": {
                    "resourceType": "Patient",
                    "id": "messy-patient-1",
                    "meta": {
                        "profile": ["https://www.medizininformatik-initiative.de/fhir/core/modul-person/StructureDefinition/Patient"]
                    },
                    # Missing: identifier, name, gender, birthDate
                },
                "request": {"method": "PUT", "url": "Patient/messy-patient-1"}
            }
        ]
    }

    # Bundle 2: Invalid date formats
    bundle2 = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "fullUrl": "Patient/messy-patient-2",
                "resource": {
                    "resourceType": "Patient",
                    "id": "messy-patient-2",
                    "meta": {
                        "profile": ["https://www.medizininformatik-initiative.de/fhir/core/modul-person/StructureDefinition/Patient"]
                    },
                    "identifier": [{"value": "123"}],
                    "name": [{"family": "Test"}],
                    "gender": "male",
                    "birthDate": "01/15/1990"  # Wrong format (should be YYYY-MM-DD)
                },
                "request": {"method": "PUT", "url": "Patient/messy-patient-2"}
            },
            {
                "fullUrl": "Encounter/messy-enc-2",
                "resource": {
                    "resourceType": "Encounter",
                    "id": "messy-enc-2",
                    "meta": {
                        "profile": ["https://www.medizininformatik-initiative.de/fhir/core/modul-fall/StructureDefinition/KontaktGesundheitseinrichtung"]
                    },
                    "status": "finished",
                    "class": {"code": "IMP"},
                    "subject": {"reference": "Patient/messy-patient-2"},
                    "period": {
                        "start": "2024-13-45",  # Invalid date
                        "end": "not-a-date"      # Invalid date
                    }
                },
                "request": {"method": "PUT", "url": "Encounter/messy-enc-2"}
            }
        ]
    }

    # Bundle 3: Invalid ICD-10-GM codes
    bundle3 = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "fullUrl": "Patient/messy-patient-3",
                "resource": {
                    "resourceType": "Patient",
                    "id": "messy-patient-3",
                    "meta": {
                        "profile": ["https://www.medizininformatik-initiative.de/fhir/core/modul-person/StructureDefinition/Patient"]
                    },
                    "identifier": [{"value": "123"}],
                    "name": [{"family": "Test"}],
                    "gender": "female",
                    "birthDate": "1985-05-20",
                    "address": [{
                        "postalCode": "123"  # Invalid German postal code (should be 5 digits)
                    }]
                },
                "request": {"method": "PUT", "url": "Patient/messy-patient-3"}
            },
            {
                "fullUrl": "Condition/messy-cond-3",
                "resource": {
                    "resourceType": "Condition",
                    "id": "messy-cond-3",
                    "meta": {
                        "profile": ["https://www.medizininformatik-initiative.de/fhir/core/modul-diagnose/StructureDefinition/Diagnose"]
                    },
                    "code": {
                        "coding": [{
                            "system": "http://fhir.de/CodeSystem/bfarm/icd-10-gm",
                            # Missing version
                            "code": "INVALID123"  # Invalid ICD-10-GM format
                        }]
                    },
                    "subject": {"reference": "Patient/messy-patient-3"}
                },
                "request": {"method": "PUT", "url": "Condition/messy-cond-3"}
            }
        ]
    }

    # Bundle 4: Broken references
    bundle4 = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "fullUrl": "Encounter/messy-enc-4",
                "resource": {
                    "resourceType": "Encounter",
                    "id": "messy-enc-4",
                    "meta": {
                        "profile": ["https://www.medizininformatik-initiative.de/fhir/core/modul-fall/StructureDefinition/KontaktGesundheitseinrichtung"]
                    },
                    "status": "finished",
                    "class": {"code": "IMP"},
                    "subject": {"reference": "Patient/DOES-NOT-EXIST"},  # Broken reference
                    "period": {
                        "start": "2024-01-01",
                        "end": "2024-01-05"
                    }
                },
                "request": {"method": "PUT", "url": "Encounter/messy-enc-4"}
            },
            {
                "fullUrl": "Condition/messy-cond-4",
                "resource": {
                    "resourceType": "Condition",
                    "id": "messy-cond-4",
                    "meta": {
                        "profile": ["https://www.medizininformatik-initiative.de/fhir/core/modul-diagnose/StructureDefinition/Diagnose"]
                    },
                    "code": {
                        "coding": [{
                            "system": "http://fhir.de/CodeSystem/bfarm/icd-10-gm",
                            "version": "2024",
                            "code": "E11.9"
                        }]
                    },
                    "subject": {"reference": "Patient/ALSO-MISSING"}  # Broken reference
                },
                "request": {"method": "PUT", "url": "Condition/messy-cond-4"}
            }
        ]
    }

    # Bundle 5: Missing MII profiles
    bundle5 = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "fullUrl": "Patient/messy-patient-5",
                "resource": {
                    "resourceType": "Patient",
                    "id": "messy-patient-5",
                    # Missing meta.profile (no MII profile)
                    "identifier": [{"value": "123"}],
                    "name": [{"family": "Test"}],
                    "gender": "other",
                    "birthDate": "2000-01-01"
                },
                "request": {"method": "PUT", "url": "Patient/messy-patient-5"}
            }
        ]
    }

    bundles = [
        ("messy_bundle_1_missing_fields.json", bundle1, "Missing required fields"),
        ("messy_bundle_2_invalid_dates.json", bundle2, "Invalid date formats"),
        ("messy_bundle_3_invalid_codes.json", bundle3, "Invalid ICD-10-GM codes and postal code"),
        ("messy_bundle_4_broken_refs.json", bundle4, "Broken patient references"),
        ("messy_bundle_5_no_profiles.json", bundle5, "Missing MII profiles"),
    ]

    for filename, bundle, description in bundles:
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(bundle, f, indent=2, ensure_ascii=False)
        print(f"✓ Created: {filename}")
        print(f"  Issues: {description}")

    print(f"\n✓ Created {len(bundles)} messy bundles in {output_dir}/")
    print("\nYou can now process these with the validator to demonstrate error detection!")
    return output_dir


if __name__ == "__main__":
    create_messy_bundles()
