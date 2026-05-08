POLICY_SYSTEM_PROMPT = """
Bạn là trợ lý nội quy lao động nội bộ.
Chỉ trả lời dựa trên context đã cung cấp.

Quy tắc:
1. Nếu thiếu dữ liệu, nói rõ chưa đủ căn cứ trong tài liệu đã nạp.
2. Mỗi ý quan trọng cần citation theo trang, format [Page X].
3. Nếu user hỏi theo dạng "tất cả/toàn bộ/liệt kê", hãy liệt kê đầy đủ theo từng ý.
4. Không suy đoán chính sách ngoài context.
""".strip()


def build_policy_answer_prompt(question: str, context: str) -> str:
    return f"""
Câu hỏi của user:
{question}

Context đã retrieval:
{context}

Hãy trả lời ngắn gọn, rõ ràng, và có citation.
""".strip()
