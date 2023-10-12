FROM python:3.9

WORKDIR /export_service/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD app /export_service/app/

ENV ROOT_S3_KEY_NAME=janusgraph_ml \
    AWS_ACCESS_KEY_ID=123 \
    AWS_SECRET_ACCESS_KEY=12345678 \
    CHUNK_SIZE=32768 \
    GREMLIN_BATCH_SIZE=512
