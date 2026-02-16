from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

from .models import (
    Colaborador,
    TipoItemAvaliacaoDesempenho,
    AvaliacaoDesempenho,
    ItemAvaliacaoDesempenho,
    StatusAvaliacao,
)
from .serializers import (
    ColaboradorSerializer,
    TipoItemAvaliacaoDesempenhoSerializer,
    ListarAvaliacaoDesempenhoSerializer,
    AvaliacaoDesempenhoSerializer,
    CriarAvaliacaoDesempenhoSerializer,
    EditarAvaliacaoDesempenhoSerializer,
    ItemAvaliacaoDesempenhoSerializer,
)


class ColaboradorViewSet(viewsets.ModelViewSet):
    queryset = Colaborador.objects.all()
    serializer_class = ColaboradorSerializer
    search_fields = ["nome"]


class TipoItemAvaliacaoDesempenhoViewSet(viewsets.ModelViewSet):
    queryset = TipoItemAvaliacaoDesempenho.objects.all()
    serializer_class = TipoItemAvaliacaoDesempenhoSerializer
    filterset_fields = ["dimensao"]
    search_fields = ["tipo_item_avaliacao_desempenho", "descricao"]


class AvaliacaoDesempenhoViewSet(viewsets.ModelViewSet):

    queryset = AvaliacaoDesempenho.objects.select_related(
        "colaborador", "supervisor"
    ).prefetch_related("itens")
    filterset_fields = ["status_avaliacao", "colaborador", "supervisor"]
    search_fields = ["colaborador__nome", "supervisor__nome"]
    ordering_fields = ["mes_competencia", "nota"]

    def get_serializer_class(self):
        if self.action == "list":
            return ListarAvaliacaoDesempenhoSerializer
        if self.action == "create":
            return CriarAvaliacaoDesempenhoSerializer
        if self.action in ["update", "partial_update"]:
            return EditarAvaliacaoDesempenhoSerializer
        return AvaliacaoDesempenhoSerializer

    def perform_update(self, serializer):
        """limita a avalicao com base na maquina de estados"""
        avaliacao = self.get_object()
        estados_permitidos = [
            StatusAvaliacao.EM_ELABORACAO,
            StatusAvaliacao.EM_AVALIACAO,
        ]
        if avaliacao.status_avaliacao not in estados_permitidos:
            raise ValidationError(
                "A avaliação só pode ser editada nos estados `Em elaboração` ou `Em avaliação`"
            )
        serializer.save()

    @extend_schema(
        request=None,
        responses={200: AvaliacaoDesempenhoSerializer},
        description="Transição: Criada para Em elaboração",
    )
    @action(detail=True, methods=["post"], url_path="iniciar")
    def iniciar(self, request, pk=None):
        """S0 da máquina de estados: CRIADA -> EM ELABORACAO"""
        avaliacao = self.get_object()
        try:
            avaliacao.iniciar()
        except ValidationError as e:
            return Response(
                {"detalhes do erro:": str(e.message)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = AvaliacaoDesempenhoSerializer(avaliacao)
        return Response(serializer.data)

    @extend_schema(
        request=None,
        responses={200: AvaliacaoDesempenhoSerializer},
        description="Transição: Em elaboração para Em avaliação",
    )
    @action(detail=True, methods=["post"], url_path="dar-feedback")
    def dar_feedback(self, request, pk=None):
        """S1 da máquina de estados: EM ELABORACAO -> EM AVALIACAO"""
        avaliacao = self.get_object()
        try:
            avaliacao.dar_feedback()
        except ValidationError as e:
            return Response(
                {"detalhes do erro:": str(e.message)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = AvaliacaoDesempenhoSerializer(avaliacao)
        return Response(serializer.data)

    @extend_schema(
        request=None,
        responses={200: AvaliacaoDesempenhoSerializer},
        description="Transição: Em avaliação para Concluída",
    )
    @action(detail=True, methods=["post"], url_path="concluir")
    def concluir(self, request, pk=None):
        """S2 da máquina de estados: EM AVALIACAO -> CONCLUIDA"""
        avaliacao = self.get_object()
        try:
            avaliacao.concluir()
        except ValidationError as e:
            return Response(
                {"detalhes do erro:": str(e.message)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = AvaliacaoDesempenhoSerializer(avaliacao)
        return Response(serializer.data)


class ItemAvaliacaoDesempenhoViewSet(viewsets.ModelViewSet):
    """
    1. editar um item -> a nota da avaliacaoo é recalculada
    2. restricao das funcoes de acordo com o status da avaliacao (m.estados)
    """

    queryset = ItemAvaliacaoDesempenho.objects.select_related(
        "avaliacao", "tipo_item_avaliacao_desempenho"
    )
    serializer_class = ItemAvaliacaoDesempenhoSerializer
    filterset_fields = ["avaliacao", "tipo_item_avaliacao_desempenho"]

    def perform_update(self, serializer):
        """restringe a edicao dos itens ao estado de "em elaboracao" e recalcula a nota"""
        item = self.get_object()
        if item.avaliacao.status_avaliacao != StatusAvaliacao.EM_ELABORACAO:
            raise ValidationError(
                "Itens só podem ser editados quando a avaliação está `Em elaboração`"
            )
        item = serializer.save()
        item.avaliacao.atualizar_nota()

    def get_queryset(self):
        """filtragem por query param"""
        queryset = super().get_queryset()
        avaliacao_id = self.request.query_params.get("avaliacao")
        if avaliacao_id:
            queryset = queryset.filter(avaliacao_id=avaliacao_id)
        return queryset
