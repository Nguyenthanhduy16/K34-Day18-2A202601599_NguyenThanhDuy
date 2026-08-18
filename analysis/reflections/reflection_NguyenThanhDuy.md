# Reflection cá nhân - Lab 18

**Họ tên:** Nguyễn Thành Duy  
**Module:** M1-M5 Production RAG

## 1. Liên hệ với bài giảng

| Khái niệm | Code | Nhận xét |
|---|---|---|
| Semantic chunking | `src/m1_chunking.py:chunk_semantic` | Gom các câu gần nhau về ngữ nghĩa và có lexical fallback khi chạy offline. |
| Hierarchical chunking | `chunk_hierarchical` | Child giúp tìm kiếm chính xác, còn parent giữ lại ngữ cảnh rộng hơn. |
| BM25 và dense fusion | `src/m2_search.py:reciprocal_rank_fusion` | RRF kết hợp matching từ khóa với similarity ngữ nghĩa mà không cần so sánh hai loại điểm thô. |
| Cross-encoder reranking | `src/m3_rerank.py:CrossEncoderReranker.rerank` | Chấm lại một tập candidate nhỏ và trả về các context phù hợp nhất. |
| Đánh giá RAGAS | `src/m4_eval.py:evaluate_ragas` | Bốn chỉ số cho thấy bốn loại lỗi khác nhau của hệ thống. |
| Contextual enrichment | `src/m5_enrichment.py:_enrich_single_call` | Một lần gọi LLM tạo summary, câu hỏi, context và metadata trước khi index. |

## 2. Khó khăn và cách giải quyết

Lỗi API đầu tiên là 401 từ OpenAI vì project dùng key OpenRouter nhưng RAGAS vẫn đọc các biến môi trường theo chuẩn OpenAI. Cách xử lý là dùng endpoint OpenAI-compatible của OpenRouter và ánh xạ `OPENROUTER_API_KEY` sang các biến mà LangChain/RAGAS sử dụng. Khi debug chỉ kiểm tra base URL, model và việc key có tồn tại hay không, không in trực tiếp secret.

Trong quá trình đánh giá, RAGAS còn báo `Missing Authentication header`. Nguyên nhân là biến môi trường cũ hoặc rỗng đã được giữ lại bởi `setdefault`. Việc gán trực tiếp biến môi trường đã khắc phục lỗi này. Một khó khăn khác là phân biệt lỗi retrieval với lỗi sinh câu trả lời; báo cáo theo từng câu hỏi và cây chẩn đoán giúp phân biệt hai trường hợp.

## 3. Kết quả và bài học

Toàn bộ 37 automated tests đều pass. Production đạt context precision 0.9208 và answer relevancy 0.5988. Faithfulness chỉ đạt 0.5708, cho thấy retriever tốt vẫn chưa đủ; generator cần từ chối khi context thiếu bằng chứng. Recall 0.6750 cũng cho thấy ba chunk cuối chưa đủ cho các câu hỏi nhiều bước.

## 4. Kế hoạch áp dụng cho project tương lai

1. [x] Dùng hierarchical chunk để giữ cấu trúc tài liệu và parent context.
2. [x] Dùng BM25 kết hợp dense vì câu hỏi policy tiếng Việt có cả từ khóa chính xác và cách diễn đạt tương đương.
3. [x] Dùng reranking để tăng precision; tăng top-k cho câu hỏi nhiều bước.
4. [x] Dùng RAGAS và xem bottom-5 failures thay vì chỉ nhìn điểm trung bình.
5. [x] Dùng combined enrichment để giảm số lần gọi API và có fallback xác định.
6. [ ] Thêm query decomposition cho câu hỏi có nhiều yêu cầu policy.
7. [ ] Thêm định dạng trả lời có answer, evidence và source.

### Timeline

- Tuần 1: thử parent retrieval, điều chỉnh top-k và prompt grounding.
- Tuần 2: query decomposition và metadata filter theo nhóm policy.
- Tuần 3: OCR cho PDF scan và regression evaluation trên bộ 20 câu hỏi.
