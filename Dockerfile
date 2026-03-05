FROM python:3.11-slim

ENV HOME /root
WORKDIR /root

COPY ./requirements.txt ./requirements.txt
COPY ./app.py ./app.py
COPY ./static ./static
COPY ./templates ./templates

RUN pip3 install -r requirements.txt

EXPOSE 8080

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && gunicorn --workers 3 --bind 0.0.0.0:8080 app:app
