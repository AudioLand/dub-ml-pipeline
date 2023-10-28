# Тест
# https://hub.docker.com/_/python
FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY . ./

RUN apt -y update
RUN apt install --no-install-recommends -y ffmpeg
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
