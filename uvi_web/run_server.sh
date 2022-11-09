#!/bin/bash -x
export FLASK_APP=/data/verbnet-service/UVI_deployable/uvi_web/uvi_flask.py
export FLASK_DEBUG=0
# source /data/verbnet-service/UVI_deployable/uvi_web/env_uvi/bin/activate && echo "Virtual Environment Activated"

VIRTUAL_ENV=/data/verbnet-service/UVI_deployable/uvi_web/env_uvi
PATH=/data/verbnet-service/UVI_deployable/uvi_web/env_uvi/bin:$PATH

nohup python -u monitor_corpora.py &
echo $! >> "monitor_script_PID"

exec gunicorn -w 4 -b 127.0.0.1:4000 uvi_flask:app