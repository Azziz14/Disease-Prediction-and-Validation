import os

def fix_broken_syntax():
    src_dir = os.path.join("frontend", "src")
    
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Undo the double replacement
                bad_string = "`${process.env.REACT_APP_API_URL || `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}'}"
                good_string = "`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}"
                
                # Also check for double quotes version
                bad_string2 = '`${process.env.REACT_APP_API_URL || `${process.env.REACT_APP_API_URL || \'http://localhost:5000\'}"'
                
                new_content = content.replace(bad_string, good_string).replace(bad_string2, good_string)
                
                # Also, we might have `} }` or `}` issues if my original script broke something. Let's look at the TSC errors.
                # The TSC errors were "TS1005: '}' expected."
                # That means there's an unmatched `{`.
                # Look at bad_string: "`${process.env.REACT_APP_API_URL || `${process.env...}"
                # It has TWO `{` but only ONE `}` closed before the rest of the string, or maybe the template literal got completely messed up.
                
                # Another variation of the bad string depending on how it was replaced:
                # Original string in file was: `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}`
                # Then we replaced `'http://localhost:5000` with `` `${process.env.REACT_APP_API_URL || 'http://localhost:5000'} ``
                # The result is `${process.env.REACT_APP_API_URL || `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}'}`
                # Notice it has two `${`, so two `{`. It has two `}`.
                # Wait, TS thinks it needs a `}` because `'http://localhost:5000'}'}` has an unclosed string or something.
                
                # Let's fix it universally using Regex
                import re
                new_content = re.sub(
                    r"\$\{process\.env\.REACT_APP_API_URL \|\| `\$\{process\.env\.REACT_APP_API_URL \|\| 'http://localhost:5000'\}[`'\"]\}",
                    r"${process.env.REACT_APP_API_URL || 'http://localhost:5000'}",
                    new_content
                )
                
                new_content = new_content.replace(
                    "${process.env.REACT_APP_API_URL || `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}'}",
                    "${process.env.REACT_APP_API_URL || 'http://localhost:5000'}"
                )
                
                # Check for just single quotes that were transformed directly
                new_content = new_content.replace(
                    "`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}'",
                    "`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}`"
                )
                new_content = new_content.replace(
                    "`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}\"",
                    "`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}`"
                )

                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Fixed: {filepath}")

if __name__ == "__main__":
    fix_broken_syntax()
