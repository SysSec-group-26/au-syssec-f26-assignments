FROM python:3.11-slim

COPY general_sender.py /app/general_sender.py
WORKDIR /app

CMD ["python", "-u", "general_sender.py", "icmp-listener"]