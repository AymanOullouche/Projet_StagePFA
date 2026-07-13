#!/usr/bin/env python
"""Fix computer detection: add missing mappings."""
p = r"d:\ENSIASD\TP S4\Projet_StagePFA\backend\fastapi\app\yolo_service.py"
with open(p, "r", encoding="utf-8") as f:
    text = f.read()

# Add missing computer prompts to EN_TO_FR mapping
old = '"laptop":"Ordinateur","screen":"Ordinateur",'
new = '"laptop":"Ordinateur","screen":"Ordinateur",\n    "pc computer":"Ordinateur","workstation computer":"Ordinateur",\n    "school computer":"Ordinateur","office computer":"Ordinateur",'

if old in text and "pc computer" not in text:
    text = text.replace(old, new)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    print("OK: Mapping ordinateurs ajoute!")
else:
    print("IGNORE: Mapping deja present ou pattern non trouve")
