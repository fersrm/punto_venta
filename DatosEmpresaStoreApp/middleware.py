from .models import DatosEmpresa

## Revisar si afecta al  superuser de admin


class DatosEmpresaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        datos_empresa = DatosEmpresa.objects.filter(id_datos_empresa=1).first()
        request.datos_empresa = datos_empresa
        response = self.get_response(request)
        return response
