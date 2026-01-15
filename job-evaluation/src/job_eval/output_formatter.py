"""
Formatter for job evaluation results to plain text format
"""
from typing import Any


def format_full_workflow(data: dict[str, Any]) -> str:
    """Format full workflow results (comparison + gauge + classification) to plain text"""
    sections = []

    # Title
    sections.append("JOB EVALUATION ANALYSIS REPORT")
    sections.append("=" * 80)
    sections.append("")

    # Tool 1: Comparison
    sections.append("TOOL 1: POSITION COMPARISON")
    sections.append("=" * 80)
    sections.append("")

    comp = data.get("comparison", {})
    sections.extend(_format_field("Original Document", comp.get("old_document")))
    sections.extend(_format_field("Updated Document", comp.get("new_document")))
    sections.extend(_format_field("Summary", comp.get("summary")))
    sections.extend(_format_field("Overall Significance", comp.get("overall_significance", "").upper()))
    sections.extend(_format_field("Changes by Section", _format_changes_by_section(comp.get("changes_by_section", {}))))
    sections.extend(_format_field("Classification Relevant Changes", _format_dict(comp.get("classification_relevant_changes", {}))))

    sections.append("")
    sections.append("-" * 80)
    sections.append("")

    # Tool 2: Gauge
    sections.append("TOOL 2: RE-EVALUATION GAUGE")
    sections.append("=" * 80)
    sections.append("")

    gauge = data.get("gauge", {})
    sections.extend(_format_field("Should Re-evaluate", "YES" if gauge.get("should_reevaluate") else "NO"))
    sections.extend(_format_field("Confidence", f"{gauge.get('confidence')}%"))
    sections.extend(_format_field("Current Level", gauge.get("current_level")))
    sections.extend(_format_field("Likely New Level Range", gauge.get("likely_new_level_range")))
    sections.extend(_format_field("Risk Assessment", gauge.get("risk_assessment", "").upper()))
    sections.extend(_format_field("Rationale", gauge.get("rationale")))
    sections.extend(_format_field("Key Factors", _format_list(gauge.get("key_factors", []))))
    sections.extend(_format_field("Categories Affected", _format_list(gauge.get("categories_affected", []))))

    sections.append("")
    sections.append("-" * 80)
    sections.append("")

    # Tool 3: Classification
    sections.append("TOOL 3: CLASSIFICATION RECOMMENDATION")
    sections.append("=" * 80)
    sections.append("")

    classif = data.get("classification", {})
    sections.extend(_format_field("Position Title", classif.get("position_title")))
    sections.extend(_format_field("Recommended Level", classif.get("recommended_level")))
    sections.extend(_format_field("Confidence", f"{classif.get('confidence')}%"))
    sections.extend(_format_field("Previous Level", classif.get("previous_level") or "N/A"))
    sections.extend(_format_field("Change Context Used", "Yes" if classif.get("change_context_used") else "No"))
    sections.extend(_format_field("Rationale", classif.get("rationale")))
    sections.extend(_format_field("Category Analysis", _format_dict(classif.get("category_analysis", {}))))
    sections.extend(_format_field("Supporting Evidence", _format_list(classif.get("supporting_evidence", []))))
    sections.extend(_format_field("Alternative Levels", _format_list(classif.get("alternative_levels", []))))
    sections.extend(_format_field("Comparable Positions", _format_list(classif.get("comparable_positions", []))))

    return "\n".join(sections)


def format_classification_only(data: dict[str, Any]) -> str:
    """Format classification-only results to plain text"""
    sections = []

    # Title
    sections.append("JOB EVALUATION ANALYSIS REPORT")
    sections.append("=" * 80)
    sections.append("")

    sections.append("CLASSIFICATION RECOMMENDATION")
    sections.append("=" * 80)
    sections.append("")

    sections.extend(_format_field("Position Title", data.get("position_title")))
    sections.extend(_format_field("Recommended Level", data.get("recommended_level")))
    sections.extend(_format_field("Confidence", f"{data.get('confidence')}%"))
    sections.extend(_format_field("Rationale", data.get("rationale")))
    sections.extend(_format_field("Category Analysis", _format_dict(data.get("category_analysis", {}))))
    sections.extend(_format_field("Supporting Evidence", _format_list(data.get("supporting_evidence", []))))
    sections.extend(_format_field("Alternative Levels", _format_list(data.get("alternative_levels", []))))
    sections.extend(_format_field("Comparable Positions", _format_list(data.get("comparable_positions", []))))

    return "\n".join(sections)


def _format_field(label: str, value: Any) -> list[str]:
    """Format a single field with label and value"""
    lines = []

    if value is None or value == "" or value == []:
        return lines

    lines.append(f"{label}:")

    if isinstance(value, str):
        # Wrap text if it contains newlines or is very long
        if "\n" in value:
            for line in value.split("\n"):
                lines.append(f"  {line}")
        else:
            lines.append(f"  {value}")
    else:
        # Already formatted (from helper functions)
        lines.append(value)

    lines.append("")
    return lines


def _format_list(items: list[str]) -> str:
    """Format a list of items"""
    if not items:
        return "  None"

    lines = []
    for item in items:
        lines.append(f"  • {item}")
    return "\n".join(lines)


def _format_dict(obj: dict[str, Any]) -> str:
    """Format a dictionary"""
    if not obj:
        return "  None"

    lines = []
    for key, value in obj.items():
        # Convert snake_case to Title Case
        formatted_key = key.replace("_", " ").title()

        if isinstance(value, list):
            lines.append(f"  {formatted_key}:")
            for item in value:
                lines.append(f"    • {item}")
        elif isinstance(value, dict):
            lines.append(f"  {formatted_key}:")
            lines.append(_format_change_category(value, indent=4))
        else:
            lines.append(f"  {formatted_key}: {value}")

    return "\n".join(lines)


def _format_changes_by_section(sections: dict[str, Any]) -> str:
    """Format changes by section"""
    if not sections:
        return "  No changes detected"

    lines = []
    for section, changes in sections.items():
        lines.append(f"  {section}:")
        lines.append(_format_change_category(changes, indent=4))

    return "\n".join(lines)


def _format_change_category(category: dict[str, list[str]], indent: int = 2) -> str:
    """Format a change category (additions/deletions/modifications)"""
    lines = []
    prefix = " " * indent

    if category.get("additions"):
        lines.append(f"{prefix}Additions:")
        for item in category["additions"]:
            lines.append(f"{prefix}  • {item}")

    if category.get("deletions"):
        lines.append(f"{prefix}Deletions:")
        for item in category["deletions"]:
            lines.append(f"{prefix}  • {item}")

    if category.get("modifications"):
        lines.append(f"{prefix}Modifications:")
        for item in category["modifications"]:
            lines.append(f"{prefix}  • {item}")

    return "\n".join(lines) if lines else f"{prefix}No changes"
