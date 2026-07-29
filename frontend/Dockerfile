# Build context is the repository root (see docker-compose.yml) because the
# frontend imports shared/* via a path alias that must exist on disk one
# directory above /app for Vite's dev-server module resolution to find it.
#
# Runs the Vite dev server rather than a production nginx build — acceptable
# for this technical-prototype milestone; see docs/known-limitations.md for
# the production-build follow-up.
FROM node:20-slim

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend/ .
COPY shared/ /shared

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
