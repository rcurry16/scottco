"""
Output Formatter for Job Description Generator

Handles both console display and text file export of job descriptions
following the Nova Scotia Government template format.
"""

import os
from datetime import datetime
from typing import Optional
from models import JobDescription
import config


def sanitize_filename(text: str) -> str:
    """Sanitize text for use in filename"""
    # Remove or replace characters that are problematic in filenames
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        text = text.replace(char, '_')
    # Replace spaces with underscores
    text = text.replace(' ', '_')
    # Limit length
    return text[:50]


def format_console_output(job_desc: JobDescription) -> str:
    """Format job description for console display with proper spacing and headers"""

    output = []

    # Header
    output.append("=" * 80)
    output.append(f"{job_desc.job_info.job_working_title.upper()}")
    output.append("JOB DESCRIPTION")
    output.append("=" * 80)
    output.append("")

    # ========================================================================
    # CLASSIFICATION JOB INFORMATION
    # ========================================================================
    output.append("CLASSIFICATION JOB INFORMATION")
    output.append("-" * 80)
    if job_desc.classification_info.sap_job_id:
        output.append(f"SAP Job ID: {job_desc.classification_info.sap_job_id}")
    output.append(f"Position/Classification Title: {job_desc.classification_info.position_classification_title}")
    if job_desc.classification_info.pay_grade:
        output.append(f"Pay Grade: {job_desc.classification_info.pay_grade}")
    if job_desc.classification_info.add_on_eligibility is not None:
        output.append(f"Add-On Eligibility: {job_desc.classification_info.add_on_eligibility}")
    output.append(f"Standardized: {'Yes' if job_desc.classification_info.standardized else 'No'}")
    output.append(f"Inactive: {'Yes' if job_desc.classification_info.inactive else 'No'}")
    if job_desc.classification_info.date_last_evaluated:
        output.append(f"Date Last Evaluated: {job_desc.classification_info.date_last_evaluated}")
    output.append("")

    # ========================================================================
    # JOB INFORMATION
    # ========================================================================
    output.append("JOB INFORMATION")
    output.append("-" * 80)
    output.append(f"Job/Working Title: {job_desc.job_info.job_working_title}")
    output.append(f"Department: {job_desc.job_info.department}")
    if job_desc.job_info.division_section:
        output.append(f"Division/Section: {job_desc.job_info.division_section}")
    reports_to_text = job_desc.job_info.reports_to
    if job_desc.job_info.reports_to_sap_id:
        reports_to_text += f" - {job_desc.job_info.reports_to_sap_id}"
    output.append(f"Reports To (Position Title): {reports_to_text}")
    output.append(f"Exclusion Status: {job_desc.job_info.exclusion_status.value}")
    output.append("")

    # ========================================================================
    # OVERALL PURPOSE
    # ========================================================================
    output.append("OVERALL PURPOSE")
    output.append("-" * 80)
    output.append(job_desc.overall_purpose.purpose_text)
    output.append("")

    # ========================================================================
    # KEY RESPONSIBILITIES
    # ========================================================================
    output.append("KEY RESPONSIBILITIES")
    output.append("-" * 80)
    for responsibility in job_desc.key_responsibilities.responsibilities:
        output.append(f"• {responsibility}")
        output.append("")

    # Boilerplate
    output.append(job_desc.boilerplate.may_perform_other_duties)
    output.append("")
    output.append(job_desc.boilerplate.assignment_specific_note)
    output.append("")

    # ========================================================================
    # PEOPLE MANAGEMENT
    # ========================================================================
    output.append("PEOPLE MANAGEMENT")
    output.append("-" * 80)
    output.append(f"Type of Role: {job_desc.people_management.type_of_role}")
    if job_desc.people_management.num_direct_reports:
        output.append(f"# of Direct Reports: {job_desc.people_management.num_direct_reports}")
    if job_desc.people_management.classifications_of_direct_reports:
        output.append(f"Classifications/Titles of Direct Reports: {job_desc.people_management.classifications_of_direct_reports}")
    if job_desc.people_management.num_indirect_reports:
        output.append(f"# of Indirect Reports: {job_desc.people_management.num_indirect_reports}")
    if job_desc.people_management.other_resources:
        output.append(f"Other Resources: {job_desc.people_management.other_resources}")
    output.append("")

    # ========================================================================
    # SCOPE
    # ========================================================================
    output.append("SCOPE")
    output.append("-" * 80)

    output.append("Contacts (Typical):")
    output.append(job_desc.scope.contacts_typical)
    output.append("")

    output.append("Innovation:")
    output.append(job_desc.scope.innovation)
    output.append("")

    output.append("Decision Making:")
    output.append(job_desc.scope.decision_making)
    output.append("")

    output.append("Impact of Results:")
    output.append(job_desc.scope.impact_of_results)
    output.append("")

    if job_desc.scope.other:
        output.append("Other:")
        output.append(job_desc.scope.other)
        output.append("")

    # ========================================================================
    # LICENSES/CERTIFICATIONS
    # ========================================================================
    output.append("LICENSES/CERTIFICATIONS")
    output.append("-" * 80)
    if job_desc.licenses_certifications.requirements:
        for req in job_desc.licenses_certifications.requirements:
            output.append(f"• {req}")
    else:
        output.append("(None specified)")
    output.append("")

    # ========================================================================
    # WORKING CONDITIONS
    # ========================================================================
    output.append("WORKING CONDITIONS")
    output.append("-" * 80)

    output.append("Physical Effort")
    output.append(job_desc.working_conditions.physical_effort)
    output.append("")

    output.append("Physical Environment")
    output.append(job_desc.working_conditions.physical_environment)
    output.append("")

    output.append("Sensory Attention")
    output.append(job_desc.working_conditions.sensory_attention)
    output.append("")

    output.append("Psychological Pressures")
    output.append(job_desc.working_conditions.psychological_pressures)
    output.append("")

    # ========================================================================
    # ADDITIONAL INFORMATION
    # ========================================================================
    if job_desc.boilerplate.additional_information:
        output.append("Additional Information:")
        output.append(job_desc.boilerplate.additional_information)
        output.append("")

    if job_desc.boilerplate.data_from_conversion:
        output.append("Data From Conversion:")
        output.append(job_desc.boilerplate.data_from_conversion)
        output.append("")

    # Footer
    output.append("=" * 80)
    output.append("End of Job Description")
    output.append("=" * 80)

    return "\n".join(output)


def display_to_console(job_desc: JobDescription) -> None:
    """Display formatted job description to console"""
    formatted_output = format_console_output(job_desc)
    print("\n\n")
    print(formatted_output)
    print("\n\n")


def save_to_file(job_desc: JobDescription, output_dir: Optional[str] = None) -> str:
    """
    Save job description to text file

    Args:
        job_desc: The JobDescription model to save
        output_dir: Directory to save to (defaults to config.OUTPUT_DIRECTORY)

    Returns:
        Path to saved file
    """
    # Use config default if not specified
    if output_dir is None:
        output_dir = config.OUTPUT_DIRECTORY

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename
    job_title_sanitized = sanitize_filename(job_desc.job_info.job_working_title)

    if config.OUTPUT_INCLUDE_TIMESTAMP:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"job_description_{job_title_sanitized}_{timestamp}.txt"
    else:
        filename = f"job_description_{job_title_sanitized}.txt"

    filepath = os.path.join(output_dir, filename)

    # Format and save
    formatted_output = format_console_output(job_desc)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(formatted_output)

    return filepath


def display_and_save(job_desc: JobDescription, output_dir: Optional[str] = None) -> str:
    """
    Display job description to console AND save to file

    Args:
        job_desc: The JobDescription model to process
        output_dir: Directory to save to (defaults to config.OUTPUT_DIRECTORY)

    Returns:
        Path to saved file
    """
    # Display to console
    display_to_console(job_desc)

    # Save to file
    filepath = save_to_file(job_desc, output_dir)

    print(f"✅ Job description saved to: {filepath}")
    print("")

    return filepath
