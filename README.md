# GreenRide – Jenkins CI/CD Demo

Minimal Flask API used to demonstrate a Jenkins pipeline:
- Build Docker image
- Run tests (pytest)
- Code quality (flake8)
- Security scans (bandit, pip-audit)
- Push to Docker Hub
- Deploy to staging (Compose on 8081)
- Manual gate -> tag prod -> deploy to 80
- Simple monitoring health check

## Local run
```bash
pip install -r app/requirements.txt
python app/app.py
# open http://localhost:8000/health
