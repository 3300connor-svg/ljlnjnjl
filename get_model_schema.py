import requests, json, sys

model_id = sys.argv[1] if len(sys.argv) > 1 else "wavespeed-ai/flux-2-dev/edit"
resp = requests.get(
    'https://api.wavespeed.ai/api/v3/models',
    headers={'Authorization': 'Bearer wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E'},
    timeout=15
)
data = resp.json()['data']
for m in data:
    if m['model_id'] == model_id:
        print(json.dumps(m, indent=2))
        break
