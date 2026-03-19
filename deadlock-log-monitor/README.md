# Deadlock Log Monitor

A containerized application that monitors Deadlock game logs in real-time to identify creep camp events and associate them with log entries.

## Features

- Real-time monitoring of Deadlock log files
- Detection of boss camps and objective events
- Timestamped logging of camp events
- JSON data export for camp events
- Containerized deployment using Docker

## Installation

1. Clone the repository
2. Build the Docker image:
   ```bash
   docker build -t deadlock-log-monitor .
   ```

## Usage

Run the monitor with:
```bash
docker run -v ~/Documents/My\ Games/Deadlock:/logs deadlock-log-monitor
```

The application will monitor the Deadlock logs directory and output camp events to `logs/camp_events.json`.

## Log Structure

Camp events are stored in JSON format with:
- Timestamp of the event
- Line number in the log file
- Entity ID and name
- Detection time

## Configuration

Configuration options can be found in the `config/` directory.

## Development

To develop locally:
1. Install dependencies: `pip install -r requirements.txt`
2. Run: `python src/main.py`

## License

MIT