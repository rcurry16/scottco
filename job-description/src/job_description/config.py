"""
Configuration file for Job Description Generator

This file contains organizational context and standard templates that are used
across all job descriptions. Edit these values to customize for your organization.
"""

# ============================================================================
# ORGANIZATIONAL CONTEXT
# ============================================================================

ORGANIZATION_NAME = "Your Organization Name"
INDUSTRY = "Public Sector"
LOCATION = "Nova Scotia, Canada"
DEPARTMENT_DEFAULT = ""  # Leave empty to prompt user, or set default

# Detailed organizational description (optional)
# Provide context about mission, values, culture, size, unique characteristics, etc.
# This helps the AI generate job descriptions that align with organizational identity
ORGANIZATION_DESCRIPTION = ""  # Example: "A progressive 500-person non-profit focused on sustainable development..."

# ============================================================================
# STANDARD WORKING CONDITIONS TEMPLATES
# ============================================================================

STANDARD_WORKING_CONDITIONS = {
    "physical_effort": {
        "light": """Work activities involve rotating positions of light physical activities, requiring little physical effort and/or easy muscle movements. Majority of time is spent in a comfortable office setting, with some site visits as required, and frequent opportunity to move about and/or change positions.""",
        "moderate": """Work activities involve a mix of sedentary and active tasks, requiring moderate physical effort. Regular movement between office and field locations, with occasional lifting or physical exertion as needed.""",
        "substantial": """Work activities require regular physical effort, including standing, walking, lifting, or other physically demanding tasks for extended periods."""
    },

    "physical_environment": {
        "standard_office": """Works in an environment with exposure to acceptable working conditions. Occasional exposure to mild unpleasant or disagreeable conditions (e.g., dust, dirt, noise, etc.) and possibility of accident or health hazards is minimal.""",
        "mixed": """Works in varied environments including office settings and field locations. Exposure to changing conditions depending on assignment, with appropriate safety measures in place.""",
        "challenging": """Regular exposure to challenging environmental conditions including weather, noise, or other factors requiring special precautions or protective equipment."""
    },

    "sensory_attention": {
        "moderate": """Work activities involve a need to concentrate on a variety of sensory inputs for short durations, several times a day, requiring attention to detail. If interrupted, some lost time is experienced to backtrack and continue activities. The need for detailed or precise work and/or repetitive tasks is moderate.""",
        "considerable": """Work activities involve a frequent need to concentrate on a variety of sensory inputs for lengthy durations requiring diligence and attention in order to interpret information. If interrupted, considerable time is spent backtracking to continue activities. The need for visual attention, mental concentration, and detailed/precise work is considerable.""",
        "extensive": """Work requires sustained, intense concentration and attention to complex sensory inputs. Frequent need to process multiple streams of information simultaneously. Interruptions result in significant lost time and require extensive refocusing."""
    },

    "psychological_pressures": {
        "low": """Work activities are performed in an environment with occasional exposure to one or more psychological pressures (e.g., deadlines, repetitive work, moderate unpleasant public/client situations, etc.). Has the ability to largely control the pace of work with few interruptions. The degree of psychological stress is not noticeably disruptive to the work, and the unpleasant reaction is not too strong/persistent. Disruption to personal life due to work, work schedules or travel is moderate.""",
        "moderate": """Work involves regular exposure to competing priorities, deadlines, and stakeholder demands. Some ability to control pace of work, though interruptions are common. Psychological stress is noticeable but manageable. Work-life balance requires conscious effort.""",
        "high": """Work activities are performed in an environment with frequent exposure to psychological pressure conditions where the psychological stress is noticeable (e.g., conflicting/competing deadlines, dealing with angry/demanding customers/clients on a continued basis, etc.). There is limited capability to control the pace of work and the number of disruptions, and concern exists about occurrence of dangerous situations. Disruption to personal life due to work, work schedules or travel is considerable."""
    }
}

# ============================================================================
# BOILERPLATE TEXT
# ============================================================================

BOILERPLATE_MAY_PERFORM_OTHER_DUTIES = "May perform other related duties as assigned"

BOILERPLATE_ASSIGNMENT_SPECIFIC = """In addition to the duties and responsibilities outlined in the job description, this job may include other, assignment-specific requirements (ex: French language, drivers license, membership in an employment equity group or security screening, etc.)"""

DATA_FROM_CONVERSION = ""  # Usually left empty

# ============================================================================
# CLASSIFICATION JOB INFORMATION DEFAULTS
# ============================================================================
# These fields are often system-generated or left as placeholders
# Set to None or empty string if not used

CLASSIFICATION_DEFAULTS = {
    "sap_job_id": "",  # Usually system-generated
    "pay_grade": "",  # Determined separately
    "add_on_eligibility": None,  # True/False/None
    "standardized": False,
    "inactive": False,
    "date_last_evaluated": ""  # Will be set to current date if empty
}

# ============================================================================
# EXCLUSION STATUS OPTIONS
# ============================================================================

EXCLUSION_STATUS_OPTIONS = ["Excluded", "Non-Excluded"]
EXCLUSION_STATUS_DEFAULT = "Non-Excluded"

# ============================================================================
# FORMATTING PREFERENCES
# ============================================================================

# How to display responsibilities in output
RESPONSIBILITIES_FORMAT = "bullets"  # Options: "bullets", "numbered", "paragraphs"

# Number of responsibilities to generate
MIN_RESPONSIBILITIES = 6
MAX_RESPONSIBILITIES = 10

# Overall Purpose paragraph count
OVERALL_PURPOSE_PARAGRAPHS = "1-3"  # Guidance for AI

# ============================================================================
# OUTPUT SETTINGS
# ============================================================================

OUTPUT_DIRECTORY = "output"
OUTPUT_FILENAME_TEMPLATE = "job_description_{job_title}_{timestamp}.txt"
OUTPUT_INCLUDE_TIMESTAMP = True

# ============================================================================
# API SETTINGS
# ============================================================================

# Mistral Model Settings (for mistral version)
MISTRAL_MODEL = "mistral:mistral-small-latest"
MISTRAL_API_KEY_NAME = "MISTRAL_API_KEY"

# Anthropic Model Settings (for anthropic/claude version)
ANTHROPIC_MODEL = "claude-sonnet-4-5-20250929"  # Claude Sonnet 4.5
ANTHROPIC_API_KEY_NAME = "ANTHROPIC_API_KEY"

# Legacy settings (for backward compatibility)
AI_MODEL = "mistral:mistral-small-latest"
AI_PROVIDER = "mistral"  # Options: "mistral", "anthropic", "openai", etc.

# Temperature settings for different agents (0.0-1.0, higher = more creative)
AGENT_TEMPERATURES = {
    "job_info": 0.3,  # More factual
    "responsibilities": 0.5,  # Balanced
    "people_mgmt": 0.3,  # More factual
    "scope": 0.6,  # More creative
    "requirements": 0.4,  # Balanced
    "working_conditions": 0.3  # More factual
}

# ============================================================================
# TOKEN USAGE & COST TRACKING
# ============================================================================

# Currency conversion
USD_TO_CAD_RATE = 1.40  # Adjust as needed

# Anthropic Claude 3.7 Sonnet pricing (USD per 1M tokens)
ANTHROPIC_SONNET_INPUT_COST = 3.00
ANTHROPIC_SONNET_OUTPUT_COST = 15.00

# Mistral Small pricing (USD per 1M tokens)
MISTRAL_SMALL_INPUT_COST = 0.10
MISTRAL_SMALL_OUTPUT_COST = 0.80
