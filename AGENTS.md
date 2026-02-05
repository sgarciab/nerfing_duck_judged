> **ARCHITECTURAL STYLE**: Service-Oriented with Dependency Injection (Clean Architecture Lite)

---

## 1. Business Domain & Value Proposition

### What is FeltSense?
FeltSense is a content intelligence layer designed to navigate the "Post-Truth" internet. As AI-generated content floods social platforms, human creators and platforms need a distinct way to measure **Authenticity** and **Impact**.

### The "Judge Agent" Product
We are building the core evaluation engine—a "Judge"—that acts as an automated arbiter for digital content.

**Key Business Questions We Answer:**
1.  **Origin Assurance:** Is this content synthetic (AI) or organic (Human)?
    * *Business Value:* Trust & Verification.
2.  **Virality Prediction:** Will this content perform well socially?
    * *Business Value:* ROI & Reach optimization.
3.  **Audience Fit:** Who is this for?
    * *Business Value:* Targeting & Distribution strategy.

---

## 2.  Proposed Architecture

We utilize a **Layered Architecture** with **Manual Dependency Injection**. This ensures our core business logic is decoupled from external vendors (OpenAI) and input methods (CLI), making the system testable and modular.

### High-Level Layers

1.  **Presentation Layer (`/cli`)**
    * **Responsibility:** Handles user input (`Typer`), formatting output (`Rich`), and loading environment variables.
    * **Rule:** The CLI *never* contains business logic. It simply instantiates the container and calls the Service.

2.  **Service Layer (`/services`)**
    * **Responsibility:** The `JudgeService`. It orchestrates the flow:
        1.  Receive raw input (Text or Video Path).
        2.  Call the `VideoProcessor` (if video).
        3.  Construct the context.
        4.  Call the `LLMProvider`.
        5.  Return a domain model (`JudgeOutput`).
    * **Rule:** The Service knows *what* to do, but not *how* the LLM works.

3.  **Infrastructure / Adapter Layer (`/providers`)**
    * **Responsibility:** Implementation details.
    * **Components:**
        * `OpenAIProvider`: Handles API keys, retries, and schema parsing.
        * `LocalVideoProcessor`: Handles OpenCV logic.
    * **Rule:** These classes implement abstract interfaces (Protocols).

4.  **Domain Layer (`/schemas`)**
    * **Responsibility:** Pure data objects (`Pydantic`).
    * **Rule:** Zero dependencies. This is the shared language of the app.

---

## 3.  Dependency Injection Strategy

We avoid heavy DI frameworks (like `dependency_injector`) for this MVP to maintain velocity, but we strictly adhere to the **Dependency Inversion Principle**.

**The Pattern:**
Services request their dependencies in their `__init__` method. The `main.py` entry point acts as the "Composition Root" where these dependencies are wired together.

**Example Contract:**

# The Service asks for a contract (Interface), not a class.
class JudgeService:
    def __init__(self, llm_provider: LLMProviderProtocol, video_processor: VideoProcessorProtocol):
        self.llm = llm_provider
        self.video = video_processor

---
## 4.  Folder Structure (Strict)
Plaintext

feltsense_challenge/
├── main.py                # Composition Root (Wiring & CLI Entry)
├── schemas.py             # Domain Models (Pydantic)
├── services/
│   ├── __init__.py
│   └── judge_service.py   # Business Logic
├── providers/
│   ├── __init__.py
│   ├── llm.py             # OpenAI Implementation
│   └── video.py           # OpenCV Implementation
├── interfaces/            # (Optional) Protocols for DI
│   └── protocols.py
└── requirements.txt

## 5. Agent Coding Standards
### Rule 1: The "No-Import" Service Rule
The JudgeService MUST NOT import openai or cv2 directly. It should only import from interfaces or providers (if skipping strict interfaces for speed).

Why? If we swap OpenAI for Anthropic later, we shouldn't have to touch the Service layer.

### Rule 2: Validation at the Gate
All inputs entering the Service Layer must be validated. If a file path doesn't exist, the Service raises a domain exception (ContentNotFoundError), not a generic OS error.

### Rule 3: Single Responsibility
VideoProcessor: Only extracts frames. Does not analyze them.

LLMProvider: Only sends prompts. Does not decide what the prompt is.

JudgeService: Decides the prompt strategy and interprets the result.

### Rule 4: Hard Typing
Use Python typing everywhere.

Bad: def analyze(content):

Good: def analyze(content: str | Path) -> JudgeOutput:

## 6. Testing Strategy
Because we use DI, we can easily create a Mock Run without hitting the API.

### Unit Tests
We use `pytest` for unit testing. The tests are located in the `tests/` directory and mirror the source code structure.

- **Service Tests**: Verify business logic and prompt construction.
- **Provider Tests**: specific behavior of `OpenAI` and `OpenCV` wrappers (mocked).
- **CLI Tests**: Verify argument parsing and command execution.

To run the tests:
```bash
source .venv/bin/activate
pytest tests/
```

### Mock Mode
Create a `MockLLMProvider` that returns a static `JudgeOutput` JSON. Inject this mock into `JudgeService` during development to iterate on the CLI UI without spending tokens.

## 7. Environment & Dependency Management

### Rule 1: Strict Python Version
The project MUST run on **Python 3.10+**.
- Ensure your local environment uses a compatible version.
- Use `python3 --version` to verify.

### Rule 2: Virtual Environments
All development MUST be done within a virtual environment.
- **Do not** install packages globally.
- Create a virtual environment named `.venv` in the project root:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- A helper script `setup_venv.sh` is provided to automate this check and setup.

### Rule 3: Dependency Locking
- Dependencies are managed in `requirements.txt`.
- Always update this file when adding new packages:
  ```bash
  pip install -r requirements.txt
  ```
  
  
## 6. Use of .venv

Obligatory: For executing commands, always use the .venv environment, when you need to execute command, always activate the .venv environment first with the command: source .venv/bin/activate