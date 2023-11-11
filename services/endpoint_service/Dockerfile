FROM bitnami/pytorch

WORKDIR /endpoint_service/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD app /endpoint_service/app/

ENV UTIL_S3_PATH=http://s3:9000 \
    UTIL_BUCKET=util-bucket \
    ENDPOINTS_CONFIG_S3_KEY=endpoints/endpoints_config.json \
    JANUS_ENDPOINT_PARAMS='{"endpoint": "ws://janusgraph:8182/gremlin"}' \
    EXPORT_SERVICE_URL=http://export_service:8081/export \
    PROCESSING_SERVICE_URL=http://processing_service:8082/processing \
    CHUNK_SIZE=32768 \
    AWS_ACCESS_KEY_ID=123 \
    AWS_SECRET_ACCESS_KEY=12345678 \
    MODEL_KEY_MAP='{"SAGE": "models/SAGE.bin"}'
