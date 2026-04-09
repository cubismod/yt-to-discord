FROM python:3.14@sha256:8428c32065df71d5a7763099ccb8ee215314129b50d395f95ad589151887d52f
COPY --from=ghcr.io/astral-sh/uv:0.11.3@sha256:90bbb3c16635e9627f49eec6539f956d70746c409209041800a0280b93152823 /uv /uvx /bin/

WORKDIR /app
ADD README.md pyproject.toml uv.lock ./
RUN uv venv

ADD . .

RUN uv sync --frozen --no-dev


# replace for api server: ["uvicorn", "api_server:app", "--workers", "10", "--loop", "uvloop"]
CMD ["uv", "run", "yt"]
