#!/bin/bash
export FLASK_APP=uvi_flask.py
export FLASK_DEBUG=1

nohup python monitor_corpora.py &

exec flask run
