# FeltSense Challenge

![Tests](https://img.shields.io/badge/tests-failing-red) ![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen)

## Overview
FeltSense is a content intelligence layer designed to navigate the "Post-Truth" internet. This repository contains the backend challenge for building the "Judge Agent".

## 🐳 Quick Start with Docker (Recommended)

Want to run the whole app without installing Python or Node.js locally? We've got you covered!

### 1. Run Everything
To start both the Backend (API) and Frontend:
```bash
docker-compose up --build
```
- **Frontend**: Open [http://localhost:3000](http://localhost:3000)
- **Backend API**: Running at [http://localhost:8000](http://localhost:8000)

### 2. Run the CLI
You can also use the Typer CLI within the Docker container to analyze content independently:

**Analyze Text:**
```bash
docker-compose run --rm backend python main.py "Suspicious crypto scheme" --mock
```

**Analyze YouTube Video:**
```bash
docker-compose run --rm backend python main.py --url https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

---

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
The agent now supports deep multimodal analysis including:
- **Frame Extraction**: Visual analysis of key frames.
- **Audio Transcription**: Speech-to-text analysis using Whisper.
- **Metadata**: Technical video properties.

**Local Video:**
```bash
python3 main.py --video path/to/video.mp4
```

**YouTube URL:**
The agent can automatically download and analyze YouTube videos:
```bash
python3 main.py --url https://www.youtube.com/watch?v=dQw4w9WgXcQ
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
pytest
```

This project uses `pytest-cov` for test coverage. The configuration in `pytest.ini` automatically enables coverage reporting.

- **Terminal Report**: A summary of coverage by file will be displayed after running tests.
- **HTML Report**: A detailed, interactive report is generated in `htmlcov/index.html`. You can view it by opening the file in your browser.

## Documentation
See [AGENTS.md](./AGENTS.md) for detailed architectural guidelines and agent definitions.
