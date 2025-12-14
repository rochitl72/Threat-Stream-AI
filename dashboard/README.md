# ThreatStream AI Dashboard

Modern, real-time dashboard for monitoring ThreatStream AI system.

## Features

- **Real-time Architecture Visualization** - Live component status and data flow
- **Kafka Topics Monitor** - Real-time message counts and rates
- **Vertex AI Processing** - AI analysis transparency and metrics
- **MITRE ATT&CK Matrix** - Interactive threat mapping visualization
- **Threat Timeline** - Chronological threat events and alerts
- **System Metrics** - CPU, memory, and performance monitoring

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000)

## Backend API

The dashboard connects to the FastAPI backend running on `http://localhost:8000`.

Make sure the backend is running:
```bash
cd /Users/rochitlen/Downloads/animus
python -m src.dashboard.api.server
```

## Build for Production

```bash
npm run build
npm start
```

