"""Regulatory/legal compliance ontology suite — validity, reuse, and cross-link tests.

CONCEPT:LP-OS.governance.compliance-ontology-suite. Validates that ``compliance.ttl``
(the shared upper ontology) and each ``compliance_<framework>.ttl`` module parse as
valid Turtle, declare the expected classes/individuals, import the upper ontology,
reuse (never redefine) the shared hub/legal.ttl classes, and are discoverable through
the package's ``scion_sdk.ontology_providers`` entry-point directory. Also proves
the asset -> data-classification -> regulation join the suite exists for (e.g. a PHI
asset resolves to HIPAA via :classifiedAs/:appliesToDataClass, and directly via
:governedBy).
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
MODULE_TTLS = sorted(ONTOLOGY_DIR.glob("compliance_*.ttl"))

class _SplitNamespace(rdflib.Namespace):
    """Names the connector declares live in its namespace; every other name is a core term."""

    _LOCAL = {'AgencyGuidance': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Assessment': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Attestation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSAAMLIndependentTestingAssessment': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSAAMLIndependentTestingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSAAMLProgramObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSAAMLTrainingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSABeneficialOwnershipControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSACTRFilingRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSACustomerDueDiligenceControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSAKYCObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSARecordkeepingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSARecordkeepingObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSASARComplianceRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSASARFilingRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSATransactionMonitoringControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSAWillfulViolationPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BSA_AML': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BeneficiaryRole': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BoardResolution': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BreachNotification72HourControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'BusinessEntity': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CCPA': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CCPACivilPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CCPAConsumerRightsObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CCPAOptOutComplianceRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CCPAOptOutObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPB': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBCivilPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBComplaintHandlingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBComplaintHandlingObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBComplaintReportingRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBConsumerProtection': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBDisclosureControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBDisclosureObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBUDAAPComplianceControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CFPBUDAAPObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CUI': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CaliforniaPrivacyProtectionAgency': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CaseLaw': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ChronologyEvent': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ClaimChart': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ClosingChecklistItem': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Company': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ComplianceGapRemediation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ComplianceGate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ComplianceRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ConsentRecord': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Contract': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ContractAmendment': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ContractClause': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ContractReviewFinding': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Control': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'CorporateGovernanceDoc': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DOLWHD': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DPIAProcessControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DSARFulfillmentControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DataProcessingAgreement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DataSubjectRequest': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DemandLetter': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Deposition': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DiligenceFinding': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoNotSellMechanismControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrank': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankCivilPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankConsumerProtectionObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankConsumerProtectionOversightControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankLivingWillControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankStressTestReportingRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankStressTestingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankSystemicRiskObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankVolckerComplianceProgramControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'DoddFrankVolckerRuleObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'EINApplication': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'EUDataProtectionAuthority': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Employee': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'EmploymentContract': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'EmploymentLawMatter': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'EnforcementAction': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'EntityComplianceDeadline': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'EscalationRoute': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ExampleLLCAnnualReportDeadline': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ExampleMarketingProcessingActivity': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ExampleMarketingProcessingActivityDPIA': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ExamplePHIVendorAgreement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ExampleWageHourChronologyEvent': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ExampleWageHourClaimChart': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ExampleWageHourMatter': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSA': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSABackWagesPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSAMinimumWageObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSAOvertimeObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSAOvertimeRuleGuidance': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSAPayrollComplianceControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSARecordkeepingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSARecordkeepingObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FLSATimekeepingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FSOC': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FederalIncomeTaxReturnRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FederalStatute': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FederalTaxation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FinCEN': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FinanceSector': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'FinancialData': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'GDPR': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'GDPRAdministrativeFine': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'GDPRBreachNotificationObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'GDPRBreachNotificationRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'GDPRDPIAObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'GDPRDataSubjectRightsObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'GovernmentSector': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HHSOCR': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAA': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAAAccessControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAAAuditLogControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAABAAControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAABAAObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAABreachNotificationObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAABreachNotificationRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAABusinessAssociateAgreement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAACivilMonetaryPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAAEncryptionControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAAIncidentResponseControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAAMinimumNecessaryControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAAOmnibusRuleNotice': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAAPHIEncryptionRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAAPrivacyRuleObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HIPAASecurityRuleObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'HandbookPolicy': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'IRS': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'IntellectualProperty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'InternalInvestigation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'InternationalExpansionProject': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Jurisdiction': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCAdministrativeDissolutionPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCAnnualReportFilingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCAnnualReportObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCAnnualReportRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCFormationFiling': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCFormationGovernance': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCFormationObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCOperatingAgreementControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCOperatingAgreementObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LLCRegisteredAgentControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LeaveRequest': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LegalHold': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LegalMatter': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LegalPrecedent': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'LegalTrust': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'MSAAgreement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'MaterialContract': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'MedicalSector': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'MisclassifiedContractorAssessment': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'MunicipalCode': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'NDAAgreement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCC': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCCBSASupervisionObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCCBankSupervision': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCCCallReportRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCCCapitalAdequacyControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCCCapitalAdequacyObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCCEnforcementActionPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCCExaminationReadinessControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'OCCSafetyAndSoundnessObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Obligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PCI': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PHI': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PHIEncryptionGapRemediation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PHIOnboardingComplianceGate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PII': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PayrollTaxDepositRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Penalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PrivacyImpactAssessment': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PrivateSector': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'PrivilegeLogEntry': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ProcessingActivity': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'RegulatoryAuthority': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'RegulatoryChangeNotice': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'RegulatoryComment': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'RegulatoryFiling': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'RenewalDeadline': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ReportingRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'RestrictiveCovenant': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'SecretaryOfState': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Sector': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'SettlorRole': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'StateStatute': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Statute': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'Subpoena': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TaxFilingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TaxFilingObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TaxPenalty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TaxRecordkeepingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TaxRecordkeepingObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TaxWithholdingControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TaxWithholdingObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TimekeepingHandbookPolicy': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'TrusteeRole': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'VendorAgreement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'WorkerClassificationAssessment': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'WrittenConsent': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'amendsContract': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'amendsRegulation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'appliesForEntity': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'appliesToDataClass': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'appliesToSector': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'arisesFromObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'assessesActivity': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'attestsTo': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'blocksClosing': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'cancelByDate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'cfrPart': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'chartsCauseOfAction': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'citation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'classificationOutcome': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'classificationTriggersObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'closingStatus': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'commentDeadline': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'companyNumber': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'concernsDataSubject': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'conflictsWithParty': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'deadlineFor': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'depositionWitness': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'derivedFromRegulation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'deviatesFromClause': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'documentedInPolicy': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'effectiveDate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'employedBy': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'employmentLawType': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'enforcedBy': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'enforcementTargets': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'escalatesFinding': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'evaluatesRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'eventSignificance': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'expandsToJurisdiction': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'expansionStructureType': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'filedBy': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'filingAgency': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'filingDeadline': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'filingStatus': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'filingType': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'findingCategory': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'findingSeverity': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'flaggedIn': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'governanceDocType': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'governedByDoc': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'governedByEmploymentStatute': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'governedByStatute': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'hasBeneficiary': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'hasClause': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'hasRenewalDeadline': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'hasReportingRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'hasSettlor': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'hasTrustee': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'holdStatus': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'imposesObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'incorporatedIn': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'incorporationDate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'investigates': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'involvesEmployee': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ipExpirationDate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ipFilingDate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ipRegistrationNumber': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ipStatus': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ipType': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'issuedByAuthority': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'issuedForMatter': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'lastAmended': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'leaveDecisionDeadline': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'leaveType': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'legalBasis': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'materialityThreshold': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'matterStatus': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'nextDueDate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'nextRefreshDate': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'noticeWindowDays': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'ownsIP': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'partOfMatter': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'precedentFor': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'precedentStrength': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'privilegeStatus': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'processesDataClass': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'processorRole': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'recordsConsent': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'registryStatus': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'remediatesGap': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'requestDeadline': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'requestType': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'requestedBy': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'requiresAttestation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'requiresControl': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'respondsToNotice': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'routesToApprover': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'statuteJurisdiction': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'subjectOfInvestigation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'subpoenaScope': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'subsidiaryOf': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'trackedByAssessment': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'tracksRequirement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'triggeredByObligation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'trustAgreement': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'trustType': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'uscSection': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#', 'violation': 'https://knuckles-team.github.io/ontology/connector/legal-peripherals#'}

    def term(self, name):
        return rdflib.URIRef(self._LOCAL[name] + name) if name in self._LOCAL else super().term(name)

    def __getitem__(self, key):
        return self.term(key) if isinstance(key, str) else super().__getitem__(key)


KG = _SplitNamespace("https://knuckles-team.github.io/ontology/core#")
CONNECTOR_NS = rdflib.Namespace("https://knuckles-team.github.io/ontology/connector/legal-peripherals#")
HUB_IRI = rdflib.URIRef("https://knuckles-team.github.io/ontology/core")
LEGAL_IRI = rdflib.URIRef("https://knuckles-team.github.io/ontology/connector/legal")
UPPER_IRI = rdflib.URIRef("https://knuckles-team.github.io/ontology/connector/legal-compliance")

EXPECTED_UPPER_CLASSES = {
    "RegulatoryAuthority",
    "Obligation",
    "Control",
    "ComplianceRequirement",
    "Penalty",
    "Sector",
    "ReportingRequirement",
    "ComplianceGate",
    "Assessment",
    "Attestation",
}

EXPECTED_UPPER_PROPERTIES = {
    "appliesToSector",
    "appliesToDataClass",
    "imposesObligation",
    "requiresControl",
    "hasReportingRequirement",
    "triggeredByObligation",
    "enforcedBy",
    "violation",
    "derivedFromRegulation",
    "evaluatesRequirement",
    "attestsTo",
}

# Classes/properties this suite must REUSE (not redefine) — already declared in
# scion_sdk' hub ontology.ttl or this package's legal.ttl.
SHARED_CLASSES_NOT_REDEFINED = {
    "Regulation",
    "DataClassification",
    "Organization",
    "System",
    "GovernedEntity",
    "Jurisdiction",
    "Statute",
    "FederalStatute",
    "StateStatute",
    "RegulatoryFiling",
    "BusinessEntity",
    "CorporateGovernanceDoc",
}
SHARED_PROPERTIES_NOT_REDEFINED = {"governedBy", "classifiedAs"}

MODULE_REGULATIONS = {
    "compliance_hipaa.ttl": "HIPAA",
    "compliance_bsa_aml.ttl": "BSA_AML",
    "compliance_occ.ttl": "OCCBankSupervision",
    "compliance_dodd_frank.ttl": "DoddFrank",
    "compliance_cfpb.ttl": "CFPBConsumerProtection",
    "compliance_flsa.ttl": "FLSA",
    "compliance_taxation.ttl": "FederalTaxation",
    "compliance_llc.ttl": "LLCFormationGovernance",
}


def _graph(*paths: Path) -> Any:
    g = rdflib.Graph()
    for p in paths:
        g.parse(str(p), format="turtle")
    return g


def _full_graph() -> Any:
    return _graph(UPPER_TTL, *MODULE_TTLS)


# --------------------------------------------------------------------------- #
# Provider discovery
# --------------------------------------------------------------------------- #


def test_provider_globs_all_compliance_modules():
    """The ontology package dir carries the upper ontology + every regulation module the
    task requires; the hub loader globs ``*.ttl`` here with zero extra code."""
    import legal_peripherals_mcp.ontology as provider

    provider_dir = Path(provider.__file__).resolve().parent
    ttls = {p.name for p in provider_dir.glob("*.ttl")}
    assert "legal.ttl" in ttls
    assert "compliance.ttl" in ttls
    for expected in MODULE_REGULATIONS:
        assert expected in ttls, f"{expected} missing from ontology provider dir"


# --------------------------------------------------------------------------- #
# Upper ontology
# --------------------------------------------------------------------------- #


def test_upper_ontology_parses_and_has_iri():
    g = _graph(UPPER_TTL)
    assert len(g) > 0
    assert (UPPER_IRI, RDF.type, OWL.Ontology) in g
    assert not set(g.objects(UPPER_IRI, OWL.imports))


def test_upper_ontology_defines_expected_classes():
    g = _graph(UPPER_TTL)
    for cls in EXPECTED_UPPER_CLASSES:
        assert (KG[cls], RDF.type, OWL.Class) in g, f"missing class :{cls}"


def test_upper_ontology_defines_expected_properties():
    g = _graph(UPPER_TTL)
    for prop in EXPECTED_UPPER_PROPERTIES:
        assert (
            KG[prop],
            RDF.type,
            OWL.ObjectProperty,
        ) in g, f"missing property :{prop}"


def test_upper_ontology_declares_canonical_individuals():
    g = _graph(UPPER_TTL)
    for sector in (
        "FinanceSector",
        "MedicalSector",
        "GovernmentSector",
        "PrivateSector",
    ):
        assert (KG[sector], RDF.type, CONNECTOR_NS.Sector) in g
    for dataclass in ("PHI", "PII", "PCI", "FinancialData", "CUI"):
        assert (KG[dataclass], RDF.type, KG.DataClassification) in g


def test_upper_ontology_reuses_shared_classes_not_redefines():
    """The compliance suite must reference — never redefine as owl:Class/owl:ObjectProperty —
    classes/properties the hub ontology or this package's legal.ttl already declare."""
    text = UPPER_TTL.read_text()
    for shared in SHARED_CLASSES_NOT_REDEFINED:
        assert f":{shared} a owl:Class" not in text, f":{shared} redefined as owl:Class"
    for shared in SHARED_PROPERTIES_NOT_REDEFINED:
        assert f":{shared} a owl:ObjectProperty" not in text, (
            f":{shared} redefined as owl:ObjectProperty"
        )
    # but it DOES reference :Regulation/:DataClassification/:governedBy/:classifiedAs
    assert ":Regulation" in text
    assert ":DataClassification" in text


# --------------------------------------------------------------------------- #
# Per-regulation modules
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("module_path", MODULE_TTLS, ids=lambda p: p.name)
def test_module_parses(module_path: Path):
    g = _graph(module_path)
    assert len(g) > 0


@pytest.mark.parametrize("module_path", MODULE_TTLS, ids=lambda p: p.name)
def test_module_declares_one_ontology_and_imports_no_core(module_path: Path):
    g = _graph(module_path)
    ontologies = list(g.subjects(RDF.type, OWL.Ontology))
    assert len(ontologies) == 1, (
        f"{module_path.name} must declare exactly one owl:Ontology"
    )
    imports = {str(i) for i in g.objects(ontologies[0], OWL.imports)}
    assert not {i for i in imports if i.startswith("https://knuckles-team.github.io/ontology/core")}, (
        f"{module_path.name} imports the core ontology; extend core classes instead"
    )


@pytest.mark.parametrize("module_name,regulation", sorted(MODULE_REGULATIONS.items()))
def test_module_declares_its_regulation_tagged_sector_and_dataclass(
    module_name: str, regulation: str
):
    """Each regulation module declares a :Regulation individual tagged with at least one
    :appliesToSector and one :appliesToDataClass, and names a :RegulatoryAuthority via
    :enforcedBy — the sector/domain-class tagging the task requires."""
    g = _graph(ONTOLOGY_DIR / module_name)
    reg_uri = KG[regulation]
    assert (
        reg_uri,
        RDF.type,
        KG.Regulation,
    ) in g, f"{module_name}: {regulation} not a :Regulation"
    sectors = list(g.objects(reg_uri, CONNECTOR_NS.appliesToSector))
    assert sectors, f"{module_name}: {regulation} has no :appliesToSector"
    dataclasses = list(g.objects(reg_uri, CONNECTOR_NS.appliesToDataClass))
    assert dataclasses, f"{module_name}: {regulation} has no :appliesToDataClass"
    authorities = list(g.objects(reg_uri, CONNECTOR_NS.enforcedBy))
    assert authorities, f"{module_name}: {regulation} has no :enforcedBy authority"
    for authority in authorities:
        assert (authority, RDF.type, CONNECTOR_NS.RegulatoryAuthority) in g


@pytest.mark.parametrize("module_name,regulation", sorted(MODULE_REGULATIONS.items()))
def test_module_obligations_have_controls(module_name: str, regulation: str):
    """Every Obligation a Regulation imposes requires at least one Control."""
    g = _graph(ONTOLOGY_DIR / module_name)
    reg_uri = KG[regulation]
    obligations = list(g.objects(reg_uri, CONNECTOR_NS.imposesObligation))
    assert obligations, f"{module_name}: {regulation} imposes no obligations"
    for ob in obligations:
        assert (ob, RDF.type, CONNECTOR_NS.Obligation) in g
        controls = list(g.objects(ob, CONNECTOR_NS.requiresControl))
        assert controls, f"{module_name}: {ob} has no :requiresControl"
        for c in controls:
            assert (c, RDF.type, CONNECTOR_NS.Control) in g


def test_sar_reporting_requirement_cross_references_aml_obligation():
    """Cross-reference required by spec: the BSA SAR ReportingRequirement is triggered by
    an AML Obligation."""
    g = _graph(ONTOLOGY_DIR / "compliance_bsa_aml.ttl")
    assert (CONNECTOR_NS.BSASARFilingRequirement, RDF.type, CONNECTOR_NS.ReportingRequirement) in g
    triggers = list(g.objects(CONNECTOR_NS.BSASARFilingRequirement, CONNECTOR_NS.triggeredByObligation))
    assert CONNECTOR_NS.BSAAMLProgramObligation in triggers


def test_llc_module_reuses_legal_ttl_formation_filing_class():
    """The LLC module must reference (not redefine) legal.ttl's :LLCFormationFiling class,
    reusing the package's existing Secretary-of-State/EIN capability."""
    text = (ONTOLOGY_DIR / "compliance_llc.ttl").read_text()
    assert ":LLCFormationFiling a owl:Class" not in text
    assert ":LLCFormationFiling" in text  # referenced in commentary/documentation


# --------------------------------------------------------------------------- #
# Full-suite integrity
# --------------------------------------------------------------------------- #


def test_full_suite_parses_as_one_graph_with_no_local_name_collisions():
    """All ttl files in the ontology dir load together into one graph (the way the hub
    federates them) and no individual/class is declared (as subject) in more than one
    compliance module."""
    all_ttls = sorted(ONTOLOGY_DIR.glob("*.ttl"))
    g = _graph(*all_ttls)
    assert len(g) > 500

    subject_owners: dict[str, set[str]] = {}
    for ttl in [p for p in all_ttls if p.name.startswith("compliance")]:
        mg = _graph(ttl)
        for s in set(mg.subjects()):
            if str(s).startswith(str(KG)):
                subject_owners.setdefault(str(s), set()).add(ttl.name)
    collisions = {s: owners for s, owners in subject_owners.items() if len(owners) > 1}
    assert not collisions, (
        f"local-name collisions across compliance modules: {collisions}"
    )


# --------------------------------------------------------------------------- #
# The asset -> DataClassification -> Regulation cross-link (the join to the shared
# infra/asset ontology).
# --------------------------------------------------------------------------- #


def test_asset_with_phi_dataclass_resolves_to_hipaa_via_applies_to_data_class():
    g = _full_graph()
    example_asset = rdflib.URIRef("http://example.org/test#ExampleAsset")
    # Mirrors how any fleet package's real System/Server node would be classified.
    g.add((example_asset, KG.classifiedAs, CONNECTOR_NS.PHI))

    query = """
    PREFIX : <https://knuckles-team.github.io/ontology/connector/legal-peripherals#>
    SELECT ?regulation WHERE {
        ?asset :classifiedAs ?dataclass .
        ?regulation :appliesToDataClass ?dataclass .
    }
    """
    resolved = {
        row.regulation for row in g.query(query, initBindings={"asset": example_asset})
    }
    assert CONNECTOR_NS.HIPAA in resolved


def test_asset_can_also_be_directly_governed_by_a_regulation():
    """:governedBy (already defined in the hub ontology) is a valid direct edge from any
    governed entity straight to a specific compliance Regulation individual."""
    g = _full_graph()
    example_asset = rdflib.URIRef("http://example.org/test#ExampleAsset2")
    g.add((example_asset, KG.governedBy, CONNECTOR_NS.HIPAA))
    assert (example_asset, KG.governedBy, CONNECTOR_NS.HIPAA) in g
    assert (CONNECTOR_NS.HIPAA, RDF.type, KG.Regulation) in g
