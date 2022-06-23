import re


import re
q = "^!add(\n(((@)?[a-zA-Z0-9_]{5,32})|([\-]?[0-9]){5,15})){2}$"
print(re.match(q, """!add
@5678678
@frewsw
""").group())
