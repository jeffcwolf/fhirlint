"""
FHIR Bundle Validator
Parses and validates FHIR bundles using fhir.resources library
"""
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from fhir.resources.bundle import Bundle
    from fhir.resources.patient import Patient
    from fhir.resources.encounter import Encounter
    from fhir.resources.condition import Condition
    from fhir.resources.medication import Medication
    from fhir.resources.medicationadministration import MedicationAdministration
    from fhir.resources.consent import Consent
except ImportError:
    print("Warning: fhir.resources not installed. Run: pip install -r requirements.txt")
    Bundle = None

from utils import extract_mii_profile_module


class BundleValidator:
    """Validates FHIR bundles and extracts metadata"""

    def __init__(self):
        self.results = {}

    def load_bundle(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load and parse a FHIR bundle from JSON file
        Uses lenient parsing to handle real-world FHIR data

        Returns:
            Dictionary with bundle metadata and validation results
        """
        result = {
            'file_path': file_path,
            'file_name': Path(file_path).name,
            'valid': False,
            'error': None,
            'bundle_type': None,
            'entry_count': 0,
            'resource_types': {},
            'mii_modules': set(),
            'bundle_data': None,
            'schema_errors': []
        }

        try:
            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            # Check if it's a Bundle
            if json_data.get('resourceType') != 'Bundle':
                result['error'] = f"Not a Bundle resource. Found: {json_data.get('resourceType')}"
                return result

            # Store raw bundle data for quality checks
            result['bundle_data'] = json_data
            result['bundle_type'] = json_data.get('type')
            result['valid'] = True

            # Try strict validation with fhir.resources (optional)
            if Bundle is not None:
                try:
                    Bundle.parse_obj(json_data)
                except Exception as e:
                    # Capture schema errors but don't fail
                    result['schema_errors'].append(f"FHIR schema validation: {str(e)[:200]}")

            # Extract entries (lenient approach)
            entries = json_data.get('entry', [])
            if entries:
                result['entry_count'] = len(entries)

                # Count resource types and extract MII profiles
                for entry in entries:
                    resource = entry.get('resource', {})
                    resource_type = resource.get('resourceType')

                    if resource_type:
                        # Count resource types
                        if resource_type not in result['resource_types']:
                            result['resource_types'][resource_type] = 0
                        result['resource_types'][resource_type] += 1

                        # Extract MII profile from meta
                        meta = resource.get('meta', {})
                        profiles = meta.get('profile', [])
                        for profile_url in profiles:
                            module = extract_mii_profile_module(profile_url)
                            if module != "unknown":
                                result['mii_modules'].add(module)

            # Convert set to list for JSON serialization
            result['mii_modules'] = list(result['mii_modules'])

        except json.JSONDecodeError as e:
            result['error'] = f"Invalid JSON: {str(e)}"
        except Exception as e:
            result['error'] = f"Error loading bundle: {str(e)}"

        return result

    def validate_bundle_structure(self, bundle_result: Dict[str, Any]) -> List[str]:
        """
        Validate bundle structure and return list of issues
        """
        issues = []

        if not bundle_result['valid']:
            issues.append(f"Bundle validation failed: {bundle_result['error']}")
            return issues

        # Check bundle type
        if bundle_result['bundle_type'] not in ['transaction', 'collection', 'batch']:
            issues.append(f"Unusual bundle type: {bundle_result['bundle_type']}")

        # Check if bundle has entries
        if bundle_result['entry_count'] == 0:
            issues.append("Bundle is empty (no entries)")

        # Check if MII profiles are present
        if len(bundle_result['mii_modules']) == 0:
            issues.append("No MII profiles detected in bundle")

        return issues

    def get_summary(self, bundle_result: Dict[str, Any]) -> str:
        """Generate human-readable summary of bundle"""
        if not bundle_result['valid']:
            return f"❌ Invalid: {bundle_result['error']}"

        summary_parts = [
            f"✓ Bundle type: {bundle_result['bundle_type']}",
            f"✓ Entries: {bundle_result['entry_count']}",
            f"✓ Resource types: {', '.join(bundle_result['resource_types'].keys())}",
            f"✓ MII modules: {', '.join(bundle_result['mii_modules']) if bundle_result['mii_modules'] else 'None detected'}"
        ]

        return "\n".join(summary_parts)
