FROM python:3.10-slim

# Working directory inside container
WORKDIR /app 

# Copy py requirements script and file
COPY requirements.txt /app/
COPY ingest_fitbit.py /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add cron and timezone support
RUN apt-get update && apt-get install -y cron tzdata && apt-get clean

# Copy the state folder (for last_OK_run.json)
COPY state/ /app/state/

# Copy cron job file (you named it crontab.txt)
COPY crontab.txt /etc/cron.d/ingestion-cron

# Give execution rights
RUN chmod 0644 /etc/cron.d/ingestion-cron

# Apply cron job
RUN crontab /etc/cron.d/ingestion-cron

# Create the cron log file (so it exists when cron starts)
RUN touch /var/log/cron.log

# Start cron + tail logs (keeps container alive)
CMD ["sh", "-c", "cron && tail -f /var/log/cron.log"]