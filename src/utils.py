"""
Utility functions for FHIR Quality Inspector
"""
import re
from typing import Dict, List, Any


def validate_german_postal_code(postal_code: str) -> bool:
    """Validate German postal code (5 digits)"""
    if not postal_code:
        return False
    return bool(re.match(r'^\d{5}$', postal_code))


def validate_icd10_gm_format(code: str) -> bool:
    """
    Validate ICD-10-GM code format (basic check)
    Format: Letter followed by digits and optional dots
    Examples: M80.15, S02.69, E11.9
    """
    if not code:
        return False
    return bool(re.match(r'^[A-Z]\d{2}(\.?\d{0,2})?$', code))


def validate_date_format(date_str: str) -> bool:
    """
    Validate FHIR date format (YYYY-MM-DD or full datetime)
    """
    if not date_str:
        return False
    # Basic check for YYYY-MM-DD format
    date_pattern = r'^\d{4}-\d{2}-\d{2}'
    return bool(re.match(date_pattern, date_str))


def extract_mii_profile_module(profile_url: str) -> str:
    """
    Extract MII module name from profile URL
    Example: https://www.medizininformatik-initiative.de/fhir/core/modul-person/StructureDefinition/Patient
    Returns: modul-person
    """
    if not profile_url or 'medizininformatik-initiative' not in profile_url:
        return "unknown"

    match = re.search(r'/modul-([^/]+)/', profile_url)
    if match:
        return f"modul-{match.group(1)}"
    return "unknown"


def calculate_quality_score(total_checks: int, passed_checks: int) -> float:
    """Calculate quality score percentage"""
    if total_checks == 0:
        return 0.0
    return round((passed_checks / total_checks) * 100, 2)
