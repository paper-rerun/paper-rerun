import re
import sys

path = sys.argv[1]
h = open(path, encoding="utf-8", errors="replace").read()
rep = {
    "\\x22": '"',
    "\\x5b": "[",
    "\\x5d": "]",
    "\\x7b": "{",
    "\\x7d": "}",
    "\\x3d": "=",
    "\\x26": "&",
}
for k, v in rep.items():
    h = h.replace(k, v)
open(path + ".unesc", "w", encoding="utf-8").write(h)

# Drive folder listing entries look like ["<fileId>","<parentId>",...,"<name>",...]
hits = re.findall(r'\["([-\w]{28,44})",\["([-\w]{28,44})"\],"([^"]{1,200})"', h)
if not hits:
    hits = re.findall(r'\["([-\w]{28,44})","([-\w]{28,44})","([^"]{1,200})"', h)
print(len(hits))
for a, b, c in hits:
    print(a, "|", c)
