import re

def parse_jsx_tags(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Find JSX tags using regex
    # Matches either:
    #   </tagName>  (closing)
    #   <tagName ... /> (self-closing)
    #   <tagName ... > (opening)
    # We skip comments like {/* ... */}
    
    # Let's strip comments first
    content_clean = re.sub(r'\{/\*.*?\*/\}', '', content, flags=re.DOTALL)
    
    # Find all tags
    # Regex logic: find < something > but be careful about < space or operators.
    # In TSX, a tag starts with < immediately followed by a letter, / or nothing (fragment <>).
    tag_pattern = re.compile(r'<(/?[a-zA-Z][a-zA-Z0-9\.\:]*|/?>)\s*([^>]*?)(/?>)')
    
    stack = []
    lines = content_clean.split('\n')
    
    print("--- Starting JSX Tag Audit ---")
    for i, line in enumerate(lines, start=1):
        for match in re.finditer(tag_pattern, line):
            raw_tag = match.group(0)
            tag_name = match.group(1)
            tail = match.group(3)
            
            # Ignore common comparisons or JS operators like < inside expressions!
            # But we are running line-based regex, which can match < inside JS ternary sometimes.
            # Let's filter: Tag names must be valid HTML, uppercase React, or fragments.
            if tag_name in ['=', ' ', '?', ':', '&&', '||'] or re.match(r'^[0-9]+$', tag_name):
                continue

            is_closing = tag_name.startswith('/')
            is_self_closing = tail == '/>' or raw_tag.endswith('/>')
            
            clean_name = tag_name.lstrip('/').strip()
            if clean_name == '>':
                clean_name = 'fragment'

            if is_self_closing:
                # Self-closing tag, do not push to stack
                # print(f"L{i}: Self-Closing <{clean_name}/>")
                pass
            elif is_closing:
                # print(f"L{i}: Closing </{clean_name}>")
                if not stack:
                    print(f"ERROR: Extra CLOSING tag </{clean_name}> at Line {i}")
                    continue
                top_name, top_line = stack.pop()
                if top_name != clean_name:
                    # JSX Fragment allows <> ... </>
                    if clean_name == 'fragment' and top_name == 'fragment':
                        pass
                    else:
                        print(f"ERROR: Mismatched Closing Tag! Opened <{top_name}> at L{top_line}, but closed with </{clean_name}> at L{i}")
            else:
                # print(f"L{i}: Opening <{clean_name}>")
                stack.append((clean_name, i))

    print("--- JSX Tag Audit Completed ---")
    if stack:
        print("\n--- UNCLOSED JSX TAGS REMAINING ON STACK ---")
        for name, line in stack:
            print(f"Unclosed <{name}> opened at Line {line}")
    else:
        print("All JSX Tags are mathematically balanced!")

parse_jsx_tags(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\DoctorDashboard.tsx")
