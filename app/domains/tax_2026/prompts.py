TAX_SYSTEM_PROMPT = """
Bạn là trợ lý hỗ trợ giải thích và tính thuế TNCN 2026.

Quy tắc:
1. Ưu tiên căn cứ từ context đã cung cấp.
2. Nếu thiếu dữ liệu đầu vào hoặc thiếu tài liệu, nói rõ chưa đủ căn cứ.
3. Nếu có tính toán, nêu công thức, giả định, và kết quả.
4. Không khẳng định quy định pháp lý khi context không có.
""".strip()


def build_tax_answer_prompt(question: str, context: str, tool_result: dict | None) -> str:
    tool_text = ""
    if tool_result:
        tool_text = f"\nKết quả tool tính toán kỹ thuật:\n{tool_result}\n"
    return f"""
Câu hỏi của user:
{question}

Context đã retrieval:
{context}
{tool_text}
Hãy trả lời rõ ràng, có citation nếu context có nguồn.
""".strip()
