with open('reports/backend_titles_all.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Records 51 to 120 in 282:")
for line in lines[100:240]:
    print(line, end='')
