from rest_framework import serializers
from .models import (
    Colaborador,
    TipoItemAvaliacaoDesempenho,
    AvaliacaoDesempenho,
    ItemAvaliacaoDesempenho,
)


class ColaboradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colaborador
        fields = ["id", "nome"]


class TipoItemAvaliacaoDesempenhoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoItemAvaliacaoDesempenho
        fields = [
            "id",
            "dimensao",
            "tipo_item_avaliacao_desempenho",
            "descricao",
        ]


class ItemAvaliacaoDesempenhoSerializer(serializers.ModelSerializer):
    tipo_item_avaliacao_desempenho_detail = TipoItemAvaliacaoDesempenhoSerializer(
        source="tipo_item_avaliacao_desempenho",
        read_only=True,
    )

    class Meta:
        model = ItemAvaliacaoDesempenho
        fields = [
            "id",
            "avaliacao",
            "tipo_item_avaliacao_desempenho",
            "tipo_item_avaliacao_desempenho_detail",
            "nota",
            "observacoes",
        ]
        read_only_fields = ["avaliacao"]


class ListaAvaliacaoDesempenhoSerializer(serializers.ModelSerializer):
    colaborador_nome = serializers.CharField(
        source="colaborador.nome",
        read_only=True,
    )
    supervisor_nome = serializers.CharField(
        source="supervisor.nome",
        read_only=True,
    )

    class Meta:
        model = AvaliacaoDesempenho
        fields = [
            "id",
            "colaborador",
            "colaborador_nome",
            "supervisor",
            "supervisor_nome",
            "mes_competencia",
            "status_avaliacao",
            "nota",
        ]
        read_only_fields = ["status_avaliacao", "nota"]


class AvaliacaoDesempenhoSerializer(serializers.ModelSerializer):
    colaborador_nome = serializers.CharField(
        source="colaborador.nome",
        read_only=True,
    )
    supervisor_nome = serializers.CharField(
        source="supervisor.nome",
        read_only=True,
    )
    itens = ItemAvaliacaoDesempenhoSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = AvaliacaoDesempenho
        fields = [
            "id",
            "colaborador",
            "colaborador_nome",
            "supervisor",
            "supervisor_nome",
            "mes_competencia",
            "status_avaliacao",
            "nota",
            "sugestoes_supervisor",
            "observacoes_avaliado",
            "itens",
        ]
        read_only_fields = ["status_avaliacao", "nota"]


class CriarAvaliacaoDesempenhoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvaliacaoDesempenho
        fields = [
            "id",
            "colaborador",
            "supervisor",
            "mes_competencia",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        if data.get("colaborador") == data.get("supervisor"):
            raise serializers.ValidationError(
                "O colaborador e o supervisor não podem ser a mesma pessoa."
            )
        return data

    def create(self, validated_data):
        avaliacao = AvaliacaoDesempenho.objects.create(**validated_data)
        avaliacao.criar_itens_avaliacao()
        return avaliacao


class EditarAvaliacaoDesempenhoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvaliacaoDesempenho
        fields = [
            "id",
            "colaborador",
            "supervisor",
            "mes_competencia",
            "status_avaliacao",
            "nota",
            "sugestoes_supervisor",
            "observacoes_avaliado",
        ]
        read_only_fields = [
            "id",
            "colaborador",
            "supervisor",
            "mes_competencia",
            "status_avaliacao",
            "nota",
        ]
