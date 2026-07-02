def fuzzy_find(key, available_keys):
    """
    بحث مرن متعدد المستويات مع تنظيف الرموز.
    """

    if not key or not available_keys:
        return None

    if key in available_keys:
        return key

    key_lower = (
        str(key)
        .lower()
        .strip()
        .replace("_", " ")
        .replace("-", " ")
        .replace("/", " ")
    )

    for item in available_keys:

        item_lower = (
            str(item)
            .lower()
            .strip()
            .replace("_", " ")
            .replace("-", " ")
            .replace("/", " ")
        )

        if key_lower == item_lower:
            return item

        if key_lower in item_lower or item_lower in key_lower:
            return item

        key_words = set(key_lower.split())
        item_words = set(item_lower.split())

        common = key_words & item_words

        if len(common) >= max(
            1,
            min(len(key_words), len(item_words)) * 0.5,
        ):
            return item

    return None
