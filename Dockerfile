FROM python:3.13

WORKDIR /app
RUN mkdir -p /app && chmod -R 777 /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]
