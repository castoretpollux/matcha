# Development vs Production

As described in [INSTALLATION](/docs/INSTALLATION.md), Matcha can be launched by :

```
python launch.py dev
```

This must be considered as suitable for development purposes only

# Production Recommandations

For production configuration, we recommend to use :

- Supervisord to manage all process (except Nginx and PostgreSQL)
- Nginx, for its performance and reverse proxy features
- Daphne ASGI server
- Django rqworker and rqscheduler

Below, you'll find our supervisor configuration file.

In our case :
- castor is our main user, and /home/castor is its hime
- all virtual environments are created in /home/castor/.virtualenvs/matcha, using virtualenvwrapper

Matcha supervisor conf file :

```
[fcgi-program:matcha_backend]
# TCP socket used by Nginx backend upstream
socket=tcp://localhost:9010

# specify settings
environment=DJANGO_SETTINGS_MODULE="matcha.settings"

# Directory where your site's project files are located
directory=/home/castor/matcha

# Each process needs to have a separate socket file, so we use process_num
# Make sure to update "mysite.asgi" to match your project name
command=/home/castor/.virtualenvs/matcha/bin/daphne -u /home/castor/matcha/run/daphne%(process_num)d.sock --fd 0 --access-log - --proxy-headers matcha.asgi:application

# Number of processes to startup, roughly the number of CPUs you have
numprocs=4

# Give each process a unique name so they can be told apart
process_name=matcha%(process_num)d

# Automatically start and recover processes
autostart=true
autorestart=true

# Choose where you want your log to go
stdout_logfile=/var/www/matcha/logs/gunicorn/gunicorn_stdout.log
redirect_stderr=true

[program:matcha_defaultworker1]
directory=/home/castor/matcha
command=/bin/bash -c 'source /home/castor/.virtualenvs/matcha/bin/activate && python manage.py rqworker default'
autostart=true
autorestart=true
stdout_logfile=/var/www/matcha/logs/workers/defaultworker1.log
redirect_stderr=true
priority = 4
startretries = 1000

[program:matcha_defaultworker2]
directory=/home/castor/matcha
command=/bin/bash -c 'source /home/castor/.virtualenvs/matcha/bin/activate && python manage.py rqworker default'
autostart=true
autorestart=true
stdout_logfile=/var/www/matcha/logs/workers/defaultworker2.log
redirect_stderr=true
priority = 4
startretries = 1000

[program:matcha_defaultworker3]
directory=/home/castor/matcha
command=/bin/bash -c 'source /home/castor/.virtualenvs/matcha/bin/activate && python manage.py rqworker default'
autostart=true
autorestart=true
stdout_logfile=/var/www/matcha/logs/workers/defaultworker3.log
redirect_stderr=true
priority = 4
startretries = 1000

[program:matcha_defaultworker4]
directory=/home/castor/matcha
command=/bin/bash -c 'source /home/castor/.virtualenvs/matcha/bin/activate && python manage.py rqworker default'
autostart=true
autorestart=true
stdout_logfile=/var/www/matcha/logs/workers/defaultworker4.log
redirect_stderr=true
priority = 4
startretries = 1000

[program:matcha_populateworker1]
directory=/home/castor/matcha
command=/bin/bash -c 'source /home/castor/.virtualenvs/matcha/bin/activate && python manage.py rqworker populate'
autostart=true
autorestart=true
stdout_logfile=/var/www/matcha/logs/workers/populateworker1.log
redirect_stderr=true
priority = 4
startretries = 1000

[program:matcha_populateworker2]
directory=/home/castor/matcha
command=/bin/bash -c 'source /home/castor/.virtualenvs/matcha/bin/activate && python manage.py rqworker populate'
autostart=true
autorestart=true
stdout_logfile=/var/www/matcha/logs/workers/populateworker2.log
redirect_stderr=true
priority = 4
startretries = 1000

[program:searchapp]
command=/home/castor/matcha/processes/searchapp/gunicorn_start.sh
user=castor
stdout_logfile=/home/castor/matcha/processes/searchapp/logs/gunicorn/gunicorn_stout.log
stderr_logfile=/home/castor/matcha/processes/searchapp/logs/gunicorn/gunicorn_sterr.log
redirect_stderr=True
autostart=True
autorestart=True
startsecs=3

[program:matcha_searchworker1]
directory=/home/castor/matcha/processes/searchapp
command=/bin/bash -c 'source /home/castor/.virtualenvs/searchapp/bin/activate && python manage.py rqworker search'
autostart=true
autorestart=true
stdout_logfile=/var/www/matcha/logs/workers/searchworker1.log
redirect_stderr=true
priority = 4
startretries = 1000

[program:matcha_searchworker2]
directory=/home/castor/matcha/processes/searchapp
command=/bin/bash -c 'source /home/castor/.virtualenvs/searchapp/bin/activate && python manage.py rqworker search'
autostart=true
autorestart=true
stdout_logfile=/var/www/matcha/logs/workers/searchworker2.log
redirect_stderr=true
priority = 4
startretries = 1000
```

Regarding Nginx, here is our configuration file :

```
upstream matcha {
    # The port must be the same than the one defined in fcgi-program:matcha_backend
    server localhost:9010;
}

server {
    server_name domain.tld; # TODO : Adapt to your needs

    # Note that nginx will serve the static files for the frontend
    root /home/castor/matcha/frontend/dist;

    access_log /var/www/matcha/logs/website/nginx/access.log;
    error_log /var/www/matcha/logs/website/nginx/error.log;

    client_max_body_size 100M;

    location /static {
        alias /var/www/matcha/website/static;
    }

    # This will serve media that have been uploaded to matcha app
    location /media/uploaded {
        alias /var/www/matcha/website/media/uploaded;
    }

    # ditto
    location /media/downloaded {
        alias /var/www/matcha/website/media/downloaded;
    }

    # This will serve media that have been uploaded to searchapp app
    location /media/uploads {
        alias /var/www/matcha/website/mediasearch/uploads;
    }

    # Classical Django admin may be made available by uncommenting the following lines
    #
    # location ~ ^/(admin|django-rq) {
    #     proxy_redirect      off;
    #     proxy_set_header    Host                    $host;
    #     proxy_set_header    X-Real-IP               $remote_addr;
    #     proxy_set_header    X-Forwarded-For         $proxy_add_x_forwarded_for;
    #     proxy_set_header    X-Forwarded-Protocol    $scheme;
    #     proxy_set_header    X-Forwarded-Port        443;
    #     proxy_pass          http://matcha;
    #     auth_basic "Acces restreint";
    #     auth_basic_user_file /var/www/matcha/.htpasswd;
    # }

    location /api {
        proxy_redirect      off;
        proxy_set_header    Host                    $host;
        proxy_set_header    X-Real-IP               $remote_addr;
        proxy_set_header    X-Forwarded-For         $proxy_add_x_forwarded_for;
        proxy_set_header    X-Forwarded-Protocol    $scheme;
        proxy_set_header    X-Forwarded-Port        443;
        proxy_pass          http://matcha;
    }

    location /ws {
        proxy_redirect      off;
        proxy_set_header    Host                    $host;
        proxy_set_header    X-Real-IP               $remote_addr;
        proxy_set_header    X-Forwarded-For         $proxy_add_x_forwarded_for;
        proxy_set_header    X-Forwarded-Protocol    $scheme;
        proxy_set_header    X-Forwarded-Port        443;
        proxy_set_header    Upgrade $http_upgrade;
        proxy_set_header    Connection "upgrade";
        proxy_pass          http://matcha;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }

    listen 443 ssl;
    ssl_certificate /path/to/fullchain.pem; # TODO : Adapt to your needs
    ssl_certificate_key /path/to/privkey.pem; # TODO : Adapt to your needs
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

}

server {
    # change domain.tld to your server's name to fit your needs :
    if ($host = domain.tld) {
        return 301 https://$host$request_uri;
    }

    server_name domain.tld;

    listen 80;
    return 404;
}
```