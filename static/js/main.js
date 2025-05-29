/**
 * =============================================================================
 * YouTube to Spotify Converter - Enhanced JavaScript
 * =============================================================================
 */

// =============================================================================
// CONFIGURATION & CONSTANTS
// =============================================================================
const CONFIG = {
    API_ENDPOINTS: {
        STATUS: '/status',
        TRANSFER: '/transfer'
    },
    TIMEOUTS: {
        FORM_VALIDATION: 300,
        LOADING_STEP: 1800,
        NOTIFICATION: 5000,
        DEBOUNCE: 500
    },
    PATTERNS: {
        YOUTUBE_PLAYLIST: [
            /youtube\.com\/playlist\?list=/i,
            /youtube\.com\/watch\?.*list=/i,
            /youtu\.be\/.*list=/i,
            /m\.youtube\.com\/playlist\?list=/i
        ]
    },
    LOADING_STEPS: [
        '<i class="fas fa-link text-primary"></i> Connecting to YouTube...',
        '<i class="fas fa-list text-danger"></i> Fetching playlist information...',
        '<i class="fas fa-music text-info"></i> Analyzing video tracks...',
        '<i class="fas fa-search text-success"></i> Searching on Spotify...',
        '<i class="fas fa-crosshairs text-warning"></i> Matching songs...',
        '<i class="fas fa-star text-primary"></i> Finding perfect matches...',
        '<i class="fas fa-plus-circle text-success"></i> Creating your playlist...',
        '<i class="fas fa-plus text-success"></i> Adding tracks to Spotify...',
        '<i class="fas fa-check text-info"></i> Almost done...',
        '<i class="fas fa-rocket text-primary"></i> Finalizing conversion...'
    ]
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================
class Utils {
    /**
     * Debounce function calls
     */
    static debounce(func, wait) {
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

    /**
     * Throttle function calls
     */
    static throttle(func, delay) {
        let timeoutId;
        let lastExecTime = 0;
        return function (...args) {
            const currentTime = Date.now();
            
            if (currentTime - lastExecTime > delay) {
                func.apply(this, args);
                lastExecTime = currentTime;
            } else {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => {
                    func.apply(this, args);
                    lastExecTime = Date.now();
                }, delay - (currentTime - lastExecTime));
            }
        };
    }

    /**
     * Check if element is in viewport
     */
    static isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    /**
     * Format numbers with commas
     */
    static formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    /**
     * Smooth scroll to element
     */
    static smoothScrollTo(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }

    /**
     * Get query parameter value
     */
    static getQueryParam(name) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    }

    /**
     * Set local storage with error handling
     */
    static setLocalStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.warn('Failed to save to localStorage:', e);
            return false;
        }
    }

    /**
     * Get local storage with error handling
     */
    static getLocalStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.warn('Failed to read from localStorage:', e);
            return defaultValue;
        }
    }
}

// =============================================================================
// NOTIFICATION SYSTEM
// =============================================================================
class NotificationSystem {
    static showAlert(message, type = 'info', options = {}) {
        const {
            timeout = CONFIG.TIMEOUTS.NOTIFICATION,
            position = 'top',
            dismissible = true,
            persistent = false
        } = options;

        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${type} ${dismissible ? 'alert-dismissible' : ''} fade show`;
        alertContainer.role = 'alert';
        
        const icon = this.getAlertIcon(type);
        alertContainer.innerHTML = `
            ${icon}
            <span class="alert-message">${message}</span>
            ${dismissible ? '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>' : ''}
        `;

        // Add accessibility attributes
        alertContainer.setAttribute('aria-live', 'polite');
        alertContainer.setAttribute('aria-atomic', 'true');

        // Insert at appropriate position
        this.insertAlert(alertContainer, position);

        // Auto-remove if not persistent
        if (!persistent && timeout > 0) {
            setTimeout(() => {
                if (alertContainer.parentNode) {
                    alertContainer.classList.remove('show');
                    setTimeout(() => alertContainer.remove(), 150);
                }
            }, timeout);
        }

        return alertContainer;
    }

    static insertAlert(alert, position) {
        const container = document.querySelector('.container');
        if (!container) return;

        let alertsContainer = document.querySelector('.alerts-container');
        if (!alertsContainer) {
            alertsContainer = document.createElement('div');
            alertsContainer.className = 'alerts-container';
            alertsContainer.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                z-index: 1050;
                max-width: 400px;
                width: 100%;
            `;
            document.body.appendChild(alertsContainer);
        }

        if (position === 'top') {
            alertsContainer.insertBefore(alert, alertsContainer.firstChild);
        } else {
            alertsContainer.appendChild(alert);
        }
    }

    static getAlertIcon(type) {
        const icons = {
            'success': '<i class="fas fa-check-circle me-2"></i>',
            'danger': '<i class="fas fa-exclamation-triangle me-2"></i>',
            'warning': '<i class="fas fa-exclamation-circle me-2"></i>',
            'info': '<i class="fas fa-info-circle me-2"></i>',
            'primary': '<i class="fas fa-bell me-2"></i>'
        };
        return icons[type] || icons['info'];
    }

    static success(message, options = {}) {
        return this.showAlert(message, 'success', options);
    }

    static error(message, options = {}) {
        return this.showAlert(message, 'danger', options);
    }

    static warning(message, options = {}) {
        return this.showAlert(message, 'warning', options);
    }

    static info(message, options = {}) {
        return this.showAlert(message, 'info', options);
    }
}

// =============================================================================
// FORM VALIDATION
// =============================================================================
class FormValidator {
    constructor(form) {
        this.form = form;
        this.validators = new Map();
        this.isValid = true;
        this.init();
    }

    init() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        this.setupRealTimeValidation();
    }

    setupRealTimeValidation() {
        const inputs = this.form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            const debouncedValidate = Utils.debounce(() => {
                this.validateField(input);
            }, CONFIG.TIMEOUTS.FORM_VALIDATION);

            input.addEventListener('input', debouncedValidate);
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('focus', () => this.clearFieldErrors(input));
        });
    }

    validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name || field.id;
        let isFieldValid = true;
        let errorMessage = '';

        // Required field validation
        if (field.hasAttribute('required') && !value) {
            isFieldValid = false;
            errorMessage = `${this.getFieldLabel(field)} is required.`;
        }

        // URL validation for playlist_url field
        if (fieldName === 'playlist_url' && value) {
            if (!this.validateYouTubeURL(value)) {
                isFieldValid = false;
                errorMessage = 'Please enter a valid YouTube playlist URL.';
            }
        }

        // Email validation
        if (field.type === 'email' && value) {
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(value)) {
                isFieldValid = false;
                errorMessage = 'Please enter a valid email address.';
            }
        }

        // Custom validators
        if (this.validators.has(fieldName)) {
            const customValidator = this.validators.get(fieldName);
            const customResult = customValidator(value, field);
            if (!customResult.isValid) {
                isFieldValid = false;
                errorMessage = customResult.message;
            }
        }

        this.updateFieldStatus(field, isFieldValid, errorMessage);
        return isFieldValid;
    }

    validateYouTubeURL(url) {
        return CONFIG.PATTERNS.YOUTUBE_PLAYLIST.some(pattern => pattern.test(url));
    }

    updateFieldStatus(field, isValid, errorMessage) {
        field.classList.remove('is-valid', 'is-invalid');
        
        const existingFeedback = field.parentNode.querySelector('.invalid-feedback, .valid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        if (isValid && field.value.trim()) {
            field.classList.add('is-valid');
            this.addFeedback(field, 'valid-feedback', '✓ Looks good!');
        } else if (!isValid) {
            field.classList.add('is-invalid');
            this.addFeedback(field, 'invalid-feedback', errorMessage);
        }
    }

    addFeedback(field, className, message) {
        const feedback = document.createElement('div');
        feedback.className = className;
        feedback.textContent = message;
        field.parentNode.appendChild(feedback);
    }

    clearFieldErrors(field) {
        const errorFeedback = field.parentNode.querySelector('.invalid-feedback');
        if (errorFeedback) {
            setTimeout(() => errorFeedback.remove(), 100);
        }
    }

    getFieldLabel(field) {
        const label = this.form.querySelector(`label[for="${field.id}"]`);
        return label ? label.textContent.replace('*', '').trim() : field.name || 'Field';
    }

    handleSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(this.form);
        const isFormValid = this.validateForm();

        if (isFormValid) {
            this.onValidSubmit(formData);
        } else {
            this.focusFirstError();
        }
    }

    validateForm() {
        const inputs = this.form.querySelectorAll('input, select, textarea');
        let isFormValid = true;

        inputs.forEach(input => {
            const isFieldValid = this.validateField(input);
            if (!isFieldValid) {
                isFormValid = false;
            }
        });

        return isFormValid;
    }

    focusFirstError() {
        const firstError = this.form.querySelector('.is-invalid');
        if (firstError) {
            firstError.focus();
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    addValidator(fieldName, validator) {
        this.validators.set(fieldName, validator);
    }

    onValidSubmit(formData) {
        // Override in specific implementations
        console.log('Form submitted with valid data:', formData);
    }
}

// =============================================================================
// LOADING SYSTEM
// =============================================================================
class LoadingSystem {
    constructor() {
        this.isLoading = false;
        this.currentStep = 0;
        this.loadingInterval = null;
        this.particlesInterval = null;
    }

    show(container, options = {}) {
        if (this.isLoading) return;

        const {
            title = 'Converting Your Playlist...',
            subtitle = 'This may take a few moments depending on playlist size',
            showProgress = true,
            steps = CONFIG.LOADING_STEPS
        } = options;

        this.isLoading = true;
        this.currentStep = 0;

        // Hide the form and show loading state
        if (container) {
            setTimeout(() => {
                const form = container.querySelector('form');
                if (form) {
                    form.classList.add('d-none');
                }

                const loadingState = container.querySelector('#loadingState');
                if (loadingState) {
                    this.setupLoadingState(loadingState, title, subtitle, showProgress);
                    loadingState.classList.remove('d-none');
                    this.startAnimation(loadingState, steps);
                }
            }, 100);
        }
    }

    setupLoadingState(loadingState, title, subtitle, showProgress) {
        // Ensure proper positioning
        const cardBody = loadingState.closest('.card-body');
        if (cardBody) {
            cardBody.style.position = 'relative';
            cardBody.style.minHeight = '400px';
        }

        // Enhanced styling
        Object.assign(loadingState.style, {
            background: 'rgba(255, 255, 255, 0.98)',
            backdropFilter: 'blur(20px)',
            borderRadius: '20px',
            boxShadow: '0 15px 35px rgba(0, 0, 0, 0.1), 0 5px 15px rgba(0, 0, 0, 0.08)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            padding: '2.5rem',
            maxWidth: '500px',
            margin: '0 auto',
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: '1000'
        });

        // Update title and subtitle if provided
        const titleElement = loadingState.querySelector('h5');
        const subtitleElement = loadingState.querySelector('p');
        
        if (titleElement) titleElement.textContent = title;
        if (subtitleElement) subtitleElement.textContent = subtitle;

        // Style the spinner
        const spinner = loadingState.querySelector('.spinner-border');
        if (spinner) {
            Object.assign(spinner.style, {
                width: '3.5rem',
                height: '3.5rem',
                borderWidth: '4px',
                filter: 'drop-shadow(0 4px 8px rgba(29, 185, 84, 0.3))',
                marginBottom: '1.5rem'
            });
        }
    }

    startAnimation(loadingState, steps) {
        const loadingStepElement = loadingState.querySelector('#loadingStep');
        if (!loadingStepElement) return;

        // Setup loading step element styles
        Object.assign(loadingStepElement.style, {
            transition: 'all 0.4s cubic-bezier(0.4, 0.0, 0.2, 1)',
            fontWeight: '600',
            fontSize: '1.1rem',
            textShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            color: '#2d3748',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            minHeight: '32px'
        });

        // Start step animation
        this.animateSteps(loadingStepElement, steps);
        
        // Create floating particles
        this.createFloatingParticles(loadingState);
    }

    animateSteps(loadingStepElement, steps) {
        const updateStep = () => {
            if (!this.isLoading) return;

            if (this.currentStep < steps.length) {
                this.transitionStep(loadingStepElement, steps[this.currentStep]);
                this.currentStep++;
                
                // Variable timing for more natural feeling
                const delay = CONFIG.TIMEOUTS.LOADING_STEP + Math.random() * 1500;
                this.loadingInterval = setTimeout(updateStep, delay);
            } else {
                // Loop back to searching/matching steps for long operations
                this.currentStep = 3; // Start from "Searching on Spotify"
                this.loadingInterval = setTimeout(updateStep, 2500);
            }
        };

        // Start the animation
        setTimeout(updateStep, 1000);
    }

    transitionStep(element, stepContent) {
        element.style.opacity = '0';
        element.style.transform = 'translateY(15px)';
        
        setTimeout(() => {
            element.innerHTML = stepContent;
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 300);
    }

    createFloatingParticles(container) {
        const particleCount = 15;
        const particles = [];

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            Object.assign(particle.style, {
                position: 'absolute',
                width: '4px',
                height: '4px',
                background: `hsl(${Math.random() * 360}, 70%, 60%)`,
                borderRadius: '50%',
                opacity: '0.6',
                pointerEvents: 'none',
                zIndex: '1',
                left: Math.random() * 100 + '%',
                top: Math.random() * 100 + '%',
                animation: `float ${3 + Math.random() * 4}s ease-in-out infinite`,
                animationDelay: Math.random() * 2 + 's'
            });

            container.appendChild(particle);
            particles.push(particle);
        }

        // Clean up particles after animation
        setTimeout(() => {
            particles.forEach(particle => {
                if (particle.parentNode) {
                    particle.parentNode.removeChild(particle);
                }
            });
        }, 10000);
    }

    hide() {
        this.isLoading = false;
        this.currentStep = 0;
        
        if (this.loadingInterval) {
            clearTimeout(this.loadingInterval);
            this.loadingInterval = null;
        }

        if (this.particlesInterval) {
            clearInterval(this.particlesInterval);
            this.particlesInterval = null;
        }

        const loadingState = document.getElementById('loadingState');
        if (loadingState) {
            loadingState.classList.add('d-none');
        }
    }
}

// =============================================================================
// CLIPBOARD UTILITY
// =============================================================================
class ClipboardManager {
    static async copy(text) {
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(text);
                NotificationSystem.success('Copied to clipboard!');
                return true;
            } else {
                return this.fallbackCopy(text);
            }
        } catch (err) {
            console.error('Failed to copy text: ', err);
            return this.fallbackCopy(text);
        }
    }

    static fallbackCopy(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.cssText = `
            position: fixed;
            left: -999999px;
            top: -999999px;
            opacity: 0;
        `;
        
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                NotificationSystem.success('Copied to clipboard!');
            } else {
                NotificationSystem.error('Failed to copy to clipboard');
            }
            return successful;
        } catch (err) {
            console.error('Fallback copy failed: ', err);
            NotificationSystem.error('Failed to copy to clipboard');
            return false;
        } finally {
            document.body.removeChild(textArea);
        }
    }
}

// =============================================================================
// CONVERSION FORM HANDLER
// =============================================================================
class ConversionFormHandler extends FormValidator {
    constructor(form) {
        super(form);
        this.loadingSystem = new LoadingSystem();
        this.setupCustomValidators();
    }

    setupCustomValidators() {
        // Add custom validator for playlist name length
        this.addValidator('playlist_name', (value) => {
            if (value && value.length > 100) {
                return {
                    isValid: false,
                    message: 'Playlist name must be 100 characters or less.'
                };
            }
            return { isValid: true };
        });

        // Add custom validator for YouTube URL with better error messages
        this.addValidator('playlist_url', (value) => {
            if (!value) {
                return { isValid: false, message: 'Please enter a YouTube playlist URL.' };
            }

            if (!this.validateYouTubeURL(value)) {
                return {
                    isValid: false,
                    message: 'This doesn\'t look like a YouTube playlist URL. Please check and try again.'
                };
            }

            return { isValid: true };
        });
    }

    onValidSubmit(formData) {
        const url = formData.get('playlist_url');
        
        // Save form data to localStorage for recovery
        Utils.setLocalStorage('lastConversion', {
            url: url,
            name: formData.get('playlist_name'),
            timestamp: Date.now()
        });

        // Show loading state
        this.loadingSystem.show(this.form.closest('.card-body'), {
            title: 'Converting Your Playlist...',
            subtitle: 'Analyzing your YouTube playlist and finding matches on Spotify'
        });

        // Submit the actual form
        this.form.submit();
    }
}

// =============================================================================
// COUNTER ANIMATION
// =============================================================================
class CounterAnimator {
    static animate(element, start, end, duration = 2000) {
        let startTimestamp = null;
        
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            
            // Use easing function for smooth animation
            const easedProgress = this.easeOutQuart(progress);
            const current = Math.floor(easedProgress * (end - start) + start);
            
            element.textContent = Utils.formatNumber(current);
            
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        
        window.requestAnimationFrame(step);
    }

    static easeOutQuart(t) {
        return 1 - (--t) * t * t * t;
    }

    static animateOnScroll() {
        const counters = document.querySelectorAll('[data-counter]');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.dataset.animated) {
                    const target = parseInt(entry.target.dataset.counter);
                    const duration = parseInt(entry.target.dataset.duration) || 2000;
                    
                    this.animate(entry.target, 0, target, duration);
                    entry.target.dataset.animated = 'true';
                }
            });
        }, { threshold: 0.5 });

        counters.forEach(counter => observer.observe(counter));
    }
}

// =============================================================================
// PROGRESS BAR ANIMATOR
// =============================================================================
class ProgressBarAnimator {
    static init() {
        const progressBars = document.querySelectorAll('.progress-bar[data-success-rate]');
        progressBars.forEach(bar => this.animateProgressBar(bar));
    }

    static animateProgressBar(progressBar) {
        const successRate = progressBar.dataset.successRate;
        
        // Initial state
        progressBar.style.width = '0%';
        
        // Animate after a delay
        setTimeout(() => {
            progressBar.style.transition = 'width 1.5s cubic-bezier(0.4, 0.0, 0.2, 1)';
            progressBar.style.width = successRate + '%';
            
            // Add success rate text if it doesn't exist
            if (!progressBar.querySelector('.progress-text')) {
                const progressText = document.createElement('span');
                progressText.className = 'progress-text';
                progressText.textContent = `${parseFloat(successRate).toFixed(1)}%`;
                progressBar.appendChild(progressText);
            }
        }, 500);
    }
}

// =============================================================================
// KEYBOARD SHORTCUTS
// =============================================================================
class KeyboardShortcuts {
    static init() {
        document.addEventListener('keydown', this.handleKeydown.bind(this));
    }

    static handleKeydown(event) {
        // Ctrl/Cmd + Enter to submit forms
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            const form = event.target.closest('form');
            if (form) {
                event.preventDefault();
                form.requestSubmit();
            }
        }

        // Escape to close modals or cancel loading
        if (event.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) bsModal.hide();
            });

            // Cancel loading if active
            const loadingStates = document.querySelectorAll('#loadingState:not(.d-none)');
            if (loadingStates.length > 0) {
                // Only cancel if user confirms
                if (confirm('Cancel conversion?')) {
                    window.location.reload();
                }
            }
        }

        // Alt + C to copy results
        if (event.altKey && event.key === 'c') {
            const playlistUrl = document.querySelector('.btn-spotify')?.href;
            if (playlistUrl) {
                ClipboardManager.copy(playlistUrl);
            }
        }
    }
}

// =============================================================================
// THEME MANAGER
// =============================================================================
class ThemeManager {
    static init() {
        this.detectPreferences();
        this.setupToggle();
    }

    static detectPreferences() {
        // Detect system dark mode preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('dark-mode-preferred');
        }

        // Listen for changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (e.matches) {
                document.body.classList.add('dark-mode-preferred');
            } else {
                document.body.classList.remove('dark-mode-preferred');
            }
        });
    }

    static setupToggle() {
        // Add theme toggle button if needed
        const navbar = document.querySelector('.navbar');
        if (navbar && !navbar.querySelector('.theme-toggle')) {
            const toggle = document.createElement('button');
            toggle.className = 'btn btn-link text-light theme-toggle';
            toggle.innerHTML = '<i class="fas fa-moon"></i>';
            toggle.title = 'Toggle theme';
            toggle.addEventListener('click', this.toggleTheme.bind(this));
            
            const navItems = navbar.querySelector('.navbar-nav');
            if (navItems) {
                navItems.appendChild(toggle);
            }
        }
    }

    static toggleTheme() {
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        
        // Update toggle icon
        const toggleIcon = document.querySelector('.theme-toggle i');
        if (toggleIcon) {
            toggleIcon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
        }

        // Save preference
        Utils.setLocalStorage('theme', isDark ? 'dark' : 'light');
    }
}

// =============================================================================
// PERFORMANCE MONITOR
// =============================================================================
class PerformanceMonitor {
    static init() {
        this.measurePageLoad();
        this.setupResourceMonitoring();
    }

    static measurePageLoad() {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData) {
                    const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
                    console.log(`Page load time: ${loadTime.toFixed(2)}ms`);
                    
                    // Log slow loads
                    if (loadTime > 3000) {
                        console.warn('Slow page load detected');
                    }
                }
            }, 0);
        });
    }

    static setupResourceMonitoring() {
        // Monitor for large images
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            img.addEventListener('load', () => {
                if (img.naturalWidth > 2000 || img.naturalHeight > 2000) {
                    console.warn('Large image detected:', img.src);
                }
            });
        });
    }
}

// =============================================================================
// MAIN APPLICATION INITIALIZATION
// =============================================================================
class App {
    static init() {
        console.log('🎵 YouTube to Spotify Converter - Loading...');
        
        // Initialize core systems
        this.initializeCoreSystems();
        
        // Initialize form handlers
        this.initializeFormHandlers();
        
        // Initialize UI components
        this.initializeUIComponents();
        
        // Initialize utilities
        this.initializeUtilities();
        
        console.log('✅ Application initialized successfully');
    }

    static initializeCoreSystems() {
        // Bootstrap tooltips and popovers
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));

        // Initialize theme management
        ThemeManager.init();
        
        // Initialize keyboard shortcuts
        KeyboardShortcuts.init();
    }

    static initializeFormHandlers() {
        // Initialize conversion form
        const convertForm = document.getElementById('convertForm');
        if (convertForm) {
            new ConversionFormHandler(convertForm);
        }

        // Initialize other forms with basic validation
        const forms = document.querySelectorAll('form:not(#convertForm)');
        forms.forEach(form => new FormValidator(form));
    }

    static initializeUIComponents() {
        // Initialize progress bars
        ProgressBarAnimator.init();
        
        // Initialize counters with scroll animation
        CounterAnimator.animateOnScroll();
        
        // Setup copy buttons
        this.setupCopyButtons();
        
        // Setup failed tracks collapse behavior
        this.setupFailedTracksCollapse();
    }

    static initializeUtilities() {
        // Initialize performance monitoring in development
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            PerformanceMonitor.init();
        }

        // Setup error handling
        this.setupErrorHandling();
        
        // Setup network status monitoring
        this.setupNetworkMonitoring();
    }

    static setupCopyButtons() {
        const copyButtons = document.querySelectorAll('[data-copy]');
        copyButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const text = button.dataset.copy || button.href || button.textContent;
                ClipboardManager.copy(text);
            });
        });
    }

    static setupFailedTracksCollapse() {
        const resultData = document.getElementById('resultData');
        if (resultData) {
            const successRate = parseFloat(resultData.dataset.successRate);
            if (successRate >= 90) {
                const failedTracksCollapse = document.getElementById('failedTracks');
                if (failedTracksCollapse) {
                    failedTracksCollapse.classList.remove('show');
                }
            }
        }
    }

    static setupErrorHandling() {
        window.addEventListener('error', (event) => {
            console.error('JavaScript error:', event.error);
            // Don't show errors to users in production
            if (window.location.hostname === 'localhost') {
                NotificationSystem.error('A JavaScript error occurred. Check console for details.');
            }
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            if (window.location.hostname === 'localhost') {
                NotificationSystem.error('An async error occurred. Check console for details.');
            }
        });
    }

    static setupNetworkMonitoring() {
        window.addEventListener('online', () => {
            NotificationSystem.success('Connection restored!');
        });

        window.addEventListener('offline', () => {
            NotificationSystem.warning('Connection lost. Some features may not work.', {
                persistent: true
            });
        });
    }
}

// =============================================================================
// INITIALIZE APPLICATION
// =============================================================================
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

// Legacy compatibility for external scripts
window.convertForm = {
    validateYouTubeURL: (url) => CONFIG.PATTERNS.YOUTUBE_PLAYLIST.some(pattern => pattern.test(url)),
    showLoading: () => new LoadingSystem().show(document.querySelector('#convertForm')),
    hideLoading: () => new LoadingSystem().hide(),
    showNotification: (message, type) => NotificationSystem.showAlert(message, type)
};

// Enhanced keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus URL input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const urlInput = document.getElementById('playlist_url');
        if (urlInput) {
            urlInput.focus();
            urlInput.select();
        }
    }
});

console.log('🎵 YouTube to Spotify Converter - Index page loaded');
console.log('💡 Keyboard shortcuts: Ctrl+K (URL focus)'); 