FROM python:3.11-alpine

RUN mkdir -p /app
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt


COPY ./app /app

EXPOSE 3000

CMD ["fastapi", "run", "/app/main.py", "--proxy-headers", "--port", "3000"]
