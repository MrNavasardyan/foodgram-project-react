import json

with open('ingredients.json', 'r') as f:
    data = json.load(f)

for i in range(len(data)):
    data[i]["pk"] = i+1
    data[i]["model"] = "recipes.Ingredient"
    data[i] = {"model": data[i]["model"],
               "pk": data[i]["pk"],
               "fields": {"name": data[i]["name"], "measurement_unit": data[i]["measurement_unit"]}}

with open("new_ingredients.json", "w", encoding="Windows-1251") as f:
    f.write(json.dumps(data, ensure_ascii=False))