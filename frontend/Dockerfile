FROM nginx:alpine

# Copy the HTML file as a template
COPY index.html /usr/share/nginx/html/index.html.template

# Use envsubst to replace BACKEND_URL and start nginx
CMD ["/bin/sh", "-c", "envsubst '${BACKEND_URL}' < /usr/share/nginx/html/index.html.template > /usr/share/nginx/html/index.html && exec nginx -g 'daemon off;'"]

EXPOSE 80
