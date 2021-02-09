FROM python:3.7

COPY . /data/python

WORKDIR /data/python

RUN chmod +x /data/python/run.sh && pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["/data/python/run.sh"]