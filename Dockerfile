FROM python:3.11.8-slim-bookworm
ARG FLAGS=""

WORKDIR /quadbot

COPY . .

RUN ./scripts/setup.sh

CMD ["python3", "./main.py", "${FLAGS}"]
