from locales import uz, ru


def t(key: str, lang: str = "uz", **kwargs) -> str:
    texts = uz.texts if lang == "uz" else ru.texts
    text = texts.get(key, uz.texts.get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text
