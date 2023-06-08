import json

with open('ingredients.json', 'r') as f:
    data = json.load(f)

for obj in data:
    obj['model'] = 'recipes.Ingredient'

with open('new_ingredients.json', 'w') as f:
    json.dump(data, f)