# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy files
COPY rag_pipeline_app.py .
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "rag_pipeline_app.py", "--server.port=8501", "--server.address=0.0.0.0"]