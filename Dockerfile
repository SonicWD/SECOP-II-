# Build UI + API en un solo contenedor (HF Spaces / Render / Railway).
FROM node:22-bookworm-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
ENV STATIC_EXPORT=1
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY api/ /app/
COPY --from=web /web/out /app/static
ENV MODEL_PATH=/app/artifacts/modelo.joblib
ENV STATIC_DIR=/app/static
EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
