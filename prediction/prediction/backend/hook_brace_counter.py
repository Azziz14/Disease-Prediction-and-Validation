import re

with open(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\DoctorDashboard.tsx", 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

lines = content.split('\n')

# Let's find all functions and hooks and print their brace counts
hooks = [
    ('useAuth', 'const { user } = useAuth();'),
    ('fetchAssignedPatients', 'const fetchAssignedPatients = React.useCallback('),
    ('fetchInboxHistory', 'const fetchInboxHistory = React.useCallback('),
    ('useEffect inbox', 'useEffect(() => {\n    if (activeTab === \'inbox\')'),
    ('handleSendInbox', 'const handleSendInbox = async (e: React.FormEvent) =>'),
    ('fetchChat', 'const fetchChat = () =>'),
    ('handleSendMessage', 'const handleSendMessage = async (e: React.FormEvent) =>'),
    ('clearNotifications', 'const clearNotifications = async () =>'),
    ('handleSearch', 'const handleSearch = async (e?: React.FormEvent, overrideQuery?: string) =>'),
    ('startVoiceSearch', 'const startVoiceSearch = () =>'),
    ('return (', 'return (')
]

# Find start indexes for all of these
positions = []
for name, target in hooks:
    idx = content.find(target)
    if idx != -1:
        positions.append((name, idx))
    else:
        print(f"Could not find: {name}")

positions.sort(key=lambda x: x[1])

for i in range(len(positions)):
    name, start = positions[i]
    end = positions[i+1][1] if i + 1 < len(positions) else len(content)
    chunk = content[start:end]
    opens = chunk.count('{')
    closes = chunk.count('}')
    print(f"{name}: opens={opens}, closes={closes}, diff={opens-closes}")
