// Main Create Page JavaScript

let dragDropManager;
let progressTracker;

class ProgressTracker {
    constructor() {
        this.overlay = null;
        this.init();
    }

    init() {
        // Create progress overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'progress-overlay';
        this.overlay.style.display = 'none';
        this.overlay.innerHTML = `
            <div class="progress-container">
                <div class="spinner"></div>
                <h3>Creating Your Reel...</h3>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" id="progressFill" style="width: 0%"></div>
                </div>
                <p class="progress-text" id="progressText">Initializing...</p>
                <button class="btn-cancel-progress" onclick="progressTracker.cancel()">Cancel</button>
            </div>
        `;
        document.body.appendChild(this.overlay);
    }

    show() {
        this.overlay.style.display = 'flex';
        this.updateProgress(0, 'Starting...');
    }

    hide() {
        this.overlay.style.display = 'none';
    }

    updateProgress(percentage, text) {
        const fill = document.getElementById('progressFill');
        const textEl = document.getElementById('progressText');
        
        if (fill) {
            fill.style.width = percentage + '%';
        }
        if (textEl) {
            textEl.textContent = text;
        }
    }

    cancel() {
        // TODO: Implement cancel functionality
        if (window.notifications) {
            window.notifications.info('Cancellation requested. Please wait...');
        }
    }
}

// Character counter and word count
function initCharacterCounter() {
    const textInput = document.getElementById('textInput');
    const charCounter = document.getElementById('charCount');
    const wordCounter = document.getElementById('wordCount');
    
    if (textInput && charCounter) {
        textInput.addEventListener('input', () => {
            const text = textInput.value;
            const count = text.length;
            const words = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;
            
            charCounter.textContent = count;
            if (wordCounter) {
                wordCounter.textContent = words;
            }
            
            // Change color based on count
            if (count > 450) {
                charCounter.style.color = '#ff0000';
            } else if (count > 400) {
                charCounter.style.color = '#ff8800';
            } else {
                charCounter.style.color = '#666';
            }
        });
    }
}

// Audio preview handler
function initAudioPreview() {
    const previewBtn = document.getElementById('previewAudioBtn');
    const textInput = document.getElementById('textInput');
    const voiceSelect = document.getElementById('voiceSelect');
    
    if (previewBtn && textInput) {
        previewBtn.addEventListener('click', async () => {
            const text = textInput.value.trim();
            if (!text) {
                if (window.notifications) {
                    window.notifications.warning('Please enter some text first.');
                }
                return;
            }
            
            const voiceId = voiceSelect ? voiceSelect.value : 'pNInz6obpgDQGcFmaJgB';
            
            previewBtn.disabled = true;
            previewBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            
            try {
                const response = await fetch('/api/preview-audio', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        text: text,
                        voice_id: voiceId
                    })
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const audioUrl = URL.createObjectURL(blob);
                    const audio = new Audio(audioUrl);
                    audio.play();
                    
                    audio.onended = () => {
                        URL.revokeObjectURL(audioUrl);
                    };
                    
                    if (window.notifications) {
                        window.notifications.success('Playing audio preview...');
                    }
                } else {
                    throw new Error('Failed to generate preview');
                }
            } catch (error) {
                console.error('Preview error:', error);
                if (window.notifications) {
                    window.notifications.error('Failed to generate audio preview. Please try again.');
                }
            } finally {
                previewBtn.disabled = false;
                previewBtn.innerHTML = '<i class="fas fa-volume-up"></i> Preview Voice';
            }
        });
    }
}

// Form submission handler
function initFormSubmission() {
    const form = document.querySelector('form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Validate form
        const textInput = document.getElementById('textInput');
        if (!textInput || !textInput.value.trim()) {
            if (window.notifications) {
                window.notifications.error('Please enter text for the voiceover.');
            }
            return;
        }

        if (!dragDropManager || dragDropManager.getFiles().length === 0) {
            if (window.notifications) {
                window.notifications.error('Please upload at least one image.');
            }
            return;
        }

        // Show progress
        if (progressTracker) {
            progressTracker.show();
            progressTracker.updateProgress(10, 'Uploading files...');
        }

        // Create FormData
        const formData = new FormData(form);
        
        // Add files from drag drop manager
        dragDropManager.getFiles().forEach((item, index) => {
            formData.append(`file${index + 1}`, item.file);
            formData.append(`duration${index + 1}`, item.duration);
        });
        
        // Ensure all form fields are included
        const voiceSelect = document.getElementById('voiceSelect');
        const voiceSpeed = document.getElementById('voiceSpeed');
        const musicSelect = document.getElementById('musicSelect');
        const musicVolume = document.getElementById('musicVolume');
        const overlayText = document.getElementById('overlayText');
        const overlayPosition = document.getElementById('overlayPosition');
        const overlayColor = document.getElementById('overlayColor');
        const overlayFont = document.getElementById('overlayFont');
        const overlaySize = document.getElementById('overlaySize');
        const aspectRatio = document.getElementById('aspectRatio');
        const quality = document.getElementById('quality');
        const transition = document.getElementById('transition');
        const customMusicInput = document.getElementById('customMusicInput');
        
        // Add advanced options if they exist
        if (voiceSelect) formData.set('voice_id', voiceSelect.value);
        if (voiceSpeed) formData.set('voice_speed', voiceSpeed.value);
        if (musicSelect) formData.set('music_file', musicSelect.value);
        if (musicVolume) formData.set('music_volume', musicVolume.value);
        if (overlayText) formData.set('overlay_text', overlayText.value);
        if (overlayPosition) formData.set('overlay_position', overlayPosition.value);
        if (overlayColor) formData.set('overlay_color', overlayColor.value);
        if (overlayFont) formData.set('overlay_font', overlayFont.value);
        if (overlaySize) formData.set('overlay_size', overlaySize.value);
        if (aspectRatio) formData.set('aspect_ratio', aspectRatio.value);
        if (quality) formData.set('quality', quality.value);
        if (transition) formData.set('transition', transition.value);
        if (customMusicInput && customMusicInput.files.length > 0) {
            formData.append('custom_music', customMusicInput.files[0]);
        }

        // Simulate progress updates
        const progressInterval = setInterval(() => {
            if (progressTracker) {
                const currentProgress = parseInt(progressTracker.overlay.querySelector('#progressFill').style.width) || 10;
                if (currentProgress < 90) {
                    progressTracker.updateProgress(
                        currentProgress + 10,
                        currentProgress < 30 ? 'Generating audio...' :
                        currentProgress < 60 ? 'Processing images...' :
                        'Creating video...'
                    );
                }
            }
        }, 1000);

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });

            clearInterval(progressInterval);

            if (response.ok) {
                if (progressTracker) {
                    progressTracker.updateProgress(100, 'Complete!');
                    setTimeout(() => {
                        progressTracker.hide();
                        window.location.reload();
                    }, 500);
                } else {
                    window.location.reload();
                }
            } else {
                throw new Error('Failed to create reel');
            }
        } catch (error) {
            clearInterval(progressInterval);
            if (progressTracker) {
                progressTracker.hide();
            }
            if (window.notifications) {
                window.notifications.error('Failed to create reel. Please try again.');
            }
            console.error('Form submission error:', error);
        }
    });
}

// Advanced options toggle
function initAdvancedOptions() {
    const toggleBtn = document.querySelector('.toggle-advanced');
    const advancedContent = document.querySelector('.advanced-content');
    
    if (toggleBtn && advancedContent) {
        toggleBtn.addEventListener('click', () => {
            advancedContent.classList.toggle('show');
            const icon = toggleBtn.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-chevron-down');
                icon.classList.toggle('fa-chevron-up');
            }
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize drag and drop
    dragDropManager = new DragDropManager('dropZone', 'previewGrid');
    window.dragDropManager = dragDropManager;

    // Initialize progress tracker
    progressTracker = new ProgressTracker();
    window.progressTracker = progressTracker;

    // Initialize character counter
    initCharacterCounter();

    // Initialize audio preview
    initAudioPreview();

    // Initialize form submission
    initFormSubmission();

    // Initialize advanced options
    initAdvancedOptions();

    // Add styles for progress overlay
    const progressStyles = `
        <style>
        .progress-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.95);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        }
        
        .progress-container {
            background: rgba(255, 255, 255, 0.98);
            padding: 3rem;
            border-radius: 20px;
            text-align: center;
            max-width: 500px;
            border: 2px solid rgba(255, 0, 0, 0.3);
        }
        
        .progress-container h3 {
            color: #ff0000;
            margin: 1rem 0;
        }
        
        .progress-text {
            margin-top: 1rem;
            color: #666;
        }
        
        .btn-cancel-progress {
            margin-top: 1.5rem;
            padding: 0.5rem 1.5rem;
            background: #666;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        
        .btn-cancel-progress:hover {
            background: #555;
        }
        </style>
    `;
    document.head.insertAdjacentHTML('beforeend', progressStyles);
});

