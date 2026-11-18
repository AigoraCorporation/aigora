# Curriculum Graph gRPC API (ADR-007). Also used as the one-shot graph publisher.
FROM python:3.12.8-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    GRPC_PORT=50051

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
RUN pip install .

COPY data ./data

RUN useradd --system --uid 10001 --no-create-home aigora
USER aigora

EXPOSE 50051

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=6 \
    CMD ["python", "-m", "aigora.curriculum_graph.presentation.grpc.healthcheck"]

CMD ["python", "-m", "aigora.curriculum_graph.bootstrap"]
