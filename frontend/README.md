# F1 AI Analyst Frontend

This is the React frontend for the F1 Agentic Analyst system. It provides a rich dashboard to visualize live Formula 1 data and a persistent chat interface to interact with the multi-agent backend.

## Features

- **Race Dashboard**: Visualizes driver standings, lap traces, and top finishers.
- **Agentic Chat Interface**: Ask questions about specific races, drivers, or strategies. The chat communicates with the multi-agent LangGraph backend, providing engineering-focused insights.
- **Automated Summary Trigger**: A one-click "Analyze Race" button to generate full post-race analyses.

## Getting Started

### Prerequisites
- Node.js (v18+)

### Environment Setup

Create a `.env` file from the `.env.example`:

```bash
cp .env.example .env
```

Set the backend API URL (defaults to `http://localhost:8000` for local dev):

```env
VITE_API_URL=http://localhost:8000
```

### Installation & Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the Vite development server:
   ```bash
   npm run dev
   ```

The application will be accessible at `http://localhost:5173`.

## Architecture

This frontend is built with React and Vite. It heavily relies on the backend FastAPI endpoints:
- `GET /api/v1/dashboard-data`: Fetches synchronous telemetry.
- `POST /api/v1/race-summary`: Triggers the asynchronous generation of a full race report.
- `POST /api/v1/chat`: Communicates with the LangGraph agent for conversational F1 insights.
