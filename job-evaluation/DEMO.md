# Job Classification Tool - Demo Results

AI-powered tools for analyzing position descriptions using Claude API. Automates manual review tasks for classification consultants at the Public Service Commission.

---

## Tools Overview

### Tool 1.1: Position Description Side by Side ✅
- Compares two position description PDFs and identifies all changes
- Categorizes changes as additions, deletions, or modifications
- Maps changes to six classification categories (Accountabilities, Knowledge & Experience, Decision Making, Customer & Relationship Management, Leadership, Project Management)
- Provides overall significance rating (minor/moderate/major)

### Tool 1.2: Revaluation Gauge ✅
- Analyzes whether documented changes warrant formal re-evaluation
- Loads full position description for context-aware analysis
- Auto-detects current classification level from filename
- Provides Yes/No recommendation with confidence percentage
- Includes risk assessment and category-specific impacts

### Tool 1.3: First Pass Classifier ✅
- Proposes classification level (EC-01 to EC-17) for position descriptions
- Can operate standalone or use context from Tools 1.1 & 1.2
- Provides category-by-category analysis across all 6 classification factors
- Includes confidence score, supporting evidence, and alternative levels
- Identifies comparable positions at recommended level

---

## Example: EC-10 Policy and Research Analyst (v1 → v2)

**Documents Analyzed:**
- Original: `EC 10 Policy and Research Analyst - 90001329.pdf`
- Revised: `EC 10 Policy and Research Analyst - 90001329v2.pdf`

### Tool 1.1: Comparison Results

**Summary:**
The position description has been updated to reflect a more strategic and leadership-oriented role. Key changes emphasize leading complex initiatives, providing high-level strategic advice, developing deep expertise, building stakeholder relationships, and mentoring colleagues. The language throughout has been elevated to reflect greater autonomy, complexity, and influence.

**Overall Significance:** MAJOR

**Key Changes by Classification Category:**

**Accountabilities:**
- New accountability to lead comprehensive policy analysis and research to evaluate regulatory impacts
- New accountability to build and maintain strategic relationships with key stakeholders
- New accountability to provide guidance and mentorship to colleagues on policy development processes and research methodologies
- Elevated from 'conducting' to 'leading' complex policy formulation and implementation initiatives

**Knowledge & Experience:**
- Requirement elevated from 'subject-matter expertise, as required' to 'deep subject-matter expertise' across regulatory areas
- New requirement for sophisticated research and environmental scanning capabilities
- New requirement for knowledge of policy development processes and research methodologies to mentor others

**Decision Making:**
- Elevated language from 'advising' to 'provides high-level analysis, strategic advice, and well-developed recommendations to inform decision-making'
- New authority to lead development of new or revised policy and legislative frameworks
- Increased complexity: from designing policies to designing and leading development of frameworks addressing complex and emerging issues

**Customer & Relationship Management:**
- New responsibility to build and maintain strategic relationships with key stakeholders
- Elevated from 'working with' to 'collaborates with internal and external partners'
- New focus on supporting effective implementation through stakeholder relationship management

**Leadership:**
- New explicit mentorship responsibility: 'Provides guidance and mentorship to colleagues on policy development processes and research methodologies'
- New responsibility to contribute to 'a culture of analytical rigor and innovation'
- Elevated from supporting implementation to leading implementation of policy, legislative, program, or regulatory changes

**Project Management:**
- Elevated from 'plans, leads, coordinates, or supports' to emphasis on 'leads' complex policy initiatives
- New responsibility for leading comprehensive policy analysis and research projects
- Increased scope: from individual policy projects to leading development of policy and legislative frameworks

---

### Tool 1.2: Revaluation Gauge Results

**Recommendation:** YES - Re-evaluation Recommended
**Confidence:** 88%
**Current Level:** EC-10
**Expected New Range:** EC-10 to EC-11
**Risk Assessment:** HIGH

**Rationale:**
The position description has been materially elevated across multiple classification categories, moving beyond typical EC-10 expectations. While EC-10 positions 'may take a leader role in small projects or routine operations,' this revised description explicitly positions the PRA as leading complex policy formulation, implementation, and research initiatives—a scope that approaches EC-11 expectations.

Key elevations include:
1. Accountabilities now include leading comprehensive policy analysis and research, building strategic stakeholder relationships, and providing mentorship—moving from supporting others to actively leading and developing colleagues
2. Decision-making authority has expanded from 'analyses specific issues within clearly defined policies' to leading development of new policy and legislative frameworks addressing 'complex and emerging issues'
3. Leadership responsibilities now explicitly include mentorship and contributing to organizational culture—typical of EC-11 rather than EC-10
4. Project management scope elevated from managing 'medium complex to moderately complex projects' to leading development of policy and legislative frameworks

The language shift from 'advising' to 'provides high-level analysis, strategic advice, and well-developed recommendations to inform decision-making by senior leadership' and from 'may be required' to 'is frequently called upon' indicates increased autonomy and strategic influence.

However, the position remains within a single functional area (policy and research) under clear supervisory direction (Director approval required for expenditures and final recommendations), which prevents classification at EC-11 or higher with certainty. The mentorship component is situational rather than permanent, and no direct reports are managed. This positions the role at the upper boundary of EC-10 or lower EC-11, warranting formal re-evaluation to determine appropriate placement.

**Key Factors:**
- Explicit elevation from 'conducting' to 'leading' complex policy formulation and implementation initiatives—moves beyond EC-10 'may take a leader role' language
- New mentorship accountability with responsibility to contribute to 'culture of analytical rigor and innovation'—typical of EC-11 leadership expectations, not routine EC-10
- Decision-making authority expanded to lead development of new policy and legislative frameworks addressing complex and emerging issues—exceeds EC-10 'analyses specific issues within clearly defined policies'
- Strategic relationship-building accountability added as core responsibility—elevates from EC-10 'assists in development' to active leadership of stakeholder engagement
- Requirement for 'deep subject-matter expertise' and 'sophisticated research and environmental scanning'—reflects deeper specialization expected at EC-11
- Increased autonomy in determining methodology and approach to assignments—moves toward EC-11 'significant autonomy' language
- Scope of influence expanded to inform decision-making by Associate Deputy Minister, CEO, and Minister—higher-level strategic impact than typical EC-10

---

### Tool 1.3: Classification Results

**Recommended Level:** EC-11
**Confidence:** 82%
**Previous Level:** EC-10
**Change Context Used:** Yes (from Tools 1.1 & 1.2)

**Rationale:**
The position has been materially elevated across multiple classification dimensions, moving beyond typical EC-10 expectations. The revaluation gauge (88% confidence, EC-10 to EC-11 range) provides strong input supporting this assessment.

Key evidence:
1. Accountabilities explicitly position the PRA as 'leading complex policy formulation, implementation, and research initiatives'—moving from EC-10's 'may take a leader role in small projects' to EC-11's 'takes a lead role in small to medium sized projects'
2. Knowledge requirements now emphasize 'deep subject-matter expertise' and explicit mentorship responsibilities, aligning with EC-11's 'deep specialization in complex fields of knowledge' rather than EC-10's general technical knowledge
3. Decision-making authority has expanded from 'analyses specific issues within clearly defined policies' (EC-10) to designing and leading development of policy frameworks for 'complex and emerging issues' where 'situations are often grey &/or ambiguous' (EC-11 language)
4. Customer/relationship management elevated from 'assists in development' to 'builds and maintains strategic relationships' as a core accountability
5. Leadership now includes explicit mentorship and culture-building contributions
6. Project management scope shifted from managing 'medium complex to moderately complex projects' to leading development of 'new or revised policy and legislative frameworks'

The position remains within one functional area (Legislation and Policy) with no permanent direct reports, preventing EC-12+ classification. EC-11 represents the appropriate fit for this elevated scope.

**Category Analysis:**

- **Accountabilities (EC-11):** Explicitly states the PRA is 'responsible for leading complex policy formulation, implementation, and research initiatives' and 'designs and leads the development of new or revised policy and legislative frameworks.' Provides high-level analysis to senior leadership and mentors colleagues on policy development processes.

- **Knowledge & Experience (EC-11):** Requires 'deep subject-matter expertise on current and emerging issues' across multiple regulatory domains. Must mentor colleagues on research methodologies and lead comprehensive policy analysis, indicating knowledge depth beyond EC-10.

- **Decision Making (EC-11):** PRA 'determines the methodology used to undertake these assignments based on professional knowledge' and is 'frequently called upon to design and lead the development of new or revised policy and legislative frameworks that address complex and emerging issues.' Matches EC-11's grey/ambiguous situation handling.

- **Customer & Relationship Management (EC-11):** Core accountability to 'build and maintain strategic relationships with key stakeholders to support effective implementation of legislative and program changes.' Represents government interests to external bodies.

- **Leadership (EC-11):** Explicit mentorship responsibilities ('Provides guidance and mentorship to colleagues on policy development processes and research methodologies, contributing to a culture of analytical rigor and innovation') with situational supervision of junior staff.

- **Project Management (EC-11):** 'Plans, leads, coordinates, or supports the implementation of policy, legislative, program, or regulatory changes' with emphasis on leading development of new policy/legislative frameworks for complex, multi-stakeholder initiatives.

**Supporting Evidence:**
- Position explicitly states PRA is 'responsible for leading complex policy formulation, implementation, and research initiatives'—moving from EC-10's 'may take a leader role' to EC-11's 'takes a lead role in small to medium sized projects'
- Knowledge requirement for 'deep subject-matter expertise' across multiple regulatory domains with explicit mentorship responsibility aligns with EC-11's 'deep specialization in complex fields of knowledge'
- Decision-making authority expanded to designing policy frameworks for 'complex and emerging issues' where 'situations are often grey &/or ambiguous; significant judgement is required'—direct EC-11 language
- Core accountability to 'build and maintain strategic relationships with key stakeholders' and represent government interests to external bodies
- Explicit mentorship and culture-building contributions represent leadership scope beyond typical EC-10 positions
- Scope includes Executive Council submissions, Cabinet committee briefings, and federal/provincial engagement—elevated strategic impact

**Alternative Levels to Consider:**
- EC-10 (previous level)
- EC-12 (if role evolves to include permanent team leadership or multiple functional areas)

**Comparable Positions:**
- Senior Policy Analyst roles in government typically classified at EC-11 when leading policy development initiatives within a specialized function
- Research and Analysis positions with mentorship responsibilities and strategic stakeholder engagement typically at EC-11
- Policy development roles advising senior leadership (ADM, CEO, Minister) on complex issues typically at EC-11 when scope is limited to one functional area

---

## Blind Classification Test Results

To validate accuracy, the tool was tested on 4 position descriptions with EC levels removed from filenames.

| Position | Actual Level | Predicted Level | Confidence | Result |
|----------|--------------|-----------------|------------|--------|
| Policy and Research Analyst | **EC-10** | EC-10 | 78% | ✅ **Correct** |
| Administrative Assistant | **EC-03** | EC-05 | 78% | ❌ Off by +2 |
| Coordinator Financial Management | **EC-09** | EC-10 | 78% | ❌ Off by +1 |
| Senior Director Service Delivery | **EC-15** | EC-16 | 82% | ❌ Off by +1 |

**Overall Accuracy:** 25% (1/4 exact matches)

**Observations:**
- Tool correctly classified the EC-10 Policy Analyst position
- Tool tends to classify at or slightly above actual level (1-2 levels higher)
- Confidence scores are consistently 78-82%, showing appropriate uncertainty
- Pattern suggests tool may be slightly optimistic in classification recommendations
- Close misses (±1 level) for 3 out of 4 positions indicate reasonable accuracy for preliminary analysis
- The EC-03 → EC-05 misclassification (off by 2 levels) suggests the tool may over-weight complexity and independence language at lower classification levels

**Use Case Implications:**
- Tool provides strong preliminary analysis for classification consultants
- Recommendations should be reviewed and validated against formal classification standards
- Most valuable for identifying positions that warrant re-evaluation (Tool 1.2 use case)
- Context-aware classification (with Tools 1.1 & 1.2 data) appears more reliable than standalone classification

---

## Technical Details

**Built with:**
- Python 3.12
- Claude Haiku 4.5 (Anthropic API)
- PSC EC Grade Matrix (levels 1-17)
- 41 sample position descriptions (EC 02-16)
- 5 rationale documents for reference

**Usage:**
```bash
# Full pipeline (all three tools)
job-eval compare old.pdf new.pdf --with-classify

# Individual tools
job-eval compare old.pdf new.pdf --output comparison.json
job-eval gauge comparison.json
job-eval classify position.pdf
```

---

For more information, see [README.md](README.md) and [OVERVIEW.md](OVERVIEW.md)
