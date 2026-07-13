with open('d:\\ENSIASD\\TP S4\\Projet_StagePFA\\backend\\fastapi\\app\\crud.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_func = '''
def create_document(session: Session, titre: str, file_path: Path) -> models.Document:
    document = models.Document(
        titre=titre,
        statut="Importe",
        content="",
        date_import=date.today(),
    )
    session.add(document)
    session.commit()
    session.refresh(document)
    return document
'''

marker = 'def get_document(session: Session, document_id: int)'
if marker in content:
    content = content.replace(marker, new_func + marker)
    with open('d:\\ENSIASD\\TP S4\\Projet_StagePFA\\backend\\fastapi\\app\\crud.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('create_document added')
else:
    print('marker not found')
