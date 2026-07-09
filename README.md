# LeetSync 

An advanced automation platform that automatically synchronizes your accepted LeetCode submissions into your GitHub repository while delivering a premium, modern developer experience.

## ✨ Key Features
- **Automated Synchronization**: Fetches newly accepted submissions from LeetCode and automatically commits them to a target GitHub repository.
- **Premium Dashboard**: A stunning, responsive, glassmorphic React/Vite dashboard to monitor system status, view sync logs, and adjust settings in real-time.
- **Smart Validation & Recovery**: Automatically fetches missing LeetCode CSRF tokens and handles Git conflicts seamlessly.
- **Rich Documentation Generation**: Generates problem-specific READMEs with dynamic difficulty and topic badges for every synced solution.
- **Background Scheduler**: Set custom intervals for background synchronization using robust cron-like executors.
- **Comprehensive Telemetry**: Structured JSON logging for deep insights into the automation engine's actions.

## 🏗️ Architecture

LeetSync Pro is engineered following **Clean Architecture** and SOLID principles to separate business logic from external frameworks, interfaces, and drivers.

### Layer Separation
- **Core**: Contains core domain concepts and entity primitives.
- **Services**: Use cases and workflows (e.g., Sync Engine, Statistics Engine, Scheduler).
- **Integrations**: Gateway client wrappers for third-party platforms (LeetCode GraphQL, GitHub API via GitPython).
- **Infrastructure**: Low-level database adapters, session configurations, and filesystem managers.
- **Models**: Database schemas (SQLAlchemy) and input-output validation schemas (Pydantic).
- **Configuration**: Dynamic environment parsing and resolution (Pydantic Settings).
- **Dashboard API**: RESTful endpoints powered by FastAPI.
- **Dashboard UI**: Aesthetic frontend interface powered by React.

---

## 💻 Tech Stack

### Backend
- **Core Engine**: Python 3.11+
- **API Framework**: FastAPI
- **Database ORM**: SQLite + SQLAlchemy 2.0
- **Validations**: Pydantic v2
- **Version Control**: GitPython
- **Job Scheduler**: APScheduler

### Frontend (Dashboard)
- **UI Framework**: React + TypeScript + Vite
- **Styling**: Tailwind CSS v4 (Glassmorphism, Neon Gradients)
- **Icons**: Lucide React

---

## 🚀 Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js (v20+) & npm
- Git installed on your system
- Docker (optional, but recommended for easy deployment)

### 🐳 Quick Start with Docker
```bash
git clone https://github.com/DnN04/LeetSync.git
cd LeetSync

# Configure your .env file
# Run with Docker Compose
docker-compose up --build
```
Access the Dashboard at `http://localhost` and the API at `http://localhost:8000/docs`.

### 🛠️ Manual Installation & Run
1. **Clone the repository**:
   ```bash
   git clone https://github.com/DnN04/LeetSync.git
   cd LeetSync
   ```
2. **Setup environment variables** in a `.env` file at the project root:
   ```env
   # GitHub Configuration
   GITHUB_TOKEN=your_fine_grained_github_pat # (Needs 'Read and Write' for Contents)
   GITHUB_REPO=username/portfolio_repo_name
   SYNC_REPO_PATH=leetcode_portfolio
   
   # LeetCode Configuration
   LEETCODE_SESSION=your_leetcode_session_cookie
   # LEETCODE_CSRF_TOKEN is fetched automatically if left empty
   
   # Engine Settings
   SYNC_INTERVAL_MINUTES=5
   LOG_LEVEL=INFO
   DATABASE_URL=sqlite:///leetsync.db
   ```
3. **Start the Backend**:
   ```bash
   cd backend
   python -m venv venv
   # Windows: .\venv\Scripts\activate | Mac/Linux: source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
4. **Start the Frontend Dashboard**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Navigate to `http://localhost:5173` in your browser.

---

## ✅ Development & Execution Status

The project is fully complete across all planned milestones:

- [x] **Phase 1: Project Structure** (Clean Architecture skeleton)
- [x] **Phase 2: Configuration** (Dynamic path resolution & environment settings)
- [x] **Phase 3: Database** (SQLAlchemy 2.0 SQLite integration)
- [x] **Phase 4: Models** (Database models and Pydantic schemas)
- [x] **Phase 5: GitHub Integration** (Git automation with token validation)
- [x] **Phase 6: LeetCode Integration** (GraphQL wrappers & auto-CSRF fetch)
- [x] **Phase 7: Sync Engine** (Duplicate filtering and commit orchestration)
- [x] **Phase 8: Documentation Generator** (SVG markdown formatters)
- [x] **Phase 9: Statistics Engine** (Stats compiler & master repository README)
- [x] **Phase 10: Scheduler** (Cron jobs and background executor)
- [x] **Phase 11: Dashboard Backend** (FastAPI controllers and endpoints)
- [x] **Phase 12: Dashboard Frontend** (Vite + React premium UI with Tailwind v4)
- [x] **Phase 13: Logging** (Structured JSON telemetry)
- [x] **Phase 14: Testing** (Comprehensive Pytest verification pipeline)
- [x] **Phase 15: Docker** (Containerized orchestration config)
- [x] **Phase 16: CI/CD** (GitHub Actions CI workflow)

---
*Engineered with Clean Architecture and Aesthetic Design principles.*
