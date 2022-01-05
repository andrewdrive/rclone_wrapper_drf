FROM python:3.8.10
ENV PYTHONUNBUFFERED=1

RUN mkdir /rclone
WORKDIR /rclone
ADD ./ /rclone/
RUN apt-get update
RUN apt install -y --allow-downgrades nano

RUN unzip rclone-v1.56.2-linux-amd64.zip && dir && cd rclone-v1.56.2-linux-amd64 \
            && cp rclone /usr/bin/ && \
            chown root:root /usr/bin/rclone && \
            chmod 755 /usr/bin/rclone