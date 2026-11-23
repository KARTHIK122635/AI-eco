with open('scripts/build_audit8_reasons.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's extract the AI_SUPPORTING_TECH section
start = text.find("cat == 'AI_SUPPORTING_TECH':")
end = text.find("cat == 'NON_AI_TECH':")
print(text[start:start+2500])
