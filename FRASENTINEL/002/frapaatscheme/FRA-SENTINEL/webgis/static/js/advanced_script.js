// Advanced FRA Atlas JavaScript
class FRAAtlas {
    constructor() {
        this.map = null;
        this.currentTheme = 'light';
        this.fraLayer = null;
        this.charts = {};
        this.init();
    }

    init() {
        this.initTheme();
        this.initMap();
        this.initTabs();
        this.loadData();
        this.initEventListeners();
        this.startPeriodicUpdates();
    }

    // Theme Management
    initTheme() {
        const savedTheme = localStorage.getItem('fra-theme') || 'light';
        this.setTheme(savedTheme);
    }

    setTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('fra-theme', theme);
        
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.innerHTML = theme === 'dark' ? 
                '☀️ Light Mode' : '🌙 Dark Mode';
        }
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    // Enhanced Map Initialization
    initMap() {
        // Initialize map with enhanced options
        this.map = L.map('map', {
            center: [21.8225, 75.6102],
            zoom: 13,
            zoomControl: false,
            attributionControl: false
        });

        // Add custom zoom control
        L.control.zoom({
            position: 'bottomright'
        }).addTo(this.map);

        // Base layers with enhanced styling
        const baseLayers = {
            "🗺️ Street Map": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }),
            "🛰️ Satellite": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: 'Esri, DigitalGlobe, GeoEye'
            }),
            "🌍 Terrain": L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
                attribution: 'OpenTopoMap'
            })
        };

        // Add default layer
        baseLayers["🗺️ Street Map"].addTo(this.map);

        // Enhanced layer control
        L.control.layers(baseLayers, null, {
            position: 'topright',
            collapsed: false
        }).addTo(this.map);

        // Add scale control
        L.control.scale({
            position: 'bottomleft'
        }).addTo(this.map);

        // Add custom controls
        this.addCustomControls();
    }

    addCustomControls() {
        // Fullscreen control
        const fullscreenControl = L.Control.extend({
            onAdd: function() {
                const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
                container.innerHTML = '⛶';
                container.style.backgroundColor = 'white';
                container.style.width = '30px';
                container.style.height = '30px';
                container.style.cursor = 'pointer';
                container.style.display = 'flex';
                container.style.alignItems = 'center';
                container.style.justifyContent = 'center';
                container.style.fontSize = '16px';
                
                container.onclick = () => {
                    if (this._map.getContainer().requestFullscreen) {
                        this._map.getContainer().requestFullscreen();
                    }
                };
                
                return container;
            }
        });

        new fullscreenControl({position: 'topright'}).addTo(this.map);

        // Home button
        const homeControl = L.Control.extend({
            onAdd: function() {
                const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
                container.innerHTML = '🏠';
                container.style.backgroundColor = 'white';
                container.style.width = '30px';
                container.style.height = '30px';
                container.style.cursor = 'pointer';
                container.style.display = 'flex';
                container.style.alignItems = 'center';
                container.style.justifyContent = 'center';
                container.style.fontSize = '16px';
                
                container.onclick = () => {
                    this._map.setView([21.8225, 75.6102], 13);
                };
                
                return container;
            }
        });

        new homeControl({position: 'topright'}).addTo(this.map);
    }

    // Tab System
    initTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabPanes = document.querySelectorAll('.tab-pane');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const target = button.getAttribute('data-tab');
                
                // Update active button
                tabButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Update active pane
                tabPanes.forEach(pane => pane.classList.remove('active'));
                document.getElementById(target).classList.add('active');
                
                // Initialize charts if needed
                if (target === 'analytics') {
                    this.initCharts();
                }
            });
        });
    }

    // Data Loading with Enhanced Animations
    async loadData() {
        try {
            // Show loading states
            this.showLoadingState();
            
            // Load FRA data
            const fraResponse = await fetch('/fra_data');
            const fraData = await fraResponse.json();
            
            // Load statistics
            const statsResponse = await fetch('/classification_stats');
            const statsData = await statsResponse.json();
            
            // Process and display data
            this.displayFRAData(fraData);
            this.displayStatistics(statsData);
            
            // Hide loading states
            this.hideLoadingState();
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load data. Please refresh the page.');
        }
    }

    showLoadingState() {
        const loadingElements = document.querySelectorAll('.loading');
        loadingElements.forEach(el => {
            el.style.display = 'flex';
        });
    }

    hideLoadingState() {
        const loadingElements = document.querySelectorAll('.loading');
        loadingElements.forEach(el => {
            el.style.display = 'none';
        });
    }

    // Enhanced FRA Data Display
    displayFRAData(data) {
        if (!data.features) return;

        // Custom marker styling
        const customIcon = L.divIcon({
            html: `
                <div style="
                    background: linear-gradient(135deg, #2c5234, #4a7c59);
                    width: 30px;
                    height: 30px;
                    border-radius: 50%;
                    border: 3px solid white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                    box-shadow: 0 4px 15px rgba(44, 82, 52, 0.3);
                    animation: pulse 2s infinite;
                ">
                    🏘️
                </div>
            `,
            className: 'custom-fra-marker',
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });

        this.fraLayer = L.geoJSON(data, {
            pointToLayer: (feature, latlng) => {
                return L.marker(latlng, { icon: customIcon });
            },
            onEachFeature: (feature, layer) => {
                const props = feature.properties;
                
                // Enhanced popup content
                const popupContent = this.createEnhancedPopup(props);
                layer.bindPopup(popupContent, {
                    maxWidth: 300,
                    className: 'custom-popup'
                });
                
                // Enhanced click handling
                layer.on('click', (e) => {
                    this.handleVillageClick(props, e);
                });
                
                // Hover effects
                layer.on('mouseover', () => {
                    layer.setOpacity(0.8);
                });
                
                layer.on('mouseout', () => {
                    layer.setOpacity(1);
                });
            }
        });
        
        this.fraLayer.addTo(this.map);
        this.map.fitBounds(this.fraLayer.getBounds(), { padding: [20, 20] });
        
        // Auto-select first village
        setTimeout(() => {
            if (data.features.length > 0) {
                this.selectVillage(data.features[0].properties);
            }
        }, 1000);
    }

    createEnhancedPopup(props) {
        return `
            <div style="font-family: 'Inter', sans-serif; padding: 10px;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
                    <div style="
                        background: linear-gradient(135deg, #2c5234, #4a7c59);
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-size: 18px;
                    ">🏘️</div>
                    <div>
                        <h4 style="margin: 0; color: #2c5234; font-size: 1.2em;">${props.village}</h4>
                        <p style="margin: 2px 0 0 0; color: #666; font-size: 0.9em;">Forest Rights Village</p>
                    </div>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9em;">
                        <div><strong>Patta Holder:</strong><br>${props.patta_holder}</div>
                        <div><strong>Area:</strong><br>${props.area_hectares} hectares</div>
                        <div><strong>Status:</strong><br><span style="color: green; font-weight: bold;">${props.claim_status}</span></div>
                        <div><strong>Coordinates:</strong><br>${props.latitude.toFixed(4)}, ${props.longitude.toFixed(4)}</div>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 15px;">
                    <button onclick="fraAtlas.generateReport('${props.village}')" style="
                        background: linear-gradient(135deg, #2c5234, #4a7c59);
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 20px;
                        cursor: pointer;
                        font-size: 0.9em;
                        transition: all 0.3s ease;
                    ">📊 View Details</button>
                </div>
            </div>
        `;
    }

    // Enhanced Statistics Display
    displayStatistics(stats) {
        if (!stats) return;

        const container = document.getElementById('land-stats');
        const statLabels = {
            'farmland': { icon: '🌾', name: 'Farmland', color: '#ffeb3b' },
            'forest': { icon: '🌲', name: 'Forest Cover', color: '#4caf50' },
            'water': { icon: '💧', name: 'Water Bodies', color: '#2196f3' },
            'homestead': { icon: '🏠', name: 'Homesteads', color: '#ff5722' }
        };

        let html = '<div class="stats-grid">';
        
        Object.entries(stats).forEach(([key, data]) => {
            if (statLabels[key]) {
                const label = statLabels[key];
                html += `
                    <div class="stat-item modern-stat" data-tooltip="${data.pixels} pixels">
                        <div class="stat-info">
                            <span class="stat-icon">${label.icon}</span>
                            <span class="stat-name">${label.name}</span>
                        </div>
                        <div class="stat-value-container">
                            <span class="stat-value">${data.percentage}%</span>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${data.percentage}%; background-color: ${label.color};">
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
        });
        
        html += '</div>';
        container.innerHTML = html;

        // Animate progress bars
        setTimeout(() => {
            document.querySelectorAll('.progress-fill').forEach(fill => {
                fill.style.width = fill.style.width;
            });
        }, 100);
    }

    // Enhanced Village Selection
    async selectVillage(props) {
        // Update village info
        this.updateVillageInfo(props);
        
        // Load recommendations
        try {
            const response = await fetch(`/dss_recommendation/${props.village}`);
            const data = await response.json();
            this.displayRecommendations(data);
        } catch (error) {
            console.error('Error loading recommendations:', error);
        }
    }

    updateVillageInfo(props) {
        const container = document.getElementById('village-info');
        
        const html = `
            <div class="village-card">
                <div class="village-header">
                    <div class="village-avatar">
                        <span>🏘️</span>
                    </div>
                    <div class="village-details">
                        <h3>${props.village}</h3>
                        <p class="village-subtitle">Forest Rights Village</p>
                    </div>
                </div>
                
                <div class="village-stats">
                    <div class="stat-row">
                        <span class="stat-label">👤 Patta Holder</span>
                        <span class="stat-value">${props.patta_holder}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">📏 Land Area</span>
                        <span class="stat-value">${props.area_hectares} hectares</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">✅ Status</span>
                        <span class="stat-value status-approved">${props.claim_status}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">📍 Location</span>
                        <span class="stat-value">${props.latitude.toFixed(4)}, ${props.longitude.toFixed(4)}</span>
                    </div>
                </div>
                
                <div class="village-actions">
                    <button onclick="fraAtlas.generateReport('${props.village}')" class="action-btn primary">
                        📊 Generate Report
                    </button>
                    <button onclick="fraAtlas.exportData('${props.village}')" class="action-btn secondary">
                        📥 Export Data
                    </button>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }

    // Enhanced Recommendations Display
    displayRecommendations(data) {
        const container = document.getElementById('recommendations');
        
        if (!data.recommendations || data.recommendations.length === 0) {
            container.innerHTML = `
                <div class="no-recommendations">
                    <div class="no-rec-icon">🎯</div>
                    <h4>No Specific Recommendations</h4>
                    <p>All current schemes are optimally distributed for this village.</p>
                </div>
            `;
            return;
        }

        let html = `
            <div class="recommendations-header">
                <h3>🎯 Smart Recommendations</h3>
                <p>AI-powered scheme suggestions based on land use analysis</p>
            </div>
        `;
        
        data.recommendations.forEach((rec, index) => {
            const priorityClass = `priority-${rec.priority.toLowerCase()}`;
            const priorityIcon = rec.priority === 'High' ? '🔥' : rec.priority === 'Medium' ? '⚡' : '📝';
            
            html += `
                <div class="recommendation-item enhanced-rec" style="animation-delay: ${index * 0.1}s;">
                    <div class="rec-header">
                        <div class="rec-title">
                            <span class="rec-icon">${priorityIcon}</span>
                            <span class="scheme-name">${rec.scheme}</span>
                        </div>
                        <span class="priority ${priorityClass}">${rec.priority}</span>
                    </div>
                    
                    <div class="rec-content">
                        <p class="scheme-benefit">💰 ${rec.benefit}</p>
                        <p class="scheme-ministry">🏛️ ${rec.ministry}</p>
                        <div class="scheme-reasons">
                            ${rec.reasons.map(reason => `<span class="reason-tag">✓ ${reason}</span>`).join('')}
                        </div>
                        <div class="eligibility-score">
                            <span>Eligibility Score: </span>
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${rec.eligibility_score}%"></div>
                            </div>
                            <span class="score-value">${rec.eligibility_score.toFixed(1)}/100</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }

    // Event Listeners
    initEventListeners() {
        // Theme toggle
        document.getElementById('theme-toggle')?.addEventListener('click', () => {
            this.toggleTheme();
        });

        // Search functionality
        document.getElementById('village-search')?.addEventListener('input', (e) => {
            this.searchVillages(e.target.value);
        });

        // Export buttons
        document.getElementById('export-pdf')?.addEventListener('click', () => {
            this.exportToPDF();
        });

        document.getElementById('export-excel')?.addEventListener('click', () => {
            this.exportToExcel();
        });
    }

    // Advanced Features
    async generateReport(village) {
        try {
            const response = await fetch(`/generate_report/${village}`);
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${village}_FRA_Report.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Error generating report:', error);
            alert('Error generating report. Please try again.');
        }
    }

    async exportData(village) {
        try {
            const response = await fetch(`/export_data/${village}`);
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${village}_data.xlsx`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Error exporting data:', error);
            alert('Error exporting data. Please try again.');
        }
    }

    // Chart Initialization
    initCharts() {
        if (document.getElementById('land-use-chart')) {
            this.createLandUseChart();
        }
        
        if (document.getElementById('scheme-analysis-chart')) {
            this.createSchemeAnalysisChart();
        }
    }

    createLandUseChart() {
        // Implementation for interactive charts using Chart.js or D3.js
        // This would create beautiful visualizations
    }

    // Periodic Updates
    startPeriodicUpdates() {
        setInterval(() => {
            this.updateTimestamp();
        }, 60000); // Update every minute
    }

    updateTimestamp() {
        const now = new Date();
        const timestamp = now.toLocaleString();
        
        const timestampElement = document.getElementById('last-updated');
        if (timestampElement) {
            timestampElement.textContent = `Last updated: ${timestamp}`;
        }
    }

    // Error Handling
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.innerHTML = `
            <div class="error-content">
                <span class="error-icon">⚠️</span>
                <span class="error-message">${message}</span>
                <button class="error-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
}

// Initialize the application
let fraAtlas;
document.addEventListener('DOMContentLoaded', () => {
    fraAtlas = new FRAAtlas();
});

// Add CSS for animations and enhanced styles
const additionalStyles = `
<style>
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.enhanced-rec {
    animation: fadeInUp 0.6s ease forwards;
}

.village-card {
    background: var(--surface-color);
    border-radius: 16px;
    padding: 25px;
    border: 1px solid var(--border-color);
    transition: all 0.3s ease;
}

.village-header {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 20px;
}

.village-avatar {
    width: 50px;
    height: 50px;
    background: var(--gradient);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5em;
}

.village-details h3 {
    margin: 0;
    color: var(--primary-color);
    font-size: 1.3em;
}

.village-subtitle {
    margin: 2px 0 0 0;
    color: var(--text-secondary);
    font-size: 0.9em;
}

.village-stats {
    margin: 20px 0;
}

.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid var(--border-color);
}

.stat-row:last-child {
    border-bottom: none;
}

.stat-label {
    color: var(--text-secondary);
    font-size: 0.9em;
}

.status-approved {
    color: #4caf50;
    font-weight: 600;
}

.village-actions {
    display: flex;
    gap: 10px;
    margin-top: 20px;
}

.action-btn {
    flex: 1;
    padding: 12px 16px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9em;
    font-weight: 500;
    transition: all 0.3s ease;
}

.action-btn.primary {
    background: var(--gradient);
    color: white;
}

.action-btn.secondary {
    background: var(--background-color);
    color: var(--primary-color);
    border: 1px solid var(--border-color);
}

.action-btn:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow);
}

.rec-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.rec-title {
    display: flex;
    align-items: center;
    gap: 10px;
}

.rec-icon {
    font-size: 1.2em;
}

.rec-content {
    padding-left: 35px;
}

.scheme-benefit, .scheme-ministry {
    margin: 8px 0;
    color: var(--text-secondary);
    font-size: 0.9em;
}

.scheme-reasons {
    margin: 15px 0;
}

.reason-tag {
    display: inline-block;
    background: var(--background-color);
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    margin: 2px 4px 2px 0;
    border: 1px solid var(--border-color);
}

.eligibility-score {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 15px;
    font-size: 0.9em;
}

.score-bar {
    flex: 1;
    height: 6px;
    background: var(--border-color);
    border-radius: 3px;
    overflow: hidden;
}

.score-fill {
    height: 100%;
    background: var(--gradient);
    transition: width 1s ease;
}

.score-value {
    font-weight: 600;
    color: var(--primary-color);
}

.error-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: #f44336;
    color: white;
    padding: 15px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(244, 67, 54, 0.3);
    z-index: 10000;
    animation: slideInRight 0.3s ease;
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.error-content {
    display: flex;
    align-items: center;
    gap: 10px;
}

.error-close {
    background: none;
    border: none;
    color: white;
    cursor: pointer;
    font-size: 1.2em;
    margin-left: 10px;
}
</style>
`;

// Inject additional styles
document.head.insertAdjacentHTML('beforeend', additionalStyles);
