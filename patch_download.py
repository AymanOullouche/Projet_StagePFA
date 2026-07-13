import pathlib
p = pathlib.Path("src/App.jsx")
text = p.read_text("utf-8")

old = """  const downloadReport = async (report) => {
    if (!report) return;

    try {
      const response = await api.get(endpoints.reportPdf(report.id), {
        responseType: \"blob\",
      });
      const url = URL.createObjectURL(new Blob([response.data], { type: \"application/pdf\" }));
      const link = document.createElement(\"a\");
      link.href = url;
      link.download = `${report.titre.replace(/[^a-z0-9]/gi, \"_\").toLowerCase()}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error(\"Impossible de telecharger le rapport PDF\", error);
      alert(\"Impossible de telecharger le rapport PDF. Verifiez que le backend est accessible.\");
    }
  };\n"""

if old in text:
    text = text.replace(old, "")
    p.write_text(text, "utf-8")
    print("removed old downloadReport")
else:
    print("old not found")
