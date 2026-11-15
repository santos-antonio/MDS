from bs4 import BeautifulSoup
from pathlib import Path
import base64
import mimetypes

# =====================================================
# LOCALIZAR HTML AUTOMATICAMENTE
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

html_files = list(BASE_DIR.glob("*.html"))

# Se não encontrar na pasta atual, procura recursivamente
if not html_files:
    html_files = list(BASE_DIR.rglob("*.html"))

if not html_files:
    raise FileNotFoundError(
        f"Nenhum arquivo HTML encontrado em:\n{BASE_DIR}"
    )

# Caso existam vários HTMLs, seleciona o maior
html_path = max(html_files, key=lambda x: x.stat().st_size)

print(f"\nHTML encontrado:")
print(html_path)

output_file = html_path.with_name(
    html_path.stem + "_embedded.html"
)

# =====================================================
# CARREGAR HTML
# =====================================================

with open(html_path, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

# =====================================================
# EMBUTIR IMAGENS
# =====================================================

embedded = 0
missing = []

for img in soup.find_all("img"):

    src = img.get("src")

    if not src:
        continue

    # Ignora imagens já embutidas
    if src.startswith("data:"):
        continue

    image_path = (html_path.parent / src).resolve()

    if not image_path.exists():
        missing.append(src)
        continue

    mime_type, _ = mimetypes.guess_type(image_path)

    if mime_type is None:
        mime_type = "image/png"

    with open(image_path, "rb") as image_file:
        img_base64 = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    img["src"] = (
        f"data:{mime_type};base64,{img_base64}"
    )

    embedded += 1

# =====================================================
# SALVAR NOVO HTML
# =====================================================

with open(output_file, "w", encoding="utf-8") as f:
    f.write(str(soup))

# =====================================================
# RELATÓRIO
# =====================================================

print("\n" + "=" * 60)
print(f"Imagens incorporadas : {embedded}")
print(f"Arquivo gerado       : {output_file}")

if missing:
    print("\nImagens não encontradas:")
    for m in missing:
        print(" -", m)

print("=" * 60)