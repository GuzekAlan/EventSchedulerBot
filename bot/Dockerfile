FROM python:3.10.0-bullseye

WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

COPY . /app

CMD ["bash", "start.sh"]