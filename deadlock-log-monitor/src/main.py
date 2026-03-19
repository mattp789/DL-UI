#!/usr/bin/env python3
"""
Deadlock Log Monitor - Real-time monitoring of Deadlock game logs
to identify creep camp events and associate them with log entries.
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DeadlockLogHandler(FileSystemEventHandler):
    """Handles file system events for Deadlock log files"""
    
    def __init__(self):
        self.camp_data = {}
        self.log_pattern = re.compile(
            r'(03\/\d{2}\s\d{2}:\d{2}:\d{2})\s(.*)'
        )
        
        # Patterns to identify boss camps/creep camps
        self.camp_patterns = [
            re.compile(r'npc_boss', re.IGNORECASE),
            re.compile(r'camp.*defeat', re.IGNORECASE),
            re.compile(r'objective.*complete', re.IGNORECASE),
            re.compile(r'destroyed', re.IGNORECASE),
            re.compile(r'defeated', re.IGNORECASE),
            re.compile(r'eliminated', re.IGNORECASE)
        ]
        
        # Camp identifiers
        self.camp_identifiers = [
            'npc_boss_tier2',
            'npc_trooper_boss'
        ]

    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
            
        if event.src_path.endswith('.txt') and 'deadlock_log' in event.src_path.lower():
            logger.info(f"Detected log file change: {event.src_path}")
            self.process_log_file(event.src_path)

    def process_log_file(self, file_path):
        """Process the log file to identify camp events"""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                
            # Process each line for camp-related events
            for i, line in enumerate(lines):
                if self.is_camp_event(line):
                    logger.info(f"Camp event found: {line.strip()}")
                    self.analyze_camp_event(line, i)
                    
        except Exception as e:
            logger.error(f"Error processing log file {file_path}: {e}")

    def is_camp_event(self, line):
        """Check if a log line contains camp-related information"""
        # Check for boss entities
        for pattern in self.camp_patterns:
            if pattern.search(line):
                return True
                
        # Check for specific camp identifiers
        for identifier in self.camp_identifiers:
            if identifier in line:
                return True
                
        return False

    def analyze_camp_event(self, line, line_number):
        """Analyze a camp event and extract relevant information"""
        timestamp = self.extract_timestamp(line)
        
        # Extract entity information
        entity_match = re.search(r'entity#(\d+)/(.*?)(?:\s|$)', line)
        if entity_match:
            entity_id = entity_match.group(1)
            entity_name = entity_match.group(2)
            
            # Store camp data with timestamp and line info
            camp_info = {
                'timestamp': timestamp,
                'line_number': line_number,
                'line_content': line.strip(),
                'entity_id': entity_id,
                'entity_name': entity_name,
                'detected_at': datetime.now().isoformat()
            }
            
            # Store in our camp data structure
            if entity_id not in self.camp_data:
                self.camp_data[entity_id] = []
            self.camp_data[entity_id].append(camp_info)
            
            logger.info(f"Camp identified - Entity: {entity_name} (ID: {entity_id}) at {timestamp}")
            
            # Save to JSON file for persistence
            self.save_camp_data()

    def extract_timestamp(self, line):
        """Extract timestamp from log line"""
        timestamp_match = re.search(r'(03\/\d{2}\s\d{2}:\d{2}:\d{2})', line)
        return timestamp_match.group(1) if timestamp_match else "Unknown"

    def save_camp_data(self):
        """Save camp data to JSON file"""
        try:
            with open('logs/camp_events.json', 'w') as f:
                json.dump(self.camp_data, f, indent=2)
            logger.info("Camp data saved to camp_events.json")
        except Exception as e:
            logger.error(f"Error saving camp data: {e}")

    def get_camp_events(self):
        """Get all camp events"""
        return self.camp_data

def main():
    """Main function to start the log monitor"""
    logger.info("Starting Deadlock Log Monitor...")
    
    # Create handler for log files
    event_handler = DeadlockLogHandler()
    
    # Set up observer to watch for file changes
    observer = Observer()
    log_dir = os.path.expanduser("~/Documents/My Games/Deadlock")  # Default Deadlock logs directory
    
    if not os.path.exists(log_dir):
        logger.warning(f"Log directory not found: {log_dir}")
        log_dir = "."  # Fallback to current directory
        
    observer.schedule(event_handler, path=log_dir, recursive=False)
    observer.start()
    
    logger.info(f"Monitoring log directory: {log_dir}")
    logger.info("Press Ctrl+C to stop monitoring")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping Deadlock Log Monitor...")
        observer.stop()
        
    observer.join()

if __name__ == "__main__":
    main()