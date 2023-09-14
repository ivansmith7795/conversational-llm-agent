FROM public.ecr.aws/docker/library/ubuntu:20.04

COPY requirements.txt  .

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt upgrade -y && \
    apt-get install tar wget openssl python3-pip build-essential zlib1g-dev openssl zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev python3-dev python3-pip -y 

# Install Python3.10
RUN wget https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tgz && \
    tar xvf Python-3.10.13.tgz && \
    cd Python-*/ && \
    ./configure --enable-optimizations && \
    make install

RUN update-alternatives --install /usr/local/bin/python python /usr/local/bin/python3.10 1

RUN  pip3 install -r requirements.txt

COPY /src/create_index.py /opt/src/create_index.py

WORKDIR /opt/src/

ENTRYPOINT ["python3", "create_index.py"]