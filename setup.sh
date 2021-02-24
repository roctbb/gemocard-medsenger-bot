sudo pip3 install -r requirements.txt
sudo cp agents_gemocard.conf /etc/supervisor/conf.d/
sudo cp agents_gemocard_nginx.conf /etc/nginx/sites-enabled/
sudo supervisorctl update
sudo systemctl restart nginx
sudo certbot --nginx -d gemocard.medsenger.ru
sudo ufw allow 5432