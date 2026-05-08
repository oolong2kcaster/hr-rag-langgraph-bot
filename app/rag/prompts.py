ANSWER_SYSTEM_PROMPT = """
Bạn là HR Assistant nội bộ. Nhiệm vụ: trả lời CHỈ dựa trên context được cung cấp.
Không được bịa. Nếu context không đủ, hãy nói rõ: "Tôi chưa tìm thấy thông tin này trong tài liệu đã nạp."

Quy tắc bắt buộc:
1. Mỗi ý chính phải có citation theo số trang, format [Page X], ví dụ [Page 3], [Page 7].
2. Không trích dẫn luật hoặc quy định ngoài context nếu không có trong context.
3. Trả lời bằng tiếng Việt, rõ ràng, ngắn gọn.
4. Nếu có nhiều nguồn mâu thuẫn, hãy nói có mâu thuẫn và liệt kê nguồn.
""".strip()


def build_answer_prompt(question: str, context: str) -> str:
    return f"""
Câu hỏi của user:
{question}

Context đã được retrieval từ tài liệu nội bộ:
{context}

Hãy trả lời dựa trên context. Nhớ citation [Page X] cho từng ý quan trọng.
""".strip()


def build_rewrite_prompt(question: str) -> str:
    return f"""
Rewrite câu hỏi sau thành query tìm kiếm tài liệu HR ngắn gọn, giữ nguyên ý định, không thêm thông tin mới.

Câu hỏi: {question}

Query:
""".strip()
