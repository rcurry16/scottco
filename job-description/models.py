"""
Data models for Job Description Generator

Implements the Nova Scotia Government job description template structure
using Pydantic for validation and structured outputs.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum
from datetime import date


# ============================================================================
# ENUMS
# ============================================================================

class RoleLevel(str, Enum):
    """Internal role level classification (never shown to user)"""
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    EXECUTIVE = "executive"


class ExclusionStatus(str, Enum):
    """Union exclusion status"""
    EXCLUDED = "Excluded"
    NON_EXCLUDED = "Non-Excluded"


# ============================================================================
# INPUT MODELS
# ============================================================================

class OrganizationalContext(BaseModel):
    """Context loaded from config.py"""
    organization_name: str
    industry: str
    location: str
    department_default: Optional[str] = ""
    organization_description: Optional[str] = ""


class UserResponses(BaseModel):
    """Captures all user input from the questionnaire"""

    # Basic Information (Questions 1-3)
    job_title: str = Field(description="Job/Working Title")
    department: str = Field(description="Department name")
    division_section: Optional[str] = Field(default="", description="Division or Section within department")
    reports_to: str = Field(description="Position title of direct supervisor")

    # Role Responsibilities (Questions 4-6)
    primary_responsibilities: str = Field(description="Main duties and outcomes")
    key_deliverables: str = Field(description="Specific outputs or results produced")
    unique_aspects: str = Field(description="What makes this role unique")

    # People & Relationships (Questions 7-8)
    manages_people: bool = Field(description="Does this role manage/supervise people?")
    num_direct_reports: Optional[str] = Field(default="", description="Number of direct reports (e.g., '3-5', 'None')")
    num_indirect_reports: Optional[str] = Field(default="", description="Number of indirect reports")
    other_resources_managed: Optional[str] = Field(default="", description="Other resources managed (consultants, students, etc.)")
    key_contacts: str = Field(description="Regular interactions (internal/external stakeholders)")

    # Scope & Decision-Making (Questions 9-11)
    decision_authority: str = Field(description="Types of decisions made independently and level of autonomy")
    innovation_problem_solving: str = Field(description="Degree of creativity, judgment, innovation required")
    impact_of_results: str = Field(description="How outcomes affect organization, clients, goals")

    # Requirements (Question 12)
    special_requirements: Optional[str] = Field(default="", description="Licenses, certifications, travel, special conditions")


# ============================================================================
# OUTPUT MODELS - Following NS Gov Template Structure
# ============================================================================

class ClassificationJobInformation(BaseModel):
    """Section 1: Classification Job Information (often system-generated or placeholder)"""
    sap_job_id: Optional[str] = Field(default="", description="SAP Job ID")
    position_classification_title: str = Field(description="Official position/classification title")
    pay_grade: Optional[str] = Field(default="", description="Pay Grade (e.g., 'EC 11', 'PR 13')")
    add_on_eligibility: Optional[bool] = Field(default=None, description="Add-On Eligibility")
    standardized: bool = Field(default=False, description="Standardized status")
    inactive: bool = Field(default=False, description="Inactive status")
    date_last_evaluated: Optional[str] = Field(default="", description="Date Last Evaluated (MM/DD/YYYY)")


class JobInformation(BaseModel):
    """Section 2: Job Information Block"""
    job_working_title: str = Field(description="Job/Working Title")
    department: str = Field(description="Department")
    division_section: Optional[str] = Field(default="", description="Division/Section")
    reports_to: str = Field(description="Reports To (Position Title)")
    reports_to_sap_id: Optional[str] = Field(default="", description="Reports To SAP ID (if known)")
    exclusion_status: ExclusionStatus = Field(description="Exclusion Status")


class OverallPurpose(BaseModel):
    """Section 3: Overall Purpose - 1-3 paragraph narrative"""
    purpose_text: str = Field(description="Comprehensive 1-3 paragraph description of role's primary function, organizational context, and value")


class KeyResponsibilities(BaseModel):
    """Section 4: Key Responsibilities - Bulleted list of major duties"""
    responsibilities: List[str] = Field(
        description="6-10 specific responsibilities using action verbs (Leads, Provides, Ensures, etc.)",
        min_items=6,
        max_items=10
    )


class PeopleManagement(BaseModel):
    """Section 5: People Management"""
    type_of_role: Literal["Individual Contributor", "Manages/Supervises People"] = Field(
        description="Individual Contributor or Manages/Supervises People"
    )
    num_direct_reports: Optional[str] = Field(default="", description="Number of direct reports (range or specific number)")
    classifications_of_direct_reports: Optional[str] = Field(default="", description="Classifications/Titles of direct reports")
    num_indirect_reports: Optional[str] = Field(default="", description="Number of indirect reports")
    other_resources: Optional[str] = Field(default="", description="Other resources managed (consultants, students, etc.)")


class ScopeSection(BaseModel):
    """Section 6: Scope - Four standardized subsections"""
    model_config = {"extra": "allow"}  # Allow extra fields Claude might add

    contacts_typical: str = Field(
        default="",
        description="Internal and external contacts, stakeholders, committees, memberships"
    )
    innovation: str = Field(
        default="",
        description="Creativity, problem-solving approach, judgment, expertise required"
    )
    decision_making: str = Field(
        default="",
        description="Authority, accountability, decision-making framework, escalation protocols"
    )
    impact_of_results: str = Field(
        default="",
        description="How results affect organization, clients, programs, broader goals"
    )
    other: Optional[str] = Field(default="", description="Additional scope information (often empty)")


class LicensesCertifications(BaseModel):
    """Section 7: Licenses/Certifications"""
    requirements: List[str] = Field(
        default_factory=list,
        description="Required licenses, certifications, professional designations (empty if none)"
    )


class WorkingConditions(BaseModel):
    """Section 8: Working Conditions - Four standardized subsections"""
    physical_effort: str = Field(description="Physical demands and effort required")
    physical_environment: str = Field(description="Environmental conditions and hazards")
    sensory_attention: str = Field(description="Concentration, attention to detail, sensory demands")
    psychological_pressures: str = Field(description="Stress levels, deadlines, work-life balance impacts")


class BoilerplateElements(BaseModel):
    """Section 9: Standard boilerplate text"""
    may_perform_other_duties: str = Field(default="May perform other related duties as assigned")
    assignment_specific_note: str = Field(
        default="In addition to the duties and responsibilities outlined in the job description, this job may include other, assignment-specific requirements (ex: French language, drivers license, membership in an employment equity group or security screening, etc.)"
    )
    data_from_conversion: Optional[str] = Field(default="", description="Data From Conversion field (usually empty)")
    additional_information: Optional[str] = Field(default="", description="Additional Information field (usually empty)")


# ============================================================================
# TOP-LEVEL JOB DESCRIPTION MODEL
# ============================================================================

class JobDescription(BaseModel):
    """Complete job description following Nova Scotia Government template"""

    classification_info: ClassificationJobInformation
    job_info: JobInformation
    overall_purpose: OverallPurpose
    key_responsibilities: KeyResponsibilities
    people_management: PeopleManagement
    scope: ScopeSection
    licenses_certifications: LicensesCertifications
    working_conditions: WorkingConditions
    boilerplate: BoilerplateElements
    usage: Optional['UsageSummary'] = Field(default=None, description="Token usage and cost summary")


# ============================================================================
# USAGE & COST TRACKING MODELS
# ============================================================================

class UsageSummary(BaseModel):
    """Token usage and cost summary for job description generation"""
    total_input_tokens: int = Field(description="Total input tokens used")
    total_output_tokens: int = Field(description="Total output tokens used")
    total_tokens: int = Field(description="Total tokens (input + output)")
    cost_usd: float = Field(description="Total cost in USD")
    cost_cad: float = Field(description="Total cost in CAD")


# ============================================================================
# INTERNAL MODELS (NOT IN FINAL OUTPUT)
# ============================================================================

class RoleLevelAssessment(BaseModel):
    """Internal model for role level inference (never shown to user)"""
    inferred_level: RoleLevel = Field(description="Entry, Mid, Senior, or Executive")
    rationale: str = Field(description="Brief explanation of why this level was chosen")
    decision_making_complexity: str = Field(description="Low, Medium, High, Strategic")
    people_leadership_scope: str = Field(description="None, Small Team, Department, Multi-Department")
    organizational_impact: str = Field(description="Individual, Team, Department, Organization-wide")
