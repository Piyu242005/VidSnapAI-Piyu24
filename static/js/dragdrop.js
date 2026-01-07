// Drag and Drop File Upload Handler

class DragDropManager {
    constructor(dropZoneId, previewContainerId) {
        this.dropZone = document.getElementById(dropZoneId);
        this.previewContainer = document.getElementById(previewContainerId);
        this.files = [];
        this.init();
    }

    init() {
        if (!this.dropZone) return;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, () => {
                this.dropZone.classList.add('drag-over');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, () => {
                this.dropZone.classList.remove('drag-over');
            }, false);
        });

        // Handle dropped files
        this.dropZone.addEventListener('drop', (e) => {
            this.handleDrop(e);
        }, false);

        // Handle click to browse
        this.dropZone.addEventListener('click', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.multiple = true;
            input.accept = 'image/*';
            input.onchange = (e) => {
                this.handleFiles(Array.from(e.target.files));
            };
            input.click();
        });
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = Array.from(dt.files).filter(file => file.type.startsWith('image/'));
        this.handleFiles(files);
    }

    handleFiles(files) {
        files.forEach(file => {
            if (this.validateFile(file)) {
                this.files.push({
                    file: file,
                    id: Date.now() + Math.random(),
                    duration: 1,
                    order: this.files.length
                });
            }
        });
        this.updatePreview();
        this.updateHiddenInputs();
    }

    validateFile(file) {
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
        
        if (!allowedTypes.includes(file.type)) {
            if (window.notifications) {
                window.notifications.error(`File ${file.name} is not a valid image type.`);
            }
            return false;
        }
        
        if (file.size > maxSize) {
            if (window.notifications) {
                window.notifications.error(`File ${file.name} is too large. Maximum size is 10MB.`);
            }
            return false;
        }
        
        return true;
    }

    updatePreview() {
        if (!this.previewContainer) return;
        
        this.previewContainer.innerHTML = '';
        
        this.files.forEach((item, index) => {
            const card = this.createPreviewCard(item, index);
            this.previewContainer.appendChild(card);
        });
    }

    createPreviewCard(item, index) {
        const card = document.createElement('div');
        card.className = 'preview-card';
        card.draggable = true;
        card.dataset.id = item.id;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            card.innerHTML = `
                <div class="preview-image-wrapper">
                    <img src="${e.target.result}" alt="Preview" class="preview-image">
                    <div class="preview-overlay">
                        <span class="preview-order">${index + 1}</span>
                    </div>
                </div>
                <div class="preview-controls">
                    <div class="duration-control">
                        <label>Duration (s):</label>
                        <input type="number" class="duration-input" value="${item.duration}" 
                               min="0.5" max="5" step="0.5" 
                               data-id="${item.id}">
                    </div>
                    <div class="card-actions">
                        <button class="btn-move-up" data-id="${item.id}" title="Move Up">
                            <i class="fas fa-arrow-up"></i>
                        </button>
                        <button class="btn-move-down" data-id="${item.id}" title="Move Down">
                            <i class="fas fa-arrow-down"></i>
                        </button>
                        <button class="btn-remove" data-id="${item.id}" title="Remove">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            `;
            
            // Add event listeners
            card.querySelector('.btn-remove').addEventListener('click', () => {
                this.removeFile(item.id);
            });
            
            card.querySelector('.btn-move-up').addEventListener('click', () => {
                this.moveFile(item.id, -1);
            });
            
            card.querySelector('.btn-move-down').addEventListener('click', () => {
                this.moveFile(item.id, 1);
            });
            
            card.querySelector('.duration-input').addEventListener('change', (e) => {
                this.updateDuration(item.id, parseFloat(e.target.value));
            });
            
            // Drag and drop for reordering
            card.addEventListener('dragstart', (e) => {
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', card.outerHTML);
                e.dataTransfer.setData('text/plain', item.id);
                card.classList.add('dragging');
            });
            
            card.addEventListener('dragend', () => {
                card.classList.remove('dragging');
            });
            
            card.addEventListener('dragover', (e) => {
                e.preventDefault();
                const afterElement = this.getDragAfterElement(this.previewContainer, e.clientY);
                const dragging = document.querySelector('.dragging');
                if (afterElement == null) {
                    this.previewContainer.appendChild(dragging);
                } else {
                    this.previewContainer.insertBefore(dragging, afterElement);
                }
            });
        };
        
        reader.readAsDataURL(item.file);
        
        return card;
    }

    getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.preview-card:not(.dragging)')];
        
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    removeFile(id) {
        this.files = this.files.filter(item => item.id !== id);
        this.updatePreview();
        this.updateHiddenInputs();
    }

    moveFile(id, direction) {
        const index = this.files.findIndex(item => item.id === id);
        if (index === -1) return;
        
        const newIndex = index + direction;
        if (newIndex < 0 || newIndex >= this.files.length) return;
        
        [this.files[index], this.files[newIndex]] = [this.files[newIndex], this.files[index]];
        this.updatePreview();
        this.updateHiddenInputs();
    }

    updateDuration(id, duration) {
        const item = this.files.find(f => f.id === id);
        if (item) {
            item.duration = duration;
        }
    }

    updateHiddenInputs() {
        // Remove old hidden inputs
        const oldInputs = document.querySelectorAll('.hidden-file-input');
        oldInputs.forEach(input => input.remove());
        
        // Create FormData and hidden inputs for submission
        const form = document.querySelector('form');
        if (!form) return;
        
        this.files.forEach((item, index) => {
            const input = document.createElement('input');
            input.type = 'file';
            input.name = `file${index + 1}`;
            input.className = 'hidden-file-input';
            input.style.display = 'none';
            
            // Create a new FileList with the file
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(item.file);
            input.files = dataTransfer.files;
            
            form.appendChild(input);
            
            // Also store duration in a hidden input
            const durationInput = document.createElement('input');
            durationInput.type = 'hidden';
            durationInput.name = `duration${index + 1}`;
            durationInput.value = item.duration;
            form.appendChild(durationInput);
        });
    }

    getFiles() {
        return this.files;
    }

    clear() {
        this.files = [];
        this.updatePreview();
        this.updateHiddenInputs();
    }
}

// Export for use
window.DragDropManager = DragDropManager;

