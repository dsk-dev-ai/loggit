FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    GIT_TERMINAL_PROMPT=0

WORKDIR /repo

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && git config --global --add safe.directory '*'

COPY pyproject.toml README.md ./
COPY loggit ./loggit

RUN pip install --no-cache-dir .

ENTRYPOINT ["loggit"]
CMD ["--help"]
