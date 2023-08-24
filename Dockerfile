FROM python:3.11.2-alpine3.17
LABEL yuchoba="yu@vtechnology.ru"
RUN apk update && apk upgrade && apk add git && apk add bash
RUN pip install --upgrade pip
RUN ["mkdir", "/app"]
RUN ["mkdir", "/app/db"]
ENV TELEGRAMM_TOKEN="telegramm_token"
ENV DB_PATH="db/sql.db"
RUN apk add --no-cache tzdata
ENV TZ Asia/Yekaterinburg
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /app
COPY ./main.py .
COPY ./images ./images
COPY ./parsers.py .
COPY ./sqltable.py .
COPY ./requirements.txt .
RUN pip install -r requirements.txt

CMD ["python3", "./main.py"]