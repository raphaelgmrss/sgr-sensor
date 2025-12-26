#!/usr/bin/env bash
set -e

export API_URL

cat << EOF > /usr/share/nginx/html/env.js
window.__ENV__ = {
  API_URL: "$API_URL"
};
EOF

gunicorn \
  --chdir /app/api \
  --bind 0.0.0.0:5000 \
  run:app &

exec nginx -g "daemon off;"
