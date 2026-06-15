FROM python:3.14@sha256:2081144b23b38daa7fae3b7ee4b42cf2f858d88b0452736274aafaba96f3a6b6
COPY --from=ghcr.io/astral-sh/uv:0.11.21@sha256:ff07b86af50d4d9391d9daf4ff89ce427bc544f9aae87057e69a1cc0aa369946 /uv /uvx /bin/

WORKDIR /app
ADD README.md pyproject.toml uv.lock ./
RUN uv venv

ADD . .

RUN uv sync --frozen --no-dev


# replace for api server: ["uvicorn", "api_server:app", "--workers", "10", "--loop", "uvloop"]
CMD ["uv", "run", "yt"]
