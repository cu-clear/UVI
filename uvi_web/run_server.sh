#!/bin/bash
export FLASK_APP=uvi_flask.py
export FLASK_DEBUG=0

nohup python -u monitor_corpora.py &
echo $! > "monitor_script_PID"

exec flask run
