FROM python:3.11-slim

RUN pip install cryptography

COPY icmp_listener.py /app/icmp_listener.py
WORKDIR /app

CMD ["python", "-u", "icmp_listener.py", "icmp-listener"]