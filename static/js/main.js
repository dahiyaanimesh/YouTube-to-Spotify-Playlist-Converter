// Main JavaScript file for YouTube to Spotify Converter

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize loading states
    initializeLoadingStates();
    
    // Initialize conversion form
    initializeConversionForm();
    
});

function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function initializeLoadingStates() {
    const loadingButtons = document.querySelectorAll('.btn-loading');
    
    loadingButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            showLoadingState(button);
        });
    });
}

function showLoadingState(button) {
    const originalText = button.innerHTML;
    const loadingText = button.dataset.loadingText || 'Loading...';
    
    button.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>${loadingText}`;
    button.disabled = true;
    
    // Store original text for potential restoration
    button.dataset.originalText = originalText;
}

function hideLoadingState(button) {
    const originalText = button.dataset.originalText;
    if (originalText) {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

function initializeConversionForm() {
    const convertForm = document.getElementById('convertForm');
    const convertBtn = document.getElementById('convertBtn');
    const loadingState = document.getElementById('loadingState');
    
    if (convertForm && convertBtn && loadingState) {
        convertForm.addEventListener('submit', function(event) {
            // Get the URL to verify it's not empty
            const urlInput = document.getElementById('playlist_url');
            const url = urlInput?.value?.trim();
            
            // Don't show loading state if URL is empty
            if (!url) {
                return;
            }
            
            // Show loading state with dynamic messages
            setTimeout(() => {
                convertBtn.style.display = 'none';
                loadingState.classList.remove('d-none');
                
                // Start the dynamic loading animation
                startDynamicLoading();
            }, 100);
        });
    }
}

function startDynamicLoading() {
    const loadingSteps = [
        "🔗 Connecting to YouTube...",
        "📋 Fetching playlist information...",
        "🎵 Analyzing video tracks...",
        "🔍 Searching on Spotify...",
        "🎯 Matching songs...",
        "✨ Finding perfect matches...",
        "📝 Creating your playlist...",
        "🎵 Adding tracks to Spotify...",
        "🎉 Almost done...",
        "🚀 Finalizing conversion..."
    ];
    
    const loadingStepElement = document.getElementById('loadingStep');
    let currentStep = 0;
    
    if (!loadingStepElement) return;
    
    // Add some visual flair to the loading container
    const loadingState = document.getElementById('loadingState');
    if (loadingState) {
        loadingState.style.background = 'rgba(255, 255, 255, 0.95)';
        loadingState.style.backdropFilter = 'blur(20px)';
        loadingState.style.borderRadius = '20px';
        loadingState.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.15)';
        loadingState.style.border = '1px solid rgba(255, 255, 255, 0.3)';
    }
    
    // Update loading message with smooth transitions
    const updateStep = () => {
        if (currentStep < loadingSteps.length) {
            loadingStepElement.style.opacity = '0';
            loadingStepElement.style.transform = 'translateY(10px)';
            
            setTimeout(() => {
                loadingStepElement.textContent = loadingSteps[currentStep];
                loadingStepElement.style.opacity = '1';
                loadingStepElement.style.transform = 'translateY(0)';
            }, 300);
            
            currentStep++;
            
            // Variable timing for more natural feeling
            const delay = 1500 + Math.random() * 2000;
            setTimeout(updateStep, delay);
        } else {
            // Loop back to searching/matching steps for long operations
            currentStep = 3; // Start from "Searching on Spotify"
            setTimeout(updateStep, 2000);
        }
    };
    
    // Add CSS transition for smooth text changes
    if (loadingStepElement) {
        loadingStepElement.style.transition = 'all 0.3s ease-in-out';
        loadingStepElement.style.fontWeight = '600';
        loadingStepElement.style.fontSize = '1.1rem';
        loadingStepElement.style.textShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
    }
    
    // Start the animation
    setTimeout(updateStep, 1000);
    
    // Add pulsing effect to the spinner
    const spinner = loadingState?.querySelector('.spinner-border');
    if (spinner) {
        spinner.style.filter = 'drop-shadow(0 0 10px rgba(29, 185, 84, 0.3))';
    }
    
    // Create floating particles effect
    createFloatingParticles(loadingState);
}

function createFloatingParticles(container) {
    if (!container) return;
    
    const particles = [];
    const particleCount = 15;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.style.position = 'absolute';
        particle.style.width = '4px';
        particle.style.height = '4px';
        particle.style.background = `hsl(${Math.random() * 360}, 70%, 60%)`;
        particle.style.borderRadius = '50%';
        particle.style.opacity = '0.6';
        particle.style.pointerEvents = 'none';
        particle.style.zIndex = '1';
        
        // Random position
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        
        // Animation
        particle.style.animation = `float ${3 + Math.random() * 4}s ease-in-out infinite`;
        particle.style.animationDelay = Math.random() * 2 + 's';
        
        container.appendChild(particle);
        particles.push(particle);
        
        // Remove particles after animation
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        }, 10000);
    }
}

// URL validation
function validateYouTubeURL(url) {
    const youtubePatterns = [
        /youtube\.com\/playlist\?list=/i,
        /youtube\.com\/watch\?.*list=/i,
        /youtu\.be\/.*list=/i,
        /m\.youtube\.com\/playlist\?list=/i
    ];
    
    return youtubePatterns.some(pattern => pattern.test(url));
}

// Show success message
function showSuccessMessage(message) {
    showAlert(message, 'success');
}

// Show error message
function showErrorMessage(message) {
    showAlert(message, 'danger');
}

// Show warning message
function showWarningMessage(message) {
    showAlert(message, 'warning');
}

// Generic alert function
function showAlert(message, type) {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.role = 'alert';
    
    const icon = getAlertIcon(type);
    alertContainer.innerHTML = `
        ${icon}
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert at top of container
    const container = document.querySelector('.container');
    const mainContent = container.querySelector('main');
    if (mainContent) {
        container.insertBefore(alertContainer, mainContent);
    } else {
        container.appendChild(alertContainer);
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.remove();
        }
    }, 5000);
}

function getAlertIcon(type) {
    const icons = {
        'success': '<i class="fas fa-check-circle me-2"></i>',
        'danger': '<i class="fas fa-exclamation-triangle me-2"></i>',
        'warning': '<i class="fas fa-exclamation-circle me-2"></i>',
        'info': '<i class="fas fa-info-circle me-2"></i>'
    };
    return icons[type] || icons['info'];
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showSuccessMessage('Copied to clipboard!');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showSuccessMessage('Copied to clipboard!');
    } catch (err) {
        showErrorMessage('Failed to copy to clipboard');
    }
    
    document.body.removeChild(textArea);
}

// Smooth scroll to element
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Debounce function for search inputs
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

// Check if element is in viewport
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// Animate counter
function animateCounter(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const current = Math.floor(progress * (end - start) + start);
        element.textContent = formatNumber(current);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
} 