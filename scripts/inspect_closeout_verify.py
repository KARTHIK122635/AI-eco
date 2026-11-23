import os

with open("scripts/verify_final_closeout_package.py", "r", encoding="utf-8") as f:
    text = f.read()

print("Lines 1-60 of verify_final_closeout_package.py:")
for line in text.splitlines()[:60]:
    print(line)
