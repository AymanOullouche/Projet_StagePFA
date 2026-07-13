import sqlite3

db = sqlite3.connect("inspection.db")
c = db.cursor()
cols = [r[1] for r in c.execute("PRAGMA table_info(inspections)")]
print("cols:", cols)
if "resultat_analyse" not in cols:
    c.execute("ALTER TABLE inspections ADD COLUMN resultat_analyse TEXT")
    db.commit()
    print("COLUMN ADDED")
else:
    print("COLUMN EXISTS")
db.close()
