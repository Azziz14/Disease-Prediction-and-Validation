import re

def parse_tokens_smart(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Remove single-line comments //...
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    # Remove multi-line comments /* ... */
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Remove string literals: '...', "...", `...`
    # But be careful about backticks which can contain ${ } expressions!
    # To do this right, let's just strip '...' and "..." first.
    # For backticks, we will handle them character-by-character.
    
    stack = []
    lines = content.split('\n')
    
    in_single_quote = False
    in_double_quote = False
    in_backtick = False
    in_template_expr = [] # Stack of template ${ } depth
    
    for line_num, line in enumerate(lines, start=1):
        col_num = 0
        length = len(line)
        while col_num < length:
            char = line[col_num]
            
            # String literals handler
            if char == "'" and not in_double_quote and not in_backtick:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote and not in_backtick:
                in_double_quote = not in_double_quote
            elif char == '`' and not in_single_quote and not in_double_quote:
                in_backtick = not in_backtick
                
            if in_single_quote or in_double_quote:
                col_num += 1
                continue
                
            # Template literals ${ ... }
            if in_backtick:
                if char == '$' and col_num + 1 < length and line[col_num+1] == '{':
                    # Template expression starts!
                    stack.append(('${', line_num, col_num))
                    in_template_expr.append(len(stack)) # Track index
                    col_num += 2
                    continue
                elif char == '}':
                    # Could close a template expr!
                    # Let's check if top of stack is '${'
                    if stack and stack[-1][0] == '${':
                        stack.pop()
                        # Resume backtick mode!
                        col_num += 1
                        continue
            
            # Normal token checking
            if char in ['{', '(', '[']:
                stack.append((char, line_num, col_num))
            elif char in ['}', ')', ']']:
                if not stack:
                    print(f"UNMATCHED CLOSING '{char}' at Line {line_num}, Col {col_num}")
                    col_num += 1
                    continue
                top, t_line, t_col = stack.pop()
                if (char == '}' and top != '{') or (char == ')' and top != '(') or (char == ']' and top != '['):
                    print(f"MISMATCH: Opened '{top}' at L{t_line}:C{t_col}, but closed with '{char}' at L{line_num}:C{col_num}")
            
            col_num += 1

    if stack:
        print("\n--- REMAINDER OF STACK (Unclosed items) ---")
        for item in stack:
            print(f"Unclosed '{item[0]}' opened at Line {item[1]}, Col {item[2]}")
            print(f"  Content: {lines[item[1]-1].strip()}")
    else:
        print("\nStack is empty! All code tokens are perfectly balanced.")

print("=== Analyzing DoctorDashboard.tsx ===")
parse_tokens_smart(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\DoctorDashboard.tsx")
