sudo pip3 install -r requirements.txt
sudo cp gemocard.ini /etc/uwsgi/apps/
sudo cp agents_gemocard.conf /etc/supervisor/conf.d/
sudo cp agents_gemocard_nginx.conf /etc/nginx/sites-enabled/
sudo supervisorctl update
sudo systemctl restart nginx
sudo certbot --nginx -d gemocard.medsenger.ru
