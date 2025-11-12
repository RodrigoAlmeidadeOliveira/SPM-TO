"""
Formulário de criação e resposta de avaliações
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TextAreaField, HiddenField, RadioField, SubmitField
from wtforms.validators import DataRequired, Optional, ValidationError
from datetime import date

class AvaliacaoForm(FlaskForm):
    """Formulário para criar uma nova avaliação"""

    paciente_id = SelectField(
        'Paciente',
        coerce=int,
        validators=[DataRequired(message='Selecione um paciente')],
        render_kw={'class': 'form-select'}
    )

    instrumento_id = SelectField(
        'Instrumento de Avaliação',
        coerce=int,
        validators=[DataRequired(message='Selecione o instrumento de avaliação')],
        render_kw={'class': 'form-select'}
    )

    contexto = SelectField(
        'Contexto da Avaliação (opcional)',
        choices=[
            ('', 'Selecione o contexto (opcional)...'),
            ('casa', 'Casa - Avaliação pelos pais/responsáveis'),
            ('escola', 'Escola - Avaliação por professores/educadores')
        ],
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )

    data_avaliacao = DateField(
        'Data da Avaliação',
        validators=[DataRequired(message='A data da avaliação é obrigatória')],
        default=date.today,
        format='%Y-%m-%d',
        render_kw={'class': 'form-control'}
    )

    relacionamento_respondente = SelectField(
        'Relacionamento do Respondente',
        choices=[
            ('', 'Selecione...'),
            ('Mãe', 'Mãe'),
            ('Pai', 'Pai'),
            ('Avô/Avó', 'Avô/Avó'),
            ('Responsável Legal', 'Responsável Legal'),
            ('Professor(a)', 'Professor(a)'),
            ('Coordenador(a)', 'Coordenador(a)'),
            ('Terapeuta', 'Terapeuta'),
            ('Outro', 'Outro')
        ],
        validators=[DataRequired(message='Especifique o relacionamento do respondente')],
        render_kw={'class': 'form-select'}
    )

    comentarios = TextAreaField(
        'Comentários Iniciais',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Observações sobre o contexto da avaliação, comportamento recente, etc.',
            'class': 'form-control',
            'rows': 3
        }
    )

    submit = SubmitField('Salvar Avaliação', render_kw={'class': 'btn btn-primary btn-lg'})

    def validate_data_avaliacao(self, field):
        """Valida se a data da avaliação não é futura"""
        if field.data > date.today():
            raise ValidationError('A data da avaliação não pode ser futura')


class RespostaForm(FlaskForm):
    """Formulário para responder uma questão"""

    DEFAULT_CHOICES = [
        ('NUNCA', 'Nunca'),
        ('OCASIONAL', 'Ocasional'),
        ('FREQUENTE', 'Frequente'),
        ('SEMPRE', 'Sempre'),
    ]

    DEFAULT_DESCRIPTIONS = {
        'NUNCA': 'Não observado',
        'OCASIONAL': 'Algumas vezes',
        'FREQUENTE': 'Muitas vezes',
        'SEMPRE': 'Sempre',
    }

    questao_id = HiddenField('Questão ID', validators=[DataRequired()])

    valor = RadioField(
        'Resposta',
        choices=[
            ('NUNCA', 'Nunca'),
            ('OCASIONAL', 'Ocasionalmente'),
            ('FREQUENTE', 'Frequentemente'),
            ('SEMPRE', 'Sempre')
        ],
        validators=[DataRequired(message='Selecione uma resposta')],
        render_kw={'class': 'form-check-input'}
    )

    submit = SubmitField('Salvar Resposta')
