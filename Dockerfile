FROM python:3.8-slim-buster

RUN adduser --gecos "" --disabled-password debian

WORKDIR /home/debian/api

COPY ./requirements.txt /home/debian/api/requirements.txt

RUN pip install --upgrade pip && \
    pip install --upgrade -r /home/debian/api/requirements.txt

RUN pip install -i https://test.pypi.org/simple/ jana

RUN python -m nltk.downloader -d /usr/local/share/nltk_data popular

COPY ./ /home/debian/api/

ENV PYTHONPATH=/home/debian/api
ENV PATH="/home/debian/.local/bin:$PATH"

RUN chown -R debian /home/debian/api

USER debian

CMD ["sh", "scripts/entrypoint.sh"]
