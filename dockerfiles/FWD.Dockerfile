FROM alpine

RUN apk update && apk add mosquitto-clients

RUN apk add python3

RUN apk add py3-pip

RUN pip3 install paho-mqtt

ADD forward.py /

CMD python3 forward.py


