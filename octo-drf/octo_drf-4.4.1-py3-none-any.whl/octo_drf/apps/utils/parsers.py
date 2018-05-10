from django.urls import resolve


def get_view_data(url, request):
    # TODO add  actions for  viewset
    resolver = resolve(url)
    view = resolve(url).func.cls
    return view.as_view()(request, *resolver.args, **resolver.kwargs).data


def modify_props(props, request, parent=None):
    """
    Парсит json виджета для замены ключей с урлами на данные из этих урлов
    """
    if isinstance(props, list):
        for i, v in enumerate(props):
            modify_props(v, request, parent={'ref': props, 'index': i})

    if isinstance(props, dict):
        for i in props:
            if i == 'type' and props[i] == 'view':
                ref = parent['ref']
                if isinstance(ref, list):
                    ref[parent['index']] = props['url'] = get_view_data(
                        props['url'], request)
                else:
                    ref[parent['key']] = props['url'] = get_view_data(
                        props['url'], request)
            else:
                modify_props(props[i], request, parent={
                             'ref': props, 'key': i})
