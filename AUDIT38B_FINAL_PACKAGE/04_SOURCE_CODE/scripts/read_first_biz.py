with open('reports/biz_titles_all.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in biz: {len(lines)}")
print("First 60 lines of biz:")
for line in lines[:60]:
    print(line, end='')
