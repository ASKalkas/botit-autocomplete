FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install -r docker/requirements.txt

EXPOSE 8000

RUN chmod +x docker/start.sh