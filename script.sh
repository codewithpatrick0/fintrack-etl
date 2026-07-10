#!/bin/bash
cd /app
python analisis.py >> /var/log/cron.log 2>&1