FROM bitnami/pytorch

WORKDIR /processing_service/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

ADD app /processing_service/app/

ENV AWS_ACCESS_KEY_ID=123 \
    AWS_SECRET_ACCESS_KEY=12345678 \
    CHUNK_SIZE=32768 \
    UTIL_BUCKET=util-bucket \
    ENCODERS_DATA_KEY=encoders