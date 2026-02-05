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

## Key Decisions & Assumptions

* **"Make vs. Buy" Strategy (LLM Selection):** I assumed the goal was to build the *orchestration layer* (The Judge) rather than training a custom classifier from scratch. I chose **OpenAI's GPT-4o** for its multimodal capabilities to prioritize velocity. However, I am aware that open-weights models like **Qwen2.5-VL** (72B) or **Llama 3.2 Vision** often outperform GPT-4o on OCR and fine-detail detection in video.
* **Multi-Source Ingestion:** I assumed the "Judge" must handle real-world user behavior. Users rarely have raw `.mp4` files handy; they share links. Therefore, I architected the system to support extensibility for YouTube/URL ingestion alongside local file processing.
* **Quality Assurance Standard:** I assumed this codebase should mimic a production environment. I prioritized **backend test coverage (pytest)** and modular design over a complex UI, ensuring the core business logic is robust and refactor-safe.
* **The "Judge" Persona:** I assumed the agent needs to explain *why* it made a decision. A binary "AI/Human" label is insufficient for trust. The system is designed to output reasoning and confidence scores alongside the classification.

## Roadmap & Future Improvements

If this were moving to production, I would prioritize the following:

1.  **Open Source & Model Agnosticism:**
    * The current architecture (`/providers`) is designed to be pluggable. I would implement a provider for **Qwen2.5-VL (via Together AI)** to reduce inference costs by ~10x and potentially improve OCR performance on video text artifacts.
    * *Goal:* Allow the user to toggle between "High Precision" (GPT-4o) and "Low Cost/Local" (Llama 3.2 11B via Groq/Ollama).

2.  **Enhanced Video Pipeline (Temporal Resolution):**
    * Currently, we sample frames to manage token context. I would upgrade this to use **Native Video Tokenization** (e.g., Gemini 1.5 Pro's 1M context window) or implement a sliding window approach to catch anomalies that happen *between* our current sample frames (e.g., glitching hands).

3.  **Real-Time Feedback Loop (WebSockets):**
    * Video downloading and processing can be latent. I would move the `VideoProcessor` to a background worker (Celery/Redis) and implement **WebSockets** to stream real-time status updates ("Downloading...", "Extracting Frames...", "Analyzing...") to the frontend.

4.  **DevOps & CI/CD:**
    * Add a GitHub Actions pipeline to enforce test coverage thresholds and linting (Ruff/Black) on every PR.
    
5.  **Frontend Robustness:**
    * Implement **Cypress** or **Playwright** End-to-End (E2E) tests to ensure the UI handles error states (e.g., "Video too large", "Invalid URL") gracefully.
