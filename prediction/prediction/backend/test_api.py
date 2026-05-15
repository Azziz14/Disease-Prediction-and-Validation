import urllib.request
import json

url = "http://127.0.0.1:5000/api/dashboard-data?role=doctor&user_id=69e80f3b9d1175f220760881"
try:
    req = urllib.request.urlopen(url)
    res = json.loads(req.read().decode('utf-8'))
    with open('api_output.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print("Saved to api_output.json")
except Exception as e:
    import urllib.error
    if isinstance(e, urllib.error.HTTPError):
        print(f"HTTPError: {e.read().decode('utf-8')}")
    else:
        print(f"Error: {e}")
