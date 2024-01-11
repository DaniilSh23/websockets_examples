FROM python:3.11

RUN mkdir "websocket_example"
COPY requirements.txt /websocket_example/

RUN apt-get update && apt-get install -y build-essential
RUN python -m pip install --no-cache-dir -r /websocket_example/requirements.txt


COPY . /websocket_example/
WORKDIR /websocket_example

EXPOSE 8080
ENTRYPOINT ["/websocket_example/entrypoint.sh"]