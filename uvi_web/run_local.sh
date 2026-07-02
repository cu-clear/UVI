#!/bin/bash
export FLASK_APP=uvi_flask.py
export FLASK_DEBUG=1
source ./env_uvi/bin/activate

exec flask run
