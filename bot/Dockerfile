FROM python:3.9.17-bullseye

WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

COPY . /app

CMD ["bash", "start.sh"]