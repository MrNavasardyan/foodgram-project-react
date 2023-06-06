FROM python:3.9-slim
RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt /app
RUN apt-get update && apt-get -y install libpq-dev gcc && pip install psycopg2
RUN pip3 install -r requirements.txt --no-cache-dir
COPY ./ /app
CMD ["gunicorn", "foodgram_api.wsgi:application", "--bind", "0:8000" ]