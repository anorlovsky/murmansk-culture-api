This is a note for myself on setting up this application in a production environment.

TODO: consider deploying in a docker container

# Requirements

This is mandatory for the app to run:
- Python 3.9+, packages from requirements.txt

These are my choices for the production environment. 
You can use other things, but the scripts/configs in this repo assume you use them:
- nginx as a reverse proxy
- systemd for managing the app as a service (restarting on reboot and crashes, etc.)

Also, make sure that ports 80 and 443 are open on firewall (e.g., `ufw allow 'Nginx FULL'`)

# Setting up nginx as a reverse proxy
`cp deployment/artmuseum-nginx.conf /etc/nginx/conf.d/`
test your config: `nginx -t`
`nginx -s reload`

# HTTPS support
Use [certbot](https://certbot.eff.org/lets-encrypt/debianbuster-nginx) to register your TLS certificates.
Certbot can optionally modify your nginx config to use the certificates.

# Setting up a systemd service 
`cp deployment/artmuseum.service ~/.config/systemd/user/`
`systemctl --user start artmuseum`
`systemctl --user enable artmuseum`
`loginctl enable-linger <user>`
and make sure it works: `systemctl --user status artmuseum`

# Resources
- https://fastapi.tiangolo.com/deployment/concepts/
- https://fastapi.tiangolo.com/advanced/behind-a-proxy
- https://www.uvicorn.org/deployment/#running-behind-nginx
- https://wiki.archlinux.org/title/Systemd/User
	- [lingering](https://wiki.archlinux.org/title/Systemd/User#Automatic_start-up_of_systemd_user_instances) 