// State management
let state = {
    workflow: 'full',
    oldFile: null,
    newFile: null,
    singleFile: null,
    isProcessing: false,
    currentJobId: null
};

// DOM elements
const workflowRadios = document.querySelectorAll('input[name="workflow"]');
const fullUploads = document.getElementById('full-uploads');
const singleUpload = document.getElementById('single-upload');
const oldFileInput = document.getElementById('old-file');
const newFileInput = document.getElementById('new-file');
const singleFileInput = document.getElementById('single-file');
const oldDrop = document.getElementById('old-drop');
const newDrop = document.getElementById('new-drop');
const singleDrop = document.getElementById('single-drop');
const submitBtn = document.getElementById('submit-btn');
const resultsSection = document.getElementById('results-section');
const resultsContent = document.getElementById('results-content');
const errorMessage = document.getElementById('error-message');

// Event listeners
workflowRadios.forEach(radio => {
    radio.addEventListener('change', handleWorkflowChange);
});

oldFileInput.addEventListener('change', () => handleFileSelect(oldFileInput, 'old'));
newFileInput.addEventListener('change', () => handleFileSelect(newFileInput, 'new'));
singleFileInput.addEventListener('change', () => handleFileSelect(singleFileInput, 'single'));

// Drag and drop
[oldDrop, newDrop, singleDrop].forEach(zone => {
    zone.addEventListener('dragover', handleDragOver);
    zone.addEventListener('dragleave', handleDragLeave);
});

oldDrop.addEventListener('drop', (e) => handleDrop(e, oldFileInput, 'old'));
newDrop.addEventListener('drop', (e) => handleDrop(e, newFileInput, 'new'));
singleDrop.addEventListener('drop', (e) => handleDrop(e, singleFileInput, 'single'));

submitBtn.addEventListener('click', handleSubmit);

// Functions
function handleWorkflowChange(e) {
    state.workflow = e.target.value;

    if (state.workflow === 'full') {
        fullUploads.style.display = 'grid';
        singleUpload.style.display = 'none';
        state.singleFile = null;
    } else {
        fullUploads.style.display = 'none';
        singleUpload.style.display = 'block';
        state.oldFile = null;
        state.newFile = null;
    }

    updateSubmitButton();
    hideError();
}

function handleFileSelect(input, type) {
    const file = input.files[0];
    if (file) {
        if (!validateFile(file)) {
            return;
        }

        if (type === 'old') {
            state.oldFile = file;
            updateFileDisplay('old-file-name', file.name, oldDrop);
        } else if (type === 'new') {
            state.newFile = file;
            updateFileDisplay('new-file-name', file.name, newDrop);
        } else if (type === 'single') {
            state.singleFile = file;
            updateFileDisplay('single-file-name', file.name, singleDrop);
        }
    }

    updateSubmitButton();
    hideError();
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e, input, type) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');

    const file = e.dataTransfer.files[0];
    if (file) {
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        input.files = dataTransfer.files;
        handleFileSelect(input, type);
    }
}

function validateFile(file) {
    const validTypes = ['.pdf', '.docx', '.doc'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();

    if (!validTypes.includes(fileExt)) {
        showError(`Invalid file type. Only PDF and DOCX files are allowed.`);
        return false;
    }

    return true;
}

function updateFileDisplay(elementId, filename, dropZone) {
    const fileNameElement = document.getElementById(elementId);
    fileNameElement.textContent = filename;
    dropZone.classList.add('has-file');
}

function updateSubmitButton() {
    let canSubmit = false;

    if (state.workflow === 'full') {
        canSubmit = state.oldFile && state.newFile;
    } else {
        canSubmit = state.singleFile;
    }

    submitBtn.disabled = !canSubmit || state.isProcessing;
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}

function showLoading() {
    state.isProcessing = true;
    submitBtn.disabled = true;
    submitBtn.querySelector('.btn-text').textContent = 'Processing...';
    submitBtn.querySelector('.loader').style.display = 'block';
    resultsSection.style.display = 'none';
    hideError();
}

function hideLoading() {
    state.isProcessing = false;
    submitBtn.querySelector('.btn-text').textContent = 'Analyze';
    submitBtn.querySelector('.loader').style.display = 'none';
    updateSubmitButton();
}

async function handleSubmit() {
    showLoading();

    try {
        let result;

        if (state.workflow === 'full') {
            result = await runFullWorkflow();
        } else {
            result = await runClassification();
        }

        displayResults(result, state.workflow);
        resultsSection.style.display = 'block';

    } catch (error) {
        showError(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

async function runFullWorkflow() {
    const formData = new FormData();
    formData.append('old_file', state.oldFile);
    formData.append('new_file', state.newFile);

    const response = await fetch('api/full-workflow', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to process documents');
    }

    return await response.json();
}

async function runClassification() {
    const formData = new FormData();
    formData.append('file', state.singleFile);

    const response = await fetch('api/classify', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to classify document');
    }

    return await response.json();
}

function displayResults(data, workflow) {
    // Store job_id for downloads
    state.currentJobId = data.job_id;

    let formattedText = '';

    // Extract result data (API now returns {job_id, result})
    const resultData = data.result || data;

    if (workflow === 'full') {
        formattedText = formatFullWorkflowResults(resultData);
    } else {
        formattedText = formatClassificationResults(resultData);
    }

    resultsContent.innerHTML = formattedText;

    // Setup download buttons after rendering
    setupDownloadButtons();
}

function formatFullWorkflowResults(data) {
    const sections = [];

    // Tool 1: Comparison
    sections.push(createToolSection('TOOL 1: POSITION COMPARISON', [
        { label: 'Original Document', value: data.comparison.old_document },
        { label: 'Updated Document', value: data.comparison.new_document },
        { label: 'Summary', value: data.comparison.summary },
        { label: 'Overall Significance', value: data.comparison.overall_significance.toUpperCase() },
        { label: 'Changes by Section', value: formatChangesBySection(data.comparison.changes_by_section) },
        { label: 'Classification Relevant Changes', value: formatDict(data.comparison.classification_relevant_changes) }
    ]));

    // Tool 2: Gauge
    sections.push(createToolSection('TOOL 2: RE-EVALUATION GAUGE', [
        { label: 'Should Re-evaluate', value: data.gauge.should_reevaluate ? 'YES' : 'NO' },
        { label: 'Confidence', value: `${data.gauge.confidence}%` },
        { label: 'Current Level', value: data.gauge.current_level },
        { label: 'Likely New Level Range', value: data.gauge.likely_new_level_range },
        { label: 'Risk Assessment', value: data.gauge.risk_assessment.toUpperCase() },
        { label: 'Rationale', value: data.gauge.rationale },
        { label: 'Key Factors', value: formatList(data.gauge.key_factors) },
        { label: 'Categories Affected', value: formatList(data.gauge.categories_affected) }
    ]));

    // Tool 3: Classification
    sections.push(createToolSection('TOOL 3: CLASSIFICATION RECOMMENDATION', [
        { label: 'Position Title', value: data.classification.position_title },
        { label: 'Recommended Level', value: data.classification.recommended_level },
        { label: 'Confidence', value: `${data.classification.confidence}%` },
        { label: 'Previous Level', value: data.classification.previous_level || 'N/A' },
        { label: 'Change Context Used', value: data.classification.change_context_used ? 'Yes' : 'No' },
        { label: 'Rationale', value: data.classification.rationale },
        { label: 'Category Analysis', value: formatDict(data.classification.category_analysis) },
        { label: 'Supporting Evidence', value: formatList(data.classification.supporting_evidence) },
        { label: 'Alternative Levels', value: formatList(data.classification.alternative_levels) },
        { label: 'Comparable Positions', value: formatList(data.classification.comparable_positions) }
    ]));

    return sections.join('');
}

function formatClassificationResults(data) {
    return createToolSection('CLASSIFICATION RECOMMENDATION', [
        { label: 'Position Title', value: data.position_title },
        { label: 'Recommended Level', value: data.recommended_level },
        { label: 'Confidence', value: `${data.confidence}%` },
        { label: 'Rationale', value: data.rationale },
        { label: 'Category Analysis', value: formatDict(data.category_analysis) },
        { label: 'Supporting Evidence', value: formatList(data.supporting_evidence) },
        { label: 'Alternative Levels', value: formatList(data.alternative_levels) },
        { label: 'Comparable Positions', value: formatList(data.comparable_positions) }
    ]);
}

function createToolSection(title, fields) {
    let html = `<div class="tool-section">`;
    html += `<div class="tool-header">${title}</div>`;

    fields.forEach(field => {
        if (field.value !== null && field.value !== undefined && field.value !== '') {
            html += `<div class="field">`;
            html += `<div class="field-label">${field.label}:</div>`;
            html += `<div class="field-value">${field.value}</div>`;
            html += `</div>`;
        }
    });

    html += `</div>`;
    return html;
}

function formatList(items) {
    if (!items || items.length === 0) return 'None';
    return '<br>' + items.map(item => `<div class="list-item">${escapeHtml(item)}</div>`).join('');
}

function formatDict(obj) {
    if (!obj || Object.keys(obj).length === 0) return 'None';
    let html = '<br>';
    for (const [key, value] of Object.entries(obj)) {
        const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        if (Array.isArray(value)) {
            html += `<div class="field-label" style="margin-top: 0.5rem;">${formattedKey}:</div>`;
            html += formatList(value);
        } else if (typeof value === 'object') {
            html += `<div class="field-label" style="margin-top: 0.5rem;">${formattedKey}:</div>`;
            html += formatChangeCategory(value);
        } else {
            html += `<div class="list-item"><strong>${formattedKey}:</strong> ${escapeHtml(value)}</div>`;
        }
    }
    return html;
}

function formatChangesBySection(sections) {
    if (!sections || Object.keys(sections).length === 0) return 'No changes detected';
    let html = '<br>';
    for (const [section, changes] of Object.entries(sections)) {
        html += `<div class="field-label" style="margin-top: 0.5rem;">${escapeHtml(section)}:</div>`;
        html += formatChangeCategory(changes);
    }
    return html;
}

function formatChangeCategory(category) {
    let html = '';

    if (category.additions && category.additions.length > 0) {
        html += '<div style="margin-left: 1rem; margin-top: 0.25rem;">';
        html += '<strong style="color: #16a34a;">Additions:</strong>';
        html += formatList(category.additions);
        html += '</div>';
    }

    if (category.deletions && category.deletions.length > 0) {
        html += '<div style="margin-left: 1rem; margin-top: 0.25rem;">';
        html += '<strong style="color: #dc2626;">Deletions:</strong>';
        html += formatList(category.deletions);
        html += '</div>';
    }

    if (category.modifications && category.modifications.length > 0) {
        html += '<div style="margin-left: 1rem; margin-top: 0.25rem;">';
        html += '<strong style="color: #2563eb;">Modifications:</strong>';
        html += formatList(category.modifications);
        html += '</div>';
    }

    return html || 'No changes';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getPlainTextResults() {
    const resultsDiv = document.getElementById('results-content');
    const toolSections = resultsDiv.querySelectorAll('.tool-section');
    let text = '=== JOB EVALUATION ANALYSIS REPORT ===\n\n';

    toolSections.forEach((section, index) => {
        const header = section.querySelector('.tool-header').textContent;
        text += `${header}\n${'='.repeat(header.length)}\n\n`;

        const fields = section.querySelectorAll('.field');
        fields.forEach(field => {
            const label = field.querySelector('.field-label').textContent;
            const value = field.querySelector('.field-value');

            text += `${label}\n`;

            // Extract text content, handling nested structures
            const listItems = value.querySelectorAll('.list-item');
            if (listItems.length > 0) {
                listItems.forEach(item => {
                    text += `  • ${item.textContent.trim()}\n`;
                });
            } else {
                const textContent = value.textContent.trim();
                if (textContent) {
                    text += `  ${textContent}\n`;
                }
            }
            text += '\n';
        });

        if (index < toolSections.length - 1) {
            text += '\n' + '-'.repeat(80) + '\n\n';
        }
    });

    return text;
}

async function handleCopy() {
    try {
        const text = getPlainTextResults();
        await navigator.clipboard.writeText(text);

        // Visual feedback
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
            </svg>
            Copied!
        `;
        copyBtn.classList.add('copied');

        setTimeout(() => {
            copyBtn.innerHTML = originalText;
            copyBtn.classList.remove('copied');
        }, 2000);

    } catch (error) {
        showError('Failed to copy to clipboard');
    }
}

function setupDownloadButtons() {
    // Remove any existing download buttons
    const existingContainer = document.querySelector('.download-buttons-container');
    if (existingContainer) {
        existingContainer.remove();
    }

    // Create download buttons container
    const container = document.createElement('div');
    container.className = 'download-buttons-container';
    container.innerHTML = `
        <button class="btn btn-download" onclick="downloadEvaluation('pdf')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            PDF
        </button>
        <button class="btn btn-download" onclick="downloadEvaluation('docx')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Word
        </button>
        <button class="btn btn-download" onclick="downloadEvaluation('txt')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Text
        </button>
    `;

    // Insert before results content
    resultsSection.insertBefore(container, resultsContent);
}

function downloadEvaluation(format) {
    if (!state.currentJobId) {
        showError('No evaluation results to download');
        return;
    }

    const url = `api/download/${state.currentJobId}/${format}`;
    window.location.href = url;
}
