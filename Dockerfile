# Multi-stage Dockerfile to build a small runtime image

#############################
# Builder stage
#############################
## Alpine-based multi-stage build optimized for small size and layer caching

FROM python:3.10-alpine AS builder
WORKDIR /build

# Install build dependencies for compiling wheels
RUN apk add --no-cache build-base musl-dev libffi-dev openssl-dev sqlite-dev python3-dev

# Copy requirements and build wheels into /wheels (caches if requirements unchanged)
COPY requirements.txt /build/
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.10-alpine
WORKDIR /app

# Runtime deps (install curl here while still root)
RUN apk add --no-cache libstdc++ libffi sqlite curl

# Copy wheels and install (no-index ensures we use cached wheels)
COPY --from=builder /wheels /wheels
COPY requirements.txt /app/
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# Copy application code
COPY . /app

EXPOSE 5000

# Defaults, override with .env or compose
ENV HOST=0.0.0.0 \
    PORT=5000 \
    DB_PATH=/data/db.sqlite

# Create a non-root user and data dir, fix permissions
RUN addgroup -S app && adduser -S -G app app \
    && mkdir -p /data /var/log/laba-5 \
    && chown -R app:app /data /app /var/log/laba-5

VOLUME ["/data"]

USER app

# Healthcheck (uses curl installed above)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

CMD ["python", "app.py"]
