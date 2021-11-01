This is a note for myself on setting up this application in a production environment.

TODO: consider deploying in a docker container

# Requirements

This is mandatory for the app to run:
- **Python 3.9+**, packages from **requirements.txt**

These are my choices for the production environment. 
You can use other things, but the scripts/configs in this repo assume you use them:
- **nginx** as a reverse proxy
- **systemd** for managing the app as a service (restarting on reboot and crashes, etc.)
- [**certbot**](https://certbot.eff.org/about/) for managing TLS certificates (to support HTTPS)

Also, make sure that ports 80 and 443 are open on firewall (e.g., `ufw allow 'Nginx FULL'`)

# Cloning the project and setting up a virtual environment
```bash
$ git clone https://github.com/anorlovsky/murmansk-culture-api.git
$ cd murmansk-culture-api
$ python -m venv env
$ source env/bin/activate
$ pip install -r requirements
```

# Setting up nginx as a reverse proxy
```bash
$ cp deployment/nginx_murmansk-culture-api.conf /etc/nginx/conf.d/
$ nginx -t
$ nginx -s reload
```

# Enabling HTTPS support
I'm using [certbot](https://certbot.eff.org/lets-encrypt/debianbuster-nginx) to register TLS certificates and modify nginx config to use them.

```bash
$ certbot --nginx
```

# Setting up a systemd service
```
$ cp deployment/systemd_murmansk-culture-api.service ~/.config/systemd/user/murmansk-culture-api.service
$ systemctl --user start murmansk-culture-api  
$ systemctl --user enable murmansk-culture-api  
$ systemctl --user status murmansk-culture-api
$ loginctl enable-linger <user>
```

# Resources
- https://fastapi.tiangolo.com/deployment/concepts/
- https://fastapi.tiangolo.com/advanced/behind-a-proxy
- https://www.uvicorn.org/deployment/#running-behind-nginx
- https://wiki.archlinux.org/title/Systemd/User
	- [systemd user lingering](https://wiki.archlinux.org/title/Systemd/User#Automatic_start-up_of_systemd_user_instances) 
