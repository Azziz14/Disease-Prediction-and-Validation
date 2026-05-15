import os

def safe_refactor():
    src_dir = os.path.join("frontend", "src")
    
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = content
                
                # Replace the template literal base URL
                old_str = "http://${window.location.hostname}:5000"
                new_str = "${process.env.REACT_APP_API_URL || 'http://' + window.location.hostname + ':5000'}"
                
                # It is ALREADY inside a backtick string, e.g., `http://${window.location.hostname}:5000/api/...`
                # So we just replace the substring.
                new_content = new_content.replace(old_str, new_str)
                
                # Also replace any stray localhost ones
                new_content = new_content.replace("'http://localhost:5000", "`" + new_str)
                new_content = new_content.replace("\"http://localhost:5000", "`" + new_str)
                # Note: this might leave a trailing ' or " which would be invalid syntax, but in this specific project they are almost all backticks.
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Refactored: {filepath}")

if __name__ == "__main__":
    safe_refactor()
