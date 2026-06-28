from fastapi import HTTPException


def clean_kind_list(kind_list: list[str]) -> list[str]:
    if not kind_list:
        raise HTTPException(status_code=400, detail="Поле 'kind' обязательно")

    cleaned = []
    for k in kind_list:
        if not isinstance(k, str):
            raise HTTPException(status_code=400, detail="Каждый элемент 'kind' должен быть строкой")

        k2 = k.lower().strip()
        if len(k2) < 2:
            raise HTTPException(status_code=400, detail="Каждый элемент 'kind' должен содержать минимум 2 символа")

        cleaned.append(k2)

    cleaned = list(set(cleaned))

    if not cleaned:
        raise HTTPException(status_code=400, detail="Список 'kind' не может быть пустым")

    return cleaned


def normalize_title_line(title: str) -> str:
    words = title.strip().split()

    normalized_words = []
    for w in words:
        if "-" in w:
            parts = w.split("-")
            parts = [p.capitalize() for p in parts]
            normalized_words.append("-".join(parts))
        else:
            normalized_words.append(w.capitalize())

    return " ".join(normalized_words)


def find_category_index(info: list, category_title: str):
    for i, block in enumerate(info):
        if category_title in block:
            return i
    return None
