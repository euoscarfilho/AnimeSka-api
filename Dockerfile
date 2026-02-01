FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (chromium only to save space)
RUN playwright install --with-deps chromium

# Copy app code
COPY . .

# Expose port
EXPOSE 8000

# Run command
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
