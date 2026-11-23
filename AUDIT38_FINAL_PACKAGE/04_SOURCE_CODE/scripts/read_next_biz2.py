with open('reports/biz_titles_all.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Lines 180 to 310 of biz:")
for line in lines[180:]:
    print(line, end='')
