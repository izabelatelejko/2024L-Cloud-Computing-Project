FROM mirror.gcr.io/library/python:3.8
WORKDIR /
COPY requirements.txt /requirements.txt
COPY src/pipelines /src/pipelines
RUN pip install --upgrade pip && pip install -r requirements.txt
ENTRYPOINT [ "bash" ]