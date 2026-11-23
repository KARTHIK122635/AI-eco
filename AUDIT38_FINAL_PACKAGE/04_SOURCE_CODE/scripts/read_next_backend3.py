with open('reports/backend_titles_all.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Records 201 to 282 in 282:")
for line in lines[400:]:
    print(line, end='')
