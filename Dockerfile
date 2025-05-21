FROM python:3.10.7-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# RUN python manage.py collectstatic --noinput

EXPOSE 8282

CMD ["python", "manage.py", "runserver", "0.0.0.0:8282"]