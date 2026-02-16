from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(
    r'colaboradores',
    views.ColaboradorViewSet,
    basename='colaborador',
)
router.register(
    r'tipos-item-avaliacao',
    views.TipoItemAvaliacaoDesempenhoViewSet,
    basename='tipo-item-avaliacao',
)
router.register(
    r'avaliacoes',
    views.AvaliacaoDesempenhoViewSet,
    basename='avaliacao',
)
router.register(
    r'itens-avaliacao',
    views.ItemAvaliacaoDesempenhoViewSet,
    basename='item-avaliacao',
)

urlpatterns = [
    path('', include(router.urls)),
]