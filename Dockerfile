FROM python:3.10.7
USER root

WORKDIR /app
COPY . /app

RUN pip install --upgrade -r /app/requirements.txt

RUN apt-get update
RUN apt-get install -y google-chrome
RUN apt-get install -y chromedriver

CMD ["python", "bot.py"]