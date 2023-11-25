FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY . ./

RUN apt-get -y update
RUN apt-get install --no-install-recommends -y ffmpeg

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "/app/src/app.py"]
