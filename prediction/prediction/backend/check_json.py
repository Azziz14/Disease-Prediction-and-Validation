import json

with open('api_output.json', 'r', encoding='utf-8') as f:
    res = json.load(f)

data = res.get('data', {})
print("Keys inside data:")
print(list(data.keys()))

if 'is_flagged' in data:
    print(f"is_flagged: {data['is_flagged']}")
else:
    print("is_flagged is NOT in data!!!")
