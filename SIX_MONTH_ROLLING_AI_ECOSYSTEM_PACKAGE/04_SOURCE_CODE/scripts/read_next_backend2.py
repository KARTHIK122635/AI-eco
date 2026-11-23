with open('reports/backend_titles_all.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Records 121 to 200 in 282:")
for line in lines[240:400]:
    print(line, end='')
