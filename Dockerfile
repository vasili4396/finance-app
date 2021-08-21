FROM python:3.6

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_SUPERUSER_USERNAME='admin'
ENV DJANGO_SUPERUSER_PASSWORD='admin'
ENV DJANGO_SUPERUSER_EMAIL='admin@admin.com'

WORKDIR /opt/project

COPY . .
RUN pip install --upgrade pip && pip install -r requirements.txt

RUN ["chmod", "+x", "entrypoint.sh"]

ENTRYPOINT ["bash", "entrypoint.sh"]
