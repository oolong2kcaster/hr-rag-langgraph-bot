# hr-rag-langgraph-bot

`hr-rag-langgraph-bot` là một chatbot AI hỗ trợ hỏi đáp tài liệu nhân sự nội bộ bằng kiến trúc RAG.

Dự án sử dụng LangGraph để điều phối luồng xử lý hội thoại, OpenAI để tạo embedding và sinh câu trả lời, Qdrant làm vector database để lưu trữ và truy xuất tài liệu liên quan.

## Tính năng chính

- Hỏi đáp dựa trên tài liệu HR nội bộ
- Tìm kiếm ngữ nghĩa bằng vector embedding
- Truy xuất tài liệu liên quan từ Qdrant
- Sinh câu trả lời có ngữ cảnh bằng OpenAI
- Điều phối workflow bằng LangGraph
- Hỗ trợ kiểm soát luồng xử lý, logging và mở rộng pipeline RAG

## Tech Stack

- Python
- LangGraph
- LangChain
- OpenAI API
- Qdrant Vector Database
- FastAPI
- Docker

## Use case

Dự án phù hợp cho các hệ thống nội bộ như:

- Hỏi đáp chính sách nhân sự
- Tra cứu quy định công ty
- Hỗ trợ onboarding nhân viên mới
- Tự động hóa trả lời câu hỏi thường gặp từ tài liệu HR
