FROM jupyter/minimal-notebook:python-3.8.8

WORKDIR /testing_service/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

ADD utils /testing_service/utils/
ADD notebooks /testing_service/notebooks/
