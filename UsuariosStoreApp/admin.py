from django.contrib import admin
from UsuariosStoreApp.models import Profile, Position

# Register your models here.


# Registro de Cargo
@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    pass


@admin.register(Profile)
class UsuarioAdmin(admin.ModelAdmin):
    pass
