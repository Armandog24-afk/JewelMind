# CadQuery ships prebuilt manylinux wheels for its OpenCascade bindings
# (cadquery-ocp), so a plain pip install on a slim Debian base is reliable —
# no conda/micromamba needed. See docs/known-limitations.md for details and
# for what has/hasn't been verified for this exact image in this milestone.
FROM python:3.11-slim

# OCP (OpenCascade) and its VTK dependency need a handful of shared
# libraries that are not present in the slim base image.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglu1-mesa \
    libxrender1 \
    libxext6 \
    libsm6 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "jewelmind.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
