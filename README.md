# LeetSync Pro

An automation platform that automatically synchronizes accepted LeetCode submissions into GitHub while maintaining a beautiful developer experience.

## Architecture

LeetSync Pro is built following **Clean Architecture** principles to separate business logic from external frameworks, interfaces, and drivers.

### Layer Separation
- **Core**: Contains core domain concepts and entity primitives.
- **Services**: Use cases and workflows (e.g. Sync Engine, Statistics Engine).
- **Integrations**: Gateway client wrappers for third-party platforms (LeetCode, GitHub).
- **Infrastructure**: Low-level database adapters, session configurations, and filesystem managers.
- **Models**: Database models (SQLAlchemy) and input-output validations schemas (Pydantic).
- **Configuration**: Settings and credentials validators (Pydantic Settings).
- **CLI / Dashboard**: User interaction layers (FastAPI + React Dashboard, CLI utility).

---

## Tech Stack

### Backend
- **Core Engine**: Python 3.14+
- **API Framework**: FastAPI
- **Database ORM**: SQLite + SQLAlchemy 2.0
- **Validations**: Pydantic v2
- **Version Control Automation**: GitPython
- **Job Scheduler**: APScheduler

### Frontend (Dashboard)
- **UI Framework**: React + TypeScript + Vite
- **Styling**: TailwindCSS + Framer Motion
- **Components**: shadcn/ui + Lucide Icons
- **Data Queries**: React Query

---

## Development & Execution Status

Below is the implementation progress milestone timeline:

- [x] **Phase 1: Project Structure** (Clean Architecture skeleton package)
- [x] **Phase 2: Configuration** (Environment settings parsing)
- [x] **Phase 3: Database** (SQLAlchemy 2.0 SQLite integration)
- [x] **Phase 4: Models** (Database models and Pydantic schemas)
- [x] **Phase 5: GitHub Integration** (Git automation flow)
- [x] **Phase 6: LeetCode Integration** (GraphQL client wrappers)
- [x] **Phase 7: Sync Engine** (Orchestrated synchronization run)
- [x] **Phase 8: Documentation Generator** (Dynamic problem-level README markdown formatter)
- [/] **Phase 9: Statistics Engine** (Currently implementing stats compiler & repository master README)
- [ ] **Phase 10: Scheduler** (Cron jobs and background executor)
- [ ] **Phase 11: Dashboard Backend** (FastAPI controllers and query endpoints)
- [ ] **Phase 12: Dashboard Frontend** (Vite + React Apple-like premium UI)
- [ ] **Phase 13: Logging** (Structured JSON telemetry logs)
- [ ] **Phase 14: Testing** (Verification pipeline)
- [ ] **Phase 15: Docker** (Containerized orchestration config)
- [ ] **Phase 16: CI/CD** (GitHub Actions CI workflow)

---

## Local Development Setup

### Prerequisites
- Python 3.10+
- Node.js & npm (for frontend dashboard)
- Git installed on system

### Installation & Run
1. Clone the repository:
   ```bash
   git clone https://github.com/DnN04/LeetSync.git
   cd LeetSync
   ```
2. Setup environment settings inside `.env`:
   ```env
   GITHUB_TOKEN=your_github_token
   GITHUB_REPO=username/portfolio_repo_name
   LEETCODE_SESSION=your_leetcode_session_cookie
   LEETCODE_CSRF_TOKEN=your_leetcode_csrf_token
   ```
3. Run backend unit tests:
   ```bash
   $env:PYTHONPATH="backend"; python -m pytest backend/tests/
   ```