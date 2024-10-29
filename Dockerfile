FROM python:3.11

RUN mkdir -p /wd

WORKDIR /wd

COPY requirements.txt ./requirements.txt

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . ./

EXPOSE $PORT

CMD alembic upgrade head && python3 app/main.py
