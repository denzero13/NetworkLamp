FROM python:3.8-slim-buster

RUN mkdir network_lamp_app
WORKDIR network_lamp_app
RUN python -m pip install --upgrade pip

COPY SNMPscan/ ./

RUN pip install -r requirements.txt

CMD [ "gunicorn", "--workers=5", "--threads=1", "--name=APP_NAME", "-b 0.0.0.0:8051", "wsgi:server"]
