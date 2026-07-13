with open('d:\\ENSIASD\\TP S4\\Projet_StagePFA\\backend\\fastapi\\app\\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_endpoint = '''
@app.post(f"{API_PREFIX}/rag/documents/upload")
async def upload_rag_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont autorises")
    
    rag_dir = UPLOADS_DIR.parent / "rag_documents"
    rag_dir.mkdir(parents=True, exist_ok=True)
    file_id = date.today().strftime('%Y%m%d') + '_' + str(int(datetime.now().timestamp()))
    file_path = rag_dir / f"{file_id}_{file.filename}"
    
    with open(file_path, 'wb') as f:
        content_bytes = await file.read()
        f.write(content_bytes)
    
    document = crud.create_document(db, titre=file.filename, file_path=file_path)
    
    return {
        "data": {
            "id": document.id,
            "titre": document.titre,
            "statut": document.statut,
            "date_import": document.date_import.isoformat(),
            "message": "Document importe. Cliquez sur 'Indexer' pour l'analyser.",
        }
    }
'''

marker = '@app.post(f"{API_PREFIX}/rag/documents/{{document_id}}/index")'
if marker in content:
    content = content.replace(marker, new_endpoint + '\n' + marker)
    with open('d:\\ENSIASD\\TP S4\\Projet_StagePFA\\backend\\fastapi\\app\\main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('upload endpoint added successfully')
else:
    print('ERROR: marker not found')
    # debug
    idx = content.find('rag/documents')
    print('found index', idx)
    if idx >= 0:
        print(content[idx:idx+80])
