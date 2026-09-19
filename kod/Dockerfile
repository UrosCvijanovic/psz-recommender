FROM python:3.14-slim

LABEL authors="Uros"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["flask", "--app", "aplikacija.app", "run", "--host=0.0.0.0", "--port=5000"]