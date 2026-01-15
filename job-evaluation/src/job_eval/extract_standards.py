"""Extract classification standards from PSC EC Grade Matrix PDF."""
import json
import os
from pathlib import Path
from typing import Any

import pdfplumber
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


def extract_matrix_text() -> str:
    """Extract full text from Grade Matrix PDF."""
    pdf_path = Path("Rationale Docs/PSC EC Grade Matrix Draft (2018).pdf")

    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            full_text.append(f"--- Page {i+1} ---\n{text}")

    return "\n\n".join(full_text)


def structure_with_claude(matrix_text: str) -> dict[str, Any]:
    """Use Claude to structure the Grade Matrix into JSON."""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = """I have extracted the PSC EC Grade Matrix document that defines classification levels EC 1-17.

Please analyze this document and create a structured JSON representation with the following schema:

{
  "classification_levels": {
    "EC-01": {
      "level": 1,
      "title": "Job title(s) at this level",
      "grade_code": "Grade codes like F III 3",
      "categories": {
        "accountabilities": ["bullet point 1", "bullet point 2", ...],
        "knowledge_experience": ["bullet point 1", ...],
        "decision_making": ["bullet point 1", ...],
        "customer_relationship": ["bullet point 1", ...],
        "leadership": ["bullet point 1", ...],
        "project_management": ["bullet point 1", ...]
      }
    },
    "EC-02": { ... },
    ...
  }
}

Extract ALL classification levels found in the document (should be EC 1-17 or EC 01-17).
For each level, extract:
1. The numeric level
2. Job title(s) mentioned
3. Grade codes
4. All bullet points under each category (Accountabilities, Knowledge & Experience, Challenges & Decision Making, Customer Focus & Relationship Management, Leadership, Project Management)

Be thorough - capture all bullet points for each category at each level.

Here is the extracted text:

""" + matrix_text

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=16000,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract JSON from response
    response_text = message.content[0].text

    # Find JSON in response (might be in code blocks)
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


def main():
    """Extract and save classification standards."""
    print("Extracting text from Grade Matrix PDF...")
    matrix_text = extract_matrix_text()

    print(f"Extracted {len(matrix_text)} characters")
    print("\nUsing Claude to structure data...")

    structured_data = structure_with_claude(matrix_text)

    # Save to file
    output_path = Path("data/classification_standards.json")
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(structured_data, f, indent=2)

    print(f"\n✓ Saved classification standards to {output_path}")
    print(f"  Found {len(structured_data.get('classification_levels', {}))} classification levels")


if __name__ == "__main__":
    main()
