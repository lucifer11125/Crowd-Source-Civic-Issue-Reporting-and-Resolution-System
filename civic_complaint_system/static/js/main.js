/**
 * Civic Complaint Management System - Main JavaScript File
 * Contains common utilities, validation, and interactive features
 */

// ===== UTILITY FUNCTIONS =====

/**
 * Format date to relative time (e.g., "2 hours ago")
 * @param {Date} date - The date to format
 * @returns {string} Formatted relative time string
 */
function formatRelativeTime(date) {
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) {
        return `${days} day${days > 1 ? 's' : ''} ago`;
    } else if (hours > 0) {
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else if (minutes > 0) {
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else {
        return 'Just now';
    }
}

/**
 * Show loading state on a button
 * @param {HTMLElement} button - The button to show loading state on
 * @param {string} loadingText - Text to show while loading
 */
function showButtonLoading(button, loadingText = 'Loading...') {
    button.disabled = true;
    button.dataset.originalText = button.innerHTML;
    button.innerHTML = `<i class="bi bi-hourglass-split spinner-border spinner-border-sm me-2"></i>${loadingText}`;
}

/**
 * Hide loading state on a button
 * @param {HTMLElement} button - The button to hide loading state from
 */
function hideButtonLoading(button) {
    button.disabled = false;
    button.innerHTML = button.dataset.originalText || button.innerHTML;
}

/**
 * Show success message
 * @param {string} message - Message to show
 * @param {string} type - Type of message (success, error, warning, info)
 */
function showMessage(message, type = 'success') {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.alert-dismissible');
    existingMessages.forEach(msg => msg.remove());

    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Insert at top of container
    const container = document.querySelector('.container, .container-fluid');
    if (container) {
        container.insertBefore(alert, container.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

/**
 * Confirm action before proceeding
 * @param {string} message - Confirmation message
 * @param {Function} callback - Function to call if confirmed
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// ===== FORM VALIDATION =====

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid email
 */
function validateEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {Object} Validation result with valid flag and message
 */
function validatePassword(password) {
    if (password.length < 8) {
        return { valid: false, message: 'Password must be at least 8 characters long' };
    }
    if (!/[a-z]/.test(password)) {
        return { valid: false, message: 'Password must contain at least one lowercase letter' };
    }
    if (!/[A-Z]/.test(password)) {
        return { valid: false, message: 'Password must contain at least one uppercase letter' };
    }
    if (!/\d/.test(password)) {
        return { valid: false, message: 'Password must contain at least one digit' };
    }
    return { valid: true, message: 'Password is strong' };
}

/**
 * Show password strength indicator
 * @param {string} password - Password to check
 * @param {HTMLElement} progressBar - Progress bar element
 * @param {HTMLElement} strengthText - Text element for strength message
 */
function showPasswordStrength(password, progressBar, strengthText) {
    let strength = 0;
    let feedback = '';
    let progressClass = 'bg-danger';

    if (password.length >= 8) strength += 25;
    if (password.length >= 12) strength += 25;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 25;
    if (/\d/.test(password)) strength += 12.5;
    if (/[^a-zA-Z\d]/.test(password)) strength += 12.5;

    if (password.length === 0) {
        progressBar.style.width = '0%';
        progressBar.className = 'progress-bar';
        strengthText.textContent = 'Enter a password to see strength';
        strengthText.className = 'form-text';
    } else if (strength < 30) {
        progressBar.style.width = strength + '%';
        progressBar.className = 'progress-bar bg-danger';
        strengthText.textContent = 'Weak password';
        strengthText.className = 'form-text text-danger';
    } else if (strength < 60) {
        progressBar.style.width = strength + '%';
        progressBar.className = 'progress-bar bg-warning';
        strengthText.textContent = 'Medium strength';
        strengthText.className = 'form-text text-warning';
    } else {
        progressBar.style.width = strength + '%';
        progressBar.className = 'progress-bar bg-success';
        strengthText.textContent = 'Strong password';
        strengthText.className = 'form-text text-success';
    }
}

/**
 * Setup form validation
 * @param {HTMLFormElement} form - Form to validate
 * @param {Object} rules - Validation rules
 */
function setupFormValidation(form, rules) {
    form.addEventListener('submit', function(e) {
        let isValid = true;
        const errors = [];

        // Validate each field
        Object.keys(rules).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (!field) return;

            const rule = rules[fieldName];
            const value = field.value.trim();

            // Required validation
            if (rule.required && !value) {
                errors.push(`${rule.label || fieldName} is required`);
                isValid = false;
                field.classList.add('is-invalid');
            } else {
                field.classList.remove('is-invalid');
            }

            // Custom validation
            if (value && rule.validate && !rule.validate(value)) {
                errors.push(rule.message || `${rule.label || fieldName} is invalid`);
                isValid = false;
                field.classList.add('is-invalid');
            }

            // Length validation
            if (value && rule.minLength && value.length < rule.minLength) {
                errors.push(`${rule.label || fieldName} must be at least ${rule.minLength} characters`);
                isValid = false;
                field.classList.add('is-invalid');
            }
        });

        if (!isValid) {
            e.preventDefault();
            showMessage(errors.join('<br>'), 'danger');

            // Scroll to first error
            const firstError = form.querySelector('.is-invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }
        }
    });
}

// ===== FILE UPLOAD =====

/**
 * Setup file upload with preview
 * @param {HTMLInputElement} fileInput - File input element
 * @param {HTMLElement} previewContainer - Container for preview
 * @param {Object} options - Upload options
 */
function setupFileUpload(fileInput, previewContainer, options = {}) {
    const defaults = {
        maxSize: 5 * 1024 * 1024, // 5MB
        allowedTypes: ['image/png', 'image/jpg', 'image/jpeg', 'image/gif'],
        previewMaxWidth: 300,
        previewMaxHeight: 300
    };

    const config = { ...defaults, ...options };

    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Validate file type
        if (!config.allowedTypes.includes(file.type)) {
            showMessage('Invalid file type. Please select PNG, JPG, JPEG, or GIF files only.', 'danger');
            fileInput.value = '';
            return;
        }

        // Validate file size
        if (file.size > config.maxSize) {
            showMessage('File size too large. Please select an image smaller than 5MB.', 'danger');
            fileInput.value = '';
            return;
        }

        // Show preview
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.className = 'img-fluid mb-2';
            img.style.maxWidth = config.previewMaxWidth + 'px';
            img.style.maxHeight = config.previewMaxHeight + 'px';

            previewContainer.innerHTML = '';
            previewContainer.appendChild(img);

            // Add remove button
            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'btn btn-sm btn-outline-danger';
            removeBtn.innerHTML = '<i class="bi bi-trash"></i> Remove';
            removeBtn.onclick = function() {
                fileInput.value = '';
                previewContainer.innerHTML = '';
            };
            previewContainer.appendChild(removeBtn);
        };
        reader.readAsDataURL(file);
    });
}

// ===== TABLE INTERACTIONS =====

/**
 * Setup table row selection
 * @param {HTMLTableElement} table - Table element
 * @param {Object} options - Selection options
 */
function setupTableSelection(table, options = {}) {
    const defaults = {
        selectAllSelector: '#selectAll',
        rowSelector: 'tbody tr',
        checkboxSelector: 'input[type="checkbox"]'
    };

    const config = { ...defaults, ...options };

    const selectAllCheckbox = table.querySelector(config.selectAllSelector);
    const rowCheckboxes = table.querySelectorAll(config.rowSelector + ' ' + config.checkboxSelector);

    // Select all functionality
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            rowCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
                checkbox.closest('tr').classList.toggle('table-active', this.checked);
            });
        });
    }

    // Row selection
    rowCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const row = this.closest('tr');
            row.classList.toggle('table-active', this.checked);

            // Update select all checkbox state
            const allChecked = Array.from(rowCheckboxes).every(cb => cb.checked);
            const someChecked = Array.from(rowCheckboxes).some(cb => cb.checked);

            if (selectAllCheckbox) {
                selectAllCheckbox.checked = allChecked;
                selectAllCheckbox.indeterminate = someChecked && !allChecked;
            }
        });
    });
}

/**
 * Export table data to CSV
 * @param {HTMLTableElement} table - Table to export
 * @param {string} filename - CSV filename
 */
function exportTableToCSV(table, filename = 'export.csv') {
    const rows = table.querySelectorAll('tr');
    const csv = [];

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];

        cols.forEach(col => {
            let text = col.textContent.trim();
            // Escape quotes and wrap in quotes if contains comma
            if (text.includes(',') || text.includes('"')) {
                text = '"' + text.replace(/"/g, '""') + '"';
            }
            rowData.push(text);
        });

        csv.push(rowData.join(','));
    });

    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ===== INITIALIZATION =====

/**
 * Initialize common functionality when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Setup tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Setup popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add fade-in animation to cards
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    });

    document.querySelectorAll('.card').forEach(card => {
        observer.observe(card);
    });
});

// ===== EXPORT FUNCTIONS =====

// Export utility functions for use in other scripts
window.CivicComplaintSystem = {
    formatRelativeTime,
    showButtonLoading,
    hideButtonLoading,
    showMessage,
    confirmAction,
    validateEmail,
    validatePassword,
    showPasswordStrength,
    setupFormValidation,
    setupFileUpload,
    setupTableSelection,
    exportTableToCSV
};