// Keyboard Shortcuts Handler

class ShortcutManager {
    constructor() {
        this.shortcuts = new Map();
        this.init();
    }

    init() {
        document.addEventListener('keydown', (e) => {
            this.handleKeyPress(e);
        });
    }

    register(key, callback, description = '') {
        const keyString = this.normalizeKey(key);
        if (!this.shortcuts.has(keyString)) {
            this.shortcuts.set(keyString, []);
        }
        this.shortcuts.get(keyString).push({
            callback,
            description
        });
    }

    normalizeKey(e) {
        const parts = [];
        if (e.ctrlKey || e.metaKey) parts.push('ctrl');
        if (e.altKey) parts.push('alt');
        if (e.shiftKey) parts.push('shift');
        parts.push(e.key.toLowerCase());
        return parts.join('+');
    }

    handleKeyPress(e) {
        // Don't trigger shortcuts when typing in inputs
        if (e.target.tagName === 'INPUT' || 
            e.target.tagName === 'TEXTAREA' || 
            e.target.isContentEditable) {
            // Allow Escape to close modals even in inputs
            if (e.key === 'Escape') {
                this.handleEscape(e);
            }
            return;
        }

        const keyString = this.normalizeKey(e);
        const handlers = this.shortcuts.get(keyString);
        
        if (handlers && handlers.length > 0) {
            e.preventDefault();
            handlers.forEach(handler => {
                try {
                    handler.callback(e);
                } catch (error) {
                    console.error('Shortcut handler error:', error);
                }
            });
        }
    }

    handleEscape(e) {
        // Close any open modals
        const modals = document.querySelectorAll('.modal-fullscreen, .success-modal, .share-modal');
        modals.forEach(modal => {
            if (modal.style.display !== 'none') {
                modal.style.display = 'none';
            }
        });
    }
}

// Initialize shortcut manager
const shortcuts = new ShortcutManager();

// Register common shortcuts
shortcuts.register('ctrl+s', (e) => {
    e.preventDefault();
    const form = document.querySelector('form');
    if (form) {
        // Save form data to localStorage
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            if (value instanceof File) {
                // Can't store files, skip
                continue;
            }
            data[key] = value;
        }
        localStorage.setItem('formDraft', JSON.stringify(data));
        if (window.notifications) {
            window.notifications.success('Form draft saved!');
        }
    }
}, 'Save form draft');

shortcuts.register('ctrl+enter', (e) => {
    const submitBtn = document.querySelector('button[type="submit"], input[type="submit"]');
    if (submitBtn && !submitBtn.disabled) {
        submitBtn.click();
    }
}, 'Submit form');

shortcuts.register('escape', (e) => {
    shortcuts.handleEscape(e);
}, 'Close modals');

// Gallery navigation shortcuts
shortcuts.register('arrowright', (e) => {
    if (window.location.pathname === '/gallery') {
        const videos = document.querySelectorAll('.reel-video');
        const current = Array.from(videos).findIndex(v => v === document.activeElement);
        if (current < videos.length - 1) {
            videos[current + 1].focus();
        }
    }
}, 'Next video');

shortcuts.register('arrowleft', (e) => {
    if (window.location.pathname === '/gallery') {
        const videos = document.querySelectorAll('.reel-video');
        const current = Array.from(videos).findIndex(v => v === document.activeElement);
        if (current > 0) {
            videos[current - 1].focus();
        }
    }
}, 'Previous video');

// Export for use in other scripts
window.shortcuts = shortcuts;

// Show shortcuts help (Ctrl+?)
shortcuts.register('ctrl+?', (e) => {
    e.preventDefault();
    showShortcutsHelp();
}, 'Show keyboard shortcuts');

function showShortcutsHelp() {
    const helpModal = document.createElement('div');
    helpModal.className = 'shortcuts-help-modal';
    helpModal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10001;
    `;
    
    const helpContent = document.createElement('div');
    helpContent.style.cssText = `
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 15px;
        max-width: 500px;
        color: #333;
    `;
    
    helpContent.innerHTML = `
        <h2 style="color: #ff0000; margin-bottom: 1rem;">Keyboard Shortcuts</h2>
        <ul style="list-style: none; padding: 0;">
            <li style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">
                <strong>Ctrl + S</strong> - Save form draft
            </li>
            <li style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">
                <strong>Ctrl + Enter</strong> - Submit form
            </li>
            <li style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">
                <strong>Escape</strong> - Close modals
            </li>
            <li style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">
                <strong>Ctrl + ?</strong> - Show this help
            </li>
            <li style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">
                <strong>Arrow Keys</strong> - Navigate gallery (when on gallery page)
            </li>
        </ul>
        <button onclick="this.closest('.shortcuts-help-modal').remove()" 
                style="margin-top: 1rem; padding: 0.5rem 1rem; background: #ff0000; color: white; border: none; border-radius: 5px; cursor: pointer;">
            Close
        </button>
    `;
    
    helpModal.appendChild(helpContent);
    document.body.appendChild(helpModal);
    
    helpModal.addEventListener('click', (e) => {
        if (e.target === helpModal) {
            helpModal.remove();
        }
    });
}

