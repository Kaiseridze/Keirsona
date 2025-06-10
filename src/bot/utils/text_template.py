from typing import Any

def return_description(profile: dict[Any]) -> str: # type: ignore
    result_text = (
        f"Ваш тип личности: {profile['type_code']} — {profile['type_name']}\n\n"
        f"{profile['description']}\n\n"
        f"Сильные стороны: {profile['strengths']}\n"
        f"Слабые стороны: {profile['weaknesses']}\n"
        f"Профессиональные качества: {profile['professional_qualities']}\n"
        f"Процент людей с таким же типом личности: {profile['percentage']}%"
    )
    return result_text