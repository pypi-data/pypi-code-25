from crudlfap.views import generic
from crudlfap_filtertables2.views import FilterTables2ListView


class HistoryView(generic.ObjectView, FilterTables2ListView):
    menus = ['object']
    material_icon = 'history'

    def get_filterset_kwargs(self):
        return {
            'data': self.request.GET or None,
            'request': self.request,
            'queryset': self.get_queryset(),
        }
