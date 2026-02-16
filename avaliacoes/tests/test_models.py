import pytest
from datetime import date
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from avaliacoes.models import (
    Colaborador,
    TipoItemAvaliacaoDesempenho,
    AvaliacaoDesempenho,
    StatusAvaliacao,
    DimensaoItemAvaliacao,
)


@pytest.fixture
def colaborador(db):
    return Colaborador.objects.create(nome="Joao Silva")


@pytest.fixture
def supervisor(db):
    return Colaborador.objects.create(nome="Maria Souza")


@pytest.fixture
def tipo_item_comportamento(db):
    return TipoItemAvaliacaoDesempenho.objects.create(
        dimensao=DimensaoItemAvaliacao.COMPORTAMENTO,
        tipo_item_avaliacao_desempenho="Pontualidade",
        descricao="avalia a pontualidade do colaborador",
    )


@pytest.fixture
def tipo_item_entregas(db):
    return TipoItemAvaliacaoDesempenho.objects.create(
        dimensao=DimensaoItemAvaliacao.ENTREGAS,
        tipo_item_avaliacao_desempenho="Qualidade",
        descricao="avalia a qualidade das entregas",
    )


@pytest.fixture
def avaliacao(db, colaborador, supervisor, tipo_item_comportamento, tipo_item_entregas):
    avaliacao = AvaliacaoDesempenho.objects.create(
        colaborador=colaborador,
        supervisor=supervisor,
        mes_competencia=date(2026, 2, 1),
    )
    avaliacao.criar_itens_avaliacao()
    return avaliacao


class TestColaborador:
    def test_criar_colaborador(self, colaborador):
        assert colaborador.nome == "Joao Silva"


class TestTipoItemAvaliacaoDesempenho:
    def test_criar_tipo_item(self, tipo_item_comportamento):
        assert tipo_item_comportamento.dimensao == DimensaoItemAvaliacao.COMPORTAMENTO
        assert tipo_item_comportamento.tipo_item_avaliacao_desempenho == "Pontualidade"


class TestAvaliacaoDesempenho:
    def test_criar_avaliacao(self, avaliacao):
        assert avaliacao.status_avaliacao == StatusAvaliacao.CRIADA
        assert (
            avaliacao.nota == 0
        )  # valida se a nota inicial ta como zero -> so mudará nos proximos estados

    def test_criar_itens_automaticamente(self, avaliacao):
        """valida a regra de negocio: quando cadastrada precisa criar itens para cada tipo"""
        assert avaliacao.itens.count() == 2

    def test_unique_colaborador_mes(self, avaliacao, colaborador, supervisor):
        """nao pode haver duas avaliacões para o mesmo colaborador no mesmo mês"""
        with pytest.raises(IntegrityError):
            AvaliacaoDesempenho.objects.create(
                colaborador=colaborador,
                supervisor=supervisor,
                mes_competencia=date(2026, 2, 1),
            )

    def test_colaborador_diferente_supervisor(self, db, colaborador):
        """colaborador e supervisor nao podem ser a mesma pessoa"""
        avaliacao = AvaliacaoDesempenho(
            colaborador=colaborador,
            supervisor=colaborador,
            mes_competencia=date(2026, 3, 1),
        )
        with pytest.raises(ValidationError):
            avaliacao.clean()


class TestMaquinaEstados:
    def test_iniciar_avaliacao(self, avaliacao):
        """criada -> em elaboracao"""
        avaliacao.iniciar()
        assert avaliacao.status_avaliacao == StatusAvaliacao.EM_ELABORACAO

    def test_iniciar_avaliacao_estado_invalido(self, avaliacao):
        """nao pode iniciar se nao estiver com status criada"""
        avaliacao.iniciar()  # vai para em elaboracao
        with pytest.raises(ValidationError):
            avaliacao.iniciar()  # tenta iniciar de novo

    def test_dar_feedback(self, avaliacao):
        """em elaboracao -> em avaliacao"""
        avaliacao.iniciar()
        avaliacao.dar_feedback()
        assert avaliacao.status_avaliacao == StatusAvaliacao.EM_AVALIACAO

    def test_dar_feedback_estado_invalido(self, avaliacao):
        """nao pode dar feedback se nao estiver mm elaboracao"""
        with pytest.raises(ValidationError):
            avaliacao.dar_feedback()

    def test_concluir(self, avaliacao):
        """em avaliacao → concluida"""
        avaliacao.iniciar()
        avaliacao.dar_feedback()
        avaliacao.concluir()
        assert avaliacao.status_avaliacao == StatusAvaliacao.CONCLUIDA

    def test_concluir_estado_invalido(self, avaliacao):
        """nao pode concluir se nao estiver em avaliacao"""
        with pytest.raises(ValidationError):
            avaliacao.concluir()
