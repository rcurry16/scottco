# Job Classification Tool - Overview

## The Problem

Classification Consultants at the Public Service Commission manually review **300-400 position descriptions annually**. Each review requires:

- Detailed analysis of changes between document versions
- Assessment of whether changes warrant re-evaluation
- Classification decisions based on complex criteria
- Documentation and justification

This is time-intensive, labor-intensive work that can be partially automated.

---

## The Solution

Three AI-powered tools that assist (not replace) Classification Consultants:

### Tool 1.1: Position Description Side by Side ✅ **Complete**

**What it does:**
Compares two position description PDFs and identifies all changes.

**Output:**
- Categorized list of additions, deletions, and modifications
- Changes mapped to six classification categories:
  - Accountabilities
  - Knowledge & Experience
  - Decision Making
  - Customer & Relationship Management
  - Leadership
  - Project Management
- Overall significance rating (minor/moderate/major)

**Value:**
Automates initial change analysis. What takes 30+ minutes now takes 2 minutes.

---

### Tool 1.2: Revaluation Gauge ✅ **Complete**

**What it does:**
Analyzes whether documented changes are material enough to warrant formal re-evaluation, with full position context and baseline comparison.

**Input:**
- Comparison results from Tool 1.1
- Automatically loads full position description
- Auto-detects current classification level from filename

**Output:**
- Yes/No recommendation with confidence level
- Current level and expected new level range
- Justification comparing changes to current level expectations
- Risk assessment and category-specific impacts
- Reference to specific classification criteria

**Key Features:**
- Contextual analysis (compares against current level baseline)
- Never suggests downgrade unless role explicitly reduced
- Considers what's typical at current level vs elevating beyond it
- Deterministic output (temperature=0) for consistency

**Value:**
Reduces 100+ unnecessary evaluations annually. Helps consultants prioritize work with context-aware recommendations.

---

### Tool 1.3: First Pass Classifier ✅ **Complete**

**What it does:**
Proposes a classification level based on comprehensive position description analysis.

**Input:**
- Position description PDF
- Optional: Results from Tool 1.1/1.2 for context-aware classification

**Output:**
- Recommended classification level (EC-01 to EC-17)
- Confidence score (0-100%)
- Detailed rationale with evidence from position description
- Category-by-category analysis (all 6 classification categories)
- Supporting evidence for recommendation
- Alternative levels to consider
- Comparable positions at this level

**Key Features:**
- **Standalone mode:** Analyzes position against all 17 levels independently
- **Context-aware mode:** Uses Tool 1.1/1.2 results to inform recommendation
- Category-level analysis across all 6 classification dimensions
- Confidence scoring reflects clarity of match
- Alternative levels must be genuinely plausible (not just ±1)
- Deterministic output (temperature=0) for consistency

**Validation Results:**
Blind test on 4 positions (titles/levels removed):
- 0/4 exact matches (25% expected baseline)
- 3/4 within ±1 level (75% near-accuracy)
- Pattern: Tends to classify 1-2 levels higher at mid-ranges (EC-03 to EC-10)
- Correctly distinguished divisional vs departmental scope at senior levels
- Confidence scores: 78-82% (appropriately moderate)

**Value:**
Provides preliminary classification analysis for consultants. Most useful for identifying positions requiring detailed review and understanding classification boundary cases. Requires calibration on coordinator vs manager distinctions (EC-09/10 vs EC-11).

---

### Tool 1.4: Position Upgrade Advisor 💡 **Concept**

**What it does:**
Takes a current position description and target classification level, then generates an updated position description that bridges the gap.

**Input:**
- Current position description PDF
- Target classification level (e.g., "upgrade EC-02 to EC-03")
- Optional: Specific areas to enhance (accountabilities, leadership, etc.)

**Output:**
- Analysis of gaps between current and target level
- Specific suggested changes mapped to classification categories
- **Updated position description document** incorporating the changes
- Justification for each enhancement

**How it works:**
1. Analyzes current position against classification standards
2. Identifies specific gaps preventing higher classification
3. Suggests concrete additions/modifications to bridge gaps
4. Generates revised position description with tracked changes
5. Validates new version would meet target level criteria

**Value:**
Assists in role development and position evolution. Helps departments strategically enhance positions to meet organizational needs while ensuring alignment with classification standards.

**Example workflow:**
```bash
job-eval upgrade position.pdf --target EC-05 --output upgraded_position.pdf
# Shows gaps, suggests changes, generates updated document
```

---

## Current Status

**Complete:**
- ✅ Tool 1.1 (Position Description Side by Side) - fully functional
- ✅ Tool 1.2 (Revaluation Gauge) - fully functional
- ✅ Tool 1.3 (First Pass Classifier) - fully functional
- ✅ CLI interface for local use
- ✅ Classification standards framework established
- ✅ Validated with 41 sample position descriptions
- ✅ Blind testing completed (4 positions)

**Planned:**
- 💡 Tool 1.4 (Position Upgrade Advisor) - concept stage
- 🚀 Web interface for easier access
- 🚀 FastAPI deployment to VPS for team use
- 🚀 Batch processing capabilities

---

## How It Works

### Technical Architecture

**1. PDF Processing Layer**
- Uses `pdfplumber` to extract text from position description PDFs
- Handles multi-page documents with varying formats/layouts
- Text extraction resilient to formatting inconsistencies between old/new documents
- No OCR required - works with native text PDFs

**2. AI Analysis Engine**
- **Model:** Claude Haiku 4.5 via Anthropic API
- **Temperature:** 0 (deterministic output for consistency)
- **Token Limits:** 8000 tokens for comparison, 4000-8000 for classification
- Semantic understanding of position descriptions (not keyword matching)
- Structured output enforced via Pydantic validation

**3. Classification Standards Framework**
- JSON-based representation of PSC EC Grade Matrix (levels 1-17)
- Six classification categories mapped:
  1. Accountabilities
  2. Knowledge & Experience
  3. Decision Making
  4. Customer & Relationship Management
  5. Leadership
  6. Project Management
- Standards loaded into each tool's context for consistent evaluation

**4. Multi-Stage Analysis Pipeline**

**Tool 1.1 (Comparator):**
- Loads both PDFs → extracts text
- Sends to Claude with comparison prompt
- Returns structured JSON: sections changed, classification impacts, significance
- Semantic diff (not line-by-line) - identifies equivalent sections despite rewording

**Tool 1.2 (Gauge):**
- Loads comparison results (Tool 1.1 output)
- Extracts current level from filename via regex pattern matching
- Loads FULL new position description PDF (not just changes)
- Pulls relevant standards (current level ±1) from framework
- Contextual assessment: "Are changes material RELATIVE TO current level baseline?"
- Never suggests downgrade unless explicit role reduction

**Tool 1.3 (Classifier):**
- Standalone mode: Analyzes position against all 17 levels
- Context-aware mode: Uses Tool 1.1/1.2 results as additional input
- Loads complete classification standards (all levels)
- Category-by-category analysis (6 categories)
- Cross-level comparison to find best fit
- Returns confidence score, alternatives, supporting evidence

**5. Output Formats**
- **Human-readable:** Rich CLI formatting with color, tables, sections
- **Machine-readable:** Structured JSON for downstream processing
- **Audit trail:** All outputs include rationale, evidence, criteria references

### Technical Workflow Example

```
# Full pipeline execution:
job-eval compare old.pdf new.pdf --with-classify

[PDF Processing Layer]
├─ Extract text from old.pdf (pdfplumber)
├─ Extract text from new.pdf (pdfplumber)
└─ Pass to Comparator

[Tool 1.1: Comparator]
├─ Load classification_standards.json
├─ Build prompt with both documents + standards
├─ API call to Claude Haiku (temperature=0, max_tokens=8000)
├─ Parse JSON response → ComparisonResult (Pydantic)
├─ Save to comparison_results.json
└─ Display formatted comparison

[Tool 1.2: Gauge]
├─ Load comparison_results.json
├─ Extract current level from filename (regex: EC[\s-]?\d{1,2})
├─ Load new.pdf FULL text (not just changes)
├─ Get relevant standards (current ±1 levels)
├─ Build contextual prompt with comparison + full position + standards
├─ API call to Claude Haiku (temperature=0, max_tokens=4000)
├─ Parse JSON response → RevaluationRecommendation (Pydantic)
├─ Save to gauge_results.json
└─ Display recommendation with confidence

[Tool 1.3: Classifier]
├─ Load gauge_results.json (for context)
├─ Load new.pdf text
├─ Get ALL classification standards (EC-01 to EC-17)
├─ Build prompt with position + context + all standards
├─ API call to Claude Haiku (temperature=0, max_tokens=8000)
├─ Parse JSON response → ClassificationRecommendation (Pydantic)
├─ Save to classification_results.json
└─ Display recommended level with category analysis

[Result: Complete audit trail in 3 JSON files]
```

### Prompt Engineering Strategy

**Tool 1.1 (Comparison):**
- Flexible section matching (semantic, not rigid)
- Six classification categories as output structure
- Significance assessment (minor/moderate/major)
- Emphasis on SEMANTIC changes, ignore formatting

**Tool 1.2 (Gauge):**
- **Critical:** Baseline thinking against CURRENT level
- Provides standards for current ±1 levels (not all 17)
- "Does this elevate BEYOND current level?" framing
- Explicit instruction: never suggest downgrade without evidence
- Risk assessment required

**Tool 1.3 (Classifier):**
- All 17 levels provided in prompt
- Category-by-category analysis forced via JSON schema
- Context-aware: respects previous level if provided
- Confidence scoring based on clarity of match
- Alternative levels must be plausible (not just ±1)

---

## Design Philosophy

**Augmentation, not replacement:**
Tools provide initial analysis and recommendations. Consultants make final decisions.

**Flexible handling:**
Works with varying document formats, old and new. Semantic understanding vs rigid parsing.

**Growing knowledge base:**
Classification standards stored as structured data. Can expand over time.

**Audit trail:**
All outputs exportable to JSON for documentation and record-keeping.

---

## Expected Impact

**Time Savings:**
- **Tool 1.1:** 20-25 minutes per review → ~100-120 hours/year saved
- **Tool 1.2:** Eliminates 100+ unnecessary full evaluations → ~200-300 hours/year saved
- **Tool 1.3:** Reduces initial classification time by 30-40% → ~100-150 hours/year saved (conservative estimate given calibration needs)

**Total potential:** 400-570 hours annually across all three tools

**Quality Improvements:**
- Consistent application of classification criteria
- Reduced oversight of minor changes
- Better documentation of rationale
- Faster turnaround for urgent reviews
- Category-by-category evidence for classification decisions

**Calibration Needs:**
- Tool 1.3 requires refinement on coordinator vs manager boundaries (EC-09/10 vs EC-11)
- Current version best used as preliminary analysis requiring consultant validation
- Blind test results inform where consultant judgment most critical

---

## Technical Foundation

**Core Technologies:**
- **Python 3.12** - Modern async/await patterns, type hints
- **uv** - Fast package manager for dependency management
- **pdfplumber** - Reliable PDF text extraction
- **Claude Haiku 4.5** - Fast, cost-effective AI analysis via Anthropic API
- **Pydantic** - Runtime validation & structured outputs
- **Typer + Rich** - Modern CLI with formatted output

**Key Libraries:**
- `anthropic` - Official Anthropic Python SDK
- `python-dotenv` - Environment variable management
- `pdfplumber` - PDF parsing (not PyPDF2 - better format handling)

**Architecture Patterns:**
- Modular design - each tool is independent class
- Separation of concerns - PDF processing → Analysis → Output
- JSON-based data interchange between tools
- Standards-as-data (not hardcoded logic)

**Deployment:**
- **Current:** Local CLI via `job-eval` command
- **Future:** FastAPI REST API + web UI on VPS for team access
- Containerization planned (Docker)

**Training Data:**
- 41 position description examples (EC 02-16) in `Position Levels/`
- 5 detailed rationale documents in `Rationale Docs/`
- Complete PSC EC Grade Matrix (levels 1-17) → extracted to JSON
- Standards extraction: `extract_standards.py` processes matrix into structured format

**Cost Profile:**
- Claude Haiku 4.5 pricing: $0.25 per million input tokens, $1.25 per million output tokens
- Typical comparison: ~3K tokens → $0.001 per analysis
- Full pipeline (compare + gauge + classify): ~15K tokens → $0.005 per position
- Annual estimate (400 positions): ~$2-5 depending on usage patterns

**Quality Assurance:**
- Pydantic validation ensures structured outputs always conform to schema
- Temperature=0 for reproducibility (same input → same output)
- JSON outputs enable programmatic testing and validation
- Can diff results across model versions to detect regressions
- Sample dataset (41 positions) used for validation testing

**Error Handling:**
- PDF extraction failures → graceful error with file path info
- API failures → clear error messages with retry guidance
- Malformed JSON responses → automatic extraction from code blocks
- Missing standards file → explicit error with setup instructions
- Invalid file paths → user-friendly path correction suggestions

---

## Next Steps

1. **Calibrate Tool 1.3** with consultant feedback on coordinator vs manager boundaries
2. **Deploy to VPS** with web interface for team use
3. **Gather real-world usage data** from consultants
4. **Iterate based on feedback** - refine prompts, adjust classification logic
5. **Explore Tool 1.4** (Position Upgrade Advisor) if demand exists

---

## Notes

- Tools work sequentially but can operate independently
- Designed for PSC EC classification system (levels 1-17)
- Can adapt to other classification frameworks
- All analysis reviewable and auditable

---

For technical documentation, see [README.md](README.md)
