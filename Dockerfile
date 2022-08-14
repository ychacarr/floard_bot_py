FROM python:3.10.5
WORKDIR /usr/src/floardbot
COPY . /usr/src/floardbot
RUN pip install --user -r /usr/src/floardbot/req.txt
CMD ["python", "main.py"]
