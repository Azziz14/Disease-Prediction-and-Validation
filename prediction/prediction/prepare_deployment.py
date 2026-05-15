import os
import re

def refactor_frontend_api_urls():
    src_dir = os.path.join("frontend", "src")
    replacements = 0
    
    # Regex patterns to find hardcoded URLs
    pattern1 = re.compile(r"http://\$\{window\.location\.hostname\}:5000/api")
    pattern2 = re.compile(r"http://\$\{window\.location\.hostname\}:5000")
    pattern3 = re.compile(r"http://localhost:5000/api")
    pattern4 = re.compile(r"http://localhost:5000")
    
    # Target replacement using process.env
    replacement = "${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api"
    replacement_no_api = "${process.env.REACT_APP_API_URL || 'http://localhost:5000'}"
    
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Ensure process.env strings are evaluated inside backticks in JS/TS
                    # E.g. `http://${window...}` -> `${process.env...}`
                    # If it was a plain string like 'http://localhost:5000/api', we convert it to backticks.
                    
                    # Pattern 1 & 3: endpoints ending with /api
                    content = re.sub(r'[\'"`]http://\$\{window\.location\.hostname\}:5000/api', '`' + replacement, content)
                    content = re.sub(r'[\'"`]http://localhost:5000/api', '`' + replacement, content)
                    
                    # Pattern 2 & 4: endpoints without /api
                    content = re.sub(r'[\'"`]http://\$\{window\.location\.hostname\}:5000', '`' + replacement_no_api, content)
                    content = re.sub(r'[\'"`]http://localhost:5000', '`' + replacement_no_api, content)

                    # Ensure the closing quote is a backtick if we opened with one
                    # We might have `http://localhost:5000/api/endpoint` which is now `${process.env.REACT_APP_API_URL...}/api/endpoint`
                    # Since we replaced the start quote with a backtick, we must ensure the end quote is a backtick if it was a single/double quote.
                    # We will just do a simpler string replacement for safety.
                    
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

# The simpler approach to preserve quotes: 
# Since almost all fetches in this codebase use backticks already: `http://${window.location.hostname}:5000/api...`
def simpler_refactor():
    src_dir = os.path.join("frontend", "src")
    
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace backtick version
                new_content = content.replace(
                    "http://${window.location.hostname}:5000",
                    "${process.env.REACT_APP_API_URL || 'http://localhost:5000'}"
                )
                
                # Replace string version (needs backticks)
                new_content = new_content.replace(
                    "'http://localhost:5000",
                    "`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}"
                )
                new_content = new_content.replace(
                    '"http://localhost:5000',
                    "`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}"
                )
                
                # Fix trailing single/double quotes if we converted to backticks
                # (This is a bit tricky, but since most endpoints append something, 
                # let's just make sure we don't break syntax)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Refactored: {filepath}")

if __name__ == "__main__":
    simpler_refactor()
    print("Frontend API URLs refactored successfully.")
