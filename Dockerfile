FROM python:3.10
COPY /algo /algo
WORKDIR /algo
RUN pip install --requirements requirements.txt

