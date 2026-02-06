FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY invoice_automation/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY invoice_automation/ ./

# Expose Streamlit port
EXPOSE 8501

# Configure Streamlit
RUN mkdir -p ~/.streamlit && \
    echo "[client]\nshowErrorDetails = true\n[logger]\nlevel = info" > ~/.streamlit/config.toml

# Run the app
CMD ["streamlit", "run", "ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
