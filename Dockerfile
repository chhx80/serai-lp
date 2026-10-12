# Static site served by nginx (for Dokploy: build type Dockerfile, port 80).
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html support.html privacy.html 404.html robots.txt sitemap.xml llms.txt /usr/share/nginx/html/
COPY assets /usr/share/nginx/html/assets
EXPOSE 80
