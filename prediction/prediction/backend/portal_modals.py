path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\AdminDashboard.tsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# I want to replace:
#       {/* ═══ SIGNAL MODAL (HOISTED) ═══ */}
# down to the end of the FLAG MODAL AnimatePresence block.

signal_modal_start = "{/* ═══ SIGNAL MODAL (HOISTED) ═══ */}"
flag_modal_end = "      </AnimatePresence>\n\n    </div>\n  );\n};\n\nexport default AdminDashboard;"

idx_start = content.find(signal_modal_start)
idx_end = content.find("</AnimatePresence>", content.find("{/* ═══ FLAG MODAL (HOISTED WITH RESOLVE BUTTON) ═══ */}")) + len("</AnimatePresence>")

if idx_start != -1 and idx_end != -1:
    modals_block = content[idx_start:idx_end]
    
    # Wrap in createPortal
    new_modals_block = "      {createPortal(\n        <>\n" + "\n".join("          " + line for line in modals_block.split("\n")) + "\n        </>,\n        document.body\n      )}"
    
    content = content[:idx_start] + new_modals_block + content[idx_end:]
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Modals successfully wrapped in createPortal!")
else:
    print("Failed to find modal boundaries.")
