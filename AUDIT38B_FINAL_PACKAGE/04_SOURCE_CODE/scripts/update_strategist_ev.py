with open('scripts/test_audit15_remediations.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    "'Own outbound prospecting and customer engagement through Stage 2 qualification Drive customer outreach and education during the M1 phase of the sales process Build trust with prospective customers and teach them about Scale AI’s capabilities, AI workflows, and output methodology'",
    "'Own outbound prospecting and customer engagement through Stage 2 qualification Drive customer outreach and education during the M1 phase of the sales process'"
)

with open('scripts/test_audit15_remediations.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated remediations script!')
