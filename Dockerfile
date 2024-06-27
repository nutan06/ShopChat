# app/Dockerfile

FROM python:3.9-slim
#FROM python:3.9.19-bookworm

COPY . /app

WORKDIR /app

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Build: docker build -t arindam29/streamlit:1.0 .
# Check: docker images
# Run: docker run -p 8501:8501 streamlit