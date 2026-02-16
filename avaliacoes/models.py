from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Colaborador(models.Model):
    """
    Classe de colaborador -> pode atuar como supervisor ou avaliado
    """

    nome = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Colaborador"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class DimensaoItemAvaliacao(models.TextChoices):  # textchoice -> enum
    """
    Enum para dimensão da avaliacao
    """

    COMPORTAMENTO = "Comportamento", "Comportamento"
    ENTREGAS = "Entregas", "Entregas"
    TRABALHO_EM_EQUIPE = "Trabalho em equipe", "Trabalho em equipe"


class StatusAvaliacao(models.TextChoices):
    """
    Enum para statis da avaliacao
    """

    CRIADA = "Criada", "Criada"
    EM_ELABORACAO = "Em elaboração", "Em elaboração"
    EM_AVALIACAO = "Em avaliação", "Em avaliação"
    CONCLUIDA = "Concluída", "Concluída"


class TipoItemAvaliacaoDesempenho(models.Model):
    """
    Classe que define os tipos de itens da avaliacao
    """

    dimensao = models.CharField(max_length=30, choices=DimensaoItemAvaliacao.choices)

    tipo_item_avaliacao_desempenho = models.CharField(
        max_length=256, verbose_name="Tipo do Item"
    )

    descricao = models.TextField(verbose_name="Descrição")

    class Meta:
        verbose_name = "Tipo de Item de Avaliação"
        ordering = ["dimensao", "tipo_item_avaliacao_desempenho"]

    def __str__(self):
        return f"{self.dimensao} - {self.tipo_item_avaliacao_desempenho}"


class AvaliacaoDesempenho(models.Model):
    """
    Classe de avaliacao de desempenhado do colaborador
    """

    colaborador = models.ForeignKey(
        Colaborador, on_delete=models.PROTECT, related_name="avaliacoes_como_avaliado"
    )

    supervisor = models.ForeignKey(
        Colaborador, on_delete=models.PROTECT, related_name="avaliacoes_como_supervisor"
    )

    # usei protect nos campos colaborador e supervisor -> pois mesmo excluidno a avaliacao, o perfil do colaborador pode ser reutilizado em outras avaliacoes

    mes_competencia = models.DateField(
        verbose_name="Mês de competência",
    )

    status_avaliacao = models.CharField(
        max_length=20, default=StatusAvaliacao.CRIADA, choices=StatusAvaliacao.choices
    )

    nota = models.FloatField(default=0, editable=False)

    sugestoes_supervisor = models.TextField(
        blank=True,
        default="",
        verbose_name="Sugestões do supervisor",
    )

    observacoes_avaliado = models.TextField(
        blank=True,
        default="",
        verbose_name="Observações do avaliado",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["colaborador", "mes_competencia"],
                name="unique_colaborador_mes_competencia",
            )
        ]
        verbose_name = "Avaliação de Desempenho"
        ordering = ["-mes_competencia", "colaborador"]

    def __str__(self):
        return f"{self.colaborador} - " f"{self.mes_competencia.strftime("%b/%Y")}"

    def clean(self):
        """Funcao para evitar que supervisor e avaliado sejam os mesmos users"""
        if self.colaborador_id and self.supervisor_id:
            if self.colaborador_id == self.supervisor_id:
                raise ValidationError(
                    "O avaliado e o supervisor nao podem ser a mesma pessoa"
                )

    """
    Funções da maquina de estados -> irei usar uma abordagem de modelos ricos -> quero garantir que a transicao do estado sempre seja repspeitada
    """

    def iniciar(self):
        """
        Transicao de CRIADA para EM ELABORACAO -> uso: apenas quando status == CRIADA
        """

        if self.status_avaliacao != StatusAvaliacao.CRIADA:
            raise ValidationError(
                "Só é possível inciar uma avaliação com status `CRIADA`"
                "Por favor verifique o status da avaliação"
            )

        self.status_avaliacao = StatusAvaliacao.EM_ELABORACAO
        self.save(
            update_fields=["status_avaliacao"]
        )  # salvar somente o campo alterado pela máquina de estados

    def dar_feedback(self):
        """
        Transicao de EM ELABORACAO para EM AVALIACAO -> uso: apenas quando status == EM ELABORACAO
        """

        if self.status_avaliacao != StatusAvaliacao.EM_ELABORACAO:
            raise ValidationError(
                "Só é possível inciar uma avaliação com status `EM ELABORACAO`"
                "Por favor verifique o status da avaliação"
            )

        self.atualizar_nota()
        self.status_avaliacao = StatusAvaliacao.EM_AVALIACAO
        self.save(update_fields=["status_avaliacao"])

    def concluir(self):
        """
        Transicao de EM AVALIACAO para CONCLUIDA -> uso: apenas quando status == EM AVALIACAO
        """

        if self.status_avaliacao != StatusAvaliacao.EM_AVALIACAO:
            raise ValidationError(
                "Só é possível inciar uma avaliação com status `EM AVALIACAO`"
                "Por favor verifique o status da avaliação"
            )

        self.atualizar_nota()
        self.status_avaliacao = StatusAvaliacao.CONCLUIDA
        self.save(update_fields=["status_avaliacao"])

    def atualizar_nota(self):
        """
        Calcula a nota com base nos itens -> sum(itens.nota) / (count(tipos) * 5) * 100
        """

        total_tipos = TipoItemAvaliacaoDesempenho.objects.count()

        if total_tipos == 0:
            self.nota = 0
        else:
            soma_notas = self.itens.aggregate(total=models.Sum("nota"))["total"] or 0
            self.nota = (soma_notas / (total_tipos * 5)) * 100

        self.save(update_fields=["nota"])

    def criar_itens_avaliacao(self):
        """
        Cadastrar -> cria um item_avaliacao_desempenho para cada tipo disponivel
        """

        tipos = TipoItemAvaliacaoDesempenho.objects.all()

        itens = [
            ItemAvaliacaoDesempenho(
                avaliacao=self,
                tipo_item_avaliacao_desempenho=tipo,
                nota=1,  # valor default -> sera recalculada depois
            )
            for tipo in tipos
        ]

        ItemAvaliacaoDesempenho.objects.bulk_create(itens)


class ItemAvaliacaoDesempenho(models.Model):
    """
    Classe de item de uma avaliação de desempenho
    """

    avaliacao = models.ForeignKey(
        AvaliacaoDesempenho,
        on_delete=models.CASCADE,
        related_name="itens",
    )

    tipo_item_avaliacao_desempenho = models.ForeignKey(
        TipoItemAvaliacaoDesempenho,
        on_delete=models.PROTECT,
        verbose_name="Tipo do item",
    )

    nota = models.IntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    observacoes = models.TextField(
        blank=True,
        default="",
        verbose_name="Observações",
    )

    class Meta:
        verbose_name = "Item de Avaliação"
        ordering = ["tipo_item_avaliacao_desempenho"]

    def __str__(self):
        return f"{self.tipo_item_avaliacao_desempenho} - " f"Nota: {self.nota}"
