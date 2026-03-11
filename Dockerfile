FROM python:3.12-slim

# Install uv python package manager
RUN pip install uv

# Create a non-root user
RUN useradd -u 1000 -m appuser

# Install git
RUN apt-get update && \ 
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Define working directory
WORKDIR /app

# Clone repo
RUN git clone https://github.com/f-creme/JobSeekersJournal.git . 

# Install dependencies
RUN uv sync

# Change the owner of the files to the non-root user
# and switch to the non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose Streamlit port 
EXPOSE 8501

# Start Streamlit
ENTRYPOINT [ "uv", "run", "streamlit", "run", "entrypoint.py", "--server.address=0.0.0.0", "--server.port=8501" ]