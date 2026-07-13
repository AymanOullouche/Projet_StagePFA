import pathlib
p = pathlib.Path('main.py')
text = p.read_text(encoding='utf-8')
old = 'from sqlalchemy.orm import Session`r`n`r`ntry:`r`n    from fpdf import FPDF`r`n    FPDF_AVAILABLE = True`r`nexcept ImportError:`r`n    FPDF_AVAILABLE = False'
new = 'from sqlalchemy.orm import Session\n\ntry:\n    from fpdf import FPDF\n    FPDF_AVAILABLE = True\nexcept ImportError:\n    FPDF_AVAILABLE = False'
if old in text:
    text = text.replace(old, new)
    p.write_text(text, encoding='utf-8')
    print('fixed import block')
else:
    print('old import block not found')
