#!/bin/bash
# scripts/auto_restart.sh

LOG_FILE="/tmp/auto_restart.log"
echo "[$(date)] Running health check..." >> $LOG_FILE

# Check if pricing-api container is running
if ! docker ps --format '{{.Names}}' | grep -q "^pricing-api$"; then
    echo "[$(date)] pricing-api is down! Attempting restart..." >> $LOG_FILE
    docker restart pricing-api >> $LOG_FILE 2>&1
    sleep 5
    
    # Verify if remediation worked
    if ! docker ps --format '{{.Names}}' | grep -q "^pricing-api$"; then
        echo "[$(date)] CRITICAL: pricing-api failed to restart." >> $LOG_FILE
        exit 1
    fi
fi

echo "[$(date)] All services healthy." >> $LOG_FILE
exit 0