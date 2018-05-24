from hexia_parameters.models import Parameter

def hexia_parameters (request):
    context = {}
    parameters = Parameter.objects.all()
    for p in parameters:
        context[p.name] = p
    return context