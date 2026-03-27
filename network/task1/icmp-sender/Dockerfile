FROM python:3.11-slim

RUN pip install cryptography

COPY icmp_sender.py /app/icmp_sender.py
WORKDIR /app

CMD ["python", "-u", "icmp_sender.py", "icmp-listener"]