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


class EmployeeInput(BaseModel):
    job_title: str
    department: str
    reporting_structure: str
    decision_authority: str
    longest_project: str
    planning_horizon: str
    primary_responsibilities: str
    performance_metrics: str
    key_deliverables: str
    education_knowledge: str
    technical_skills: str
    special_requirements: str


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
    
    Analyze the provided job information and determine the appropriate stratum level based on:
    - Stratum I: Direct operational work; timeframe 1 day to 3 months
    - Stratum II: First-line management/specialized work; timeframe 3 months to 1 year  
    - Stratum III: Unit management; timeframe 1-2 years
    - Stratum IV: Business unit management; timeframe 2-5 years
    - Stratum V: Multi-value stream business management; timeframe 5-10 years
    - Stratum VI: Corporate/enterprise management; timeframe 10-20 years
    
    Focus on the longest project timeframe and planning horizon as key indicators.
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
    - Estimate realistic timeline for deliverable completion
    
    Analyze timeline consistency - if there's wide disparity (e.g., some tasks taking days, others years),
    flag this as a potential job design issue where the role may be doing work below its stratum level.
    
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
    - Leadership and management abilities
    - Communication and interpersonal skills
    - Problem-solving and analytical thinking
    - Adaptability, collaboration, influence
    
    Ensure each category is distinct and aligns with the stratum level and role complexity.
    Be specific rather than generic in all requirements.
    """
)


async def interactive_input():
    """Interactive questionnaire to gather employee inputs"""
    print("\n=== Job Description Generator ===")
    print("Please answer the following questions about your role:\n")
    
    job_title = input("What is your current job title? ")
    department = input("What department are you in? ")
    reporting_structure = input("Who do you report to and who reports to you? (titles only) ")
    decision_authority = input("What decisions can you make independently without requiring approval? (Consider budget, staffing, resources, processes) ")
    
    print("\nNow let's talk about your work timeframes...")
    print("Think about the things you need to get done and when they need to be completed.")
    longest_project = input("What is something you need to get done that takes the longest from start to finish? What is it and by when does it need to be completed? ")
    planning_horizon = input("When you make decisions or plan for your role, how far into the future are you typically planning? Give an example of what you're planning and by when it needs to be ready. ")
    print("\nLet's talk about what you need to accomplish...")
    primary_responsibilities = input("What are the main things you need to get done in your role? What are the key outcomes you're expected to deliver? ")
    performance_metrics = input("How is your performance measured? What results are you accountable for? ")
    
    print("\nWhat do you produce and by when?")
    key_deliverables = input("What specific things do you regularly produce or deliver? For each one, by when does it typically need to be completed? ")
    education_knowledge = input("What education, certifications, or specialized knowledge is required for your role? ")
    technical_skills = input("What technical skills and tools proficiency are needed to succeed in this position? ")
    special_requirements = input("Does your role have any special requirements (travel, physical demands, scheduling)? ")
    
    return EmployeeInput(
        job_title=job_title,
        department=department,
        reporting_structure=reporting_structure,
        decision_authority=decision_authority,
        longest_project=longest_project,
        planning_horizon=planning_horizon,
        primary_responsibilities=primary_responsibilities,
        performance_metrics=performance_metrics,
        key_deliverables=key_deliverables,
        education_knowledge=education_knowledge,
        technical_skills=technical_skills,
        special_requirements=special_requirements
    )


async def generate_job_description_multicall(employee_input: EmployeeInput) -> JobDescription:
    """Generate job description using multi-call approach with structured outputs"""
    
    # Call 1: Stratum determination and basic info
    stratum_prompt = f"""
    Analyze this job information and determine the stratum level:
    
    Job Title: {employee_input.job_title}
    Department: {employee_input.department}
    Reporting Structure: {employee_input.reporting_structure}
    Longest Project: {employee_input.longest_project}
    Planning Horizon: {employee_input.planning_horizon}
    Decision Authority: {employee_input.decision_authority}
    
    Primary Responsibilities:
    {employee_input.primary_responsibilities}
    """
    
    stratum_result = await stratum_agent.run(stratum_prompt)
    stratum_info = stratum_result.output
    
    # Call 2: Detailed accountabilities
    accountability_prompt = f"""
    Based on this stratum {stratum_info.assigned_stratum.value} position, break down the responsibilities into detailed accountabilities:
    
    Job Title: {stratum_info.title}
    Stratum Level: {stratum_info.assigned_stratum.value}
    
    Primary Responsibilities:
    {employee_input.primary_responsibilities}
    
    Performance Metrics: {employee_input.performance_metrics}
    Key Deliverables: {employee_input.key_deliverables}
    
    Extract specific accountabilities with purpose, deliverables, and timelines. Analyze for job design consistency.
    """
    
    accountability_result = await accountability_agent.run(accountability_prompt)
    accountabilities = accountability_result.output
    
    # Call 3: Authorities
    authority_prompt = f"""
    Define authorities for this Stratum {stratum_info.assigned_stratum.value} position:
    
    Job Title: {stratum_info.title}
    Stratum Level: {stratum_info.assigned_stratum.value}
    
    Decision Authority Information:
    {employee_input.decision_authority}
    
    Reporting Structure: {employee_input.reporting_structure}
    
    Create specific authorities appropriate for this stratum level.
    """
    
    authority_result = await authority_agent.run(authority_prompt)
    authorities = authority_result.output
    
    # Call 4: Requirements and abilities
    requirements_prompt = f"""
    Define requirements and demonstrated abilities for this Stratum {stratum_info.assigned_stratum.value} position:
    
    Job Title: {stratum_info.title}
    Stratum Level: {stratum_info.assigned_stratum.value}
    
    Education/Knowledge: {employee_input.education_knowledge}
    Technical Skills: {employee_input.technical_skills}
    Special Requirements: {employee_input.special_requirements}
    
    Primary Responsibilities Context:
    {employee_input.primary_responsibilities}
    
    Create comprehensive requirements including demonstrated abilities.
    """
    
    requirements_result = await requirements_agent.run(requirements_prompt)
    requirements = requirements_result.output
    
    return JobDescription(
        stratum_info=stratum_info,
        accountabilities=accountabilities,
        authorities=authorities,
        requirements=requirements
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
    # Get user input
    employee_input = await interactive_input()
    
    print("\n🔄 Generating job description using multi-call approach...")
    print("📋 Call 1: Determining stratum level and basic info...")
    print("📋 Call 2: Analyzing accountabilities and deliverables...")
    print("📋 Call 3: Defining authorities...")
    print("📋 Call 4: Creating requirements and abilities...")
    
    # Generate job description
    job_description = await generate_job_description_multicall(employee_input)
    
    # Display results
    display_job_description(job_description)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())