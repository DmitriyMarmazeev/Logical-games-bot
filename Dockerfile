FROM python:3.11-slim

WORKDIR /app

COPY ./app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app .

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

VOLUME /app/data

EXPOSE $PORT

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "main.py"]