# strainshare — analysis image (pure-Python half: analyze / benchmark / diagnostic / plots).
# The heavy mapping/profiling steps (bowtie2, inStrain, StrainGE, MetaPhlAn) run via the
# conda `environment.yml` on a cluster; this image is the portable analysis + CLI.
FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/jyu9675/bioai-strainshare"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app
COPY pyproject.toml README.md ./
COPY strainshare ./strainshare
RUN pip install --no-cache-dir .

# smoke-check the install at build time
RUN strainshare version && strainshare benchmark --selftest

ENTRYPOINT ["strainshare"]
CMD ["--help"]
