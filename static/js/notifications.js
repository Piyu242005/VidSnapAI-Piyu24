// Toast Notification System

class NotificationManager {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('toast-container');
        }
    }

    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = this.getIcon(type);
        toast.innerHTML = `
            <div class="toast-content">
                <i class="${icon}"></i>
                <span class="toast-message">${message}</span>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
        `;
        
        this.container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                this.remove(toast);
            }, duration);
        }
        
        return toast;
    }

    success(message, duration = 3000) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 5000) {
        return this.show(message, 'error', duration);
    }

    info(message, duration = 3000) {
        return this.show(message, 'info', duration);
    }

    warning(message, duration = 4000) {
        return this.show(message, 'warning', duration);
    }

    getIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    remove(toast) {
        toast.classList.add('hide');
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 300);
    }

    clear() {
        const toasts = this.container.querySelectorAll('.toast');
        toasts.forEach(toast => this.remove(toast));
    }
}

// Initialize notification manager
const notifications = new NotificationManager();

// Add toast styles dynamically
const toastStyles = `
<style>
.toast {
    background: linear-gradient(135deg, rgba(0, 0, 0, 0.95) 0%, rgba(0, 0, 0, 0.95) 50%, rgba(255, 0, 0, 0.2) 100%);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(255, 0, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-width: 300px;
    max-width: 100%;
    margin-bottom: 10px;
    opacity: 0;
    transform: translateX(400px);
    transition: all 0.3s ease;
    border-left: 4px solid #ff0000;
    border: 1px solid rgba(255, 0, 0, 0.3);
}

.toast.show {
    opacity: 1;
    transform: translateX(0);
}

.toast.hide {
    opacity: 0;
    transform: translateX(400px);
}

.toast-success {
    border-left-color: #28a745;
}

.toast-error {
    border-left-color: #dc3545;
}

.toast-warning {
    border-left-color: #ffc107;
}

.toast-info {
    border-left-color: #17a2b8;
}

.toast-content {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
}

.toast-content i {
    font-size: 1.2rem;
}

.toast-success .toast-content i {
    color: #28a745;
}

.toast-error .toast-content i {
    color: #dc3545;
}

.toast-warning .toast-content i {
    color: #ffc107;
}

.toast-info .toast-content i {
    color: #17a2b8;
}

.toast-message {
    flex: 1;
}

.toast-close {
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    margin-left: 15px;
    opacity: 0.7;
    transition: opacity 0.3s;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.toast-close:hover {
    opacity: 1;
}

@media (max-width: 576px) {
    .toast {
        min-width: auto;
        width: 100%;
    }
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', toastStyles);

// Export for use in other scripts
window.notifications = notifications;

