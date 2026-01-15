"""
Job Description Generator V2

AI-powered job description generator using Nova Scotia Government template structure.
Uses 6 specialized agents to generate each section of the job description.

Usage:
    python job_desc_generator_v2.py
"""

import os
from datetime import datetime
from pydantic_ai import Agent
from pydantic_ai.providers.mistral import MistralProvider
from pydantic_ai.models.mistral import MistralModel

import config
from models import (
    UserResponses,
    OrganizationalContext,
    JobDescription,
    ClassificationJobInformation,
    JobInformation,
    OverallPurpose,
    KeyResponsibilities,
    PeopleManagement,
    ScopeSection,
    LicensesCertifications,
    WorkingConditions,
    BoilerplateElements,
    RoleLevelAssessment,
    RoleLevel,
    ExclusionStatus,
    UsageSummary
)
import output_formatter


# ============================================================================
# API SETUP
# ============================================================================

def get_mistral_provider():
    """Initialize Mistral provider with API key"""
    api_key = "lenpipOpfSKOm57F8XyLxp0rvjh8wZHz"
    return MistralProvider(api_key=api_key)


provider = get_mistral_provider()
model = MistralModel("mistral-small-latest", provider=provider)


# ============================================================================
# AGENT 1: JOB INFORMATION & PURPOSE AGENT
# ============================================================================

job_info_agent = Agent(
    model=model,
    output_type=tuple[JobInformation, OverallPurpose, RoleLevelAssessment],
    retries=3,
    system_prompt="""
    You are an expert HR professional specializing in writing formal job descriptions for government positions.

    Your task is to generate:
    1. The Job Information block (formal metadata about the position)
    2. The Overall Purpose section (1-3 paragraph narrative describing the role's primary function)
    3. An internal role level assessment (Entry/Mid/Senior/Executive) - this is for internal use only and will NOT be shown to the user

    TONE AND STYLE:
    - Formal, third-person perspective
    - Present tense for responsibilities
    - Action-verb heavy (Leads, Provides, Ensures, Conducts, etc.)
    - Government/professional terminology
    - Overall Purpose should be longer, complex sentences establishing context

    OVERALL PURPOSE STRUCTURE:
    - Paragraph 1: Primary function, organizational context, reporting structure
    - Paragraph 2 (optional): Key strategic or operational contributions
    - Paragraph 3 (optional): Broader organizational impact or unique aspects

    ROLE LEVEL INFERENCE:
    Assess the role level based on:
    - Decision-making authority and autonomy
    - People management responsibilities
    - Scope of organizational impact
    - Complexity of problem-solving required

    Entry: Individual contributor, limited autonomy, task-focused, local impact
    Mid: Some autonomy, may lead small teams or projects, department-level impact
    Senior: High autonomy, leads teams/functions, organizational impact, expert-level judgment
    Executive: Strategic decision-making, multi-department leadership, organization-wide impact

    Use role level to calibrate the language sophistication and scope of the Overall Purpose.
    """
)


# ============================================================================
# AGENT 2: KEY RESPONSIBILITIES AGENT
# ============================================================================

responsibilities_agent = Agent(
    model=model,
    output_type=KeyResponsibilities,
    retries=3,
    system_prompt="""
    You are an expert at analyzing job responsibilities and creating detailed accountability frameworks for government positions.

    Create 6-10 specific, actionable key responsibilities:
    - Start each with a strong action verb (Leads, Develops, Manages, Ensures, Provides, Conducts, Coordinates, Oversees, etc.)
    - Be specific about scope, scale, and impact
    - Avoid generic or vague language
    - Use present tense, third person
    - Each should be a complete sentence or paragraph
    - Order from most strategic/important to more operational
    - Align detail level with role complexity (entry = straightforward, executive = multi-faceted)

    EXAMPLES:
    Entry-level: "Provides administrative support including data entry, file management, and correspondence preparation."
    Mid-level: "Coordinates the implementation of quality assurance processes across multiple child care facilities, ensuring compliance with provincial regulations."
    Senior-level: "Leads the development and application of classification and compensation policies across government departments, ensuring corporate consistency and equity."
    Executive: "Provides strategic financial leadership by developing integrated long-term financial strategies, funding methodologies, and operational reviews aligned with government priorities."

    Calibrate sophistication, scope, and strategic vs operational focus based on the role level provided.
    """
)


# ============================================================================
# AGENT 3: PEOPLE MANAGEMENT AGENT
# ============================================================================

people_mgmt_agent = Agent(
    model=model,
    output_type=PeopleManagement,
    retries=3,
    system_prompt="""
    You are an expert at defining organizational structure and people management responsibilities.

    Based on the input, determine:
    - Type of Role: "Individual Contributor" or "Manages/Supervises People"
    - Number of direct reports (if applicable - can be a range like "2-5" or specific number)
    - Classifications/titles of direct reports (if applicable)
    - Number of indirect reports (if applicable)
    - Other resources managed (consultants, students, casuals, contractors, etc.)

    If the role does not manage people:
    - Set type_of_role to "Individual Contributor"
    - Leave other fields empty

    If the role manages people:
    - Set type_of_role to "Manages/Supervises People"
    - Provide realistic estimates based on the role level and responsibilities
    - Entry/Mid managers typically have 1-5 direct reports
    - Senior managers typically have 3-10 direct reports
    - Executives may have broader ranges (2-5 direct, 10-40 indirect)

    Be realistic and conservative - don't inflate numbers without clear evidence.
    """
)


# ============================================================================
# AGENT 4: SCOPE AGENT
# ============================================================================

scope_agent = Agent(
    model=model,
    output_type=ScopeSection,
    retries=3,
    system_prompt="""
    You are an expert at defining organizational scope and complexity for government positions.

    Generate detailed content for all four Scope subsections:

    1. CONTACTS (Typical):
       - Internal: departments, divisions, teams, committees
       - External: stakeholders, partners, agencies, public
       - Be specific about frequency and purpose of contact
       - Mention any formal memberships or committee participation

    2. INNOVATION:
       - Describe the degree of creativity, judgment, and problem-solving required
       - Explain how the role applies expertise and knowledge
       - Discuss innovation in methods, processes, or approaches
       - Note the complexity of issues addressed
       - Mention flexibility and adaptability requirements

    3. DECISION MAKING:
       - Define the authority and accountability framework
       - Describe what decisions can be made independently
       - Explain what requires escalation and to whom
       - Mention frameworks, policies, or legislation that guide decisions
       - Note the complexity and impact of decisions

    4. IMPACT OF RESULTS:
       - Explain how the role's outcomes affect the organization, clients, or programs
       - Describe the scope of impact (individual, team, department, organization-wide)
       - Note any public-facing or high-stakes consequences
       - Connect to broader organizational or governmental objectives

    CALIBRATE BY ROLE LEVEL:
    - Entry: Brief, straightforward descriptions (2-4 sentences each)
    - Mid: Moderate detail (4-6 sentences or short paragraph)
    - Senior: Detailed descriptions (6-8 sentences or full paragraph)
    - Executive: Highly detailed, multi-paragraph responses showing strategic complexity

    Use formal, professional language. Be specific and concrete.
    """
)


# ============================================================================
# AGENT 5: REQUIREMENTS AGENT
# ============================================================================

requirements_agent = Agent(
    model=model,
    output_type=LicensesCertifications,
    retries=3,
    system_prompt="""
    You are an expert at identifying licensing, certification, and special requirement needs for positions.

    Extract any licenses, certifications, or professional designations mentioned or implied:
    - Professional certifications (CPA, CFA, PMP, etc.)
    - Licenses (professional licenses, driver's license if required)
    - Educational credentials (if they function as requirements rather than preferences)
    - Memberships in professional associations (if required)

    IMPORTANT:
    - Only include items that are REQUIRED or strongly implied as necessary
    - Do NOT include preferences or "nice to have" items
    - If NO specific requirements are mentioned or clearly needed, return an empty list
    - Be conservative - when in doubt, leave it out

    EXAMPLES:
    Required: "Chartered Professional Accountants of Canada (CPA) member in good standing or suitable equivalency"
    Required: "Valid driver's license and access to reliable transportation"
    Not required (just preference): "Bachelor's degree preferred"

    Return a list of requirement strings, or an empty list if none are required.
    """
)


# ============================================================================
# AGENT 6: WORKING CONDITIONS AGENT
# ============================================================================

working_conditions_agent = Agent(
    model=model,
    output_type=WorkingConditions,
    retries=3,
    system_prompt="""
    You are an expert at assessing working conditions for positions based on job requirements.

    Generate content for all four Working Conditions subsections using the standard templates provided,
    but adjust based on any special requirements or role characteristics:

    1. PHYSICAL EFFORT:
       - Default to "light" for most office positions
       - Adjust if role involves physical demands (frequent travel, field work, lifting, etc.)

    2. PHYSICAL ENVIRONMENT:
       - Default to "standard_office" for most positions
       - Adjust if role involves varied locations, outdoor work, or challenging conditions

    3. SENSORY ATTENTION:
       - Entry/Mid: Usually "moderate" (occasional concentration, some detail work)
       - Senior: Often "considerable" (frequent concentration, significant detail work)
       - Executive: May be "extensive" if managing complex, high-stakes information streams

    4. PSYCHOLOGICAL PRESSURES:
       - Entry: Usually "low" (some deadlines, manageable stress)
       - Mid: Often "moderate" (competing priorities, noticeable stress)
       - Senior/Executive: Often "high" (frequent pressure, limited control of pace, significant work-life impact)

    Use the exact template text from the configuration, selecting the appropriate level based on the role.
    Customize slightly only if there are specific demands mentioned (e.g., frequent travel, high-stress client interactions).

    Be realistic and aligned with government position standards.
    """
)


# ============================================================================
# INTERACTIVE QUESTIONNAIRE
# ============================================================================

async def collect_user_responses() -> UserResponses:
    """
    Interactive questionnaire to collect user input (8-12 questions)
    """
    print("\n" + "=" * 80)
    print("JOB DESCRIPTION GENERATOR")
    print("=" * 80)
    print("\nThis tool will guide you through creating a comprehensive job description.")
    print("Please answer the following questions about the position.\n")

    print("--- BASIC INFORMATION (Questions 1-3) ---\n")

    # Question 1: Job Title
    job_title = input("1. What is the Job/Working Title for this position? \n   → ").strip()

    # Question 2: Department and Division
    department = input("\n2. What is the Department name? \n   → ").strip()
    division_section = input("   Division or Section (if applicable, press Enter to skip): \n   → ").strip()

    # Question 3: Reports To
    reports_to = input("\n3. This position reports to (enter the position title of the direct supervisor): \n   → ").strip()

    print("\n--- ROLE RESPONSIBILITIES (Questions 4-6) ---\n")

    # Question 4: Primary Responsibilities
    print("4. What are the main duties and outcomes this role is responsible for?")
    print("   (Describe the key work performed and results expected)")
    primary_responsibilities = input("   → ").strip()

    # Question 5: Key Deliverables
    print("\n5. What specific outputs or results does this role produce?")
    print("   (e.g., reports, analyses, programs, services)")
    key_deliverables = input("   → ").strip()

    # Question 6: Unique Aspects
    print("\n6. What makes this role unique or different from a typical position with this title?")
    print("   (Special focus areas, unique challenges, specific context)")
    unique_aspects = input("   → ").strip()

    print("\n--- PEOPLE & RELATIONSHIPS (Questions 7-8) ---\n")

    # Question 7: People Management
    manages_people_input = input("7. Does this role manage or supervise people? (yes/no) \n   → ").strip().lower()
    manages_people = manages_people_input in ['yes', 'y']

    num_direct_reports = ""
    num_indirect_reports = ""
    other_resources_managed = ""

    if manages_people:
        num_direct_reports = input("   How many direct reports? (e.g., '3', '2-5', or 'varies') \n   → ").strip()
        num_indirect_reports = input("   How many indirect reports? (press Enter if none) \n   → ").strip()
        other_resources_managed = input("   Any other resources managed? (consultants, students, etc. - press Enter if none) \n   → ").strip()

    # Question 8: Key Contacts
    print("\n8. Who does this role interact with regularly?")
    print("   (Internal stakeholders, external partners, committees, etc.)")
    key_contacts = input("   → ").strip()

    print("\n--- SCOPE & DECISION-MAKING (Questions 9-11) ---\n")

    # Question 9: Decision Authority
    print("9. What types of decisions can this role make independently?")
    print("   (Describe the level of autonomy and decision-making authority)")
    decision_authority = input("   → ").strip()

    # Question 10: Innovation & Problem-Solving
    print("\n10. What degree of creativity, judgment, or innovation is required in this role?")
    print("    (How complex are the problems? How much expert judgment is needed?)")
    innovation_problem_solving = input("    → ").strip()

    # Question 11: Impact of Results
    print("\n11. How do the outcomes of this role affect the organization, clients, or broader goals?")
    print("    (Describe the scope and significance of impact)")
    impact_of_results = input("    → ").strip()

    print("\n--- REQUIREMENTS (Question 12) ---\n")

    # Question 12: Special Requirements
    print("12. Are there any special requirements for this role?")
    print("    (Licenses, certifications, travel, specific working conditions, etc.)")
    print("    (Press Enter if none)")
    special_requirements = input("    → ").strip()

    print("\n" + "=" * 80)
    print("Thank you! Generating your job description...")
    print("=" * 80 + "\n")

    return UserResponses(
        job_title=job_title,
        department=department,
        division_section=division_section,
        reports_to=reports_to,
        primary_responsibilities=primary_responsibilities,
        key_deliverables=key_deliverables,
        unique_aspects=unique_aspects,
        manages_people=manages_people,
        num_direct_reports=num_direct_reports,
        num_indirect_reports=num_indirect_reports,
        other_resources_managed=other_resources_managed,
        key_contacts=key_contacts,
        decision_authority=decision_authority,
        innovation_problem_solving=innovation_problem_solving,
        impact_of_results=impact_of_results,
        special_requirements=special_requirements
    )


# ============================================================================
# MAIN GENERATION WORKFLOW
# ============================================================================

async def generate_job_description(user_responses: UserResponses, org_context: OrganizationalContext) -> JobDescription:
    """
    Generate complete job description using 6 specialized agents
    """
    print(f"\n{'='*80}")
    print(f"🚀 STARTING JOB DESCRIPTION GENERATION (Mistral)")
    print(f"{'='*80}")
    print(f"Position: {user_responses.job_title}")
    print(f"Department: {user_responses.department}")
    print(f"Organization: {org_context.organization_name}")
    print(f"{'='*80}\n")

    # Initialize token tracking
    total_input_tokens = 0
    total_output_tokens = 0

    # ------------------------------------------------------------------------
    # AGENT 1: Job Information & Overall Purpose (+ Role Level Inference)
    # ------------------------------------------------------------------------
    print("📋 Step 1/6: Generating job information and overall purpose...")
    print(f"   Using model: mistral-small-latest")

    job_info_prompt = f"""
    Generate the Job Information block and Overall Purpose section for this position:

    ORGANIZATIONAL CONTEXT:
    Organization: {org_context.organization_name}
    Industry: {org_context.industry}
    Location: {org_context.location}
    {f"Organization Description: {org_context.organization_description}" if org_context.organization_description else ""}

    POSITION DETAILS:
    Job Title: {user_responses.job_title}
    Department: {user_responses.department}
    Division/Section: {user_responses.division_section or 'N/A'}
    Reports To: {user_responses.reports_to}

    ROLE INFORMATION:
    Primary Responsibilities: {user_responses.primary_responsibilities}
    Unique Aspects: {user_responses.unique_aspects}
    Key Deliverables: {user_responses.key_deliverables}
    Decision Authority: {user_responses.decision_authority}
    Impact: {user_responses.impact_of_results}

    PEOPLE MANAGEMENT:
    Manages People: {user_responses.manages_people}
    Direct Reports: {user_responses.num_direct_reports or 'None'}

    Generate:
    1. JobInformation block (use "Non-Excluded" as default exclusion status)
    2. Overall Purpose (1-3 compelling paragraphs)
    3. Internal role level assessment (Entry/Mid/Senior/Executive)
    """

    job_info_result = await job_info_agent.run(job_info_prompt)
    job_info, overall_purpose, role_level_assessment = job_info_result.output

    # Track tokens
    usage = job_info_result.usage()
    total_input_tokens += usage.request_tokens
    total_output_tokens += usage.response_tokens

    print(f"   ✓ Role level assessed as: {role_level_assessment.inferred_level.value.upper()}")

    # ------------------------------------------------------------------------
    # AGENT 2: Key Responsibilities
    # ------------------------------------------------------------------------
    print("📋 Step 2/6: Generating key responsibilities...")

    responsibilities_prompt = f"""
    Generate 6-10 key responsibilities for this {role_level_assessment.inferred_level.value}-level position:

    Position: {user_responses.job_title}
    Role Level: {role_level_assessment.inferred_level.value}

    Overall Purpose: {overall_purpose.purpose_text}

    PRIMARY RESPONSIBILITIES:
    {user_responses.primary_responsibilities}

    KEY DELIVERABLES:
    {user_responses.key_deliverables}

    UNIQUE ASPECTS:
    {user_responses.unique_aspects}

    Generate {config.MIN_RESPONSIBILITIES}-{config.MAX_RESPONSIBILITIES} specific, actionable responsibilities.
    Calibrate language sophistication and scope for a {role_level_assessment.inferred_level.value}-level role.
    """

    responsibilities_result = await responsibilities_agent.run(responsibilities_prompt)
    key_responsibilities = responsibilities_result.output

    # Track tokens
    usage = responsibilities_result.usage()
    total_input_tokens += usage.request_tokens
    total_output_tokens += usage.response_tokens

    # ------------------------------------------------------------------------
    # AGENT 3: People Management
    # ------------------------------------------------------------------------
    print("📋 Step 3/6: Generating people management details...")

    people_mgmt_prompt = f"""
    Determine people management structure for this position:

    Position: {user_responses.job_title}
    Role Level: {role_level_assessment.inferred_level.value}

    PEOPLE MANAGEMENT INFO:
    Manages People: {user_responses.manages_people}
    Number of Direct Reports: {user_responses.num_direct_reports or 'Not specified'}
    Number of Indirect Reports: {user_responses.num_indirect_reports or 'Not specified'}
    Other Resources Managed: {user_responses.other_resources_managed or 'None'}

    PRIMARY RESPONSIBILITIES:
    {user_responses.primary_responsibilities}

    Generate realistic people management details based on the role level and information provided.
    """

    people_mgmt_result = await people_mgmt_agent.run(people_mgmt_prompt)
    people_management = people_mgmt_result.output

    # Track tokens
    usage = people_mgmt_result.usage()
    total_input_tokens += usage.request_tokens
    total_output_tokens += usage.response_tokens

    # ------------------------------------------------------------------------
    # AGENT 4: Scope (4 subsections)
    # ------------------------------------------------------------------------
    print("📋 Step 4/6: Generating scope details (contacts, innovation, decision-making, impact)...")

    scope_prompt = f"""
    Generate detailed Scope section (4 subsections) for this {role_level_assessment.inferred_level.value}-level position:

    Position: {user_responses.job_title}
    Department: {user_responses.department}
    Role Level: {role_level_assessment.inferred_level.value}

    KEY CONTACTS:
    {user_responses.key_contacts}

    INNOVATION/PROBLEM-SOLVING:
    {user_responses.innovation_problem_solving}

    DECISION AUTHORITY:
    {user_responses.decision_authority}

    IMPACT OF RESULTS:
    {user_responses.impact_of_results}

    Overall Purpose: {overall_purpose.purpose_text}

    Generate all four Scope subsections:
    1. Contacts (Typical)
    2. Innovation
    3. Decision Making
    4. Impact of Results

    Calibrate detail level for {role_level_assessment.inferred_level.value} role (entry=brief, executive=detailed).
    """

    scope_result = await scope_agent.run(scope_prompt)
    scope = scope_result.output

    # Track tokens
    usage = scope_result.usage()
    total_input_tokens += usage.request_tokens
    total_output_tokens += usage.response_tokens

    # ------------------------------------------------------------------------
    # AGENT 5: Licenses/Certifications
    # ------------------------------------------------------------------------
    print("📋 Step 5/6: Identifying licenses and certifications...")

    requirements_prompt = f"""
    Identify any required licenses, certifications, or professional designations for this position:

    Position: {user_responses.job_title}
    Department: {user_responses.department}

    SPECIAL REQUIREMENTS PROVIDED:
    {user_responses.special_requirements or 'None specified'}

    PRIMARY RESPONSIBILITIES:
    {user_responses.primary_responsibilities}

    Extract ONLY required (not preferred) licenses, certifications, or designations.
    If none are clearly required, return an empty list.
    """

    requirements_result = await requirements_agent.run(requirements_prompt)
    licenses_certs = requirements_result.output

    # Track tokens
    usage = requirements_result.usage()
    total_input_tokens += usage.request_tokens
    total_output_tokens += usage.response_tokens

    # ------------------------------------------------------------------------
    # AGENT 6: Working Conditions
    # ------------------------------------------------------------------------
    print("📋 Step 6/6: Generating working conditions...")

    # Determine working condition levels based on role level
    physical_effort_level = "light"  # Default for most office roles
    physical_env_level = "standard_office"  # Default
    sensory_level = "moderate" if role_level_assessment.inferred_level in [RoleLevel.ENTRY, RoleLevel.MID] else "considerable"
    psych_pressure_level = "low" if role_level_assessment.inferred_level == RoleLevel.ENTRY else ("moderate" if role_level_assessment.inferred_level == RoleLevel.MID else "high")

    working_conditions_prompt = f"""
    Generate Working Conditions section for this {role_level_assessment.inferred_level.value}-level position:

    Position: {user_responses.job_title}
    Role Level: {role_level_assessment.inferred_level.value}

    SPECIAL REQUIREMENTS:
    {user_responses.special_requirements or 'Standard office environment'}

    TEMPLATES AVAILABLE:
    Physical Effort levels: light, moderate, substantial
    Physical Environment levels: standard_office, mixed, challenging
    Sensory Attention levels: moderate, considerable, extensive
    Psychological Pressures levels: low, moderate, high

    RECOMMENDED LEVELS (adjust if special requirements indicate otherwise):
    - Physical Effort: {physical_effort_level}
    - Physical Environment: {physical_env_level}
    - Sensory Attention: {sensory_level}
    - Psychological Pressures: {psych_pressure_level}

    Use the standard templates from config, selecting appropriate levels.
    Adjust only if special requirements clearly indicate different conditions.
    """

    # Provide templates in context
    working_conditions_templates = {
        "physical_effort": config.STANDARD_WORKING_CONDITIONS["physical_effort"],
        "physical_environment": config.STANDARD_WORKING_CONDITIONS["physical_environment"],
        "sensory_attention": config.STANDARD_WORKING_CONDITIONS["sensory_attention"],
        "psychological_pressures": config.STANDARD_WORKING_CONDITIONS["psychological_pressures"]
    }

    working_conditions_result = await working_conditions_agent.run(working_conditions_prompt)
    working_conditions = working_conditions_result.output

    # Track tokens
    usage = working_conditions_result.usage()
    total_input_tokens += usage.request_tokens
    total_output_tokens += usage.response_tokens

    # ------------------------------------------------------------------------
    # Calculate Usage Summary
    # ------------------------------------------------------------------------
    total_tokens = total_input_tokens + total_output_tokens

    # Calculate costs (per 1M tokens)
    cost_usd = (
        (total_input_tokens / 1_000_000) * config.MISTRAL_SMALL_INPUT_COST +
        (total_output_tokens / 1_000_000) * config.MISTRAL_SMALL_OUTPUT_COST
    )
    cost_cad = cost_usd * config.USD_TO_CAD_RATE

    usage_summary = UsageSummary(
        total_input_tokens=total_input_tokens,
        total_output_tokens=total_output_tokens,
        total_tokens=total_tokens,
        cost_usd=cost_usd,
        cost_cad=cost_cad
    )

    print(f"\n💰 Token Usage: {total_input_tokens:,} input + {total_output_tokens:,} output = {total_tokens:,} total")
    print(f"💵 Cost: ${cost_usd:.4f} USD / ${cost_cad:.4f} CAD\n")

    # ------------------------------------------------------------------------
    # Assemble Complete Job Description
    # ------------------------------------------------------------------------
    print("\n✅ All sections generated! Assembling final job description...\n")

    # Create Classification Info (mostly placeholders/defaults)
    classification_info = ClassificationJobInformation(
        sap_job_id=config.CLASSIFICATION_DEFAULTS["sap_job_id"],
        position_classification_title=user_responses.job_title,
        pay_grade=config.CLASSIFICATION_DEFAULTS["pay_grade"],
        add_on_eligibility=config.CLASSIFICATION_DEFAULTS["add_on_eligibility"],
        standardized=config.CLASSIFICATION_DEFAULTS["standardized"],
        inactive=config.CLASSIFICATION_DEFAULTS["inactive"],
        date_last_evaluated=datetime.now().strftime("%m/%d/%Y")
    )

    # Create Boilerplate
    boilerplate = BoilerplateElements(
        may_perform_other_duties=config.BOILERPLATE_MAY_PERFORM_OTHER_DUTIES,
        assignment_specific_note=config.BOILERPLATE_ASSIGNMENT_SPECIFIC,
        data_from_conversion=config.DATA_FROM_CONVERSION
    )

    # Assemble final job description
    job_description = JobDescription(
        classification_info=classification_info,
        job_info=job_info,
        overall_purpose=overall_purpose,
        key_responsibilities=key_responsibilities,
        people_management=people_management,
        scope=scope,
        licenses_certifications=licenses_certs,
        working_conditions=working_conditions,
        boilerplate=boilerplate,
        usage=usage_summary
    )

    return job_description


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main execution function"""

    # Load organizational context from config
    org_context = OrganizationalContext(
        organization_name=config.ORGANIZATION_NAME,
        industry=config.INDUSTRY,
        location=config.LOCATION,
        department_default=config.DEPARTMENT_DEFAULT,
        organization_description=config.ORGANIZATION_DESCRIPTION
    )

    # Collect user responses via interactive questionnaire
    user_responses = await collect_user_responses()

    # Generate job description using 6 specialized agents
    job_description = await generate_job_description(user_responses, org_context)

    # Display to console and save to file
    output_formatter.display_and_save(job_description)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
