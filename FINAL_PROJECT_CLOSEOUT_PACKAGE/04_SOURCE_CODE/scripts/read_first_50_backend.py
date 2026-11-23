import json

with open('reports/backend_titles_all.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("First 50 records in 282:")
for line in lines[:100]:
    print(line, end='')
