FROM python:3.11.8-slim-bookworm

WORKDIR /quadbot

COPY . .

RUN ./scripts/setup.sh

CMD ["python3", "src/main.py"]
