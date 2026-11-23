with open('reports/biz_titles_all.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Lines 60 to 180 of biz:")
for line in lines[60:180]:
    print(line, end='')
