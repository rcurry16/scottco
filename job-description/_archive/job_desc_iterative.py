from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from pydantic_ai import Agent
from pydantic_ai.providers.mistral import MistralProvider
import os
from enum import Enum


class StratumLevel(str, Enum):
    I = "I"
    II = "II"
    III = "III"
    IV = "IV"
    V = "V"
    VI = "VI"


# Simplified initial input - just 4 key fields
class BasicInput(BaseModel):
    org_name: str
    org_description: str  
    job_title: str
    department: str


# Targeted refinement questions
class RefinementInput(BaseModel):
    role_uniqueness: str = Field(description="What makes this role unique from a typical job with this title?")
    scope_of_impact: str = Field(description="What's the scope of your impact? (team size, budget, geographic reach, etc.)")
    decision_independence: str = Field(description="What level of independence do you have in decision-making?")
    special_factors: str = Field(description="Any special challenges, requirements, or constraints?")


# Combined input for final generation
class EmployeeInput(BaseModel):
    org_name: str
    org_description: str
    job_title: str
    department: str
    role_uniqueness: str
    scope_of_impact: str
    decision_independence: str
    special_factors: str


# Call 1: Stratum + Basic Info
class StratumInfo(BaseModel):
    title: str = Field(description="Exact job title")
    department: str = Field(description="Department name")
    reports_to: str = Field(description="Title of direct supervisor")
    assigned_stratum: StratumLevel = Field(description="Determined stratum level (I-VI)")
    stratum_rationale: str = Field(description="Brief explanation of why this stratum was chosen based on complexity and timeframes")
    position_summary: str = Field(description="Concise 4-5 line summary including stratum level, primary purpose, scope, business contribution, and organizational position")


# Call 2: Detailed Accountabilities
class Accountability(BaseModel):
    accountability: str = Field(description="Clear accountability statement starting with action verb")
    purpose: str = Field(description="The 'goodness' or value this accountability delivers")
    major_deliverable: str = Field(description="Primary deliverable produced")
    timeline: str = Field(description="How long this deliverable takes to complete")
    timeline_category: Literal["days", "weeks", "months", "years"] = Field(description="Broad timeline category")


class AccountabilitySection(BaseModel):
    accountabilities: List[Accountability] = Field(description="6-8 key accountabilities with details", min_items=6, max_items=8)
    longest_deliverable: str = Field(description="The longest single deliverable timeline identified")
    timeline_analysis: str = Field(description="Analysis of timeline consistency and potential job design issues")


# Call 3: Authorities  
class AuthoritySection(BaseModel):
    financial_authorities: List[str] = Field(description="Budget and financial decision authorities")
    people_authorities: List[str] = Field(description="Staffing and people management authorities") 
    resource_authorities: List[str] = Field(description="Resource allocation authorities")
    process_authorities: List[str] = Field(description="Process and operational authorities")


# Call 4: Requirements + Abilities
class RequirementsSection(BaseModel):
    knowledge_experience: List[str] = Field(description="Education, certifications, knowledge base, and experience requirements")
    technical_skills: List[str] = Field(description="Required technical skills and tools proficiency")
    behavioural_skills: List[str] = Field(description="Soft skills, interpersonal abilities, and behavioral competencies")
    other_requirements: List[str] = Field(description="Travel, physical, scheduling requirements")


# Final combined model
class JobDescription(BaseModel):
    stratum_info: StratumInfo
    accountabilities: AccountabilitySection
    authorities: AuthoritySection
    requirements: RequirementsSection


# Set up API and agents
os.environ['MISTRAL_API_KEY'] = 'lenpipOpfSKOm57F8XyLxp0rvjh8wZHz'
provider = MistralProvider(api_key='lenpipOpfSKOm57F8XyLxp0rvjh8wZHz')

# Agent 1: Stratum determination and basic info
stratum_agent = Agent(
    model='mistral:mistral-small-latest',
    model_provider=provider,
    output_type=StratumInfo,
    system_prompt="""
    You are an expert in Requisite Organization (RO) methodology and job stratification.
    
    Analyze the provided job information and determine the appropriate stratum level based on DELIVERY TIMESPAN ONLY:
    - Stratum I: Tasks/deliverables completed in 1 day to 3 months
    - Stratum II: Tasks/deliverables completed in 3 months to 1 year  
    - Stratum III: Tasks/deliverables completed in 1-2 years
    - Stratum IV: Tasks/deliverables completed in 2-5 years
    - Stratum V: Tasks/deliverables completed in 5-10 years
    - Stratum VI: Tasks/deliverables completed in 10-20 years
    
    Focus ONLY on the longest deliverable timespan - how long it takes to complete the most complex work output.
    Ignore planning horizons, forecasting periods, and forward-looking activities.
    Extract reporting relationships clearly from the reporting structure.
    Create a concise but specific position summary that captures what makes this role unique and valuable.
    """
)

# Agent 2: Detailed accountabilities
accountability_agent = Agent(
    model='mistral:mistral-small-latest', 
    model_provider=provider,
    output_type=AccountabilitySection,
    system_prompt="""
    You are an expert at analyzing job responsibilities and creating detailed accountability frameworks.
    
    Break down the primary responsibilities into 6-8 specific accountabilities. For each:
    - Start with a strong action verb (Develop, Lead, Manage, Ensure, etc.)
    - Include the purpose/value delivered 
    - Identify the major deliverable produced
    - Estimate realistic timeline for DELIVERABLE COMPLETION (not planning horizon)
    
    Focus on actual work output completion times. Examples:
    - Monthly reports = 1-4 weeks to complete
    - Annual budget = 2-4 months to complete  
    - System implementation = 6-18 months to complete
    
    Analyze timeline consistency - the longest deliverable determines the stratum level.
    Be specific about deliverables - avoid generic terms. Include scope, scale, and impact details.
    """
)

# Agent 3: Authorities
authority_agent = Agent(
    model='mistral:mistral-small-latest',
    model_provider=provider, 
    output_type=AuthoritySection,
    system_prompt="""
    You are an expert at defining organizational authorities and decision-making scope.
    
    Based on the decision authority information and stratum level, clearly define:
    - Financial/budgetary authorities (be specific about dollar amounts and scope)
    - People/staffing authorities (hiring, firing, performance management)
    - Resource allocation authorities (equipment, technology, vendor selection)
    - Process/operational authorities (policy setting, procedure changes)
    
    Ensure authorities align with the stratum level - higher strata should have broader scope.
    Be specific rather than generic in authority descriptions.
    
    Match authority levels to the determined stratum - lower strata have more limited authorities, higher strata have broader decision-making scope.
    """
)

# Agent 4: Requirements and abilities
requirements_agent = Agent(
    model='mistral:mistral-small-latest',
    model_provider=provider,
    output_type=RequirementsSection, 
    system_prompt="""
    You are an expert at defining job requirements across knowledge, technical, and behavioral dimensions.
    
    Categorize requirements into three distinct areas:
    
    Knowledge & Experience:
    - Education (degrees, certifications, licenses)
    - Years of experience in relevant areas
    - Specific industry or functional expertise
    - Knowledge of methodologies, frameworks, regulations
    
    Technical Skills:
    - Software, tools, and technology proficiency
    - Technical methodologies and processes
    - System and platform knowledge
    - Data analysis and technical capabilities
    
    Behavioral Skills:
    - Communication and interpersonal skills
    - Problem-solving and analytical thinking  
    - Attention to detail and accuracy
    - Time management and prioritization
    - Collaboration and teamwork
    
    Ensure each category is distinct and aligns with the stratum level and role complexity.
    Be specific rather than generic in all requirements.
    Focus on core skills needed for the role without over-emphasizing unique aspects in every requirement.
    """
)


async def basic_input():
    """Collect basic organizational and role information"""
    print("\n=== Job Description Generator - Phase 1 ===")
    print("Let's start with some basic information:\n")
    
    org_name = input("What is your organization's name? ")
    org_description = input("Briefly describe what your organization does: ")
    job_title = input("What is your job title? ")
    department = input("What department are you in? ")
    
    return BasicInput(
        org_name=org_name,
        org_description=org_description,
        job_title=job_title,
        department=department
    )


async def refinement_input(job_title: str):
    """Collect targeted refinement information"""
    print(f"\n=== Job Description Generator - Phase 2 ===")
    print(f"Now let's customize this {job_title} role with a few targeted questions:\n")
    
    role_uniqueness = input(f"What makes this {job_title} role unique from a typical {job_title}? ")
    scope_of_impact = input("What's the scope of your impact? (team size, budget, geographic reach, etc.) ")
    decision_independence = input("What level of independence do you have in decision-making? ")
    special_factors = input("Any special challenges, requirements, or constraints for this role? ")
    
    return RefinementInput(
        role_uniqueness=role_uniqueness,
        scope_of_impact=scope_of_impact,
        decision_independence=decision_independence,
        special_factors=special_factors
    )


async def generate_base_job_description(basic_input: BasicInput) -> JobDescription:
    """Generate base job description from minimal input"""
    
    # Call 1: Stratum determination and basic info from minimal data
    stratum_prompt = f"""
    Create a job description for this role based on typical industry standards:
    
    Organization: {basic_input.org_name}
    Organization Description: {basic_input.org_description}
    Job Title: {basic_input.job_title}
    Department: {basic_input.department}
    
    Based on typical roles with this title in this type of organization, make reasonable assumptions about:
    - Stratum level based on typical complexity
    - Reporting relationships
    - Scope and responsibilities
    """
    
    stratum_result = await stratum_agent.run(stratum_prompt)
    stratum_info = stratum_result.output
    
    # Call 2: Standard accountabilities for this role type
    accountability_prompt = f"""
    Based on this stratum {stratum_info.assigned_stratum.value} {basic_input.job_title} position at {basic_input.org_name}, create typical accountabilities:
    
    Organization Type: {basic_input.org_description}
    Job Title: {stratum_info.title}
    Department: {basic_input.department}
    Stratum Level: {stratum_info.assigned_stratum.value}
    
    Create 6-8 standard accountabilities that would be typical for this role type.
    """
    
    accountability_result = await accountability_agent.run(accountability_prompt)
    accountabilities = accountability_result.output
    
    # Call 3: Standard authorities for this role type
    authority_prompt = f"""
    Define typical authorities for a Stratum {stratum_info.assigned_stratum.value} {basic_input.job_title} at {basic_input.org_name}:
    
    Organization Type: {basic_input.org_description}
    Job Title: {stratum_info.title}
    Department: {basic_input.department}
    Stratum Level: {stratum_info.assigned_stratum.value}
    
    Create standard authorities appropriate for this role type and stratum level.
    """
    
    authority_result = await authority_agent.run(authority_prompt)
    authorities = authority_result.output
    
    # Call 4: Standard requirements for this role type
    requirements_prompt = f"""
    Define typical requirements for a Stratum {stratum_info.assigned_stratum.value} {basic_input.job_title} in {basic_input.department}:
    
    Organization Type: {basic_input.org_description}
    Job Title: {stratum_info.title}
    Department: {basic_input.department}
    Stratum Level: {stratum_info.assigned_stratum.value}
    
    Create standard requirements typical for this role type.
    """
    
    requirements_result = await requirements_agent.run(requirements_prompt)
    requirements = requirements_result.output
    
    return JobDescription(
        stratum_info=stratum_info,
        accountabilities=accountabilities,
        authorities=authorities,
        requirements=requirements
    )


async def refine_job_description(base_job_desc: JobDescription, employee_input: EmployeeInput) -> JobDescription:
    """Refine the base job description with specific role details"""
    
    # Refine stratum and basic info based on specifics
    stratum_prompt = f"""
    Refine this job description based on specific role details:
    
    Current Job Description:
    Title: {base_job_desc.stratum_info.title}
    Department: {base_job_desc.stratum_info.department}
    Stratum: {base_job_desc.stratum_info.assigned_stratum.value}
    Summary: {base_job_desc.stratum_info.position_summary}
    
    Role-Specific Information:
    Organization: {employee_input.org_name} - {employee_input.org_description}
    Role Uniqueness: {employee_input.role_uniqueness}
    Scope of Impact: {employee_input.scope_of_impact}
    Decision Independence: {employee_input.decision_independence}
    Special Factors: {employee_input.special_factors}
    
    Adjust stratum level if needed based on actual scope and complexity. Update summary to reflect specific role characteristics.
    """
    
    stratum_result = await stratum_agent.run(stratum_prompt)
    refined_stratum_info = stratum_result.output
    
    # Refine accountabilities based on role specifics
    accountability_prompt = f"""
    Refine accountabilities for this specific role:
    
    Base Accountabilities: {[acc.accountability for acc in base_job_desc.accountabilities.accountabilities]}
    
    Role Specifics:
    - Uniqueness: {employee_input.role_uniqueness}
    - Scope: {employee_input.scope_of_impact}
    - Independence: {employee_input.decision_independence}
    - Special Factors: {employee_input.special_factors}
    
    Modify accountabilities to reflect the actual scope, complexity, and unique aspects of this specific role.
    """
    
    accountability_result = await accountability_agent.run(accountability_prompt)
    refined_accountabilities = accountability_result.output
    
    # Refine authorities based on decision independence
    authority_prompt = f"""
    Refine authorities based on actual decision-making scope:
    
    Current Authorities:
    Financial: {base_job_desc.authorities.financial_authorities}
    People: {base_job_desc.authorities.people_authorities}
    Resource: {base_job_desc.authorities.resource_authorities}
    Process: {base_job_desc.authorities.process_authorities}
    
    Decision Independence Details: {employee_input.decision_independence}
    Scope of Impact: {employee_input.scope_of_impact}
    
    Adjust authorities to match the actual decision-making scope and independence level.
    """
    
    authority_result = await authority_agent.run(authority_prompt)
    refined_authorities = authority_result.output
    
    # Refine requirements based on role uniqueness and special factors
    requirements_prompt = f"""
    Refine requirements based on specific role characteristics:
    
    Base Requirements:
    Knowledge: {base_job_desc.requirements.knowledge_experience}
    Technical: {base_job_desc.requirements.technical_skills}
    Behavioral: {base_job_desc.requirements.behavioural_skills}
    Other: {base_job_desc.requirements.other_requirements}
    
    Role-Specific Factors:
    - Uniqueness: {employee_input.role_uniqueness}
    - Special Factors: {employee_input.special_factors}
    - Scope: {employee_input.scope_of_impact}
    
    Adjust requirements to reflect the specific demands and characteristics of this role.
    """
    
    requirements_result = await requirements_agent.run(requirements_prompt)
    refined_requirements = requirements_result.output
    
    return JobDescription(
        stratum_info=refined_stratum_info,
        accountabilities=refined_accountabilities,
        authorities=refined_authorities,
        requirements=refined_requirements
    )


def display_job_description(job_desc: JobDescription):
    """Display the formatted job description"""
    print("\n\n=== GENERATED JOB DESCRIPTION (MULTI-CALL) ===\n")
    
    # Basic Information
    print("Position Information:")
    print(f"- Title: {job_desc.stratum_info.title}")
    print(f"- Department: {job_desc.stratum_info.department}")
    print(f"- Reports to: {job_desc.stratum_info.reports_to}")
    print(f"- Assigned Stratum: {job_desc.stratum_info.assigned_stratum.value}")
    print(f"- Stratum Rationale: {job_desc.stratum_info.stratum_rationale}\n")
    
    # Position Summary
    print("Position Summary:")
    print(f"{job_desc.stratum_info.position_summary}\n")
    
    # Authorities
    print("Position Specific Authorities:")
    print("Financial/Budgetary:")
    for auth in job_desc.authorities.financial_authorities:
        print(f"- {auth}")
    print("People/Staffing:")
    for auth in job_desc.authorities.people_authorities:
        print(f"- {auth}")
    print("Resource Allocation:")
    for auth in job_desc.authorities.resource_authorities:
        print(f"- {auth}")
    print("Process/Operational:")
    for auth in job_desc.authorities.process_authorities:
        print(f"- {auth}")
    print()
    
    # Accountabilities
    print("Position Specific Accountabilities:")
    for acc in job_desc.accountabilities.accountabilities:
        print(f"- {acc.accountability}")
        print(f"  Purpose: {acc.purpose}")
        print(f"  Deliverable: {acc.major_deliverable} ({acc.timeline})")
    print()
    
    # Timeline Analysis
    print("Timeline Analysis:")
    print(f"Longest Deliverable: {job_desc.accountabilities.longest_deliverable}")
    print(f"Analysis: {job_desc.accountabilities.timeline_analysis}\n")
    
    # Requirements
    print("Knowledge & Experience:")
    for req in job_desc.requirements.knowledge_experience:
        print(f"- {req}")
    print()
    
    print("Technical Skills:")
    for skill in job_desc.requirements.technical_skills:
        print(f"- {skill}")
    print()
    
    print("Behavioural Skills:")
    for skill in job_desc.requirements.behavioural_skills:
        print(f"- {skill}")
    print()
    
    print("Other Requirements:")
    for req in job_desc.requirements.other_requirements:
        print(f"- {req}")


async def main():
    """Main execution function"""
    # Phase 1: Get basic input and generate base job description
    basic_info = await basic_input()
    
    print("\n🔄 Generating base job description...")
    print("📋 Analyzing organization and role type...")
    print("📋 Creating standard accountabilities and authorities...")
    print("📋 Setting typical requirements...")
    
    base_job_desc = await generate_base_job_description(basic_info)
    
    print("\n✅ Base job description generated!")
    print("\n=== PREVIEW - BASE JOB DESCRIPTION ===\n")
    print(f"Title: {base_job_desc.stratum_info.title}")
    print(f"Stratum: {base_job_desc.stratum_info.assigned_stratum.value}")
    print(f"Summary: {base_job_desc.stratum_info.position_summary}")
    
    # Phase 2: Get refinement input and customize
    refinement_info = await refinement_input(basic_info.job_title)
    
    # Combine inputs
    combined_input = EmployeeInput(
        org_name=basic_info.org_name,
        org_description=basic_info.org_description,
        job_title=basic_info.job_title,
        department=basic_info.department,
        role_uniqueness=refinement_info.role_uniqueness,
        scope_of_impact=refinement_info.scope_of_impact,
        decision_independence=refinement_info.decision_independence,
        special_factors=refinement_info.special_factors
    )
    
    print("\n🔄 Refining job description with your specific details...")
    print("📋 Adjusting stratum and scope...")
    print("📋 Customizing accountabilities...")
    print("📋 Refining authorities and requirements...")
    
    # Generate refined job description
    final_job_desc = await refine_job_description(base_job_desc, combined_input)
    
    # Display final results
    print("\n✅ Job description customized!")
    display_job_description(final_job_desc)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())