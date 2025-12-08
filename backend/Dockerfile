FROM python:3.8-bullseye

RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install torch --index-url https://download.pytorch.org/whl/cpu

RUN ln -sf /usr/share/zoneinfo/America/Sao_Paulo /etc/timezone && \
    ln -sf /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime 

WORKDIR /app

COPY ./api ./api
COPY ./database/blob_storage ./database/blob_storage
COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/api

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
