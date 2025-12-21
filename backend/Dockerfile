FROM python:3.10-bookworm

WORKDIR /app

COPY ./dist/api ./api
COPY ./dist/database ./database
COPY ./requirements.txt .

RUN apt-get update
RUN apt-get install -y python3-pip
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
RUN ln -sf /usr/share/zoneinfo/America/Sao_Paulo /etc/timezone && \
    ln -sf /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime 

WORKDIR /app/api

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
