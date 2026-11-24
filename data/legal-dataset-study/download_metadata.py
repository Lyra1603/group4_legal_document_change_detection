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

# Lượt 1 được giữ trong bộ quy tắc; lượt 2 bổ sung vào danh sách đã có.
# Không ghi lại riêng tập 506 dòng trước khi chạy, tránh làm mất kết quả lượt 2.
from civil_metadata_rules import expand_candidates

result = expand_candidates(output / "metadata.csv", output / "ung_vien_dan_su.csv")
print("Số ứng viên lượt 1:", result["summary"]["round1_rows"])
print("Số ứng viên sau lượt 2:", result["summary"]["total_candidates"])
print("Số dòng bổ sung trong lần chạy:", result["summary"]["added_this_run"])
print("Đã lưu vào:", output.resolve())
