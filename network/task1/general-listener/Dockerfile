FROM python:3.11-slim

RUN pip install cryptography

COPY general_listener.py /app/general_listener.py
WORKDIR /app

CMD ["python", "-u", "general_listener.py", "general-listener"]