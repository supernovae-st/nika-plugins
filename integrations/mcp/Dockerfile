# Nika MCP oracle — read-only stdio server (validate + learn · no execution)
# Runs `nika mcp`: agents validate .nika.yaml workflows and learn the language
# (schema · templates · examples · catalogs). Execution stays on the CLI.
#
# Build:  docker build -t nika-mcp .
# Run:    docker run -i --rm nika-mcp        (stdio JSON-RPC)
# Pin a version: docker build --build-arg NIKA_VERSION=0.116.2 -t nika-mcp .

FROM ubuntu:24.04 AS fetch
ARG NIKA_VERSION=0.116.2
ARG TARGETARCH
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*
RUN set -eu; \
    case "${TARGETARCH}" in \
      amd64) A=x64 ;; \
      arm64) A=arm64 ;; \
      *) echo "unsupported arch: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    T="nika-linux-${A}-${NIKA_VERSION}.tar.gz"; \
    cd /tmp; \
    curl -fsSL -O "https://github.com/supernovae-st/nika/releases/download/v${NIKA_VERSION}/${T}"; \
    curl -fsSL -O "https://github.com/supernovae-st/nika/releases/download/v${NIKA_VERSION}/SHA256SUMS"; \
    grep " ${T}\$" SHA256SUMS | sha256sum -c -; \
    tar -xzf "${T}" -C /usr/local/bin nika; \
    chmod +x /usr/local/bin/nika

FROM ubuntu:24.04
COPY --from=fetch /usr/local/bin/nika /usr/local/bin/nika
# The oracle is offline by design: vendored spec, no network calls of its own.
ENTRYPOINT ["nika", "mcp"]
