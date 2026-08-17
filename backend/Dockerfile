FROM python:3.12-slim

WORKDIR /app

# Install dependencies in a separate layer so it's cached between deploys.
# This layer only re-runs when requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source after dependencies are installed.
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
