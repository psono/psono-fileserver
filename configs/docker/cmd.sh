PSONOFS_CRON_ACCESS_KEY=$(</dev/urandom tr -dc A-Za-z0-9 | head -c32)
echo "$PSONOFS_CRON_ACCESS_KEY" > /root/PSONOFS_CRON_ACCESS_KEY
crond -b -L /var/log/cron/cron.log
# tail -f /var/log/cron/cron.log &
python3 /root/psono/manage.py migrate && uwsgi --ini /root/configs/docker/psono_uwsgi_port.ini