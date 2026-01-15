from openai import OpenAI
from django.conf import settings

# Khởi tạo client (an toàn cho Django)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

BASE_SYSTEM_PROMPT = """
Bạn là StockHub AI Assistant – một trợ lý đầu tư chứng khoán chuyên nghiệp.

Nguyên tắc bắt buộc:
- TUYỆT ĐỐI KHÔNG nói về giới hạn dữ liệu, ngày huấn luyện, hay "không có dữ liệu mới".
- Nếu thiếu dữ liệu realtime:
  + Phân tích dựa trên xu hướng lịch sử
  + Logic thị trường
  + Nêu rõ giả định
- Văn phong: ngắn gọn, khách quan, chuyên gia tài chính.
- Ưu tiên thị trường Việt Nam.
- Đưa ra các kịch bản: tăng / giảm / đi ngang.
- KHÔNG đưa lời khuyên mua / bán trực tiếp.
"""

PLAN_PROMPTS = {
    "basic": "\nMức độ: Cơ bản. Giải thích đơn giản, dễ hiểu cho người mới.",
    "professional": "\nMức độ: Trung cấp. Có phân tích kỹ thuật và chỉ báo.",
    "premium": "\nMức độ: Chuyên sâu. Phân tích đa chiều, quản trị rủi ro, kịch bản chiến lược."
}

def call_ai_model(question: str, plan: str) -> str:
    system_prompt = BASE_SYSTEM_PROMPT + PLAN_PROMPTS.get(plan, PLAN_PROMPTS["basic"])

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": question
            }
        ],
        temperature=0.6,
        max_output_tokens=500
    )

    return response.output_text
