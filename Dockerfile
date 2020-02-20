FROM python:3.6-alpine

ENV FLASK_APP dashboard.py
ENV FLASK_CONFIG development

WORKDIR /home/dashboard

COPY . .

RUN pip install -r requirements.txt

# runtime configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]