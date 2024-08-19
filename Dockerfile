FROM python:3.12.5-slim-bookworm

WORKDIR /quadbot

COPY . .

RUN ./scripts/setup.sh

CMD ["python3", "-u", "src/main.py"]
