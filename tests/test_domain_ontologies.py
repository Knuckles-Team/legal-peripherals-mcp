"""Legal practice-area domain ontology suite — validity, reuse, and cross-link
tests for the ``domain_<name>.ttl`` modules.

CONCEPT:LP-OS.governance.legal-domain-suite. Validates that each
``domain_regulatory.ttl`` / ``domain_employment.ttl`` / ``domain_commercial.ttl`` /
``domain_privacy.ttl`` / ``domain_corporate.ttl`` / ``domain_litigation.ttl`` module
parses as valid Turtle, imports ``compliance.ttl`` + ``legal.ttl``, declares its
expected classes, is discoverable through the ``scion_sdk.ontology_providers``
entry-point directory, and cross-links into the existing compliance/legal ontology
(FLSA, HIPAA, LLC) rather than floating disconnected. Mirrors
``test_compliance_ontology.py``'s style.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

rdflib = pytest.importorskip("rdflib")
from rdflib.namespace import OWL, RDF  # noqa: E402

ONTOLOGY_DIR = (
    Path(__file__).resolve().parent.parent / "legal_peripherals_mcp" / "ontology"
)
UPPER_TTL = ONTOLOGY_DIR / "compliance.ttl"
LEGAL_TTL = ONTOLOGY_DIR / "legal.ttl"
DOMAIN_TTLS = sorted(ONTOLOGY_DIR.glob("domain_*.ttl"))

class _SplitNamespace(rdflib.Namespace):
    """Names the connector declares live in its namespace; every other name is a core term."""

    _LOCAL = {'AgencyGuidance': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Assessment': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Attestation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSAAMLIndependentTestingAssessment': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSAAMLIndependentTestingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSAAMLProgramObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSAAMLTrainingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSABeneficialOwnershipControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSACTRFilingRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSACustomerDueDiligenceControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSAKYCObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSARecordkeepingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSARecordkeepingObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSASARComplianceRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSASARFilingRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSATransactionMonitoringControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSAWillfulViolationPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSA_AML': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BeneficiaryRole': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BoardResolution': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BreachNotification72HourControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BusinessEntity': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CCPA': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CCPACivilPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CCPAConsumerRightsObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CCPAOptOutComplianceRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CCPAOptOutObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPB': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBCivilPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBComplaintHandlingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBComplaintHandlingObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBComplaintReportingRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBConsumerProtection': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBDisclosureControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBDisclosureObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBUDAAPComplianceControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBUDAAPObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CUI': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CaliforniaPrivacyProtectionAgency': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CaseLaw': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ChronologyEvent': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ClaimChart': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ClosingChecklistItem': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Company': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ComplianceGapRemediation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ComplianceGate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ComplianceRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ConsentRecord': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Contract': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ContractAmendment': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ContractClause': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ContractReviewFinding': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Control': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CorporateGovernanceDoc': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DOLWHD': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DPIAProcessControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DSARFulfillmentControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DataProcessingAgreement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DataSubjectRequest': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DemandLetter': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Deposition': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DiligenceFinding': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoNotSellMechanismControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrank': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankCivilPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankConsumerProtectionObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankConsumerProtectionOversightControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankLivingWillControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankStressTestReportingRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankStressTestingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankSystemicRiskObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankVolckerComplianceProgramControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankVolckerRuleObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'EINApplication': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'EUDataProtectionAuthority': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Employee': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'EmploymentContract': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'EmploymentLawMatter': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'EnforcementAction': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'EntityComplianceDeadline': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'EscalationRoute': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ExampleLLCAnnualReportDeadline': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ExampleMarketingProcessingActivity': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ExampleMarketingProcessingActivityDPIA': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ExamplePHIVendorAgreement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ExampleWageHourChronologyEvent': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ExampleWageHourClaimChart': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ExampleWageHourMatter': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSA': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSABackWagesPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSAMinimumWageObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSAOvertimeObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSAOvertimeRuleGuidance': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSAPayrollComplianceControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSARecordkeepingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSARecordkeepingObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSATimekeepingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FSOC': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FederalIncomeTaxReturnRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FederalStatute': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FederalTaxation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FinCEN': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FinanceSector': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FinancialData': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'GDPR': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'GDPRAdministrativeFine': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'GDPRBreachNotificationObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'GDPRBreachNotificationRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'GDPRDPIAObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'GDPRDataSubjectRightsObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'GovernmentSector': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HHSOCR': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAA': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAAAccessControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAAAuditLogControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAABAAControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAABAAObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAABreachNotificationObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAABreachNotificationRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAABusinessAssociateAgreement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAACivilMonetaryPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAAEncryptionControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAAIncidentResponseControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAAMinimumNecessaryControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAAOmnibusRuleNotice': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAAPHIEncryptionRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAAPrivacyRuleObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAASecurityRuleObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HandbookPolicy': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'IRS': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'IntellectualProperty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'InternalInvestigation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'InternationalExpansionProject': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Jurisdiction': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCAdministrativeDissolutionPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCAnnualReportFilingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCAnnualReportObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCAnnualReportRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCFormationFiling': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCFormationGovernance': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCFormationObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCOperatingAgreementControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCOperatingAgreementObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCRegisteredAgentControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LeaveRequest': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LegalHold': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LegalMatter': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LegalPrecedent': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LegalTrust': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'MSAAgreement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'MaterialContract': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'MedicalSector': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'MisclassifiedContractorAssessment': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'MunicipalCode': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'NDAAgreement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCC': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCCBSASupervisionObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCCBankSupervision': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCCCallReportRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCCCapitalAdequacyControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCCCapitalAdequacyObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCCEnforcementActionPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCCExaminationReadinessControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCCSafetyAndSoundnessObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Obligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PCI': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PHI': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PHIEncryptionGapRemediation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PHIOnboardingComplianceGate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PII': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PayrollTaxDepositRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Penalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PrivacyImpactAssessment': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PrivateSector': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PrivilegeLogEntry': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ProcessingActivity': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'RegulatoryAuthority': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'RegulatoryChangeNotice': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'RegulatoryComment': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'RegulatoryFiling': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'RenewalDeadline': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ReportingRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'RestrictiveCovenant': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'SecretaryOfState': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Sector': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'SettlorRole': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'StateStatute': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Statute': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Subpoena': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TaxFilingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TaxFilingObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TaxPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TaxRecordkeepingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TaxRecordkeepingObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TaxWithholdingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TaxWithholdingObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TimekeepingHandbookPolicy': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TrusteeRole': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'VendorAgreement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'WorkerClassificationAssessment': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'WrittenConsent': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'amendsContract': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'amendsRegulation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'appliesForEntity': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'appliesToDataClass': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'appliesToSector': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'arisesFromObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'assessesActivity': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'attestsTo': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'blocksClosing': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'cancelByDate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'cfrPart': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'chartsCauseOfAction': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'citation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'classificationOutcome': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'classificationTriggersObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'closingStatus': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'commentDeadline': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'companyNumber': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'concernsDataSubject': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'conflictsWithParty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'deadlineFor': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'depositionWitness': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'derivedFromRegulation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'deviatesFromClause': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'documentedInPolicy': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'effectiveDate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'employedBy': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'employmentLawType': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'enforcedBy': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'enforcementTargets': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'escalatesFinding': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'evaluatesRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'eventSignificance': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'expandsToJurisdiction': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'expansionStructureType': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'filedBy': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'filingAgency': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'filingDeadline': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'filingStatus': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'filingType': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'findingCategory': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'findingSeverity': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'flaggedIn': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'governanceDocType': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'governedByDoc': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'governedByEmploymentStatute': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'governedByStatute': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'hasBeneficiary': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'hasClause': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'hasRenewalDeadline': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'hasReportingRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'hasSettlor': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'hasTrustee': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'holdStatus': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'imposesObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'incorporatedIn': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'incorporationDate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'investigates': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'involvesEmployee': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ipExpirationDate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ipFilingDate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ipRegistrationNumber': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ipStatus': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ipType': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'issuedByAuthority': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'issuedForMatter': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'lastAmended': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'leaveDecisionDeadline': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'leaveType': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'legalBasis': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'materialityThreshold': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'matterStatus': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'nextDueDate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'nextRefreshDate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'noticeWindowDays': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ownsIP': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'partOfMatter': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'precedentFor': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'precedentStrength': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'privilegeStatus': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'processesDataClass': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'processorRole': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'recordsConsent': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'registryStatus': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'remediatesGap': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'requestDeadline': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'requestType': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'requestedBy': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'requiresAttestation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'requiresControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'respondsToNotice': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'routesToApprover': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'statuteJurisdiction': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'subjectOfInvestigation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'subpoenaScope': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'subsidiaryOf': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'trackedByAssessment': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'tracksRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'triggeredByObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'trustAgreement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'trustType': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'uscSection': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'violation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#'}

    def term(self, name):
        return rdflib.URIRef(self._LOCAL[name] + name) if name in self._LOCAL else super().term(name)

    def __getitem__(self, key):
        return self.term(key) if isinstance(key, str) else super().__getitem__(key)


KG = _SplitNamespace("https://knuckles-team.github.io/ontology/core#")
CONNECTOR_NS = rdflib.Namespace("https://knuckles-team.github.io/ontology/connector/legal-peripherals#")
UPPER_IRI = rdflib.URIRef("https://knuckles-team.github.io/ontology/connector/legal-compliance")
LEGAL_IRI = rdflib.URIRef("https://knuckles-team.github.io/ontology/connector/legal")

DOMAIN_MODULES = {
    "domain_regulatory.ttl": {
        "iri": "https://knuckles-team.github.io/ontology/connector/legal-domain-regulatory",
        "classes": {
            "RegulatoryChangeNotice",
            "RegulatoryComment",
            "AgencyGuidance",
            "EnforcementAction",
            "ComplianceGapRemediation",
        },
    },
    "domain_employment.ttl": {
        "iri": "https://knuckles-team.github.io/ontology/connector/legal-domain-employment",
        "classes": {
            "Employee",
            "EmploymentContract",
            "RestrictiveCovenant",
            "HandbookPolicy",
            "WorkerClassificationAssessment",
            "InternalInvestigation",
            "LeaveRequest",
            "InternationalExpansionProject",
        },
    },
    "domain_commercial.ttl": {
        "iri": "https://knuckles-team.github.io/ontology/connector/legal-domain-commercial",
        "classes": {
            "Contract",
            "NDAAgreement",
            "MSAAgreement",
            "VendorAgreement",
            "ContractAmendment",
            "RenewalDeadline",
            "ContractReviewFinding",
            "EscalationRoute",
        },
    },
    "domain_privacy.ttl": {
        "iri": "https://knuckles-team.github.io/ontology/connector/legal-domain-privacy",
        "classes": {
            "DataSubjectRequest",
            "DataProcessingAgreement",
            "PrivacyImpactAssessment",
            "ProcessingActivity",
            "ConsentRecord",
        },
    },
    "domain_corporate.ttl": {
        "iri": "https://knuckles-team.github.io/ontology/connector/legal-domain-corporate",
        "classes": {
            "Company",
            "BoardResolution",
            "WrittenConsent",
            "DiligenceFinding",
            "MaterialContract",
            "ClosingChecklistItem",
            "EntityComplianceDeadline",
        },
    },
    "domain_litigation.ttl": {
        "iri": "https://knuckles-team.github.io/ontology/connector/legal-domain-litigation",
        "classes": {
            "DemandLetter",
            "LegalHold",
            "Deposition",
            "PrivilegeLogEntry",
            "Subpoena",
            "ClaimChart",
            "ChronologyEvent",
        },
    },
}


def _graph(*paths: Path) -> Any:
    g = rdflib.Graph()
    for p in paths:
        g.parse(str(p), format="turtle")
    return g


def _full_graph() -> Any:
    return _graph(
        UPPER_TTL, LEGAL_TTL, *ONTOLOGY_DIR.glob("compliance_*.ttl"), *DOMAIN_TTLS
    )


# --------------------------------------------------------------------------- #
# Provider discovery
# --------------------------------------------------------------------------- #


def test_provider_globs_all_domain_modules():
    """The ontology package dir carries every domain module; the hub loader globs
    ``*.ttl`` here with zero extra code."""
    import legal_peripherals_mcp.ontology as provider

    provider_dir = Path(provider.__file__).resolve().parent
    ttls = {p.name for p in provider_dir.glob("*.ttl")}
    for expected in DOMAIN_MODULES:
        assert expected in ttls, f"{expected} missing from ontology provider dir"


def test_init_docstring_documents_domain_modules():
    """The task requires each new domain module be added to __init__.py's docstring."""
    import legal_peripherals_mcp.ontology as provider

    doc = provider.__doc__ or ""
    for module_name in DOMAIN_MODULES:
        assert module_name in doc, (
            f"{module_name} not documented in ontology/__init__.py"
        )


# --------------------------------------------------------------------------- #
# Per-module structure
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("module_path", DOMAIN_TTLS, ids=lambda p: p.name)
def test_module_parses(module_path: Path):
    g = _graph(module_path)
    assert len(g) > 0


@pytest.mark.parametrize(
    "module_name,spec",
    sorted(DOMAIN_MODULES.items()),
    ids=lambda x: x if isinstance(x, str) else "",
)
def test_module_declares_ontology_iri_without_core_imports(
    module_name: str, spec: dict
):
    g = _graph(ONTOLOGY_DIR / module_name)
    onto_iri = rdflib.URIRef(spec["iri"])
    assert (onto_iri, RDF.type, OWL.Ontology) in g
    imports = {str(i) for i in g.objects(onto_iri, OWL.imports)}
    assert not {i for i in imports if i.startswith("https://knuckles-team.github.io/ontology/core")}, (
        f"{module_name} imports the core ontology; extend core classes instead"
    )


@pytest.mark.parametrize(
    "module_name,spec",
    sorted(DOMAIN_MODULES.items()),
    ids=lambda x: x if isinstance(x, str) else "",
)
def test_module_defines_expected_classes(module_name: str, spec: dict):
    g = _graph(ONTOLOGY_DIR / module_name)
    for cls in spec["classes"]:
        assert (
            KG[cls],
            RDF.type,
            OWL.Class,
        ) in g, f"{module_name}: missing class :{cls}"


# --------------------------------------------------------------------------- #
# Cross-domain links (the task's explicit ask: FLSA / HIPAA / LLC cross-links)
# --------------------------------------------------------------------------- #


def test_employment_worker_classification_cross_links_flsa_obligations():
    g = _full_graph()
    outcomes = list(
        g.objects(
            CONNECTOR_NS.MisclassifiedContractorAssessment, CONNECTOR_NS.classificationTriggersObligation
        )
    )
    assert CONNECTOR_NS.FLSAMinimumWageObligation in outcomes
    assert CONNECTOR_NS.FLSAOvertimeObligation in outcomes


def test_commercial_contract_cross_links_hipaa_attestation_via_dataclass():
    g = _full_graph()
    assert (CONNECTOR_NS.ExamplePHIVendorAgreement, KG.classifiedAs, CONNECTOR_NS.PHI) in g
    assert (CONNECTOR_NS.ExamplePHIVendorAgreement, KG.governedBy, CONNECTOR_NS.HIPAA) in g
    assert (
        CONNECTOR_NS.ExamplePHIVendorAgreement,
        CONNECTOR_NS.requiresAttestation,
        CONNECTOR_NS.HIPAABusinessAssociateAgreement,
    ) in g


def test_corporate_entity_compliance_deadline_tracks_llc_reporting_requirement():
    g = _full_graph()
    assert (
        CONNECTOR_NS.ExampleLLCAnnualReportDeadline,
        CONNECTOR_NS.tracksRequirement,
        CONNECTOR_NS.LLCAnnualReportRequirement,
    ) in g


def test_privacy_declares_gdpr_and_ccpa_tagged_pii():
    g = _full_graph()
    for reg in (CONNECTOR_NS.GDPR, CONNECTOR_NS.CCPA):
        assert (reg, RDF.type, KG.Regulation) in g
        assert (reg, CONNECTOR_NS.appliesToDataClass, CONNECTOR_NS.PII) in g
        obligations = list(g.objects(reg, CONNECTOR_NS.imposesObligation))
        assert obligations
        for ob in obligations:
            assert list(g.objects(ob, CONNECTOR_NS.requiresControl))


def test_litigation_matter_composes_with_employment_domain():
    """A litigation ClaimChart/ChronologyEvent attaches to the SAME EmploymentLawMatter
    individual employment's module would use — proving the domain modules compose on
    one shared entity rather than each owning a disconnected silo."""
    g = _full_graph()
    assert (CONNECTOR_NS.ExampleWageHourMatter, RDF.type, CONNECTOR_NS.EmploymentLawMatter) in g
    assert (CONNECTOR_NS.ExampleWageHourMatter, CONNECTOR_NS.governedByEmploymentStatute, CONNECTOR_NS.FLSA) in g
    assert (
        CONNECTOR_NS.ExampleWageHourClaimChart,
        CONNECTOR_NS.chartsCauseOfAction,
        CONNECTOR_NS.ExampleWageHourMatter,
    ) in g
    assert (
        CONNECTOR_NS.ExampleWageHourChronologyEvent,
        CONNECTOR_NS.partOfMatter,
        CONNECTOR_NS.ExampleWageHourMatter,
    ) in g


def test_regulatory_gap_remediation_cross_links_hipaa_requirement():
    g = _full_graph()
    assert (
        CONNECTOR_NS.PHIEncryptionGapRemediation,
        CONNECTOR_NS.remediatesGap,
        CONNECTOR_NS.HIPAAPHIEncryptionRequirement,
    ) in g


# --------------------------------------------------------------------------- #
# Full-suite integrity
# --------------------------------------------------------------------------- #


def test_full_suite_including_domain_modules_parses_as_one_graph():
    all_ttls = sorted(ONTOLOGY_DIR.glob("*.ttl"))
    g = _graph(*all_ttls)
    assert len(g) > 1000


def test_domain_modules_declare_no_duplicate_class_across_each_other():
    """No two domain modules primarily TYPE (rdf:type) the same local-named subject —
    intentional cross-file *enrichment* triples (e.g. domain_employment.ttl adding
    :documentedInPolicy to compliance_flsa.ttl's :FLSATimekeepingControl) are fine and
    expected; a duplicate ``a owl:Class``/individual declaration is not."""
    typed_subject_owners: dict[str, set[str]] = {}
    for ttl in DOMAIN_TTLS:
        g = _graph(ttl)
        for s in set(g.subjects(RDF.type, None)):
            if str(s).startswith(str(KG)):
                typed_subject_owners.setdefault(str(s), set()).add(ttl.name)
    collisions = {
        s: owners for s, owners in typed_subject_owners.items() if len(owners) > 1
    }
    assert not collisions, (
        f"duplicate type declarations across domain modules: {collisions}"
    )


def test_new_classes_do_not_redefine_existing_upper_or_legal_or_compliance_classes():
    """Guards against the domain modules accidentally redeclaring a class already
    owned by compliance.ttl / legal.ttl / another compliance_<x>.ttl module."""
    already_declared: set[str] = set()
    for ttl in [UPPER_TTL, LEGAL_TTL, *sorted(ONTOLOGY_DIR.glob("compliance_*.ttl"))]:
        g = _graph(ttl)
        already_declared |= {
            str(s).rsplit("#", 1)[-1] for s in g.subjects(RDF.type, OWL.Class)
        }
    for module_name, spec in DOMAIN_MODULES.items():
        overlap = spec["classes"] & already_declared
        assert not overlap, f"{module_name} redeclares existing class(es): {overlap}"
