// Preview and Audio Preview Handler

class PreviewManager {
    constructor() {
        this.audioPreview = null;
        this.init();
    }

    init() {
        // Audio preview button handler
        const previewBtn = document.getElementById('preview-audio-btn');
        if (previewBtn) {
            previewBtn.addEventListener('click', () => {
                this.previewAudio();
            });
        }
    }

    async previewAudio() {
        const textInput = document.getElementById('textInput');
        const voiceSelect = document.getElementById('voice-select');
        const speedInput = document.getElementById('voice-speed');
        
        if (!textInput || !textInput.value.trim()) {
            if (window.notifications) {
                window.notifications.warning('Please enter some text first.');
            }
            return;
        }

        const text = textInput.value;
        const voiceId = voiceSelect ? voiceSelect.value : 'pNInz6obpgDQGcFmaJgB';
        const speed = speedInput ? parseFloat(speedInput.value) : 1.0;

        // Show loading
        const previewBtn = document.getElementById('preview-audio-btn');
        if (previewBtn) {
            previewBtn.disabled = true;
            previewBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        }

        try {
            const response = await fetch('/api/preview-audio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    voice_id: voiceId,
                    speed: speed
                })
            });

            if (!response.ok) {
                throw new Error('Failed to generate preview');
            }

            const blob = await response.blob();
            const audioUrl = URL.createObjectURL(blob);
            
            // Stop previous preview if playing
            if (this.audioPreview) {
                this.audioPreview.pause();
                this.audioPreview = null;
            }

            // Create audio element and play
            this.audioPreview = new Audio(audioUrl);
            this.audioPreview.play();
            
            if (window.notifications) {
                window.notifications.success('Playing audio preview...');
            }

            // Clean up when done
            this.audioPreview.onended = () => {
                URL.revokeObjectURL(audioUrl);
                this.audioPreview = null;
            };

        } catch (error) {
            console.error('Preview error:', error);
            if (window.notifications) {
                window.notifications.error('Failed to generate audio preview. Please try again.');
            }
        } finally {
            if (previewBtn) {
                previewBtn.disabled = false;
                previewBtn.innerHTML = '<i class="fas fa-volume-up"></i> Preview Voice';
            }
        }
    }

    stopPreview() {
        if (this.audioPreview) {
            this.audioPreview.pause();
            this.audioPreview = null;
        }
    }
}

// Initialize preview manager
const previewManager = new PreviewManager();
window.previewManager = previewManager;

