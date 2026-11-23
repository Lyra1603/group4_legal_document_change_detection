from pathlib import Path

from datasets import load_dataset

output = Path("data")
output.mkdir(exist_ok=True)

dataset = load_dataset(
    "th1nhng0/vietnamese-legal-documents",
    "metadata",
    split="data",
    revision="8977887f17be2defae4c5171d55562e1cde7d695",
)

df = dataset.to_pandas()

df.to_csv(
    output / "metadata.csv",
    index=False,
    encoding="utf-8-sig",
)

print("Số dòng:", len(df))
print("Các cột:", df.columns.tolist())
print(df.head().to_string(index=False))

# Xem những nhãn lĩnh vực thực sự có trong dữ liệu.
df["linh_vuc"].fillna("(trống)").value_counts().to_csv(
    output / "thong_ke_linh_vuc.csv",
    encoding="utf-8-sig",
)

# Tập ứng viên ban đầu để khảo sát thêm.
civil_candidates = df[
    df["linh_vuc"].fillna("").str.contains("dân sự", case=False)
    | df["title"].fillna("").str.contains("dân sự", case=False)
]

civil_candidates.to_csv(
    output / "ung_vien_dan_su.csv",
    index=False,
    encoding="utf-8-sig",
)

print("Số ứng viên theo tên/lĩnh vực:", len(civil_candidates))
print("Đã lưu vào:", output.resolve())