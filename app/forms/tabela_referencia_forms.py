"""
Formulários relacionados a Tabelas de Referência
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length


class TabelaReferenciaForm(FlaskForm):
    """Formulário de cadastro/edição de tabelas de referência"""

    dominio_codigo = StringField(
        'Código do Domínio',
        validators=[
            DataRequired(message='Informe o código do domínio'),
            Length(max=10, message='O código deve ter no máximo 10 caracteres')
        ],
        render_kw={'placeholder': 'Ex: SOC, VIS, HEA', 'class': 'form-control'}
    )

    escore_min = IntegerField(
        'Escore Mínimo',
        validators=[
            DataRequired(message='Informe o escore mínimo'),
            NumberRange(min=0, max=500, message='O escore deve estar entre 0 e 500')
        ],
        render_kw={'class': 'form-control', 'min': 0}
    )

    escore_max = IntegerField(
        'Escore Máximo',
        validators=[
            DataRequired(message='Informe o escore máximo'),
            NumberRange(min=0, max=500, message='O escore deve estar entre 0 e 500')
        ],
        render_kw={'class': 'form-control', 'min': 0}
    )

    t_score = IntegerField(
        'T-Score',
        validators=[
            DataRequired(message='Informe o T-Score'),
            NumberRange(min=0, max=200, message='O T-Score deve estar entre 0 e 200')
        ],
        render_kw={'class': 'form-control', 'min': 0}
    )

    percentil_min = IntegerField(
        'Percentil Mínimo',
        validators=[NumberRange(min=0, max=100, message='O percentil deve estar entre 0 e 100')],
        render_kw={'class': 'form-control', 'min': 0, 'max': 100}
    )

    percentil_max = IntegerField(
        'Percentil Máximo',
        validators=[NumberRange(min=0, max=100, message='O percentil deve estar entre 0 e 100')],
        render_kw={'class': 'form-control', 'min': 0, 'max': 100}
    )

    classificacao = SelectField(
        'Classificação',
        choices=[
            ('', 'Selecione...'),
            ('TIPICO', 'Típico'),
            ('PROVAVEL_DISFUNCAO', 'Provável Disfunção'),
            ('DISFUNCAO_DEFINITIVA', 'Disfunção Definitiva')
        ],
        validators=[DataRequired(message='Selecione a classificação')],
        render_kw={'class': 'form-select'}
    )

    submit = SubmitField('Salvar Tabela', render_kw={'class': 'btn btn-primary'})

    def validate(self, extra_validators=None):
        """Validações extras"""
        initial_validation = super().validate(extra_validators=extra_validators)
        if not initial_validation:
            return False

        if self.escore_max.data < self.escore_min.data:
            self.escore_max.errors.append('O escore máximo deve ser maior ou igual ao mínimo.')
            return False

        if self.percentil_min.data and self.percentil_max.data:
            if self.percentil_max.data < self.percentil_min.data:
                self.percentil_max.errors.append('O percentil máximo deve ser maior ou igual ao mínimo.')
                return False

        return True
