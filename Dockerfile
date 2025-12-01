FROM python:3.14@sha256:edf6433343f65f94707985869aeaafe8beadaeaee11c4bc02068fca52dce28dd
COPY --from=ghcr.io/astral-sh/uv:0.9.13@sha256:f07d1bf7b1fb4b983eed2b31320e25a2a76625bdf83d5ff0208fe105d4d8d2f5 /uv /uvx /bin/

WORKDIR /app
ADD README.md pyproject.toml uv.lock ./
RUN uv venv

ADD . .

RUN uv sync --frozen --no-dev


# replace for api server: ["uvicorn", "api_server:app", "--workers", "10", "--loop", "uvloop"]
CMD ["uv", "run", "yt"]
