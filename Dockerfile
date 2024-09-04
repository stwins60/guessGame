FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl --fail http://localhost:8501/_stcore/health || exit 1


ENTRYPOINT ["python3", "-m", "streamlit", "run", "app.py", "--server.enableCORS", "true", "--server.port=8501", "--server.address=0.0.0.0", "--browser.gatherUsageStats", "false"]