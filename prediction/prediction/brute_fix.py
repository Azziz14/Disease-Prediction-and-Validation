import os
import re

def brute_force_fix():
    src_dir = os.path.join("frontend", "src")
    
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace the double nested mess
                # `${process.env.REACT_APP_API_URL || `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}'}/api
                
                # The easiest way: just replace ALL process.env things back to http://${window.location.hostname}:5000
                content = re.sub(
                    r"\`\$\{process\.env\.REACT_APP_API_URL \|\| `\$\{process\.env\.REACT_APP_API_URL \|\| 'http://localhost:5000'\}[`'\"]\}",
                    r"http://${window.location.hostname}:5000",
                    content
                )
                content = re.sub(
                    r"\$\{process\.env\.REACT_APP_API_URL \|\| `\$\{process\.env\.REACT_APP_API_URL \|\| 'http://localhost:5000'\}[`'\"]\}",
                    r"http://${window.location.hostname}:5000",
                    content
                )
                content = content.replace(
                    "${process.env.REACT_APP_API_URL || `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}'}",
                    "http://${window.location.hostname}:5000"
                )
                content = content.replace(
                    "`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}'",
                    "`http://${window.location.hostname}:5000`"
                )
                content = content.replace(
                    "`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}\"",
                    "`http://${window.location.hostname}:5000`"
                )
                content = content.replace(
                    "${process.env.REACT_APP_API_URL || 'http://localhost:5000'}",
                    "http://${window.location.hostname}:5000"
                )

                # Now do a CLEAN single-pass replacement for PROD
                # ONLY match exact strings that are safe
                content = content.replace(
                    "`http://${window.location.hostname}:5000",
                    "`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}"
                )
                content = content.replace(
                    "http://${window.location.hostname}:5000",
                    "${process.env.REACT_APP_API_URL || 'http://localhost:5000'}"
                )
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

if __name__ == "__main__":
    brute_force_fix()
    print("Done")
