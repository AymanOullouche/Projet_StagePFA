from pathlib import Path
import PyPDF2
path = Path('cahier_des_charges_Stage.pdf')
reader = PyPDF2.PdfReader(str(path))
for i, page in enumerate(reader.pages):
    print(f'--- PAGE {i+1} ---')
    print(page.extract_text() or '(no text)')
