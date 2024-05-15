docker build --progress=plain -t sanghyunc7/sox_batch_processor .
docker build --no-cache --progress=plain -t sanghyunc7/sox_batch_processor .

docker run -it sox_batch_processor
docker push sanghyunc7/sox_batch_processor:latest
