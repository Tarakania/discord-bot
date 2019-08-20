FROM python:3.7-alpine

ARG UID=1500
ARG GID=1500

ARG WH_PORT=8081
ENV WH_PORT ${WH_PORT}

# enables proper stdout flushing
ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN apk add --no-cache \
	git \
	gcc \
	musl-dev

# avoid cache invalidation after copying entire directory
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN apk del \
	gcc \
	musl-dev

EXPOSE ${WH_PORT}

RUN addgroup -g $GID -S tarakania && \
    adduser -u $UID -S discord-bot -G tarakania

COPY . .

RUN chown -R $GID:$UID /code
USER $UID

ENTRYPOINT ["python", "tarakania_rpg/main.py"]
