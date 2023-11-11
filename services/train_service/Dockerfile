FROM bitnami/pytorch

WORKDIR /train_service/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD app /train_service/app/
ADD config /train_service/config/

ENV num_search_trials=10 \
    batch_size=1024 \
    ml_device=cpu \
    aws_access_key_id=123 \
    aws_secret_access_key=12345678 \
    chunk_size=32768 \
    util_bucket=util-bucket \
    util_dir_s3_key=util_dir \
    create_endpoint_url=http://endpoint_service:8084/create_endpoint \
