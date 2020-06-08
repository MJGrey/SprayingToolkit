FROM python:3-alpine

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

WORKDIR /sprayingtoolkit

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "atomizer.py" ]
