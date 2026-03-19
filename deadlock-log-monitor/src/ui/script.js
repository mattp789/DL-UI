// Simple web UI for Deadlock Log Monitor
class LogMonitorUI {
    constructor() {
        this.campEvents = [];
        this.updateInterval = null;
        
        // Initialize the UI
        this.init();
        
        // Start auto-refresh
        this.startAutoRefresh();
    }
    
    init() {
        // Set up event listeners
        document.getElementById('refresh-btn').addEventListener('click', () => this.refreshData());
        document.getElementById('clear-btn').addEventListener('click', () => this.clearLogs());
        
        // Initial data load
        this.refreshData();
    }
    
    async refreshData() {
        try {
            // Update status
            const now = new Date();
            document.getElementById('last-update').textContent = `Last update: ${this.formatTime(now)}`;
            
            // Fetch camp events from the backend
            const response = await fetch('/api/camp-events');
            if (response.ok) {
                this.campEvents = await response.json();
                this.updateCampEventsDisplay();
                this.updateStatus('Data refreshed successfully');
            } else {
                throw new Error('Failed to fetch camp events');
            }
            
            // Fetch log content
            const logResponse = await fetch('/api/log-content');
            if (logResponse.ok) {
                const logContent = await logResponse.text();
                document.getElementById('log-output').textContent = logContent;
            }
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.updateStatus('Error: Failed to refresh data');
        }
    }
    
    updateCampEventsDisplay() {
        const eventsContainer = document.getElementById('camp-events');
        
        if (this.campEvents.length === 0) {
            eventsContainer.innerHTML = '<p>No camp events detected yet.</p>';
            return;
        }
        
        // Sort by timestamp descending
        const sortedEvents = Object.values(this.campEvents)
            .flat()
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            
        const eventsHTML = sortedEvents.map(event => `
            <div class="event-card">
                <h3>Entity: ${event.entity_name}</h3>
                <div class="event-details">
                    <div><strong>ID:</strong> ${event.entity_id}</div>
                    <div><strong>Time:</strong> ${event.timestamp}</div>
                    <div><strong>Line:</strong> ${event.line_number}</div>
                    <div><strong>Detected:</strong> ${this.formatTime(new Date(event.detected_at))}</div>
                </div>
            </div>
        `).join('');
        
        eventsContainer.innerHTML = eventsHTML;
    }
    
    updateStatus(message) {
        document.getElementById('status').textContent = message;
    }
    
    clearLogs() {
        this.campEvents = [];
        document.getElementById('camp-events').innerHTML = '<p>No camp events detected yet.</p>';
        this.updateStatus('Logs cleared');
    }
    
    startAutoRefresh() {
        // Refresh every 5 seconds
        this.updateInterval = setInterval(() => {
            this.refreshData();
        }, 5000);
    }
    
    formatTime(date) {
        return date.toLocaleTimeString();
    }
}

// Initialize the UI when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new LogMonitorUI();
});