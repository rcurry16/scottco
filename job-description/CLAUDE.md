# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Install: `pip install -r requirements.txt`
- Run new job description generator (V2): `python job_desc_generator_v2.py`
- Configure organization: Edit `config.py`
- Test simple chat interface: `python chat.py`
- Set API key: `export MISTRAL_API_KEY=your_api_key_here`

## Architecture Overview

This codebase implements an AI-powered job description generator following the **Nova Scotia Government job description template structure**. It uses a 6-agent architecture with `pydantic-ai` and Mistral AI.

### Key Design Decisions

1. **No Requisite Organization (RO) Stratum Classification**: All references to stratum levels have been removed from user-facing output
2. **Internal Role Level Inference**: System infers role level (Entry/Mid/Senior/Executive) for quality calibration only - never shown to user
3. **Admin Configuration**: Organizational context loaded from `config.py` once at startup
4. **Moderate-Depth Questions**: 12 strategic questions across 5 categories (basic info, responsibilities, people, scope, requirements)
5. **Multi-Agent Generation**: 6 specialized agents each handle one section of the template
6. **Dual Output**: Console display + text file export

## File Structure

```
job-desc-tool/
├── config.py                      # Admin configuration (org context, templates, settings)
├── models.py                      # Pydantic data models (NS Gov template structure)
├── output_formatter.py            # Console display and text file export functions
├── job_desc_generator_v2.py       # Main generator with 6 agents and questionnaire
├── output/                        # Generated job description text files
├── _archive/                      # Archived old generator versions
│   ├── job_desc_comprehensive.py  # OLD: 12-question single-pass approach
│   └── job_desc_iterative.py      # OLD: 2-phase approach
├── job-desc-examples/             # Reference PDFs (NS Gov job descriptions)
├── chat.py                        # Simple chat interface for API testing
├── requirements.txt               # pydantic-ai==0.1.6, pydantic>=2.0.0
├── README.md                      # User documentation
└── CLAUDE.md                      # This file
```

## Nova Scotia Government Template Structure

The generator creates job descriptions with these sections (in order):

1. **Classification Job Information**: SAP Job ID, Position Title, Pay Grade, Add-On Eligibility, Standardized/Inactive status, Date Last Evaluated
2. **Job Information**: Job/Working Title, Department, Division/Section, Reports To, Exclusion Status
3. **Overall Purpose**: 1-3 paragraph narrative describing role's primary function and organizational context
4. **Key Responsibilities**: 6-10 bulleted responsibilities using action verbs (Leads, Provides, Ensures, etc.)
5. **People Management**: Type of Role, Direct/Indirect Reports, Other Resources Managed
6. **Scope**: Four subsections - Contacts (Typical), Innovation, Decision Making, Impact of Results, Other (usually empty)
7. **Licenses/Certifications**: Required licenses, certs, professional designations (often empty)
8. **Working Conditions**: Four subsections - Physical Effort, Physical Environment, Sensory Attention, Psychological Pressures
9. **Boilerplate**: "May perform other related duties as assigned", assignment-specific requirements note

## Multi-Agent Architecture

### Agent 1: Job Information & Purpose Agent
- **Generates**: `JobInformation` + `OverallPurpose` + `RoleLevelAssessment` (internal)
- **Input**: Questions 1-3, 6, organizational context
- **Purpose**: Creates formal job metadata block and 1-3 paragraph narrative summary
- **Key Feature**: Infers role level (Entry/Mid/Senior/Executive) based on decision authority, people management, impact, and innovation complexity
- **Role Level Use**: Passed to other agents to calibrate language sophistication and detail depth

### Agent 2: Key Responsibilities Agent
- **Generates**: `KeyResponsibilities` (6-10 items)
- **Input**: Questions 4-5, role level, overall purpose
- **Purpose**: Creates specific, actionable responsibilities starting with action verbs
- **Calibration**: Entry roles = straightforward tasks; Executive = multi-faceted strategic initiatives

### Agent 3: People Management Agent
- **Generates**: `PeopleManagement`
- **Input**: Question 7, role level
- **Purpose**: Determines individual contributor vs manager, number of reports, other resources
- **Logic**: Conservative estimates based on role level (Entry/Mid: 1-5 direct; Senior: 3-10; Executive: 2-5 direct, 10-40 indirect)

### Agent 4: Scope Agent
- **Generates**: `ScopeSection` (all 4 subsections)
- **Input**: Questions 8-11, role level
- **Purpose**: Creates detailed Contacts, Innovation, Decision Making, Impact of Results subsections
- **Calibration**: Entry = 2-4 sentences each; Mid = 4-6 sentences; Senior = 6-8 sentences; Executive = multi-paragraph

### Agent 5: Requirements Agent
- **Generates**: `LicensesCertifications`
- **Input**: Question 12, key responsibilities
- **Purpose**: Extracts REQUIRED (not preferred) licenses/certs
- **Conservative**: Returns empty list if no clear requirements mentioned

### Agent 6: Working Conditions Agent
- **Generates**: `WorkingConditions` (all 4 subsections)
- **Input**: Question 12, standard templates from config, role level
- **Purpose**: Selects appropriate working condition descriptions from templates
- **Templates**: Uses exact text from `config.STANDARD_WORKING_CONDITIONS` based on role level and special requirements

## Data Models (models.py)

### Input Models
- **OrganizationalContext**: Loaded from config (org name, industry, location, dept default)
- **UserResponses**: Captures all 12 user answers from questionnaire

### Output Models (matching NS Gov template)
- **ClassificationJobInformation**: SAP ID, title, pay grade, dates (mostly placeholders)
- **JobInformation**: Title, department, division, reports to, exclusion status
- **OverallPurpose**: Single string field (1-3 paragraph narrative)
- **KeyResponsibilities**: List of 6-10 responsibility strings
- **PeopleManagement**: Type, direct/indirect reports, other resources
- **ScopeSection**: Four string fields (contacts, innovation, decision_making, impact, other)
- **LicensesCertifications**: List of requirement strings (can be empty)
- **WorkingConditions**: Four string fields (physical_effort, physical_environment, sensory_attention, psychological_pressures)
- **BoilerplateElements**: Standard text (may perform other duties, assignment-specific note, data from conversion)
- **JobDescription**: Top-level model combining all sections above

### Internal Models (never in final output)
- **RoleLevelAssessment**: Inferred level (Entry/Mid/Senior/Executive) + rationale
- **RoleLevel**: Enum with four values

## Configuration (config.py)

### Organizational Context
- `ORGANIZATION_NAME`: Default org name
- `INDUSTRY`: Industry type
- `LOCATION`: Geographic location
- `DEPARTMENT_DEFAULT`: Optional department default

### Working Conditions Templates
- Predefined text for each working condition level:
  - Physical Effort: light, moderate, substantial
  - Physical Environment: standard_office, mixed, challenging
  - Sensory Attention: moderate, considerable, extensive
  - Psychological Pressures: low, moderate, high

### Boilerplate Text
- `BOILERPLATE_MAY_PERFORM_OTHER_DUTIES`
- `BOILERPLATE_ASSIGNMENT_SPECIFIC`
- `DATA_FROM_CONVERSION` (usually empty)

### Classification Defaults
- SAP Job ID, Pay Grade, Add-On Eligibility, Standardized, Inactive, Date Last Evaluated

### Output Settings
- `OUTPUT_DIRECTORY`: Default "output"
- `OUTPUT_FILENAME_TEMPLATE`: Template string with job_title and timestamp
- `OUTPUT_INCLUDE_TIMESTAMP`: Boolean

### AI Settings
- `AI_MODEL`: Default "mistral:mistral-small-latest"
- `AI_PROVIDER`: Default "mistral"
- `AGENT_TEMPERATURES`: Dict with temperature for each agent (0.0-1.0)

## Questionnaire Flow (12 Questions)

### Phase 1: Basic Information (3 questions)
1. Job/Working Title
2. Department + Division/Section (optional)
3. Reports To (position title)

### Phase 2: Role Responsibilities (3 questions)
4. Primary Responsibilities (main duties and outcomes)
5. Key Deliverables (specific outputs/results)
6. Unique Aspects (what makes this role different)

### Phase 3: People & Relationships (2 questions)
7. People Management (yes/no, then number of direct/indirect reports if yes)
8. Key Contacts (internal/external stakeholders)

### Phase 4: Scope & Decision-Making (3 questions)
9. Decision Authority (types of decisions, level of autonomy)
10. Innovation & Problem-Solving (degree of creativity, judgment, innovation)
11. Impact of Results (how outcomes affect organization/clients/goals)

### Phase 5: Requirements (1 question)
12. Special Requirements (licenses, certs, travel, working conditions, etc.)

## Generation Workflow

1. Load `config.py` (organizational context)
2. Display intro and collect 12 user responses via `collect_user_responses()`
3. Run **Agent 1** → Generate Job Info + Overall Purpose + Infer Role Level
4. Run **Agent 2** → Generate Key Responsibilities (using role level)
5. Run **Agent 3** → Generate People Management (using role level)
6. Run **Agent 4** → Generate Scope (using role level)
7. Run **Agent 5** → Generate Licenses/Certifications
8. Run **Agent 6** → Generate Working Conditions (using role level + templates)
9. Assemble all sections into `JobDescription` model
10. Display to console via `output_formatter.display_to_console()`
11. Save to text file via `output_formatter.save_to_file()`

## Output Formatting (output_formatter.py)

### Console Display
- Formatted with clear section headers (uppercase, with separator lines)
- Bullet points for lists
- Clean spacing between sections
- Matches visual structure of NS Gov PDFs (text-based version)

### Text File Export
- Same content as console display
- Saved to: `output/job_description_[sanitized_job_title]_[YYYYMMDD_HHMMSS].txt`
- Plain text format, well-structured for copy/paste or further editing
- Filename sanitization: replaces invalid chars, spaces with underscores, limits length to 50 chars

## Role Level Inference Logic

**Agent 1** (Job Information & Purpose Agent) infers role level based on:

- **Decision-making authority and autonomy** (Question 9)
  - Entry: Limited autonomy, requires approval for most decisions
  - Mid: Some autonomy, can make routine decisions independently
  - Senior: High autonomy, makes complex decisions within framework
  - Executive: Strategic decision-making, sets policy/direction

- **People management responsibilities** (Question 7)
  - Entry: No direct reports
  - Mid: May lead small teams (1-5 direct reports)
  - Senior: Leads teams/functions (3-10 direct reports)
  - Executive: Multi-department leadership (2-5 direct, 10-40 indirect)

- **Scope of organizational impact** (Question 11)
  - Entry: Individual or local team impact
  - Mid: Department-level impact
  - Senior: Organizational impact, cross-functional influence
  - Executive: Organization-wide, strategic impact

- **Innovation/problem-solving complexity** (Question 10)
  - Entry: Follows established procedures, routine problem-solving
  - Mid: Applies judgment within frameworks, moderate complexity
  - Senior: Expert-level judgment, complex novel problems
  - Executive: Creates new approaches, navigates strategic ambiguity

**Output**: `RoleLevelAssessment` with inferred level + rationale (for internal use only)

**Usage**: Passed to Agents 2-6 to calibrate:
- Language sophistication (formal vs strategic)
- Scope detail depth (brief vs multi-paragraph)
- Working conditions (entry = lower stress, executive = higher stress)
- Responsibility framing (task-oriented vs strategic)

## Styling and Tone

### Overall Tone
- **Formal, third-person perspective** throughout
- **Present tense** for responsibilities and duties
- **Action-verb heavy**: Leads, Provides, Ensures, Conducts, Develops, Manages, Coordinates, Oversees
- **Government/professional terminology**: Use terms like "client departments," "stakeholders," "strategic," "accountability"

### Sentence Structure
- **Overall Purpose**: Longer, complex sentences establishing context (1-3 paragraphs)
- **Key Responsibilities**: Shorter, direct action statements (complete sentences)
- **Scope sections**: Mix of sentence fragments and full sentences

### Examples by Role Level

**Entry-level** (e.g., Financial Services Officer 1):
- "Provides information and recommendations to financial staff on matters relating to accounting and audit procedures, financial policies, and government financial reporting system (SAP)."

**Mid-level** (e.g., Program Administration Officer 3):
- "Conduct audits of licensed child care programs to assess service quality, policy alignment, and compliance with departmental standards and federal/provincial funding requirements."

**Senior** (e.g., Classification Consultant):
- "Leads the assessment and analysis of jobs, conducting the job evaluation, determining the classification, preparing the written evaluation rationale for the client and advising on/analyzing compensation policies and procedures for jobs."

**Executive** (e.g., Executive Director):
- "Provides strategic financial leadership by developing integrated long-term financial strategies, funding methodologies, and operational reviews aligned with government priorities, and provides high-level strategic, operational, and policy advice to senior leaders, including the Minister, Deputy Minister, and Associate Deputy Minister."

## Security Notes
- **CRITICAL**: Both old generator scripts had hardcoded API keys - these have been archived
- API keys should ONLY be set via environment variables: `export MISTRAL_API_KEY=your_api_key_here`
- Never commit files containing actual API keys
- The new V2 generator properly checks for environment variable and raises error if not set

## Code Style Guidelines
- Use PEP 8 conventions for Python code
- Imports: group standard library, third-party, and local imports with blank lines between groups
- Type annotations: use for all function parameters and return types
- Naming: snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
- String formatting: use f-strings for readability
- Docstrings: include for all functions and classes
- Error handling: use try/except blocks with specific exceptions
- Pydantic models: use for all data structures with strict type validation
- Async: use async/await patterns for API calls and I/O operations

## Testing Guidance

When testing the generator, use scenarios across different role levels:

### Entry-level Test (e.g., Financial Analyst, Administrative Assistant)
- Limited decision authority
- No people management
- Department-level impact
- Straightforward problem-solving

### Mid-level Test (e.g., Program Officer, Financial Advisor)
- Some autonomy
- May manage 1-3 people
- Department/cross-department impact
- Moderate complexity problem-solving

### Senior Test (e.g., Senior Consultant, Program Manager)
- High autonomy
- Manages team of 3-8
- Organizational impact
- Expert judgment, complex problems

### Executive Test (e.g., Director, Executive Director)
- Strategic decision-making
- Multi-department leadership (2-5 direct, 10-40 indirect)
- Organization-wide impact
- Creates new approaches, navigates ambiguity

## Common Modifications

### Adding a New Question
1. Edit `collect_user_responses()` in `job_desc_generator_v2.py`
2. Add new field to `UserResponses` model in `models.py`
3. Update agent prompts to use new information

### Changing Working Conditions Templates
1. Edit `STANDARD_WORKING_CONDITIONS` in `config.py`
2. Agent 6 will automatically use updated templates

### Adjusting Output Format
1. Edit `format_console_output()` in `output_formatter.py`
2. Changes apply to both console and file output

### Changing Number of Responsibilities
1. Edit `MIN_RESPONSIBILITIES` and `MAX_RESPONSIBILITIES` in `config.py`
2. Update `KeyResponsibilities` model min_items/max_items in `models.py`

## Archive

Old generator versions are in `_archive/`:
- `job_desc_comprehensive.py`: 12-question single-pass approach with RO stratum classification
- `job_desc_iterative.py`: 2-phase approach (4 basic questions → generate → 4 refinement questions)

These are preserved for reference but should not be used going forward.
