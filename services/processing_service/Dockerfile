FROM bitnami/pytorch

WORKDIR /processing_service/

ADD app /processing_service/app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV AWS_ACCESS_KEY_ID=123 \
    AWS_SECRET_ACCESS_KEY=12345678 \
    CHUNK_SIZE=32768 \
    UTIL_BUCKET=util-bucket \
    ENCODERS_DATA_KEY=encoders