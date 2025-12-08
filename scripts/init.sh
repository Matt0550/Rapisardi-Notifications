#!/bin/bash

# Export env vars for cron
# Filter out LANG to avoid warning about /etc/environment deprecation for locale
printenv | grep -v "^LANG=" > /etc/environment

# Start cron
service cron start

if [ ! -z "$PUID" ] && [ ! -z "$PGID" ]; then
    groupmod -g $PGID $APP_USER
    usermod -u $PUID -g $PGID $APP_USER

    chown -R $PUID:$PGID /home

    exec gosu $APP_USER python3 /home/src/main.py
else
    chown -R 0:0 /home
    
    exec python3 /home/src/main.py
fi