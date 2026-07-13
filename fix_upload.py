with open('d:\\ENSIASD\\TP S4\\Projet_StagePFA\\backend\\fastapi\\app\\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    rag_dir = UPLOADS_DIR.parent / "rag_documents"
    rag_dir.mkdir(parents=True, exist_ok=True)
    file_id = date.today().strftime('%Y%m%d') + '_' + str(int(datetime.now().timestamp()))
    file_path = rag_dir / f"{file_id}_{file.filename}"
    
    with open(file_path, 'wb') as f:
        content_bytes = await file.read()
        f.write(content_bytes)
    
    document = crud.create_document(db, titre=file.filename, file_path=file_path)'''

new = '''    rag_dir = UPLOADS_DIR.parent / "rag_documents"
    rag_dir.mkdir(parents=True, exist_ok=True)
    
    # D'abord creer le document en base pour obtenir l'ID
    document = crud.create_document(db, titre=file.filename, file_path=Path(''))
    
    # Sauvegarder le fichier avec l'ID du document comme prefixe
    file_path = rag_dir / f"{document.id}_{file.filename}"
    
    with open(file_path, 'wb') as f:
        content_bytes = await file.read()
        f.write(content_bytes)
    
    # Mettre a jour le chemin du fichier
    document.content = str(file_path)
    db.commit()
    db.refresh(document)'''

if old in content:
    content = content.replace(old, new)
    with open('d:\\ENSIASD\\TP S4\\Projet_StagePFA\\backend\\fastapi\\app\\main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('upload fixed')
else:
    print('pattern not found')
