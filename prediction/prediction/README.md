# AI Healthcare Decision Support System

Full-stack application with Flask backend and React frontend.

## Prerequisites
- Python 3.8+
- Node.js LTS
- Docker Desktop (recommended for easy run)

## Docker Run (Recommended)
1. Install Docker Desktop: https://www.docker.com/products/docker-desktop
2. Run:
   ```
   docker compose up --build
   ```
- Backend: http://localhost:5000
- Frontend: http://localhost:3000

## Manual Run
**Backend:**
```
cd backend
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

**Frontend (new terminal):**
```
cd frontend
npm install
npm start
```

## Notes
- ML models may need training: python backend/models/model_trainer.py
- Use datasets/sample_data.csv for testing.
