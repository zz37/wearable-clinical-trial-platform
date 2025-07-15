FROM python:3.10-slim

# Working directory inside container
WORKDIR /app 

# Copy ingestion script and requirements
COPY . /app 

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add cron and timezone support
RUN apt-get update && apt-get install -y cron tzdata

# Copy cron job file (you named it crontab.txt)
COPY crontab.txt /etc/cron.d/ingestion-cron

# Give execution rights
RUN chmod 0644 /etc/cron.d/ingestion-cron

# Apply cron job
RUN crontab /etc/cron.d/ingestion-cron

# Start cron + tail logs (keeps container alive)
CMD ["sh", "-c", "cron && tail -f /var/log/cron.log"]