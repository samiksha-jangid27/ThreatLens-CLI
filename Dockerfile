FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    THREATLENS_DATA_DIR=/data

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir . \
    && useradd --create-home --uid 10001 threatlens \
    && mkdir /data && chown threatlens:threatlens /data
USER threatlens
VOLUME ["/data"]
ENTRYPOINT ["threatlens"]
CMD ["--help"]
