import requests, json

resp = requests.get(
    'https://api.wavespeed.ai/api/v3/models',
    headers={'Authorization': 'Bearer wsk_live_MWD0E5QYAIV4CP2S3ya2QPZvTApxlw8oBSqPaeLIZ-E'},
    timeout=15
)
data = resp.json()['data']
for m in data:
    print(f"{m['model_id']:70s} ${m['base_price']} ({m['type']})")
