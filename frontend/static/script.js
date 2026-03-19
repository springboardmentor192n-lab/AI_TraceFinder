/* ==========================================================================
   AI TraceFinder - Frontend JavaScript Application
   Advanced Image Forensics & Scanner Identification
   ========================================================================== */

class AITraceFinder {
    constructor() {
        this.apiBaseUrl = '/api';
        this.currentAnalysis = null;
        this.selectedFiles = [];
        this.maxFiles = 10;
        this.maxFileSize = 50 * 1024 * 1024; // 50MB
        this.validExtensions = ['jpg', 'jpeg', 'png', 'tif', 'tiff', 'bmp'];
        this.init();
    }

    init() {
        console.log('%c🔬 AI TraceFinder Initialized', 'color: #2563eb; font-weight: bold; font-size: 14px;');
        this.setupEventListeners();
        this.setupNewEventListeners();
        this.checkApiHealth();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target));
        });

        // Upload areas
        this.setupUploadArea('uploadArea', 'imageInput', 'single');
        this.setupUploadArea('batchUploadArea', 'batchImageInput', 'batch');

        // Analyze buttons
        const analyzeBtn = document.getElementById('analyzeBtn');
        const batchAnalyzeBtn = document.getElementById('batchAnalyzeBtn');
        
        if (analyzeBtn) analyzeBtn.addEventListener('click', () => this.analyzeSingleImage());
        if (batchAnalyzeBtn) batchAnalyzeBtn.addEventListener('click', () => this.analyzeBatchImages());

        // Result buttons
        const downloadBtn = document.getElementById('downloadResultsBtn');
        const newAnalysisBtn = document.getElementById('newAnalysisBtn');
        const newBatchBtn = document.getElementById('newBatchAnalysisBtn');
        
        if (downloadBtn) downloadBtn.addEventListener('click', () => this.downloadResults());
        if (newAnalysisBtn) newAnalysisBtn.addEventListener('click', () => this.resetAnalysis());
        if (newBatchBtn) newBatchBtn.addEventListener('click', () => this.resetBatchAnalysis());

        // API Documentation
        const apiDocsBtn = document.getElementById('apiDocsBtn');
        if (apiDocsBtn) apiDocsBtn.addEventListener('click', () => this.showApiDocs());

        // Modal close
        const modal = document.getElementById('apiModal');
        if (modal) {
            const closeBtn = modal.querySelector('.modal-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => { modal.style.display = 'none'; });
            }
            
            window.addEventListener('click', (e) => {
                if (e.target === modal) modal.style.display = 'none';
            });
        }

        // Toast close buttons
        document.querySelectorAll('.toast-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.target.closest('.toast').style.display = 'none';
            });
        });
    }

    setupUploadArea(areaId, inputId, type) {
        const area = document.getElementById(areaId);
        const input = document.getElementById(inputId);

        if (!area || !input) return;

        area.addEventListener('click', () => input.click());

        ['dragover', 'dragenter'].forEach(eventName => {
            area.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                area.classList.add('dragover');
            });
        });

        area.addEventListener('dragleave', (e) => {
            if (e.target === area) {
                area.classList.remove('dragover');
            }
        });

        area.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            area.classList.remove('dragover');
            
            const files = Array.from(e.dataTransfer.files);
            this.handleFileSelection(files, type);
        });

        input.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            this.handleFileSelection(files, type);
        });
    }

    handleFileSelection(files, type) {
        const validFiles = files.filter(f => this.isValidImageFile(f));
        
        if (validFiles.length === 0) {
            this.showToast('No valid image files selected', 'error');
            return;
        }

        if (type === 'single') {
            if (validFiles.length > 1) {
                this.showToast('Please select only one image for single analysis', 'warning');
                this.handleSingleFile(validFiles[0]);
            } else {
                this.handleSingleFile(validFiles[0]);
            }
        } else {
            if (validFiles.length > this.maxFiles) {
                this.showToast(`Maximum ${this.maxFiles} files allowed`, 'warning');
                this.handleMultipleFiles(validFiles.slice(0, this.maxFiles));
            } else {
                this.handleMultipleFiles(validFiles);
            }
        }
    }

    isValidImageFile(file) {
        const ext = file.name.split('.').pop().toLowerCase();
        
        if (!this.validExtensions.includes(ext)) {
            return false;
        }
        
        if (file.size > this.maxFileSize) {
            this.showToast(`File "${file.name}" exceeds 50MB limit`, 'error');
            return false;
        }
        
        return true;
    }

    handleSingleFile(file) {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            const preview = document.getElementById('previewImage');
            const fileName = document.getElementById('fileName');
            const fileSize = document.getElementById('fileSize');
            
            if (preview) preview.src = e.target.result;
            if (fileName) fileName.textContent = file.name;
            if (fileSize) fileSize.textContent = this.formatFileSize(file.size);
            
            const uploadArea = document.getElementById('uploadArea');
            const previewContainer = document.getElementById('previewContainer');
            const analyzeBtn = document.getElementById('analyzeBtn');
            
            if (uploadArea) uploadArea.style.display = 'none';
            if (previewContainer) previewContainer.style.display = 'block';
            if (analyzeBtn) analyzeBtn.style.display = 'inline-flex';
            
            this.selectedFiles = [file];
        };
        
        reader.onerror = () => {
            this.showToast('Failed to read file', 'error');
        };
        
        reader.readAsDataURL(file);
    }

    handleMultipleFiles(files) {
        this.selectedFiles = files;
        const filesList = document.getElementById('filesList');
        
        if (filesList) {
            filesList.innerHTML = this.selectedFiles
                .map(f => `<li>📄 ${f.name} <span style="color: var(--text-muted);">(${this.formatFileSize(f.size)})</span></li>`)
                .join('');
        }
        
        const batchUploadArea = document.getElementById('batchUploadArea');
        const batchFileList = document.getElementById('batchFileList');
        const batchAnalyzeBtn = document.getElementById('batchAnalyzeBtn');
        
        if (batchUploadArea) batchUploadArea.style.display = 'none';
        if (batchFileList) batchFileList.style.display = 'block';
        if (batchAnalyzeBtn) batchAnalyzeBtn.style.display = 'inline-flex';
    }

    async analyzeSingleImage() {
        if (this.selectedFiles.length === 0) {
            this.showToast('No file selected', 'error');
            return;
        }

        const file = this.selectedFiles[0];
        await this.performAnalysis(file);
    }

    async analyzeBatchImages() {
        if (this.selectedFiles.length === 0) {
            this.showToast('No files selected', 'error');
            return;
        }

        await this.performBatchAnalysis();
    }

    async performAnalysis(file) {
        const formData = new FormData();
        formData.append('image', file);

        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.classList.add('loading');
            analyzeBtn.disabled = true;
        }

        this.showToast('🔍 Analyzing image...', 'info');

        try {
            const response = await fetch(`${this.apiBaseUrl}/analyze`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.currentAnalysis = result.data;
                this.displayResults(result.data);
                this.showToast('✓ Analysis complete!', 'success');
            } else {
                this.showToast(`❌ ${result.error || 'Analysis failed'}`, 'error');
            }
        } catch (error) {
            this.showToast(`❌ Error: ${error.message}`, 'error');
            console.error('Analysis error:', error);
        } finally {
            if (analyzeBtn) {
                analyzeBtn.classList.remove('loading');
                analyzeBtn.disabled = false;
            }
        }
    }

    async performBatchAnalysis() {
        const formData = new FormData();
        this.selectedFiles.forEach(file => {
            formData.append('images', file);
        });

        const batchBtn = document.getElementById('batchAnalyzeBtn');
        if (batchBtn) {
            batchBtn.classList.add('loading');
            batchBtn.disabled = true;
        }

        this.showToast(`🔍 Analyzing ${this.selectedFiles.length} images...`, 'info');

        try {
            const response = await fetch(`${this.apiBaseUrl}/batch-analyze`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.displayBatchResults(result);
                this.showToast(`✓ Analyzed ${result.analyzed}/${result.total} images!`, 'success');
            } else {
                this.showToast(`❌ ${result.error || 'Batch analysis failed'}`, 'error');
            }
        } catch (error) {
            this.showToast(`❌ Error: ${error.message}`, 'error');
            console.error('Batch analysis error:', error);
        } finally {
            if (batchBtn) {
                batchBtn.classList.remove('loading');
                batchBtn.disabled = false;
            }
        }
    }

    displayResults(data) {
        // Hide batch results
        const batchContainer = document.getElementById('batchResultsContainer');
        if (batchContainer) batchContainer.style.display = 'none';
        
        const noResults = document.getElementById('noResultsMessage');
        if (noResults) noResults.style.display = 'none';
        
        const mainCard = document.getElementById('mainResultCard');
        if (mainCard) mainCard.style.display = 'block';

        // Scanner ID
        const scannerId = document.getElementById('scannerId');
        if (scannerId) scannerId.textContent = data.scanner_id;

        // Confidence bar with animation
        const confidence = Math.round(data.confidence * 100);
        const confidenceFill = document.getElementById('confidenceFill');
        const confidenceText = document.getElementById('confidenceText');
        
        if (confidenceFill) {
            confidenceFill.style.width = '0%';
            setTimeout(() => {
                confidenceFill.style.width = confidence + '%';
            }, 100);
        }
        if (confidenceText) confidenceText.textContent = confidence + '%';

        // Image Info
        if (data.image_info) {
            this.updateElementText('imageDim', `${data.image_info.shape?.[0] || '?'} × ${data.image_info.shape?.[1] || '?'}`);
            this.updateElementText('imageDataType', data.image_info.dtype || 'N/A');
            if (data.image_info.min_val !== undefined) this.updateElementText('imageMinVal', parseFloat(data.image_info.min_val).toFixed(4));
            if (data.image_info.max_val !== undefined) this.updateElementText('imageMaxVal', parseFloat(data.image_info.max_val).toFixed(4));
        }

        // FFT Analysis
        if (data.fft_analysis) {
            const fft = data.fft_analysis;
            if (fft.mean_magnitude !== undefined) this.updateElementText('fftMean', parseFloat(fft.mean_magnitude).toFixed(4));
            if (fft.max_magnitude !== undefined) this.updateElementText('fftMax', parseFloat(fft.max_magnitude).toFixed(4));
            if (fft.peak_frequency_ratio !== undefined) this.updateElementText('fftPeakRatio', parseFloat(fft.peak_frequency_ratio).toFixed(4));
            if (fft.energy_concentration !== undefined) this.updateElementText('fftEnergy', (parseFloat(fft.energy_concentration) * 100).toFixed(2) + '%');
        }

        // Texture Metrics
        if (data.texture_metrics) {
            const texture = data.texture_metrics;
            if (texture.mean_texture !== undefined) this.updateElementText('textureMean', parseFloat(texture.mean_texture).toFixed(4));
            if (texture.texture_std !== undefined) this.updateElementText('textureStd', parseFloat(texture.texture_std).toFixed(4));
            if (texture.edge_strength !== undefined) this.updateElementText('edgeStrength', parseFloat(texture.edge_strength).toFixed(4));
        }

        // Noise Level (top-level field)
        if (data.noise_pattern_strength !== undefined) {
            this.updateElementText('noiseLevel', parseFloat(data.noise_pattern_strength).toFixed(4));
        }

        // Forensic Indicators
        if (data.forensic_indicators) {
            const forensic = data.forensic_indicators;
            this.updateElementText('compressionArtifacts', forensic.compression_artifacts ? '✓ Detected' : '✗ None');
            this.updateElementText('unusualPatterns', forensic.unusual_patterns ? '✓ Detected' : '✗ None');
            this.updateElementText('tampering', forensic.potential_tampering ? '⚠ Possible' : '✓ Clean');
            this.updateElementText('channelMismatch', forensic.color_channel_mismatch ? '⚠ Yes' : '✓ No');
        }

        // Recommendations
        const recommendationsList = document.getElementById('recommendations');
        if (recommendationsList && data.recommendations) {
            recommendationsList.innerHTML = data.recommendations
                .map(rec => `<li>${rec}</li>`)
                .join('');
        }

        // Scroll to results
        const resultsSection = document.getElementById('results');
        if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    displayBatchResults(data) {
        const mainCard = document.getElementById('mainResultCard');
        if (mainCard) mainCard.style.display = 'none';
        
        const noResults = document.getElementById('noResultsMessage');
        if (noResults) noResults.style.display = 'none';
        
        const batchContainer = document.getElementById('batchResultsContainer');
        if (batchContainer) batchContainer.style.display = 'block';

        // Summary stats
        this.updateElementText('totalAnalyzed', data.total);
        this.updateElementText('totalSuccessful', data.analyzed);
        this.updateElementText('totalFailed', data.total - data.analyzed);

        // Results table
        const tableBody = document.getElementById('batchResultsBody');
        if (tableBody && data.results) {
            tableBody.innerHTML = data.results.map(result => `
                <tr>
                    <td>${this.escapeHtml(result.filename)}</td>
                    <td>
                        <span class="badge ${result.success ? 'success' : 'error'}">
                            ${result.success ? '✓ Success' : '✗ Failed'}
                        </span>
                    </td>
                    <td>${result.scanner_id}</td>
                    <td>${(result.confidence * 100).toFixed(1)}%</td>
                </tr>
            `).join('');
        }

        const resultsSection = document.getElementById('results');
        if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    downloadResults() {
        if (!this.currentAnalysis) {
            this.showToast('No results to download', 'warning');
            return;
        }

        const report = {
            timestamp: new Date().toISOString(),
            scanner_id: this.currentAnalysis.scanner_id,
            confidence: this.currentAnalysis.confidence,
            image_info: this.currentAnalysis.image_info,
            fft_analysis: this.currentAnalysis.fft_analysis,
            texture_metrics: this.currentAnalysis.texture_metrics,
            forensic_indicators: this.currentAnalysis.forensic_indicators,
            recommendations: this.currentAnalysis.recommendations,
            feature_vector_size: this.currentAnalysis.feature_vector ? this.currentAnalysis.feature_vector.length : 0
        };

        const dataStr = JSON.stringify(report, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `forensics_report_${new Date().getTime()}.json`;
        link.click();
        URL.revokeObjectURL(url);

        this.showToast('✓ Report downloaded', 'success');
    }

    resetAnalysis() {
        this.selectedFiles = [];
        this.currentAnalysis = null;

        const uploadArea = document.getElementById('uploadArea');
        const previewContainer = document.getElementById('previewContainer');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const mainCard = document.getElementById('mainResultCard');
        const imageInput = document.getElementById('imageInput');

        if (uploadArea) uploadArea.style.display = 'block';
        if (previewContainer) previewContainer.style.display = 'none';
        if (analyzeBtn) analyzeBtn.style.display = 'none';
        if (mainCard) mainCard.style.display = 'none';
        if (imageInput) imageInput.value = '';

        this.showToast('Ready for new analysis', 'info');
    }

    resetBatchAnalysis() {
        this.selectedFiles = [];

        const batchUploadArea = document.getElementById('batchUploadArea');
        const batchFileList = document.getElementById('batchFileList');
        const batchBtn = document.getElementById('batchAnalyzeBtn');
        const batchResults = document.getElementById('batchResultsContainer');
        const batchInput = document.getElementById('batchImageInput');

        if (batchUploadArea) batchUploadArea.style.display = 'block';
        if (batchFileList) batchFileList.style.display = 'none';
        if (batchBtn) batchBtn.style.display = 'none';
        if (batchResults) batchResults.style.display = 'none';
        if (batchInput) batchInput.value = '';

        this.showToast('Ready for new batch analysis', 'info');
    }

    switchTab(button) {
        // Deactivate all tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        // Activate clicked tab
        button.classList.add('active');
        const tabId = button.getAttribute('data-tab');
        const tabContent = document.getElementById(tabId);
        if (tabContent) tabContent.classList.add('active');
    }

    async checkApiHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const data = await response.json();
            console.log('%c✓ API Health Check', 'color: #10b981; font-weight: bold;', data.message);
        } catch (error) {
            console.warn('%c⚠ API Health Check Failed', 'color: #f59e0b; font-weight: bold;', error.message);
            this.showToast('Backend connection issue - features may not work', 'warning');
        }
    }

    async showApiDocs() {
        try {
            // Open the beautiful HTML API documentation in a new tab
            window.open(`${this.apiBaseUrl}/api/docs-html`, 'API_Documentation', 
                'width=1200,height=800,scrollbars=yes,resizable=yes');
        } catch (error) {
            this.showToast('Failed to load API documentation', 'error');
            console.error('API docs error:', error);
        }
    }

    showToast(message, type = 'info') {
        const container = document.querySelector('.toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <span>${message}</span>
            <button class="toast-close">✕</button>
        `;
        
        container.appendChild(toast);

        const closeBtn = toast.querySelector('.toast-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 300);
            });
        }

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    }

    updateElementText(elementId, text) {
        const element = document.getElementById(elementId);
        if (element) element.textContent = text;
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    // ==================== NEW SECTION NAVIGATION ====================
    
    switchSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('section[id]').forEach(section => {
            section.style.display = 'none';
        });
        
        // Show selected section
        const section = document.getElementById(sectionId);
        if (section) {
            section.style.display = 'block';
            
            // Load content based on section
            if (sectionId === 'history') this.loadAnalysisHistory();
            else if (sectionId === 'about') this.loadAboutStats();
            else if (sectionId === 'help') this.loadHelpSection();
        }
        
        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + sectionId) {
                link.classList.add('active');
            }
        });
    }

    // ==================== HISTORY MANAGEMENT ====================
    
    async loadAnalysisHistory() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/history`);
            const data = await response.json();
            
            if (data.success) {
                this.displayAnalysisHistory(data.history);
            }
        } catch (error) {
            this.showToast('Failed to load history', 'error');
        }
    }

    displayAnalysisHistory(history) {
        const tbody = document.getElementById('historyTableBody');
        if (!tbody) return;
        
        if (history.length === 0) {
            tbody.innerHTML = '<tr class="empty-row"><td colspan="6">No analysis history yet</td></tr>';
            return;
        }
        
        tbody.innerHTML = history.map((item, idx) => `
            <tr>
                <td>${new Date(item.timestamp).toLocaleString()}</td>
                <td>${this.escapeHtml(item.filename)}</td>
                <td>${item.scanner_id}</td>
                <td><span class="confidence-badge" style="background-color: ${this.getConfidenceColor(item.confidence)}">${(item.confidence * 100).toFixed(1)}%</span></td>
                <td><span class="status-badge success">Success</span></td>
                <td><button onclick="app.compareFromHistory(${idx})" class="btn-small">Compare</button></td>
            </tr>
        `).join('');
    }

    getConfidenceColor(confidence) {
        if (confidence >= 0.8) return '#00d4ff';
        if (confidence >= 0.6) return '#ffa500';
        return '#e94560';
    }

    async clearAnalysisHistory() {
        if (confirm('Are you sure? This cannot be undone.')) {
            try {
                await fetch(`${this.apiBaseUrl}/history`, { method: 'DELETE' });
                this.loadAnalysisHistory();
                this.showToast('History cleared', 'success');
            } catch (error) {
                this.showToast('Failed to clear history', 'error');
            }
        }
    }

    // ==================== COMPARISON ====================
    
    async startComparison() {
        try {
            // Load history
            const response = await fetch(`${this.apiBaseUrl}/history`);
            const data = await response.json();
            
            if (!data.success || !data.history || data.history.length < 2) {
                this.showToast('Need at least 2 analyses in history to compare', 'warning');
                return;
            }
            
            // Show selection modal
            this.showComparisonSelectionModal(data.history);
        } catch (error) {
            this.showToast('Failed to load history for comparison', 'error');
            console.error('Comparison error:', error);
        }
    }

    showComparisonSelectionModal(history) {
        // Create modal
        const modal = document.createElement('div');
        modal.className = 'comparison-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        `;
        
        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            background: #1e293b;
            border: 1px solid rgba(100, 116, 139, 0.3);
            border-radius: 12px;
            padding: 30px;
            max-width: 500px;
            width: 90%;
            max-height: 70vh;
            overflow-y: auto;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
        `;
        
        const title = document.createElement('h3');
        title.textContent = 'Select Images to Compare';
        title.style.cssText = 'color: #3b82f6; margin-bottom: 20px; font-size: 1.3em;';
        
        const selectForm = document.createElement('div');
        selectForm.style.cssText = 'display: flex; flex-direction: column; gap: 15px; margin-bottom: 20px;';
        
        // Add checkboxes for each history item
        history.forEach((item, idx) => {
            const label = document.createElement('label');
            label.style.cssText = `
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 12px;
                background: rgba(30, 41, 59, 0.6);
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
                color: #e2e8f0;
            `;
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = idx;
            checkbox.style.cssText = 'width: 18px; height: 18px; cursor: pointer;';
            
            const info = document.createElement('span');
            info.innerHTML = `
                <strong>${this.escapeHtml(item.filename)}</strong><br>
                <small style="color: #94a3b8;">
                    ${item.scanner_id} • ${(item.confidence * 100).toFixed(1)}% • 
                    ${new Date(item.timestamp).toLocaleString()}
                </small>
            `;
            info.style.flex = '1';
            
            label.appendChild(checkbox);
            label.appendChild(info);
            
            label.addEventListener('mouseenter', () => {
                label.style.background = 'rgba(59, 130, 246, 0.1)';
            });
            label.addEventListener('mouseleave', () => {
                label.style.background = 'rgba(30, 41, 59, 0.6)';
            });
            
            selectForm.appendChild(label);
        });
        
        // Buttons
        const buttonContainer = document.createElement('div');
        buttonContainer.style.cssText = 'display: flex; gap: 10px; justify-content: flex-end;';
        
        const cancelBtn = document.createElement('button');
        cancelBtn.textContent = 'Cancel';
        cancelBtn.style.cssText = `
            padding: 10px 20px;
            background: #475569;
            color: #e2e8f0;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.95em;
        `;
        
        const compareBtn = document.createElement('button');
        compareBtn.textContent = 'Compare Selected';
        compareBtn.style.cssText = `
            padding: 10px 20px;
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.95em;
            font-weight: 600;
        `;
        
        cancelBtn.addEventListener('click', () => modal.remove());
        compareBtn.addEventListener('click', () => {
            const selected = Array.from(selectForm.querySelectorAll('input[type="checkbox"]:checked'))
                .map(cb => parseInt(cb.value));
            
            if (selected.length < 2) {
                this.showToast('Please select at least 2 images to compare', 'warning');
                return;
            }
            
            modal.remove();
            this.performComparison(selected);
        });
        
        buttonContainer.appendChild(cancelBtn);
        buttonContainer.appendChild(compareBtn);
        
        modalContent.appendChild(title);
        modalContent.appendChild(selectForm);
        modalContent.appendChild(buttonContainer);
        modal.appendChild(modalContent);
        
        document.body.appendChild(modal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    }

    async performComparison(indices) {
        const btn = document.getElementById('selectCompareImagesBtn');
        if (btn) {
            btn.classList.add('loading');
            btn.disabled = true;
        }
        
        this.showToast('⚙️ Comparing analyses...', 'info');
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/compare`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ indices: indices })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayComparison(result.comparisons, result.summary);
                this.showToast('✓ Comparison complete!', 'success');
            } else {
                this.showToast(`❌ ${result.error || 'Comparison failed'}`, 'error');
            }
        } catch (error) {
            this.showToast(`❌ Error: ${error.message}`, 'error');
            console.error('Comparison error:', error);
        } finally {
            if (btn) {
                btn.classList.remove('loading');
                btn.disabled = false;
            }
        }
    }

    displayComparison(comparisons, summary) {
        const resultsDiv = document.getElementById('comparisonResults');
        const noMessageDiv = document.getElementById('noComparisonMessage');
        const gridDiv = document.getElementById('comparisonGrid');
        const summaryDiv = document.getElementById('comparisonSummaryContent');
        
        if (noMessageDiv) noMessageDiv.style.display = 'none';
        if (resultsDiv) resultsDiv.style.display = 'block';
        
        // Display comparison cards
        if (gridDiv && comparisons) {
            gridDiv.innerHTML = comparisons.map((item, idx) => `
                <div class="comparison-card">
                    <div class="card-header">
                        <span class="card-index">Analysis ${idx + 1}</span>
                        <span class="card-date">${new Date(item.timestamp).toLocaleDateString()}</span>
                    </div>
                    <div class="card-filename">${this.escapeHtml(item.filename)}</div>
                    <div class="card-scanner">
                        <strong>${item.scanner_id}</strong>
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${item.confidence * 100}%"></div>
                    </div>
                    <div class="card-confidence">${(item.confidence * 100).toFixed(1)}% Confidence</div>
                </div>
            `).join('');
        }
        
        // Display summary
        if (summaryDiv && summary) {
            summaryDiv.innerHTML = `
                <div class="summary-item">
                    <span class="summary-label">Total Compared:</span>
                    <span class="summary-value">${summary.total_compared}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Average Confidence:</span>
                    <span class="summary-value">${(summary.average_confidence * 100).toFixed(1)}%</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Confidence Range:</span>
                    <span class="summary-value">${summary.confidence_range}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Same Scanner:</span>
                    <span class="summary-value">${summary.same_scanner ? '✓ Yes' : '✗ No'}</span>
                </div>
                <div class="summary-items-grid">
                    ${summary.scanner_models.map((scanner, idx) => `
                        <div class="model-badge">Model ${idx + 1}: <strong>${scanner}</strong></div>
                    `).join('')}
                </div>
            `;
        }
        
        // Scroll to comparison section
        const compareSection = document.getElementById('compare');
        if (compareSection) {
            compareSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    compareFromHistory(index) {
        // Navigate to compare section and show toast
        this.switchSection('compare');
        this.startComparison();
    }

    // ==================== ABOUT SECTION ====================
    
    loadAboutStats() {
        // Fetch and display statistics
        fetch(`${this.apiBaseUrl}/statistics`)
            .then(r => r.json())
            .then(data => {
                if (data.stats) {
                    this.updateElementText('totalAnalysisCount', (data.stats.total_analyzed || 0).toString());
                    this.updateElementText('averageConfidenceStats', (data.stats.average_confidence || 0).toFixed(1) + '%');
                    this.updateElementText('successRateStats', (data.stats.success_rate || 0).toFixed(1) + '%');
                }
            })
            .catch(err => console.error('Failed to load stats:', err));
    }

    // ==================== HELP SECTION ====================
    
    loadHelpSection() {
        // Help section is pre-loaded in HTML
        const helpApiBtn = document.getElementById('helpApiDocsBtn');
        if (helpApiBtn) {
            helpApiBtn.addEventListener('click', () => this.showApiDocs());
        }
    }

    // ==================== SETUP NEW EVENT LISTENERS ====================

    setupNewEventListeners() {
        // Navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                if (href && href.startsWith('#')) {
                    e.preventDefault();
                    const sectionId = href.substring(1);
                    this.switchSection(sectionId);
                }
            });
        });

        // History controls
        const searchInput = document.getElementById('historySearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', () => this.filterHistory());
        }

        const sortBy = document.getElementById('historySortBy');
        if (sortBy) {
            sortBy.addEventListener('change', () => this.sortHistory());
        }

        const clearBtn = document.getElementById('clearHistoryBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearAnalysisHistory());
        }

        // Comparison button
        const compareBtn = document.getElementById('selectCompareImagesBtn');
        if (compareBtn) {
            compareBtn.addEventListener('click', () => this.startComparison());
        }
    }

    filterHistory() {
        // Filter history based on search input and scanner filter
        const searchTerm = (document.getElementById('historySearchInput')?.value || '').toLowerCase();
        const scannerFilter = document.getElementById('historyScannerFilter')?.value || '';
        
        const rows = document.querySelectorAll('#historyTableBody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const scanner = row.querySelector('td:nth-child(3)')?.textContent || '';
            
            const matchSearch = text.includes(searchTerm);
            const matchScanner = !scannerFilter || scanner === scannerFilter;
            
            row.style.display = (matchSearch && matchScanner) ? '' : 'none';
        });
    }

    sortHistory() {
        // Sorting will be handled by reloading history with sort parameter
        this.loadAnalysisHistory();
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AITraceFinder();
});
