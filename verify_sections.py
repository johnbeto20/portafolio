import json
import re

with open('js/projects-data.js', encoding='utf-8') as f:
    content = f.read()

# Extract the JSON part - find PROJECTS array
match = re.search(r'const PROJECTS = ([\s\S]*?);\s*$', content)
if match:
    json_str = match.group(1).strip()
    data = json.loads(json_str)
else:
    print("No se encontro PROJECTS en el archivo")
    exit(1)

# Find Pildoras project
pildoras = [p for p in data if 'Pildora' in p['title']]

print(f'Total Pildoras projects: {len(pildoras)}\n')

for p in pildoras:
    print(f"Slug: {p['slug']}")
    print(f"Title: {p['title']}")
    print(f"Has sections: {'sections' in p}")
    if 'sections' in p:
        print(f"Number of sections: {len(p['sections'])}")
        for i, s in enumerate(p['sections']):
            print(f"  Section {i+1}:")
            print(f"    Title: {s.get('title', 'N/A')}")
            print(f"    URL: {s.get('url', 'N/A')}")
            print(f"    GitHub: {s.get('github', 'N/A')}")
            print(f"    AssociatedImage: {s.get('associatedImage', 'N/A')}")
    print("---")
