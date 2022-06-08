#!/bin/bash
export FLASK_APP=uvi_flask.py
export FLASK_DEBUG=0
./env_uvi/Scripts/activate

sudo service gunicorn_uvi stop
nohup python -u monitor_corpora.py &
echo $! >> "monitor_script_PID"

#exec gunicorn -w 4 -b 127.0.0.1:4000 uvi_flask:app
sudo service gunicorn_uvi start
