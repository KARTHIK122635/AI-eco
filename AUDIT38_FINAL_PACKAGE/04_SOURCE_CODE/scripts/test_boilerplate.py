import re

BOILERPLATE_PATTERNS = [
    r'while candidates in the listed locations',
    r'remote candidates in other',
    r'shape the trajectory of one of the most',
    r'we develop reliable ai systems',
    r'anthropic is dedicated to developing',
    r'anthropic is building ai systems',
    r'scale ai is at the forefront',
    r'at scale, we develop',
    r'mission is to create reliable',
    r'committed researchers, engineers',
    r'werde teil der digitalen zukunft',
    r'req\s*id:',
    r'location:\s*',
    r'hybrid policy',
    r'visa sponsorship'
]

def is_boilerplate(text):
    if not text:
        return True
    t = text.lower()
    return any(re.search(p, t) for p in BOILERPLATE_PATTERNS)

print("Testing is_boilerplate:")
print(is_boilerplate("P-146 While candidates in the listed locations are encouraged for this role, we are open to remote candidates in other at Databricks."))
print(is_boilerplate("anthropic is building AI systems that will shape the trajectory of one of the most"))
print(is_boilerplate("conduct research and implement solutions in areas such as model architecture"))
