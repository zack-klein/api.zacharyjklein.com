set -ex

gunicorn -w 2 --bind 0.0.0.0:5000 --timeout 120 app:app
