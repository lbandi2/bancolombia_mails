#!/bin/bash

mkdir -p logs
cd /home/sergio/scripts/cashflow/
. ./env/bin/activate
/home/sergio/scripts/cashflow/env/bin/python3 /home/sergio/scripts/cashflow/main.py >> logs/cashflow-"`date +"%Y-%m-%d_%H.%M.%S"`".log 2>&1
deactivate
