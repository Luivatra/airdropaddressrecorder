FROM python:3.9-slim-bullseye
ADD . ./ergo/
ADD ../util ./util/
WORKDIR ./ergo
RUN pip install -r ./requirements.txt
CMD ["python","./bot.py"]