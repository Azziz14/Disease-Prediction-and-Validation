import re

path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\frontend\src\pages\dashboards\DoctorDashboard.tsx"

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 1. Re-write activeTab === 'overview' using bulletproof ternary
# Search for the condition block start and end.
# Start anchor: {activeTab === 'overview' &&
# End anchor: } \n\n      {activeTab === 'inbox'

# Let's do a precise replacement
content = content.replace(
    "      {activeTab === 'overview' &&\n\n      <div className=\"grid grid-cols-1 lg:grid-cols-3 gap-8\">",
    "      {activeTab === 'overview' ? (\n\n      <div className=\"grid grid-cols-1 lg:grid-cols-3 gap-8\">"
)

# End of overview:
# In the previous replacement, we had:
#           </div>
#         </div>
#       }
# 
#       {activeTab === 'inbox' &&

content = content.replace(
    "          </div>\n        </div>\n      }\n\n      {activeTab === 'inbox' &&",
    "          </div>\n        </div>\n      ) : null}\n\n      {activeTab === 'inbox' ? ("
)

# 2. Re-write end of activeTab === 'inbox' using bulletproof ternary
# Current bottom:
#             </div>\n          </div>\n        </motion.section>\n      }\n    </div>\n  );\n};

content = content.replace(
    "            </div>\n          </div>\n        </motion.section>\n      }\n    </div>\n  );\n};",
    "            </div>\n          </div>\n        </motion.section>\n      ) : null}\n    </div>\n  );\n};"
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully rewrote DoctorDashboard.tsx using the bulletproof ternary conditional pattern!")
