from pathlib import Path
import webbrowser

import pandas as pd
from datasets import load_dataset

document_id = "111436"
output = Path("data")
metadata = pd.read_csv(output / "metadata.csv", dtype={"id": str})

selected = metadata[metadata["id"] == document_id]
if selected.empty:
    raise SystemExit("Không tìm thấy ID trong metadata.csv")

print(selected[["id", "so_ky_hieu", "title"]].to_string(index=False))

documents = load_dataset(
    "th1nhng0/vietnamese-legal-documents",
    "content",
    split="data",
    streaming=True,
    revision="8977887f17be2defae4c5171d55562e1cde7d695",
)

print("Đang tìm toàn văn. Lần đầu có thể cần chờ tải dữ liệu…")

for document in documents:
    if str(document["id"]) == document_id:
        html = document.get("content_html") or ""
        if not html.strip():
            raise SystemExit("Bản ghi có nội dung HTML rỗng.")

        path = output / f"vbpl-{document_id}.html"
        path.write_text(html, encoding="utf-8")

        print("Đã lưu:", path.resolve())
        webbrowser.open(path.resolve().as_uri())
        break
else:
    print("Có metadata nhưng chưa tìm thấy toàn văn tương ứng.")
