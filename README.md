# GitHub Dev Card Generator

A powerful, AI-driven full-stack application that generates beautiful developer profile cards from any public GitHub username. It uses Google's Gemini models via the Agent Development Kit (ADK) to scrape, analyze, and generate custom HTML cards dynamically.

## 🚀 Features

- **AI-Powered Analysis**: Uses `gemini-2.5-flash-lite` to deeply analyze GitHub profiles, repositories, and languages.
- **Dynamic HTML Generation**: The AI agent builds the final card layout and styling entirely from scratch.
- **Microservices Architecture**: 
  - A responsive Vite/React Frontend.
  - A robust Python backend utilizing FastAPI and the ADK MCP framework.
- **Cloud-Ready**: Fully containerized and deployable to Google Cloud Run.

## 🛠️ Tech Stack

- **Frontend**: HTML/CSS/JavaScript (via Nginx when containerized)
- **Backend**: Python 3.12, FastAPI, Google GenAI SDK, Google ADK (Agent Development Kit)
- **Deployment**: Docker, Google Cloud Run

## ⚙️ Environment Variables

To run this application, you will need to set up the following environment variables in your `backend/.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_personal_access_token
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
PORT=8000
```

> **Note:** A `GITHUB_TOKEN` is heavily recommended to prevent aggressive rate-limiting by the public GitHub API during the scraping phase.

## 💻 Local Development

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or `.\venv\Scripts\Activate.ps1` on Windows
pip install -r requirements.txt
```

Run the backend server:
```bash
python main.py
```

### 2. Frontend Setup

Since the frontend is static HTML with dynamic replacement, you can serve it via any static server or simply open the `index.html` locally. If you run it via Docker, it uses Nginx to replace the `BACKEND_URL` environment variable at runtime.

## ☁️ Deployment (Google Cloud Run)

Both services include their own `Dockerfile`s and can be deployed directly to Google Cloud Run using the gcloud CLI.

**Deploying the Backend:**
```bash
gcloud run deploy github-card-backend --source ./backend --port 8080 --set-env-vars="GOOGLE_CLOUD_PROJECT=...,GEMINI_API_KEY=...,GITHUB_TOKEN=..." --allow-unauthenticated
```

**Deploying the Frontend:**
```bash
gcloud run deploy github-card-frontend --source ./frontend --port 80 --set-env-vars="BACKEND_URL=<YOUR_BACKEND_URL>" --allow-unauthenticated
```

## 📝 License

This project is open-source and available under the MIT License.
