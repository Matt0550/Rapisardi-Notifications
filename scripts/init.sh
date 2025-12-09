#!/bin/bash

# Export env vars for cron
python3 -c "import os, shlex; print('\n'.join([f'{k}={shlex.quote(v)}' for k,v in os.environ.items() if k != 'LANG']))" > /etc/environment

# Handle User Permissions first
if [ ! -z "$PUID" ] && [ ! -z "$PGID" ]; then
    groupmod -g $PGID $APP_USER
    usermod -u $PUID -g $PGID $APP_USER
    chown -R $PUID:$PGID /home
else
    chown -R 0:0 /home
fi

# Install crontab for APP_USER
# We use -u to install it for the specific user so jobs run as that user
crontab -u $APP_USER /etc/cron.d/rapisardi-cron

# Setup cron logging
touch /var/log/cron.log
chmod 0666 /var/log/cron.log
# Tail the log file in background so it appears in docker logs
tail -f /var/log/cron.log &

# Start cron
service cron start

# Verify cron is running
if pgrep cron > /dev/null; then
    echo "Cron started successfully. Installed crontab for $APP_USER:"
    crontab -u $APP_USER -l
else
    echo "Failed to start cron"
fi

# Start App
if [ ! -z "$PUID" ] && [ ! -z "$PGID" ]; then
    exec gosu $APP_USER python3 /home/src/main.py
else
    exec python3 /home/src/main.py
fi