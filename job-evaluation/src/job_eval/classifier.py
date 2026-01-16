"""First pass classifier - propose classification level for position."""
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .document_processor import DocumentProcessor
from .logging_config import log_with_extra

load_dotenv()

logger = logging.getLogger("job_eval.classifier")


class ClassificationRecommendation(BaseModel):
    """Classification recommendation for a position description."""

    position_title: str = Field(
        description="Extracted position title from document"
    )
    recommended_level: str = Field(
        description="Recommended classification level (e.g., 'EC-10')"
    )
    confidence: int = Field(
        ge=0, le=100,
        description="Confidence level in recommendation (0-100%)"
    )
    previous_level: str | None = Field(
        default=None,
        description="Previous classification level (if available from context)"
    )
    rationale: str = Field(
        description="Detailed justification for the recommendation"
    )
    category_analysis: dict[str, str] = Field(
        default_factory=dict,
        description="Analysis per classification category (6 categories)"
    )
    supporting_evidence: list[str] = Field(
        default_factory=list,
        description="Key factors supporting the recommended level"
    )
    alternative_levels: list[str] = Field(
        default_factory=list,
        description="Other plausible classification levels to consider"
    )
    change_context_used: bool = Field(
        default=False,
        description="Whether comparison/gauge context was used in analysis"
    )
    comparable_positions: list[str] = Field(
        default_factory=list,
        description="Similar positions at this level (from standards)"
    )


class FirstPassClassifier:
    """Classify position descriptions using AI analysis."""

    def __init__(self, api_key: str | None = None):
        """Initialize classifier with Claude API."""
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

    def classify(
        self,
        pdf_path: str | Path,
        comparison_data: dict[str, Any] | None = None,
        gauge_data: dict[str, Any] | None = None
    ) -> ClassificationRecommendation:
        """
        Classify a position description.

        Args:
            pdf_path: Path to position description PDF
            comparison_data: Optional comparison results from Tool 1.1
            gauge_data: Optional gauge results from Tool 1.2

        Returns:
            Classification recommendation with confidence and justification
        """
        # Extract position text
        print("Loading position description...")
        processor = DocumentProcessor(pdf_path)
        position_text = processor.extract_text()

        # Determine if using context
        has_context = comparison_data is not None or gauge_data is not None

        if has_context:
            print("Analyzing position with change context...")
        else:
            print("Analyzing position (standalone mode)...")

        # Use Claude to classify
        result = self._analyze_with_claude(
            position_text,
            comparison_data,
            gauge_data
        )

        return ClassificationRecommendation(**result)

    def _analyze_with_claude(
        self,
        position_text: str,
        comparison_data: dict[str, Any] | None,
        gauge_data: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Use Claude to classify position."""
        prompt = self._build_classification_prompt(
            position_text,
            comparison_data,
            gauge_data
        )

        # Log LLM call start
        start_time = time.time()
        log_with_extra(
            logger,
            logging.INFO,
            "LLM call started",
            provider="anthropic",
            operation="classify",
            model="claude-haiku-4-5",
            event="llm_call_start"
        )

        try:
            message = self.client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=8000,
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
                operation="classify",
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
                operation="classify",
                model="claude-haiku-4-5",
                duration_seconds=round(duration, 3),
                success=False,
                error=str(e),
                error_type=type(e).__name__,
                event="llm_call_complete"
            )
            raise

    def _build_classification_prompt(
        self,
        position_text: str,
        comparison_data: dict[str, Any] | None,
        gauge_data: dict[str, Any] | None
    ) -> str:
        """Build prompt for Claude to classify position."""

        # Get all classification standards
        standards_context = self._get_all_standards()

        # Build context section if data provided
        context_section = ""
        has_context = False
        previous_level = None

        if gauge_data:
            has_context = True
            previous_level = gauge_data.get('current_level', 'Unknown')
            context_section += f"""
**CONTEXT FROM REVALUATION GAUGE (Tool 1.2):**
- Previous Classification: {previous_level}
- Should Reevaluate: {gauge_data.get('should_reevaluate', 'N/A')}
- Gauge Confidence: {gauge_data.get('confidence', 'N/A')}%
- Likely New Level Range: {gauge_data.get('likely_new_level_range', 'N/A')}
- Gauge Rationale: {gauge_data.get('rationale', 'N/A')[:500]}...
- Categories Affected: {', '.join(gauge_data.get('categories_affected', []))}

"""

        if comparison_data:
            has_context = True
            context_section += f"""
**CONTEXT FROM COMPARISON (Tool 1.1):**
- Overall Significance: {comparison_data.get('overall_significance', 'N/A')}
- Summary: {comparison_data.get('summary', 'N/A')}

Classification-Relevant Changes:
{json.dumps(comparison_data.get('classification_relevant_changes', {}), indent=2)[:1000]}...

"""

        context_instruction = ""
        if has_context:
            context_instruction = f"""
**IMPORTANT: You have context from previous analysis steps.**
- Start from the baseline of the previous level: {previous_level or 'as indicated above'}
- Consider the documented changes and their significance
- Use the gauge recommendation as INPUT (not constraint) for your analysis
- Your classification should align with the evidence but be independent
"""
        else:
            context_instruction = """
**NOTE: You are analyzing this position WITHOUT change context.**
- Classify based solely on the position description content
- Match against all 17 classification levels independently
"""

        return f"""You are a classification consultant analyzing a position description to recommend an appropriate EC classification level.

**Classification Framework:**
Positions are classified using PSC EC Grade Matrix (levels 1-17) across six categories:
1. Accountabilities (Key Responsibilities)
2. Knowledge & Experience
3. Decision Making (Challenges & Decision Making)
4. Customer & Relationship Management
5. Leadership
6. Project Management

{context_section}

{context_instruction}

{standards_context}

**Position Description to Classify:**
{position_text[:10000]}

**Your Task:**
Analyze this position against ALL classification levels (EC-01 through EC-17) and recommend the best fit.

For each of the 6 categories, assess:
1. What level of complexity/responsibility is demonstrated?
2. Which classification level best matches this?
3. What specific evidence supports this level?

Then synthesize across categories to determine overall recommended level.

**Required Output Format:**
Respond with ONLY valid JSON:

{{
  "position_title": "Extracted title from document",
  "recommended_level": "EC-XX",
  "confidence": 85,
  "previous_level": {json.dumps(previous_level)},
  "rationale": "Comprehensive justification explaining why this level is appropriate. Reference specific criteria from classification standards and evidence from position description. If context available, explain how changes influenced recommendation.",
  "category_analysis": {{
    "accountabilities": "Analysis of responsibilities - what level they match and why",
    "knowledge_experience": "Analysis of knowledge/education requirements - matching level",
    "decision_making": "Analysis of decision-making complexity - matching level",
    "customer_relationship": "Analysis of customer/stakeholder management - matching level",
    "leadership": "Analysis of leadership requirements - matching level",
    "project_management": "Analysis of project management scope - matching level"
  }},
  "supporting_evidence": [
    "Key factor 1 from position that supports this level",
    "Key factor 2 that differentiates from lower levels",
    "Key factor 3 that shows fit at this level vs higher"
  ],
  "alternative_levels": ["EC-XX", "EC-YY"],
  "change_context_used": {json.dumps(has_context)},
  "comparable_positions": [
    "Similar position type 1 typically at this level",
    "Similar position type 2 at this level"
  ]
}}

**Guidelines:**
- Be precise about level matching - look for clear differentiators between adjacent levels
- Confidence should reflect clarity of match (ambiguous = lower confidence)
- Alternative levels should be genuinely plausible, not just ±1 from recommendation
- Set previous_level to EXACTLY {json.dumps(previous_level)} (do not extract from filename or document)
- If context provided, previous_level should be respected unless evidence clearly shows different level
- Never recommend level lower than previous unless position explicitly reduced
- Reference specific standards criteria in rationale and category analysis"""

        return prompt

    def _get_all_standards(self) -> str:
        """
        Get all classification standards formatted for prompt.

        Returns:
            Formatted string with all levels and categories
        """
        if not self.standards:
            return "Classification standards not available."

        summary = "\n**PSC EC Grade Matrix - Classification Standards:**\n"

        classification_levels = self.standards.get('classification_levels', {})

        # Show all 17 levels with summarized criteria
        for level_num in range(1, 18):
            level_key = f"EC-{level_num:02d}"

            if level_key in classification_levels:
                level_data = classification_levels[level_key]

                summary += f"\n**{level_key}: {level_data.get('title', 'N/A')}**\n"
                summary += f"Grade Code: {level_data.get('grade_code', 'N/A')}\n"

                # Show key criteria from each category (first 2 items)
                categories = level_data.get('categories', {})
                for cat_name, cat_items in categories.items():
                    if cat_items and len(cat_items) > 0:
                        summary += f"  {cat_name.replace('_', ' ').title()}:\n"
                        # Show first 2 items to keep prompt manageable
                        for item in cat_items[:2]:
                            summary += f"    • {item[:150]}{'...' if len(item) > 150 else ''}\n"

        return summary
