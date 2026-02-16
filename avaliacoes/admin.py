from django.contrib import admin
from .models import (
    Colaborador,
    TipoItemAvaliacaoDesempenho,
    AvaliacaoDesempenho,
    ItemAvaliacaoDesempenho,
)


@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ["id", "nome"]
    search_fields = ["nome"]
    ordering = ["nome"]


@admin.register(TipoItemAvaliacaoDesempenho)
class TipoItemAvaliacaoDesempenhoAdim(admin.ModelAdmin):
    list_display = ["id", "dimensao", "tipo_item_avaliacao_desempenho"]
    search_fields = ["tipo_item_avaliacao_desempenho", "descricao"]
    list_filter = ["dimensao"]


class ItemAvaliacaoDesempenhoInline(admin.TabularInline):
    """editar itens no formulário da avaliacao"""

    model = ItemAvaliacaoDesempenho
    fields = ["tipo_item_avaliacao_desempenho", "nota", "observacoes"]
    extra = 0 # problema que resolvi -> por padrao ele vem com extra = 3, por isso que no admin toda vez que ia inciar uma nova avaliacao ele colocava 3 itens defaults la
    


@admin.register(AvaliacaoDesempenho)
class AvaliacaoDesempenhoAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "colaborador",
        "supervisor",
        "mes_competencia",
        "status_avaliacao",
        "nota",
    ]
    list_filter = ["status_avaliacao", "mes_competencia"]
    search_fields = ["colaborador__nome", "supervisor__nome"]
    readonly_fields = ["nota", "status_avaliacao"]
    inlines = [ItemAvaliacaoDesempenhoInline]
    date_hierarchy = "mes_competencia"  # filtragem por data


@admin.register(ItemAvaliacaoDesempenho)
class ItemAvaliacaoDesempenhoAdmin(admin.ModelAdmin):
    list_display = ["id", "avaliacao", "tipo_item_avaliacao_desempenho", "nota"]
    list_filter = ["tipo_item_avaliacao_desempenho__dimensao"]
    search_fields = ["avaliacao__colaborador__nome"]
