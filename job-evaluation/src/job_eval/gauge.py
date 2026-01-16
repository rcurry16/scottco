"""Revaluation gauge - assess if changes warrant re-evaluation."""
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .document_processor import DocumentProcessor
from .logging_config import log_with_extra

load_dotenv()

logger = logging.getLogger("job_eval.gauge")


class RevaluationRecommendation(BaseModel):
    """Recommendation on whether changes warrant re-evaluation."""

    should_reevaluate: bool = Field(
        description="Yes/No - do changes warrant formal re-evaluation?"
    )
    confidence: int = Field(
        ge=0, le=100,
        description="Confidence level in recommendation (0-100%)"
    )
    current_level: str = Field(
        description="Current classification level (e.g., 'EC-10')"
    )
    likely_new_level_range: str = Field(
        description="Expected classification level range after changes (e.g., 'EC-10 to EC-11')"
    )
    rationale: str = Field(
        description="Detailed justification for the recommendation"
    )
    key_factors: list[str] = Field(
        default_factory=list,
        description="Key factors influencing the decision"
    )
    categories_affected: list[str] = Field(
        default_factory=list,
        description="Which classification categories have significant changes"
    )
    risk_assessment: str = Field(
        description="Risk of not re-evaluating (low/medium/high)"
    )


class RevaluationGauge:
    """Assess whether position description changes warrant re-evaluation."""

    def __init__(self, api_key: str | None = None):
        """Initialize gauge with Claude API."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY must be set in environment or .env file"
            )
        self.client = Anthropic(api_key=self.api_key)

        # Load classification standards
        self.standards = self._load_standards()

    def _load_standards(self) -> dict[str, Any]:
        """Load classification standards from JSON."""
        standards_path = Path("data/classification_standards.json")
        if not standards_path.exists():
            raise FileNotFoundError(
                f"Classification standards not found at {standards_path}. "
                "Run: python src/job_eval/extract_standards.py"
            )

        with open(standards_path) as f:
            return json.load(f)

    def assess(
        self,
        comparison_json_path: str | Path
    ) -> RevaluationRecommendation:
        """
        Assess if changes from comparison warrant re-evaluation.

        Args:
            comparison_json_path: Path to comparison JSON from Tool 1.1

        Returns:
            Recommendation with confidence and justification
        """
        # Load comparison results
        with open(comparison_json_path) as f:
            comparison = json.load(f)

        # Extract new document path and load PDF
        new_doc_path = comparison.get('new_document')
        if not new_doc_path or not Path(new_doc_path).exists():
            raise FileNotFoundError(
                f"New document not found: {new_doc_path}. "
                "Ensure comparison JSON contains valid 'new_document' path."
            )

        print("Loading position description...")
        processor = DocumentProcessor(new_doc_path)
        new_position_text = processor.extract_text()

        # Extract current classification level from filename
        current_level = self._extract_level_from_path(new_doc_path)

        print(f"Analyzing change materiality for {current_level} position...")

        # Use Claude to assess with full context
        result = self._analyze_with_claude(comparison, new_position_text, current_level)

        return RevaluationRecommendation(**result)

    def _extract_level_from_path(self, path: str) -> str:
        """
        Extract EC level from filename.

        Examples:
            "EC 10 Policy Analyst.pdf" -> "EC-10"
            "EC-05 Executive Assistant.pdf" -> "EC-05"
        """
        # Try to find EC XX pattern in filename
        filename = Path(path).name
        match = re.search(r'EC[\s-]?(\d{1,2})', filename, re.IGNORECASE)

        if match:
            level_num = match.group(1).zfill(2)  # Pad to 2 digits
            return f"EC-{level_num}"

        # Default if not found
        return "EC-Unknown"

    def _analyze_with_claude(
        self,
        comparison: dict[str, Any],
        new_position_text: str,
        current_level: str
    ) -> dict[str, Any]:
        """Use Claude to assess if changes warrant re-evaluation."""
        prompt = self._build_assessment_prompt(comparison, new_position_text, current_level)

        # Log LLM call start
        start_time = time.time()
        log_with_extra(
            logger,
            logging.INFO,
            "LLM call started",
            provider="anthropic",
            operation="gauge",
            model="claude-haiku-4-5",
            event="llm_call_start"
        )

        try:
            message = self.client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=4000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text

            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text.strip()

            result = json.loads(json_text)

            # Log LLM call success with token usage
            duration = time.time() - start_time
            log_with_extra(
                logger,
                logging.INFO,
                "LLM call completed",
                provider="anthropic",
                operation="gauge",
                model="claude-haiku-4-5",
                duration_seconds=round(duration, 3),
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
                total_tokens=message.usage.input_tokens + message.usage.output_tokens,
                success=True,
                event="llm_call_complete"
            )

            return result

        except Exception as e:
            # Log LLM call failure
            duration = time.time() - start_time
            log_with_extra(
                logger,
                logging.ERROR,
                f"LLM call failed: {str(e)}",
                provider="anthropic",
                operation="gauge",
                model="claude-haiku-4-5",
                duration_seconds=round(duration, 3),
                success=False,
                error=str(e),
                error_type=type(e).__name__,
                event="llm_call_complete"
            )
            raise

    def _build_assessment_prompt(
        self,
        comparison: dict[str, Any],
        new_position_text: str,
        current_level: str
    ) -> str:
        """Build prompt for Claude to assess re-evaluation need."""

        # Get standards for current level and adjacent levels
        standards_context = self._get_relevant_standards(current_level)

        return f"""You are assessing whether changes to a position description are material enough to warrant formal re-evaluation.

**CRITICAL CONTEXT:**
- **Current Classification Level:** {current_level}
- You have the FULL position description (after changes) for context
- You also have the documented CHANGES between old and new versions
- Focus on: Are changes material enough to potentially move classification RELATIVE TO {current_level}?

**Important Rules:**
1. If changes enhance role but within {current_level} scope → MAY NOT warrant re-evaluation (or confirm same level)
2. If changes elevate beyond {current_level} expectations → Likely warrants re-evaluation for HIGHER level
3. NEVER suggest a LOWER level unless the role was explicitly reduced in scope
4. Consider what's EXPECTED at {current_level} when assessing changes

**Classification Framework:**
Positions are classified using PSC EC Grade Matrix (levels 1-17) across six categories:
1. Accountabilities (Key Responsibilities)
2. Knowledge & Experience
3. Decision Making (Challenges & Decision Making)
4. Customer & Relationship Management
5. Leadership
6. Project Management

{standards_context}

**Comparison Results:**
Summary: {comparison.get('summary', 'N/A')}

Overall Significance: {comparison.get('overall_significance', 'N/A')}

Changes by Section:
{json.dumps(comparison.get('changes_by_section', {}), indent=2)}

Classification-Relevant Changes:
{json.dumps(comparison.get('classification_relevant_changes', {}), indent=2)}

**Full Position Description (New Version):**
{new_position_text[:8000]}

**Your Task:**
Determine if these changes warrant formal re-evaluation RELATIVE TO {current_level} baseline. Consider:

1. **Do changes stay within {current_level} scope?** - If yes, may not warrant re-evaluation
2. **Do changes elevate beyond {current_level} expectations?** - If yes, likely warrants re-evaluation for higher level
3. **Categories affected** - which of the 6 classification categories have meaningful changes?
4. **Expected new level range** - Based on changes + full position context, what level range is appropriate?
5. **Risk assessment** - what's the risk of NOT re-evaluating?

**Required Output Format:**
Respond with ONLY valid JSON:

{{
  "should_reevaluate": true or false,
  "confidence": 85,
  "current_level": "{current_level}",
  "likely_new_level_range": "EC-10 to EC-11" (or "EC-10" if staying same, or "EC-11 to EC-12" if clearly elevated),
  "rationale": "Detailed explanation referencing {current_level} expectations and how changes compare",
  "key_factors": [
    "Factor 1 that influenced decision",
    "Factor 2",
    "Factor 3"
  ],
  "categories_affected": [
    "List of classification categories with significant changes"
  ],
  "risk_assessment": "low|medium|high"
}}

**Guidelines:**
- NEVER suggest lower than {current_level} unless role explicitly reduced
- Compare changes against what's EXPECTED at {current_level}
- Consider if mentorship/leadership are TYPICAL at this level or ELEVATING beyond it
- Be specific about new level range based on full position + changes
- Reference specific classification criteria for {current_level} and adjacent levels"""

        return prompt

    def _get_relevant_standards(self, current_level: str) -> str:
        """
        Get standards for current level and adjacent levels for comparison.

        Args:
            current_level: Current EC level (e.g., "EC-10")

        Returns:
            Formatted string with relevant level standards
        """
        if not self.standards:
            return "Classification standards not available."

        # Extract level number
        try:
            level_num = int(current_level.split('-')[1])
        except (IndexError, ValueError):
            return "Unable to extract level from current_level."

        # Get current, one below, one above
        levels_to_show = []
        for offset in [-1, 0, 1]:
            check_level = level_num + offset
            if 1 <= check_level <= 17:
                level_key = f"EC-{check_level:02d}"
                levels_to_show.append(level_key)

        summary = "\n**Relevant Classification Standards:**\n"

        for level_key in levels_to_show:
            if level_key in self.standards.get('classification_levels', {}):
                level_data = self.standards['classification_levels'][level_key]
                is_current = (level_key == current_level)
                marker = " ← CURRENT LEVEL" if is_current else ""

                summary += f"\n**{level_key}{marker}:** {level_data.get('title', 'N/A')}\n"

                # Show key differentiators from each category
                categories = level_data.get('categories', {})
                for cat_name, cat_items in categories.items():
                    if cat_items and len(cat_items) > 0:
                        # Show first 2 items from each category
                        summary += f"  {cat_name.replace('_', ' ').title()}:\n"
                        for item in cat_items[:2]:
                            summary += f"    - {item[:120]}...\n"

        return summary

    def _get_standards_summary(self) -> str:
        """Get summary of classification standards for context (deprecated, use _get_relevant_standards)."""
        return self._get_relevant_standards("EC-10")  # Default
