# Báo cáo nhóm - Lab 18: Production RAG

**Nhóm:** Nguyễn Thành Duy  
**Ngày:** 18/08/2026

## Phân công và kết quả

| Module | Nội dung triển khai | Tests |
|---|---|---:|
| M1: Chunking | Semantic, hierarchical, structure-aware | 12 |
| M2: Hybrid Search | BM25 tiếng Việt, dense Qdrant, RRF | 12 |
| M3: Reranking | CrossEncoder và lexical fallback | 12 |
| M4: Evaluation | 4 chỉ số RAGAS và phân tích lỗi | 12 |
| M5: Enrichment | Combined mode, một lần gọi cho mỗi chunk | Đạt |

## So sánh RAGAS

| Chỉ số | Baseline | Production | Thay đổi |
|---|---:|---:|---:|
| Faithfulness | 1.0000 | 0.5708 | -0.4292 |
| Answer relevancy | 0.3547 | 0.5988 | +0.2441 |
| Context precision | 0.1867 | 0.9208 | +0.7342 |
| Context recall | 0.8467 | 0.6750 | -0.1717 |

## Phát hiện chính

1. Cải thiện lớn nhất: hybrid retrieval và reranking nâng context precision lên 0.9208.
2. Thách thức lớn nhất: LLM đôi khi sinh thông tin không có trong context.
3. Phát hiện đáng chú ý: baseline có context recall cao hơn, cho thấy top-k production đang quá thấp với câu hỏi nhiều bước.

## Ghi chú thuyết trình

1. Điểm mạnh chính là chất lượng retrieval, nhưng khả năng grounding của câu trả lời còn cần cải thiện.
2. Ca lỗi tiêu biểu là câu hỏi kết hợp chính sách lương và nghỉ phép.
3. Cây lỗi cho thấy cần kiểm tra context bị thiếu trước, sau đó mới chỉnh prompt.
4. Tối ưu tiếp theo: lấy parent chunk và tăng rerank top-k lên 5.
