# FeltSense Challenge

![Tests](https://img.shields.io/badge/tests-passing-green) ![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen)

## What I Built
I built a **Multimodal Content Intelligence System** (the "Judge Agent") designed to analyze digital content for authenticity, virality, and audience fit. The system features a **Service-Oriented Backend** (FastAPI) that orchestrates analysis logic and a **React Frontend** (Vite + Tailwind CSS) that allows users to analyze Text, Local Videos, and YouTube URLs seamlessly. If the interface is not wanted, you can always use the CLI tools directly. Examples below

## Prerequisites 
The **only thing you need** to run this project is an **OpenAI API Key**.
The system uses GPT-4o for its multimodal analysis capabilities.

1.  Create a `.env` file in the root directory.
2.  Add your key:
    ```bash
    OPENAI_API_KEY=sk-your-key-here
    ```

## How to Run It

### 🚀 Option A: The Web Application (RECOMMENDED)
The easiest way to see the full system in action is using Docker Compose.

```bash
docker compose up --build
```
This command spins up both the Backend API and the Frontend React App.

- **Frontend Access**: [http://localhost:5173](http://localhost:5173) (Open this in your browser!)
- **Backend Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

**Capabilities in the Web App:**
1.  **Text Analysis**: Paste any text to detect AI generation.
2.  **Video Upload**: Upload a local video file directly.
3.  **YouTube Analysis**: Paste a YouTube URL for automatic download and analysis.

---

### 💻 Option B: Command Line Interface (CLI)
You can also run the agent tools directly via Docker, without installing Python locally.

**1. Analyze Text**
```bash
docker compose run --rm backend python3 main.py "This is a suspicious post about cryptocurrency" --context "Twitter"
```

**2. Analyze Local Video**
(Uses the sample video mapped in `data/`)
```bash
docker compose run --rm backend python3 main.py --video data/video.mp4
```

**3. Analyze YouTube URL**
```bash
docker compose run --rm backend python3 main.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Assumptions
- I assumed i could use Python to build this
- Another asupmtion is that the video could come in some forms, not only in a file format. I added the Youtube (and others) compatibility
- I assumed the user would have an OpenAI API Key
- Another assumption is that the challenge needs coverage tests in backend and frontend
- Another assumption is that i was allowed to use public LLMs like OpenAI instead of building my own model or using open source models like Qwen2.5-VL that provides better OCR capabilites and noticing details in videos or even Llama 3.2 Vision
- What I prioritized was to deliver a working product that could be used by the user, so i prioritized the frontend and backend to be functional and easy to use, instead of focusing on the model itself.

## Future Improvements
With more time, I would:
1.  **Integrate Real Vision Models**: Replace the current metadata/frame-sampling proxy with actual OpenAI GPT-4o Vision API calls for deeper visual understanding.
2.  **Real-Time Progress**: Implement WebSockets to show real-time progress for video downloads and analysis (which can be slow).
3.  **Cloud Deployment**: Add Terraform/CDK configurations for deploying to AWS/GCP.
4.  **Enhanced Testing**: Add integration tests specifically for the video processing pipeline.
5.  **Add Frontend Tests**: Add frontend tests to ensure the frontend is working as expected with tests
6.  **CI/CD**: Add CI/CD pipeline to run the tests and  run the script to update the coverage badges
7.  **Open Source Strategy**: While this MVP uses OpenAI for velocity, the architecture (/interfaces) is designed to support Qwen2.5-VL (via Together AI) or Llama 3.2 (via Groq) if we add it as another Provider in /provider
