"""Position description comparison using Claude."""
import json
import os
from pathlib import Path
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .document_processor import DocumentProcessor

load_dotenv()


class ChangeCategory(BaseModel):
    """Represents changes in a specific category."""
    additions: list[str] = Field(default_factory=list, description="New content added")
    deletions: list[str] = Field(default_factory=list, description="Content removed")
    modifications: list[str] = Field(
        default_factory=list,
        description="Content that was changed (old -> new)"
    )


class ComparisonResult(BaseModel):
    """Results from comparing two position descriptions."""
    old_document: str = Field(description="Path to original document")
    new_document: str = Field(description="Path to updated document")
    summary: str = Field(description="High-level summary of changes")
    changes_by_section: dict[str, ChangeCategory] = Field(
        default_factory=dict,
        description="Changes organized by document section"
    )
    classification_relevant_changes: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Changes mapped to classification categories (Accountabilities, Knowledge/Experience, etc.)"
    )
    overall_significance: str = Field(
        description="Assessment of change significance: minor, moderate, or major"
    )


class PositionComparator:
    """Compare two position descriptions and identify changes."""

    def __init__(self, api_key: str | None = None):
        """Initialize comparator with Claude API."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY must be set in environment or .env file"
            )
        self.client = Anthropic(api_key=self.api_key)

        # Load classification standards if available
        self.standards = self._load_standards()

    def _load_standards(self) -> dict[str, Any]:
        """Load classification standards from JSON."""
        standards_path = Path("data/classification_standards.json")
        if standards_path.exists():
            with open(standards_path) as f:
                return json.load(f)
        return {}

    def compare(
        self,
        old_pdf_path: str | Path,
        new_pdf_path: str | Path,
    ) -> ComparisonResult:
        """
        Compare two position description documents (PDF or DOCX).

        Args:
            old_pdf_path: Path to original position description
            new_pdf_path: Path to updated position description

        Returns:
            Structured comparison results
        """
        # Extract text from both documents
        print("Extracting text from documents...")
        old_processor = DocumentProcessor(old_pdf_path)
        new_processor = DocumentProcessor(new_pdf_path)

        old_text = old_processor.extract_text()
        new_text = new_processor.extract_text()

        # Use Claude to analyze differences
        print("Analyzing differences with Claude...")
        result = self._analyze_with_claude(old_text, new_text)

        return ComparisonResult(
            old_document=str(old_pdf_path),
            new_document=str(new_pdf_path),
            **result
        )

    def _analyze_with_claude(
        self,
        old_text: str,
        new_text: str
    ) -> dict[str, Any]:
        """Use Claude to perform semantic comparison."""
        prompt = self._build_comparison_prompt(old_text, new_text)

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

        return json.loads(json_text)

    def _build_comparison_prompt(self, old_text: str, new_text: str) -> str:
        """Build prompt for Claude to compare documents."""
        standards_context = ""
        if self.standards:
            standards_context = """
You have access to the PSC EC Grade Matrix classification standards. When identifying changes,
map them to these six classification categories where relevant:
1. Accountabilities (Key Responsibilities & Accountabilities)
2. Knowledge/Experience (Knowledge & Experience)
3. Decision Making (Challenges & Decision Making)
4. Customer/Relationship Management (Customer Focus & Relationship Management)
5. Leadership
6. Project Management (Project Management Accountabilities)
"""

        return f"""You are analyzing changes between two position descriptions for a job classification system.

{standards_context}

Your task is to:
1. Identify all changes between the documents (additions, deletions, modifications)
2. Organize changes by the document sections they appear in (be flexible - sections may have different names)
3. Map significant changes to classification categories (Accountabilities, Knowledge/Experience, Decision Making, Customer/Relationship, Leadership, Project Management)
4. Assess overall significance (minor, moderate, or major)

Be flexible with section identification - old and new documents may structure content differently.
Focus on SEMANTIC changes, not just formatting differences.

===== ORIGINAL DOCUMENT =====
{old_text}

===== UPDATED DOCUMENT =====
{new_text}

===== REQUIRED OUTPUT FORMAT =====
Respond with ONLY valid JSON in this exact structure:

{{
  "summary": "Brief overview of what changed (2-3 sentences)",
  "changes_by_section": {{
    "Section Name": {{
      "additions": ["New bullet or paragraph 1", "New bullet 2"],
      "deletions": ["Removed text 1", "Removed text 2"],
      "modifications": ["Old text -> New text", "Another change"]
    }},
    "Another Section": {{ ... }}
  }},
  "classification_relevant_changes": {{
    "accountabilities": ["Change that affects accountabilities"],
    "knowledge_experience": ["Change that affects required knowledge"],
    "decision_making": ["Change affecting decision authority"],
    "customer_relationship": ["Change in stakeholder management"],
    "leadership": ["Change in leadership responsibilities"],
    "project_management": ["Change in project scope"]
  }},
  "overall_significance": "minor|moderate|major"
}}

Rules:
- Only include categories with actual changes
- Be specific about what changed
- For modifications, show before -> after
- Assess significance based on scope and impact of changes"""

        return prompt
