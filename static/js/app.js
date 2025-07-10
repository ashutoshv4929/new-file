// Smart File Converter - Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the app
    initializeApp();
    
    // Initialize drag and drop functionality
    initializeDragAndDrop();
    
    // Initialize file upload handlers
    initializeFileUploads();
    
    // Initialize theme switcher
    initializeTheme();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize stats refresh
    initializeStatsRefresh();
});

// App initialization
function initializeApp() {
    console.log('Smart File Converter initialized');
    
    // Show loading spinner for any forms being submitted
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                
                // Re-enable button after 30 seconds as fallback
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 30000);
            }
        });
    });
}

// Drag and drop functionality
function initializeDragAndDrop() {
    const uploadAreas = document.querySelectorAll('.upload-area');
    
    uploadAreas.forEach(area => {
        const fileInput = area.querySelector('input[type="file"]');
        if (!fileInput) return;
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            area.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            area.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            area.addEventListener(eventName, unhighlight, false);
        });
        
        // Handle dropped files
        area.addEventListener('drop', handleDrop, false);
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        function highlight(e) {
            area.classList.add('dragover');
        }
        
        function unhighlight(e) {
            area.classList.remove('dragover');
        }
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0], area);
            }
        }
    });
}

// File upload handlers
function initializeFileUploads() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                const uploadArea = e.target.closest('.upload-area');
                handleFileSelect(e.target.files[0], uploadArea);
            }
        });
    });
}

// Handle file selection
function handleFileSelect(file, uploadArea) {
    // Validate file
    if (!validateFile(file)) {
        return;
    }
    
    // Update UI
    updateFileInfo(file, uploadArea);
    
    // Add file selected class
    if (uploadArea) {
        uploadArea.classList.add('file-selected');
    }
}

// Validate file
function validateFile(file) {
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'image/png',
        'image/jpeg',
        'image/gif'
    ];
    
    if (file.size > maxSize) {
        showAlert('File too large. Maximum size is 16MB.', 'error');
        return false;
    }
    
    if (!allowedTypes.includes(file.type)) {
        showAlert('Invalid file type. Please upload PDF, DOC, DOCX, TXT, or image files.', 'error');
        return false;
    }
    
    return true;
}

// Update file info display
function updateFileInfo(file, uploadArea) {
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    
    if (fileInfo && fileName && fileSize) {
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        fileInfo.style.display = 'block';
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Show alert messages
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertContainer, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertContainer.remove();
        }, 5000);
    }
}

// Theme initialization
function initializeTheme() {
    const themeSelect = document.getElementById('themeSelect');
    if (themeSelect) {
        themeSelect.addEventListener('change', function() {
            const theme = this.value;
            applyTheme(theme);
            localStorage.setItem('theme', theme);
        });
        
        // Load saved theme
        const savedTheme = localStorage.getItem('theme') || 'dark';
        themeSelect.value = savedTheme;
        applyTheme(savedTheme);
    }
}

// Apply theme
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    
    if (theme === 'light') {
        document.body.classList.add('light-theme');
        document.body.classList.remove('dark-theme');
    } else {
        document.body.classList.add('dark-theme');
        document.body.classList.remove('light-theme');
    }
}

// Initialize tooltips
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
}

// Initialize stats refresh
function initializeStatsRefresh() {
    // Refresh stats every 30 seconds
    setInterval(refreshStats, 30000);
}

// Refresh stats
function refreshStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            updateStatsDisplay(data);
        })
        .catch(error => {
            console.error('Error refreshing stats:', error);
        });
}

// Update stats display
function updateStatsDisplay(stats) {
    const statNumbers = document.querySelectorAll('.stat-number');
    if (statNumbers.length >= 3) {
        statNumbers[0].textContent = stats.today;
        statNumbers[1].textContent = stats.total;
        statNumbers[2].textContent = stats.saved;
    }
}

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showAlert('Text copied to clipboard!', 'success');
    }, function() {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showAlert('Text copied to clipboard!', 'success');
    });
}

// File download function
function downloadFile(filename, content, mimeType = 'text/plain') {
    const blob = new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Progress bar animation
function animateProgressBar(progressBar, targetWidth, duration = 1000) {
    const startWidth = 0;
    const startTime = Date.now();
    
    function updateProgress() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const currentWidth = startWidth + (targetWidth - startWidth) * progress;
        
        progressBar.style.width = currentWidth + '%';
        
        if (progress < 1) {
            requestAnimationFrame(updateProgress);
        }
    }
    
    requestAnimationFrame(updateProgress);
}

// Handle network errors
function handleNetworkError(error) {
    console.error('Network error:', error);
    showAlert('Network error. Please check your connection and try again.', 'error');
}

// Loading state management
function showLoading(element, text = 'Loading...') {
    element.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2"></span>
        ${text}
    `;
    element.disabled = true;
}

function hideLoading(element, originalText) {
    element.innerHTML = originalText;
    element.disabled = false;
}

// Smooth scroll to element
function scrollToElement(element) {
    element.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Mobile detection
function isMobile() {
    return window.innerWidth <= 768;
}

// Handle mobile-specific functionality
if (isMobile()) {
    // Add mobile-specific classes
    document.body.classList.add('mobile');
    
    // Adjust upload area for mobile
    const uploadAreas = document.querySelectorAll('.upload-area');
    uploadAreas.forEach(area => {
        area.style.padding = '2rem 1rem';
    });
}

// Export functions for global use
window.SmartConverter = {
    showAlert,
    copyToClipboard,
    downloadFile,
    formatFileSize,
    formatDate,
    isMobile,
    debounce,
    throttle
};
