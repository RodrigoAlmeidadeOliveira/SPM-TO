"""
Formulário de cadastro e edição de pacientes
"""
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from datetime import date


class PacienteForm(FlaskForm):
    """Formulário para cadastro e edição de pacientes"""

    nome = StringField(
        'Nome Completo',
        validators=[
            DataRequired(message='O nome é obrigatório'),
            Length(min=3, max=200, message='O nome deve ter entre 3 e 200 caracteres')
        ],
        render_kw={'placeholder': 'Ex: João Silva Santos', 'class': 'form-control'}
    )

    identificacao = StringField(
        'Identificação/Código',
        validators=[
            DataRequired(message='A identificação é obrigatória'),
            Length(min=1, max=50, message='A identificação deve ter entre 1 e 50 caracteres')
        ],
        render_kw={'placeholder': 'Ex: PAC001', 'class': 'form-control'}
    )

    data_nascimento = DateField(
        'Data de Nascimento',
        validators=[DataRequired(message='A data de nascimento é obrigatória')],
        format='%Y-%m-%d',
        render_kw={'class': 'form-control'}
    )

    sexo = SelectField(
        'Sexo',
        choices=[
            ('', 'Selecione...'),
            ('M', 'Masculino'),
            ('F', 'Feminino'),
            ('O', 'Outro')
        ],
        validators=[DataRequired(message='O sexo é obrigatório')],
        render_kw={'class': 'form-select'}
    )

    raca_etnia = SelectField(
        'Raça/Etnia',
        choices=[
            ('', 'Selecione...'),
            ('Branca', 'Branca'),
            ('Preta', 'Preta'),
            ('Parda', 'Parda'),
            ('Amarela', 'Amarela'),
            ('Indígena', 'Indígena'),
            ('Não declarada', 'Não declarada')
        ],
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )

    observacoes = TextAreaField(
        'Observações',
        validators=[Optional(), Length(max=1000, message='As observações devem ter no máximo 1000 caracteres')],
        render_kw={
            'placeholder': 'Informações adicionais sobre o paciente...',
            'class': 'form-control',
            'rows': 4
        }
    )

    ativo = BooleanField(
        'Paciente Ativo',
        default=True,
        render_kw={'class': 'form-check-input'}
    )

    def validate_data_nascimento(self, field):
        """Valida se a data de nascimento não é futura e se a idade é válida para avaliação"""
        if field.data > date.today():
            raise ValidationError('A data de nascimento não pode ser futura')

        hoje = date.today()
        idade_anos = hoje.year - field.data.year
        if (hoje.month, hoje.day) < (field.data.month, field.data.day):
            idade_anos -= 1

        if idade_anos < 3:
            raise ValidationError('O paciente deve ter pelo menos 3 anos para ser avaliado com os instrumentos SPM')

        if idade_anos > 12:
            raise ValidationError('Os instrumentos SPM são projetados para crianças de 3 a 12 anos. Verifique se este é o instrumento adequado.')
