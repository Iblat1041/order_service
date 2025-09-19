FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY order_service/ .

# CMD ["sh", "-c", "python manage.py migrate && \
#                 python manage.py collectstatic --noinput && \
#                 python manage.py runserver 0.0.0.0:8000"]
