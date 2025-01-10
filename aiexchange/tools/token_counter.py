

import google.generativeai as genai


def count_tokens(model_name: str, text: str) -> int:
    model = genai.GenerativeModel(model_name)
    response = model.count_tokens(text)
    return response.total_tokens
