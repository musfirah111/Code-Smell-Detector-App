# Code Smell Detector App

Minimal steps to run tests and the backend on Windows.

## Prerequisites
- Python 3.9+ installed and available as `python`

## Run tests
```powershell
python -m pytest tests/tests.py -v
```

## Start backend server
```powershell
python backend\scripts\run_backend_server.py
```

Optional (module form):
```powershell
python -m backend.scripts.run_backend_server
```

## Frontend (optional)
Open `frontend/index.html` in your browser, or serve it locally:
```powershell
cd frontend
python -m http.server 8000
# Visit http://localhost:8000
```
