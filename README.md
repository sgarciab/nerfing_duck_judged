# FeltSense Challenge

## Overview
FeltSense is a content intelligence layer designed to navigate the "Post-Truth" internet. This repository contains the backend challenge for building the "Judge Agent".

## Setup

### Prerequisites
- Linux
- Python 3.10+

### Installation

1. **System Dependencies**
   Ensure you have the Python 3.12 venv package installed:
   ```bash
   sudo apt install python3.12-venv
   ```

2. **Virtual Environment**
   Run the setup script to create and configure your virtual environment:
   ```bash
   ./setup_venv.sh
   source .venv/bin/activate
   ```

3. **Dependencies**
   Install Python dependencies (once you have added them to requirements.txt):
   ```bash
   pip install -r requirements.txt
   ```

## Usage

The Agent handles both text and video inputs.

**Important:** Always run commands within the virtual environment:
```bash
source .venv/bin/activate
```

### 1. Analyze Text Content
Use the mock provider (no API key needed):
```bash
python3 main.py "This is a suspicious post about cryptocurrency" --mock --context "Twitter"
```

Use the real OpenAI provider (requires `.env` setup):
```bash
python3 main.py "Just saw this amazing new tech!" --context "Reddit"
```

### 2. Analyze Video Content
Analyze a video file (uses metadata extraction + LLM judgment):
```bash
python3 main.py --video path/to/video.mp4
```

### 3. Help
View all available options:
```bash
python3 main.py --help
```

## Testing
Run the unit suite to verify logic without API usage:
```bash
source .venv/bin/activate
pytest tests/
```

## Documentation
See [AGENTS.md](./AGENTS.md) for detailed architectural guidelines and agent definitions.
