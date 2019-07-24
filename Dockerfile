FROM python:3.6-slim

WORKDIR /root/

COPY . .

RUN pip3.6 install -r requirements.txt

EXPOSE 9118
ENV JENKINS_CONFIG_FILE="config/config.ini"
ENV DEBUG=0

ENTRYPOINT [ "python3.6",  "./jenkins_exporter.py" ]