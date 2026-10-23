# syntax=docker/dockerfile:1

# ---- Build stage: Node only exists here ----
FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
ARG APP_VERSION=dev
ENV VITE_APP_VERSION=${APP_VERSION}
RUN npm run build

# ---- Runtime stage: static files served by nginx as a non-root user (UID 101) ----
FROM nginxinc/nginx-unprivileged:1.31-alpine
ARG APP_VERSION=dev
LABEL org.opencontainers.image.title="stockpilot-frontend" \
      org.opencontainers.image.revision="${APP_VERSION}"
ENV BACKEND_URL=http://backend:8000 \
    NGINX_ENTRYPOINT_LOCAL_RESOLVERS=1
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
