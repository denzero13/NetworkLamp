FROM python:3.8-slim-buster

RUN mkdir NetworkLamp
WORKDIR NetworkLamp
COPY SNMPscan/ ./

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["gunicorn","--workers=15","--name=SCAN", "main:run"]
CMD [ "gunicorn", "--workers=5", "--threads=1", "--name=APP_NAME", "-b 0.0.0.0:8051", "wsgi:server"]
