# Phân tích lỗi - Lab 18: Production RAG

## Điểm RAGAS

Dưới đây là kết quả của lần chạy gần nhất trên 20 câu hỏi.

| Chỉ số | Baseline | Production | Thay đổi |
|---|---:|---:|---:|
| Faithfulness - độ trung thực với context | 1.0000 | 0.5708 | -0.4292 |
| Answer relevancy - độ liên quan câu trả lời | 0.3547 | 0.5988 | +0.2441 |
| Context precision - độ chính xác context | 0.1867 | 0.9208 | +0.7342 |
| Context recall - độ bao phủ context | 0.8467 | 0.6750 | -0.1717 |

Production cải thiện mạnh độ chính xác của context và độ liên quan của câu trả lời. Tuy nhiên, điểm faithfulness thấp cho thấy LLM đôi khi thêm thông tin không có trong context. Điểm recall thấp hơn cho thấy một số câu hỏi nhiều bước cần nhiều chunk hơn ba chunk hiện tại.

## 5 lỗi có điểm thấp nhất

### 1. Nhân viên được nghỉ bao nhiêu ngày phép năm?

- Chỉ số thấp nhất: faithfulness (0.0000)
- Chẩn đoán: Câu trả lời chưa bám đủ vào context được chọn.
- Cây lỗi: Đầu ra sai → context có thể thiếu → top-k rerank quá nhỏ → prompt cho phép LLM tự hoàn thiện.
- Nguyên nhân gốc: Câu hỏi yêu cầu một con số chính xác và chính sách nghỉ phép theo phiên bản có thể bị chia thành nhiều chunk.
- Cách sửa: Lấy parent chunk, tăng rerank top-k từ 3 lên 5 và yêu cầu model chỉ trả về con số có bằng chứng.

### 2. Lương thử việc của nhân viên Junior mức cao nhất là bao nhiêu?

- Chỉ số thấp nhất: faithfulness (0.0000)
- Chẩn đoán: Model có thể trả lời theo kiến thức chung thay vì chính sách.
- Cây lỗi: Đầu ra sai → context chứa bảng lương lân cận → thiếu bằng chứng số cụ thể → câu trả lời không có căn cứ.
- Nguyên nhân gốc: Cần lấy đầy đủ dòng Junior và khoảng lương trong cùng một context.
- Cách sửa: Bổ sung quy tắc kiểm tra bằng chứng số và lấy toàn bộ parent section của bảng lương.

### 3. Thông tin lương thuộc cấp độ phân loại dữ liệu nào?

- Chỉ số thấp nhất: faithfulness (0.0000)
- Chẩn đoán: Câu trả lời chưa bám vào chính sách phân loại dữ liệu.
- Cây lỗi: Đầu ra sai → context liên quan chưa được lấy đủ → LLM tự suy luận → không có cơ chế từ chối.
- Nguyên nhân gốc: Câu hỏi cần nối thông tin giữa chính sách lương và phần phân loại dữ liệu.
- Cách sửa: Lọc metadata theo nhóm policy/data-classification và trả lời “Không đủ thông tin” nếu thiếu bằng chứng.

### 4. Mua laptop 30 triệu cho nhân viên mới cần ai phê duyệt và cần gì từ phòng CNTT?

- Chỉ số thấp nhất: faithfulness (0.0000)
- Chẩn đoán: Đây là câu hỏi nhiều bước, gồm hạn mức phê duyệt và yêu cầu từ CNTT.
- Cây lỗi: Đầu ra sai → thiếu một trong hai context → chỉ trả lời được một bước → câu trả lời không đầy đủ.
- Nguyên nhân gốc: Hybrid search tìm được context chính xác nhưng không lấy đủ cả hai chính sách.
- Cách sửa: Tăng số candidate, giữ liên kết parent-child và tìm kiếm riêng cho từng ý trong câu hỏi.

### 5. Nhân viên Senior có 9 năm thâm niên được nghỉ bao nhiêu ngày phép và lương trong khoảng nào?

- Chỉ số thấp nhất: faithfulness (0.0000)
- Chẩn đoán: Câu hỏi kết hợp chính sách nghỉ phép và bảng lương.
- Cây lỗi: Đầu ra sai → context thiếu → không tách hai nguồn → LLM tự ghép thông tin.
- Nguyên nhân gốc: Hệ thống lấy được tài liệu liên quan nhưng chưa yêu cầu model tách bằng chứng theo từng nguồn.
- Cách sửa: Tìm context nghỉ phép và lương độc lập, gắn nhãn nguồn rồi chỉ tổng hợp các giá trị có bằng chứng.

## Cây lỗi và hướng tối ưu tiếp theo

```text
Câu trả lời không có căn cứ?
  → Bằng chứng cần thiết có trong context không?
       Không → cải thiện query decomposition, parent retrieval và top-k
       Có   → siết prompt và yêu cầu LLM từ chối khi thiếu bằng chứng
  → Câu hỏi có nhiều bước không?
       Có → tìm kiếm riêng cho từng ý nhỏ
```

Thay đổi có giá trị cao nhất tiếp theo là lấy parent chunk và dùng prompt yêu cầu câu trả lời có căn cứ. Cách này tác động trực tiếp đến hai điểm yếu là faithfulness và recall, đồng thời giữ được context precision hiện tại.
