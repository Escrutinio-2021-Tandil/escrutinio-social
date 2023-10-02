docker rm -f es-app
docker run -d -p 80:8000 --name es-app -v .:/src --env-file .env-deploy app
