import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [campEvents, setCampEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch camp events from the backend API
    const fetchCampEvents = async () => {
      try {
        // In a real implementation, fetch from the local API endpoint
        const response = await fetch('/api/camp-events');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setCampEvents(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch camp events');
        setLoading(false);
      }
    };

    // Initial fetch
    fetchCampEvents();
    
    // Set up polling to refresh data every 5 seconds
    const interval = setInterval(fetchCampEvents, 5000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="app">Loading camp events...</div>;
  }

  if (error) {
    return <div className="app error">Error: {error}</div>;
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Deadlock Log Monitor</h1>
        <p>Camp Events Dashboard</p>
      </header>
      
      <div className="content">
        <div className="events-container">
          <h2>Active Camp Events</h2>
          
          {Object.keys(campEvents).length === 0 ? (
            <p className="no-events">No camp events detected yet</p>
          ) : (
            <div className="events-grid">
              {Object.entries(campEvents).map(([entityId, events]) => (
                <div key={entityId} className="event-card">
                  <h3>Entity: {events[0].entity_name} (ID: {entityId})</h3>
                  <div className="event-list">
                    {events.map((event, eventIndex) => (
                      <div key={eventIndex} className="event-item">
                        <p><strong>Timestamp:</strong> {event.timestamp}</p>
                        <p><strong>Line:</strong> {event.line_number}</p>
                        <p><strong>Content:</strong> {event.line_content}</p>
                        <p><strong>Detection Time:</strong> {event.detected_at}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;