import re

def parse_tokens(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    stack = []
    lines = content.split('\n')
    
    # Simple regex to find JSX opening/closing tags and parentheses/braces
    # We need to track '{', '}', '(', ')', '<tag>', '</tag>'
    # Note: We will simplify and just track brackets and paren nesting to see where the mismatch happens
    for line_num, line in enumerate(lines, start=1):
        for col_num, char in enumerate(line, start=1):
            if char in ['{', '(', '[']:
                stack.append((char, line_num, col_num))
            elif char in ['}', ')', ']']:
                if not stack:
                    print(f"Unmatched CLOSING '{char}' at Line {line_num}, Col {col_num}")
                    continue
                top, t_line, t_col = stack.pop()
                # Match check
                if (char == '}' and top != '{') or (char == ')' and top != '(') or (char == ']' and top != '['):
                    print(f"MISMATCH: Opened '{top}' at L{t_line}:C{t_col}, but closed with '{char}' at L{line_num}:C{col_num}")
                    # Let's print a snippet
                    print(f"  Line {t_line}: {lines[t_line-1].strip()}")
                    print(f"  Line {line_num}: {line.strip()}")

    if stack:
        print("\n--- REMAINDER OF STACK (Unclosed items) ---")
        for item in stack:
            print(f"Unclosed '{item[0]}' opened at Line {item[1]}, Col {item[2]}")
            print(f"  Content: {lines[item[1]-1].strip()}")
    else:
        print("\nStack is empty! All basic tokens are balanced.")

print("=== Analyzing DoctorDashboard.tsx ===")
parse_tokens(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\DoctorDashboard.tsx")
