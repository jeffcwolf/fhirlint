"""
FHIR Data Quality Checker
Implements MII Kerndatensatz quality rules
"""
from typing import Dict, List, Any
from utils import (
    validate_german_postal_code,
    validate_icd10_gm_format,
    validate_date_format,
    calculate_quality_score
)


class QualityIssue:
    """Represents a data quality issue"""

    def __init__(self, severity: str, category: str, description: str,
                 resource_type: str = None, resource_id: str = None):
        self.severity = severity  # 'error', 'warning', 'info'
        self.category = category  # 'missing_data', 'invalid_format', 'reference', 'terminology'
        self.description = description
        self.resource_type = resource_type
        self.resource_id = resource_id

    def __repr__(self):
        return f"[{self.severity.upper()}] {self.description}"

    def to_dict(self):
        return {
            'severity': self.severity,
            'category': self.category,
            'description': self.description,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id
        }


class QualityChecker:
    """Checks FHIR bundle data quality against MII rules"""

    def __init__(self):
        self.issues = []
        self.checks_performed = 0
        self.checks_passed = 0

    def check_bundle(self, bundle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all quality checks on a bundle

        Returns:
            Dictionary with quality analysis results
        """
        self.issues = []
        self.checks_performed = 0
        self.checks_passed = 0

        if not bundle_data:
            return self._get_results()

        entries = bundle_data.get('entry', [])

        # Collect all resources by type
        resources = {
            'Patient': [],
            'Encounter': [],
            'Condition': [],
            'Medication': [],
            'MedicationAdministration': [],
            'Consent': []
        }

        for entry in entries:
            resource = entry.get('resource', {})
            resource_type = resource.get('resourceType')
            if resource_type in resources:
                resources[resource_type].append(resource)

        # Run quality checks by resource type
        for patient in resources['Patient']:
            self._check_patient(patient)

        for encounter in resources['Encounter']:
            self._check_encounter(encounter)

        for condition in resources['Condition']:
            self._check_condition(condition)

        for medication in resources['Medication']:
            self._check_medication(medication)

        for med_admin in resources['MedicationAdministration']:
            self._check_medication_administration(med_admin)

        # Cross-resource checks
        self._check_references(resources)

        return self._get_results()

    def _check_patient(self, patient: Dict[str, Any]):
        """Check Patient resource quality"""
        resource_id = patient.get('id', 'unknown')

        # Check MII profile
        self._check_mii_profile(patient, 'modul-person', resource_id)

        # Required fields
        self._check_required_field(patient, 'identifier', 'Patient', resource_id)
        self._check_required_field(patient, 'name', 'Patient', resource_id)
        self._check_required_field(patient, 'gender', 'Patient', resource_id)
        self._check_required_field(patient, 'birthDate', 'Patient', resource_id)

        # Birth date format
        birth_date = patient.get('birthDate')
        if birth_date:
            if not validate_date_format(birth_date):
                self._add_issue('error', 'invalid_format',
                               f"Invalid birthDate format: {birth_date}", 'Patient', resource_id)
                self.checks_performed += 1
            else:
                self.checks_performed += 1
                self.checks_passed += 1

        # German postal code validation
        addresses = patient.get('address', [])
        for addr in addresses:
            postal_code = addr.get('postalCode')
            if postal_code:
                if not validate_german_postal_code(postal_code):
                    self._add_issue('warning', 'invalid_format',
                                   f"Invalid German postal code: {postal_code}", 'Patient', resource_id)
                    self.checks_performed += 1
                else:
                    self.checks_performed += 1
                    self.checks_passed += 1

    def _check_encounter(self, encounter: Dict[str, Any]):
        """Check Encounter resource quality"""
        resource_id = encounter.get('id', 'unknown')

        # Check MII profile
        self._check_mii_profile(encounter, 'modul-fall', resource_id)

        # Required fields
        self._check_required_field(encounter, 'status', 'Encounter', resource_id)
        self._check_required_field(encounter, 'class', 'Encounter', resource_id)
        self._check_required_field(encounter, 'subject', 'Encounter', resource_id)

        # Period dates
        period = encounter.get('period', {})
        if period:
            start = period.get('start')
            end = period.get('end')

            if start and not validate_date_format(start):
                self._add_issue('error', 'invalid_format',
                               f"Invalid encounter start date: {start}", 'Encounter', resource_id)
                self.checks_performed += 1
            elif start:
                self.checks_performed += 1
                self.checks_passed += 1

            if end and not validate_date_format(end):
                self._add_issue('error', 'invalid_format',
                               f"Invalid encounter end date: {end}", 'Encounter', resource_id)
                self.checks_performed += 1
            elif end:
                self.checks_performed += 1
                self.checks_passed += 1

    def _check_condition(self, condition: Dict[str, Any]):
        """Check Condition resource quality (ICD-10-GM)"""
        resource_id = condition.get('id', 'unknown')

        # Check MII profile
        self._check_mii_profile(condition, 'modul-diagnose', resource_id)

        # Required fields
        self._check_required_field(condition, 'code', 'Condition', resource_id)
        self._check_required_field(condition, 'subject', 'Condition', resource_id)

        # ICD-10-GM code validation
        code = condition.get('code', {})
        codings = code.get('coding', [])

        for coding in codings:
            system = coding.get('system', '')
            code_value = coding.get('code', '')

            # Check if it's ICD-10-GM
            if 'icd-10-gm' in system.lower():
                if not validate_icd10_gm_format(code_value):
                    self._add_issue('warning', 'terminology',
                                   f"Invalid ICD-10-GM code format: {code_value}", 'Condition', resource_id)
                    self.checks_performed += 1
                else:
                    self.checks_performed += 1
                    self.checks_passed += 1

                # Check if version is specified
                version = coding.get('version')
                if not version:
                    self._add_issue('info', 'terminology',
                                   f"ICD-10-GM version not specified for code {code_value}",
                                   'Condition', resource_id)
                    self.checks_performed += 1
                else:
                    self.checks_performed += 1
                    self.checks_passed += 1

    def _check_medication(self, medication: Dict[str, Any]):
        """Check Medication resource quality"""
        resource_id = medication.get('id', 'unknown')

        # Check MII profile
        self._check_mii_profile(medication, 'modul-medikation', resource_id)

        # Check if code is present
        code = medication.get('code')
        if not code:
            self._add_issue('warning', 'missing_data',
                           "Medication code is missing", 'Medication', resource_id)
            self.checks_performed += 1
        else:
            self.checks_performed += 1
            self.checks_passed += 1

    def _check_medication_administration(self, med_admin: Dict[str, Any]):
        """Check MedicationAdministration resource quality"""
        resource_id = med_admin.get('id', 'unknown')

        # Check MII profile
        self._check_mii_profile(med_admin, 'modul-medikation', resource_id)

        # Required fields
        self._check_required_field(med_admin, 'status', 'MedicationAdministration', resource_id)
        self._check_required_field(med_admin, 'subject', 'MedicationAdministration', resource_id)

    def _check_references(self, resources: Dict[str, List]):
        """Check reference integrity across resources"""
        # Get all Patient IDs
        patient_ids = set(p.get('id') for p in resources['Patient'] if p.get('id'))

        # Check Encounter references to Patient
        for encounter in resources['Encounter']:
            subject_ref = encounter.get('subject', {}).get('reference', '')
            if subject_ref:
                # Extract patient ID from reference (e.g., "Patient/123")
                if '/' in subject_ref:
                    ref_id = subject_ref.split('/')[-1]
                    if ref_id not in patient_ids:
                        self._add_issue('error', 'reference',
                                       f"Encounter references non-existent Patient: {subject_ref}",
                                       'Encounter', encounter.get('id'))
                        self.checks_performed += 1
                    else:
                        self.checks_performed += 1
                        self.checks_passed += 1

        # Check Condition references to Patient
        for condition in resources['Condition']:
            subject_ref = condition.get('subject', {}).get('reference', '')
            if subject_ref:
                if '/' in subject_ref:
                    ref_id = subject_ref.split('/')[-1]
                    if ref_id not in patient_ids:
                        self._add_issue('error', 'reference',
                                       f"Condition references non-existent Patient: {subject_ref}",
                                       'Condition', condition.get('id'))
                        self.checks_performed += 1
                    else:
                        self.checks_performed += 1
                        self.checks_passed += 1

    def _check_mii_profile(self, resource: Dict[str, Any], expected_module: str, resource_id: str):
        """Check if resource has MII profile"""
        meta = resource.get('meta', {})
        profiles = meta.get('profile', [])

        has_mii_profile = any(expected_module in p for p in profiles)

        if not has_mii_profile:
            self._add_issue('warning', 'missing_data',
                           f"Missing MII {expected_module} profile",
                           resource.get('resourceType'), resource_id)
            self.checks_performed += 1
        else:
            self.checks_performed += 1
            self.checks_passed += 1

    def _check_required_field(self, resource: Dict[str, Any], field_name: str,
                              resource_type: str, resource_id: str):
        """Check if required field is present and non-empty"""
        value = resource.get(field_name)

        if value is None or (isinstance(value, (list, str)) and len(value) == 0):
            self._add_issue('error', 'missing_data',
                           f"Required field '{field_name}' is missing or empty",
                           resource_type, resource_id)
            self.checks_performed += 1
        else:
            self.checks_performed += 1
            self.checks_passed += 1

    def _add_issue(self, severity: str, category: str, description: str,
                   resource_type: str = None, resource_id: str = None):
        """Add a quality issue"""
        issue = QualityIssue(severity, category, description, resource_type, resource_id)
        self.issues.append(issue)

    def _get_results(self) -> Dict[str, Any]:
        """Get quality check results"""
        # Count issues by severity
        errors = sum(1 for i in self.issues if i.severity == 'error')
        warnings = sum(1 for i in self.issues if i.severity == 'warning')
        infos = sum(1 for i in self.issues if i.severity == 'info')

        # Calculate quality score
        quality_score = calculate_quality_score(self.checks_performed, self.checks_passed)

        return {
            'quality_score': quality_score,
            'checks_performed': self.checks_performed,
            'checks_passed': self.checks_passed,
            'total_issues': len(self.issues),
            'errors': errors,
            'warnings': warnings,
            'infos': infos,
            'issues': [issue.to_dict() for issue in self.issues],
            'passed': errors == 0  # Bundle passes if no errors
        }
