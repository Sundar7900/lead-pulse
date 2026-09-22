# LeadPulse - Sales Intelligence Dashboard

A full-stack sales intelligence application for monitoring leads, calculating lead scores, and managing alerts.

## Tech Stack

**Backend:**
- Python 3.10+
- FastAPI
- MongoDB (PyMongo)

**Frontend:**
- React 18
- Bootstrap 5
- React Router 6
- Axios

## Prerequisites

1. Python 3.10 or higher
2. Node.js 18+ and npm
3. MongoDB 7.0

## MongoDB Setup

### Option 1: Docker (Recommended)

```bash
# Start MongoDB container
docker run -d --name leadpulse-mongodb -p 27017:27017 mongo:7.0

# Or use docker-compose from project root
cd lead-pulse
docker compose up -d
```

### Option 2: Install MongoDB Locally

**Ubuntu/Debian:**
```bash
# Import MongoDB GPG key
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Install MongoDB
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0
```

**Windows:**
Download from https://www.mongodb.com/try/download/community

## Backend Setup

```bash
cd lead-pulse/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run the server
uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

## Frontend Setup

```bash
cd lead-pulse/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:5173

## Environment Variables

Backend (`.env`):
```
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=leadpulse
```

## Project Structure

```
lead-pulse/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── config.py        # Configuration settings
│   │   ├── database.py     # MongoDB connection
│   │   ├── models/          # Data models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routes/          # API routes
│   │   ├── services/        # Business logic
│   │   ├── repositories/    # Data access layer
│   │   └── utils/           # Utilities
│   ├── seed/                # Mock data seeder
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service
│   │   ├── hooks/           # Custom hooks
│   │   ├── utils/           # Utilities
│   │   ├── layouts/         # Layout components
│   │   └── App.jsx          # App entry point
│   └── package.json
│
└── docker-compose.yml       # MongoDB container
```

## Development

The project is built incrementally in phases:

1. ✅ Project Structure
2. ✅ FastAPI + MongoDB Connection
3. 🔄 Models/Schemas + Mock Data
4. Lead APIs
5. Scoring Service
6. Alert System
7. Dashboard APIs
8. React Dashboard
9. Lead List
10. Lead Details
11. Alerts UI
12. Polish & Error Handling

## License

MIT
