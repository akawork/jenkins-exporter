FROM python:3.6-slim

WORKDIR /root/
COPY . .
RUN pip3.6 install -r requirements.txt

EXPOSE 9118
ENTRYPOINT [ "/bin/bash",  "entrypoint.sh" ]
