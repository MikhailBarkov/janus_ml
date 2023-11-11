FROM python:3.9

WORKDIR /export_service/

ADD app /export_service/app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV ROOT_S3_KEY_NAME=janusgraph_ml \
    AWS_ACCESS_KEY_ID=123 \
    AWS_SECRET_ACCESS_KEY=12345678 \
    CHUNK_SIZE=32768 \
    JANUSGRAPH_POOL_SIZE=4 \
    JASNUGRAPH_MAX_CONTENT_LENGTH=262144 \
    JANUSGRAPH_BATCH_SIZE=700
