// Global state
let currentJobId = null;

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Load current config
    loadConfig();

    // Setup event listeners
    setupEventListeners();
});

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function setupEventListeners() {
    // Config save button
    document.getElementById('save-config-btn').addEventListener('click', saveConfig);

    // Form submission
    document.getElementById('job-desc-form').addEventListener('submit', handleFormSubmit);

    // Manages people toggle
    document.getElementById('manages-people').addEventListener('change', toggleManagementDetails);

    // Download buttons (will be set dynamically after generation)
}

function toggleManagementDetails(event) {
    const managementDetails = document.getElementById('management-details');
    if (event.target.value === 'true') {
        managementDetails.style.display = 'block';
    } else {
        managementDetails.style.display = 'none';
    }
}

// ============================================================================
// CONFIG MANAGEMENT
// ============================================================================

async function loadConfig() {
    try {
        const response = await fetch('api/config');
        const config = await response.json();

        document.getElementById('org-name').value = config.organization_name;
        document.getElementById('industry').value = config.industry;
        document.getElementById('location').value = config.location;
        document.getElementById('org-description').value = config.organization_description || '';
    } catch (error) {
        console.error('Failed to load config:', error);
        showNotification('Failed to load configuration', 'error');
    }
}

async function saveConfig() {
    const config = {
        organization_name: document.getElementById('org-name').value,
        industry: document.getElementById('industry').value,
        location: document.getElementById('location').value,
        organization_description: document.getElementById('org-description').value || ''
    };

    try {
        const response = await fetch('api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });

        if (response.ok) {
            showNotification('Configuration saved successfully!', 'success');
        } else {
            showNotification('Failed to save configuration', 'error');
        }
    } catch (error) {
        console.error('Failed to save config:', error);
        showNotification('Failed to save configuration', 'error');
    }
}

// ============================================================================
// FORM SUBMISSION & GENERATION
// ============================================================================

async function handleFormSubmit(event) {
    event.preventDefault();

    // Show loading state
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results-section').style.display = 'none';
    document.getElementById('generate-btn').disabled = true;

    // Scroll to loading indicator
    document.getElementById('loading').scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Collect form data
    const formData = collectFormData();

    try {
        const response = await fetch('api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Generation failed');
        }

        const result = await response.json();

        // Store job ID for downloads
        currentJobId = result.job_id;

        // Display results
        displayResults(result);

        // Hide loading, show results
        document.getElementById('loading').style.display = 'none';
        document.getElementById('results-section').style.display = 'block';

        // Scroll to results
        document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Generation failed:', error);
        document.getElementById('loading').style.display = 'none';
        showNotification(`Generation failed: ${error.message}`, 'error');
    } finally {
        document.getElementById('generate-btn').disabled = false;
    }
}

function collectFormData() {
    return {
        job_title: document.getElementById('job-title').value,
        department: document.getElementById('department').value,
        division_section: document.getElementById('division-section').value || '',
        reports_to: document.getElementById('reports-to').value,
        primary_responsibilities: document.getElementById('primary-responsibilities').value,
        key_deliverables: document.getElementById('key-deliverables').value,
        unique_aspects: document.getElementById('unique-aspects').value,
        manages_people: document.getElementById('manages-people').value === 'true',
        num_direct_reports: document.getElementById('num-direct-reports').value || '',
        num_indirect_reports: document.getElementById('num-indirect-reports').value || '',
        other_resources_managed: document.getElementById('other-resources').value || '',
        key_contacts: document.getElementById('key-contacts').value,
        decision_authority: document.getElementById('decision-authority').value,
        innovation_problem_solving: document.getElementById('innovation-problem-solving').value,
        impact_of_results: document.getElementById('impact-of-results').value,
        special_requirements: document.getElementById('special-requirements').value || ''
    };
}

// ============================================================================
// RESULTS DISPLAY
// ============================================================================

function displayResults(result) {
    // Format and display Option 1 (Anthropic)
    document.getElementById('option1-output').innerHTML = formatJobDescription(result.anthropic_output);

    // Format and display Option 2 (Mistral)
    document.getElementById('option2-output').innerHTML = formatJobDescription(result.mistral_output);

    // Store job ID globally for downloads
    window.currentJobId = result.job_id;

    // Show results section
    document.getElementById('results-section').style.display = 'block';
}

function formatJobDescription(text) {
    // Format plain text output into HTML with proper structure
    let html = '';
    const lines = text.split('\n');
    let inList = false;
    let skipUntilNextSection = false;
    let startRendering = false;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();

        // Skip separator lines
        if (line.match(/^[=\-]{10,}$/)) continue;

        // Start rendering from JOB INFORMATION section
        if (line.match(/^JOB INFORMATION$/i)) {
            startRendering = true;
        }

        // Skip everything before JOB INFORMATION
        if (!startRendering) continue;

        // Skip Classification Job Information section entirely
        if (line.match(/^CLASSIFICATION JOB INFORMATION/i)) {
            skipUntilNextSection = true;
            continue;
        }

        // Check if we've reached the next major section (ALL CAPS line)
        if (skipUntilNextSection && line === line.toUpperCase() && line.length > 0 && !line.match(/^[•\-\*]/)) {
            skipUntilNextSection = false;
        }

        // Skip lines within Classification Job Information section
        if (skipUntilNextSection) continue;

        // Skip Exclusion Status line
        if (line.match(/^Exclusion Status:/i)) continue;

        // Detect major section headers (ALL CAPS, standalone)
        if (line === line.toUpperCase() && line.length > 0 && !line.match(/^[•\-\*]/) && !line.includes(':')) {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            // Convert ALL CAPS to Title Case
            const titleCase = toTitleCase(line);
            html += `<h3 class="section-title">${escapeHtml(titleCase)}</h3>`;
        }
        // Detect bullet points
        else if (line.match(/^[•\-\*]/)) {
            if (!inList) {
                html += '<ul>';
                inList = true;
            }
            html += `<li>${escapeHtml(line.replace(/^[•\-\*]\s*/, ''))}</li>`;
        }
        // Detect subsection headers (ends with colon, no text after)
        else if (line.endsWith(':') && line.length < 50) {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            html += `<h4 class="subsection-title">${escapeHtml(line)}</h4>`;
        }
        // Regular text (field: value pairs and paragraphs)
        else if (line.length > 0) {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            // Check if it's a field: value pair
            if (line.includes(':') && line.split(':')[0].length < 40) {
                const parts = line.split(':');
                const field = parts[0].trim();
                const value = parts.slice(1).join(':').trim();
                html += `<p><span class="field-label">${escapeHtml(field)}:</span> ${escapeHtml(value)}</p>`;
            } else {
                html += `<p>${escapeHtml(line)}</p>`;
            }
        }
    }

    if (inList) html += '</ul>';
    return html;
}

function toTitleCase(str) {
    return str.toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================================
// COPY TO CLIPBOARD
// ============================================================================

async function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const text = element.textContent;

    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard!', 'success');
    } catch (error) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.select();

        try {
            document.execCommand('copy');
            showNotification('Copied to clipboard!', 'success');
        } catch (err) {
            console.error('Failed to copy:', err);
            showNotification('Failed to copy to clipboard', 'error');
        }

        document.body.removeChild(textArea);
    }
}

// ============================================================================
// DOWNLOAD
// ============================================================================

function downloadJobDescription(provider, jobId, format) {
    const url = `api/download/${provider}/${jobId}/${format}`;
    window.location.href = url;
}

// ============================================================================
// NOTIFICATIONS
// ============================================================================

function showNotification(message, type = 'success') {
    // Remove any existing notification
    const existingNotification = document.querySelector('.notification-toast');
    if (existingNotification) {
        existingNotification.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification-toast notification-${type}`;
    notification.textContent = message;

    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#10b981' : '#ef4444'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        font-weight: 600;
        animation: slideIn 0.3s ease-out;
    `;

    // Add to page
    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ============================================================================
// TOGGLE SWITCH
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Toggle switch for options
    const toggle = document.getElementById('option-toggle');
    const labels = document.querySelectorAll('.toggle-label');

    if (toggle) {
        toggle.addEventListener('change', function() {
            const option1 = document.getElementById('option1-content');
            const option2 = document.getElementById('option2-content');

            if (this.checked) {
                // Show Option 2
                option1.classList.remove('active');
                option2.classList.add('active');
                labels[0].classList.remove('active');
                labels[1].classList.add('active');
            } else {
                // Show Option 1
                option1.classList.add('active');
                option2.classList.remove('active');
                labels[0].classList.add('active');
                labels[1].classList.remove('active');
            }
        });

        // Set initial active label
        labels[0].classList.add('active');
    }
});

