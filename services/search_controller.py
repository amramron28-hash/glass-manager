# services/search_controller.py

def process_search_query(
    search_query_value,
    current_phone_attr,
    suggestions_list_attr,
    show_curtain_attr,
    autocomplete_index_attr,
):
    """معالجة البحث والإكمال التلقائي."""

    query = str(search_query_value).strip()
    current_phone_attr.set(query)

    if not query:
        suggestions_list_attr.set([])
        show_curtain_attr.set(False)
        return

    trie = autocomplete_index_attr()
    if trie is None:
        suggestions_list_attr.set([])
        show_curtain_attr.set(False)
        return

    matches = trie.search_prefix(query, 10)
    exact = trie.contains_exact(query)

    if matches and not exact:
        suggestions_list_attr.set(matches)
        show_curtain_attr.set(True)
    else:
        suggestions_list_attr.set([])
        show_curtain_attr.set(False)
