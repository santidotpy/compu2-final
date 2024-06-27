FROM python:3.10.12

ADD chat/server.py /chat/server.py

COPY requirements.txt ./

RUN pip install -r requirements.txt
# # Copy the credentials file
COPY credentials.json .

RUN pwd && ls


EXPOSE 55555

CMD [ "python", "/chat/server.py" ]
