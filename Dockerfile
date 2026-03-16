FROM python:3.14@sha256:7aea6827c8787754f99339ffed8cfc41fb09421f9c7d0e77a198b08422a3455e
COPY --from=ghcr.io/astral-sh/uv:0.10.10@sha256:cbe0a44ba994e327b8fe7ed72beef1aaa7d2c4c795fd406d1dbf328bacb2f1c5 /uv /uvx /bin/

WORKDIR /app
ADD README.md pyproject.toml uv.lock ./
RUN uv venv

ADD . .

RUN uv sync --frozen --no-dev


# replace for api server: ["uvicorn", "api_server:app", "--workers", "10", "--loop", "uvloop"]
CMD ["uv", "run", "yt"]
