FROM nginx:alpine

ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache bash &&\
    apk add --no-cache python3 &&\
    apk add --no-cache jq &&\
    apk add --no-cache curl &&\
    apk add --no-cache openssh-client &&\
    apk add --no-cache supervisor

COPY config/nginx.conf /etc/nginx/nginx.conf
RUN rm /etc/nginx/conf.d/default.conf

COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /var/www/html && mkdir -p /var/log/supervisor

WORKDIR /var/www/html

RUN wget https://wordpress.org/latest.tar.gz && \
    tar -zxvf latest.tar.gz && \
    rm -rf /var/www/html/latest.tar.gz

RUN chown -R nginx.nginx /var/www/html && \
    chown -R nginx.nginx /run && \
    chown -R nginx.nginx /var/log/nginx


ENTRYPOINT ["/docker-entrypoint.sh"]

STOPSIGNAL SIGQUIT

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

EXPOSE 8080