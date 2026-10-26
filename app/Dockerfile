# Meta Builder web server in a container. Build from the repo root (it needs the built index.html):
#   docker build -f app/Dockerfile -t meta-builder .
#   docker run -p 3000:3000 meta-builder
FROM node:22-alpine
WORKDIR /srv/app
ENV NODE_ENV=production PORT=3000 HOST=0.0.0.0
COPY app/package.json app/server.js ./
COPY index.html ./www/index.html
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:3000/healthz || exit 1
CMD ["node", "server.js"]
