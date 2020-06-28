FROM alpine
# install mosquitto
RUN apk update && apk add mosquitto
# run mosquitto
CMD /usr/sbin/mosquitto
