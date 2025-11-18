# CampusTransport-UNRC-2025

Repository for the **Project 2025** course at UNRC. The goal is to develop an app that connects drivers and passengers within the campus, optimizing trips so that drivers don’t deviate much from their routes. A *Reinforcement Learning* algorithm will decide which passengers are worth picking up based on their location and route.

## Key Features

- **Free system**; no payments or cost-sharing are considered.  
- Any university member can register as a **driver** or **passenger**; roles can be switched at any time.  
- Route optimization using *Reinforcement Learning* to approach results similar to **Dijkstra/A\***.  
- Development methodology: **Scrum**.

## Technologies

- **Frontend:** React + Tailwind + Vite + TypeScript  
- **Backend:** Python + Flask + Pytest  
- **AI/ML:** numpy, pandas, scikit-learn, tensorflow, keras, stable-baselines3
- **Street Graphs:** OpenStreetMap + osmnx  

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)
- Node.js 18+ (for frontend development)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/Uni-Mov/rl-campus-transport.git
   cd rl-campus-transport
   ```

2. **Build and run with Docker Compose**
   ```bash
   cd docker
   docker-compose up --build
   ```

3. **Access the services**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000
   - Database: PostgreSQL on port 5432

### API Usage

#### Calculate Route

**GET Request:**
```bash
curl "http://localhost:5000/paths/calculate?start_node=-64.351,-33.123&end_node=-64.350,-33.124"
```

**POST Request:**
```bash
curl -X POST http://localhost:5000/paths/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "start_node": [-64.351, -33.123],
    "end_node": [-64.350, -33.124],
    "waypoints": [[-64.3505, -33.123]]
  }'
```

**Response:**
```json
{
  "route": [
    {
      "coordinates": [
        [-64.351276, -33.1226042],
        [-64.3502838, -33.1228578],
        [-64.3493391, -33.1230822],
        [-64.3496873, -33.1241433]
      ],
      "distance": 313.38,
      "duration": 376.06
    }
  ],
  "waypoints": []
}
```

## Project Structure

```
rl-campus-transport/
├── backend/          # Flask API
├── frontend/         # React application
├── ia_ml/           # Reinforcement Learning model
│   ├── src/
│   │   ├── api/     # API integration
│   │   ├── envs/    # RL environments
│   │   ├── training/# Training scripts
│   │   └── utils/   # Utilities
│   ├── scripts/     # Helper scripts
│   └── logs/        # Training logs and models
├── docker/          # Docker configuration
└── docs/           # Documentation
```

## Contribution

- We will follow **1–2 week Scrum sprints**, including retrospectives with course instructors.  

## Team Members

- Agustin Alieni   
- Francisco Barosco   
- Hernan Jara   
- Francisco Natale 
- Franco Vesnaver 
- Valentino Vilar 

## License

This project is released under the **MIT License**. See [LICENSE](LICENSE) for details.
