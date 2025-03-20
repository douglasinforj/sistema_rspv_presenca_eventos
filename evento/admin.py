from django.contrib import admin
from django.utils.html import format_html
from .models import Evento, Convidado, Confirmacao

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data', 'local', 'criado_em')
    list_filter = ('data', 'local', 'criado_em')
    search_fields = ('nome', 'local', 'descricao')
    ordering  = ('-data',)
    date_hierarchy = 'data'


@admin.register(Convidado)
class ConvidadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'evento', 'evento_data')
    list_filter = ('evento',)
    search_fields = ('nome', 'email', 'evento__nome')
    ordering = ('nome',)

    def evento_data(self, obj):
        return obj.evento.data.strftime('%d/%m/%Y %H:%M')
    evento_data.short_description = 'Data do Evento'


@admin.register(Confirmacao)
class ConfirmacaoAdmin(admin.ModelAdmin):
    list_display = ('convidado', 'evento', 'confirmado', 'restricoes_alimentares_formatadas')
    list_filter = ('confirmado',)
    search_fields = ('convidado__nome', 'convidado__email', 'convidado__evento__nome')
    ordering = ('-confirmado',)

    actions = ['marcar_como_confirmado', 'marcar_como_nao_confirmado']

    def evento(self, obj):
        return obj.convidado.evento
    evento.short_description = "Evento"

    def restricoes_alimentares_formatadas(self, obj):
        return format_html(f'<span style="color: red;">{obj.restricoes_alimentares}</span>') if obj.restricoes_alimentares else "Nenhuma"
    restricoes_alimentares_formatadas.short_description = "Restrições Alimentares"

    @admin.action(description="Marcar convidados como Confirmado")
    def marcar_como_confirmado(self, request, queryset):
        queryset.update(confirmado=True)

    @admin.action(description="Marcar convidados como Não Confirmado")
    def marcar_como_nao_confirmado(self, request, queryset):
        queryset.update(confirmado=False)
