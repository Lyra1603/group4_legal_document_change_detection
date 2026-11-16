# Bản thử nghiệm phân tích độc lập

`analysis_contracts.py`, `local_analysis.py`, `text_diff/`, `semantic_diff/` và
`classifier_scorer/` trong thư mục này là đường chạy thử nghiệm riêng. Chạy bằng
`python -m unittest test_pipeline_modules -v` với `requirements-analysis.txt`.

Luồng backend dùng `backend/app/change_analysis/` và contract trong
`backend/app/schemas/contracts.py`. Không thay schema backend bằng các model ở đây.
`src.local_analysis.analyze_amendment()` thêm `needs_review`/`review_reason` ở cấp
ngoài để thử nghiệm; output đó không được gửi thẳng như `AmendmentResult` của API.
`AmendmentResult` chung có đúng bốn phần `amendment`, `text_diff`, `semantic_diff`,
`scoring`; cảnh báo thuộc các đối tượng con theo contract.

Các test synthetic trong thư mục này không chứng minh độ chính xác pháp lý,
không xác nhận Context thật đầy đủ và không phải bằng chứng tích hợp web demo.
