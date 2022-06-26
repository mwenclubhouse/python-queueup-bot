docker run -d \
    --name container-name \
    -v bucket:/app/bucket \
    --env-file .env \
    -p 2000:8000  \
    queueup-bot 
