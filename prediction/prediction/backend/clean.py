import os

for root, _, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    text = file.read()
                new_text = text.replace('[OK]', '[OK]').replace('[ERROR]', '[ERROR]').replace('->', '->').replace('[WARNING]', '[WARNING]')
                if new_text != text:
                    with open(path, 'w', encoding='utf-8') as file:
                        file.write(new_text)
                    print(f'Cleaned {path}')
            except Exception as e:
                print(f"Skipping {path} due to error: {e}")
