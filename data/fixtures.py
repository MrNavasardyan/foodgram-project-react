import json

with open('ingredients.json', 'r') as f:
    data = json.load(f)

for i, obj in enumerate(data):
    obj.update({"model": "recipes.Ingredient", "pk": i+1})

updated_data = json.dumps(data, ensure_ascii=False)
print(updated_data)
with open('new_ingredients.json', 'w', encoding='Windows-1251') as f:
    f.write(updated_data)