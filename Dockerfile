FROM python:3.10-slim AS backend

WORKDIR /app

COPY backend/requirements.txt .
COPY backend/build/dist .


FROM node:20-alpine AS frontend

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci

COPY frontend .
RUN npm run build


FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=backend /app /app
COPY backend/requirements.txt .
RUN apt-get update && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu --no-deps

COPY --from=frontend /frontend/dist /usr/share/nginx/html

RUN rm -f /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/sites-enabled/default

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80 5000

CMD ["/entrypoint.sh"]
