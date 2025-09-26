FROM alpine:3.21 AS build

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

FROM python:3.12-slim-bookworm

COPY --from=build /root/.local/bin/uv /root/.local/bin/uvx /bin/

WORKDIR /app

COPY ./pyproject.toml .

RUN uv sync 

COPY . .

EXPOSE 8080

CMD ["uv","run","src/main.py"]