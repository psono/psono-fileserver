crond -b -L /var/log/cron/cron.log
# tail -f /var/log/cron/cron.log &
python3 /root/psono/manage.py migrate && uwsgi --ini /root/configs/docker/psono_uwsgi_port.ini