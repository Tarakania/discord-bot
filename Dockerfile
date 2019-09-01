FROM python:3.7-alpine

ARG WH_PORT=60000
ENV WH_PORT ${WH_PORT}

# enables proper stdout flushing
ENV PYTHONUNBUFFERED 1

# pip optimizations
ENV PIP_NO_CACHE_DIR 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

WORKDIR /code

RUN apk add --no-cache \
	git

# avoid cache invalidation after copying entire directory
COPY requirements.txt .

RUN apk add --no-cache --virtual build-deps \
		gcc \
		musl-dev && \
    pip install -r requirements.txt && \
    apk del build-deps

EXPOSE ${WH_PORT}

COPY . .

ENTRYPOINT ["python", "tarakania_rpg/main.py"]
