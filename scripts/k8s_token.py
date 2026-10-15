#!/usr/bin/env python3
import json
import urllib.request
import urllib.parse
import os

adc_path = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
with open(adc_path) as f:
    c = json.load(f)

data = urllib.parse.urlencode({
    "client_id": c["client_id"],
    "client_secret": c["client_secret"],
    "refresh_token": c["refresh_token"],
    "grant_type": "refresh_token"
}).encode()

req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
res = json.loads(urllib.request.urlopen(req).read().decode())

print(json.dumps({
    "apiVersion": "client.authentication.k8s.io/v1",
    "kind": "ExecCredential",
    "status": {
        "token": res["access_token"]
    }
}))
