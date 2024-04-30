FROM python:3.10.12

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 7755

CMD ["bash","run.sh"]