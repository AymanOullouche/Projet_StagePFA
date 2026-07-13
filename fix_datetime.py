with open('d:\\ENSIASD\\TP S4\\Projet_StagePFA\\backend\\fastapi\\app\\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = 'from datetime import date'
new = 'from datetime import date, datetime'

if old in content:
    content = content.replace(old, new)
    with open('d:\\ENSIASD\\TP S4\\Projet_StagePFA\\backend\\fastapi\\app\\main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('datetime import fixed')
else:
    print('old import not found')
