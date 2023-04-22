FROM python:3.9-slim
RUN mkdir -p /revchat
COPY . /revchat
WORKDIR /revchat
RUN pip3 install -r requirements.txt
RUN pip3 install flask
EXPOSE 8080
CMD ["python", "app.py"]