#!/bin/bash
KIBANA_URL="http://localhost:5601"
DASHBOARD_FILE="monitoring/kibana_dashboard.json"

if [ ! -f "$DASHBOARD_FILE" ]; then
  echo "Error: $DASHBOARD_FILE not found. Export it from the Kibana UI first."
  exit 1
fi

echo "Importing Kibana dashboards..."
curl -X POST "$KIBANA_URL/api/saved_objects/_import?overwrite=true" \
  -H "kbn-xsrf: true" \
  --form file=@$DASHBOARD_FILE

echo -e "\nDashboard import complete."