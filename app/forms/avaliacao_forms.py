"""
Formulários de Avaliação
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TextAreaField, SubmitField, RadioField, HiddenField
from wtforms.validators import DataRequired, Optional


class AvaliacaoForm(FlaskForm):
    """Formulário de criação de avaliação"""
    paciente_id = SelectField('Paciente', validators=[
        DataRequired(message='Selecione um paciente')
    ], coerce=int)

    instrumento_id = SelectField('Instrumento', validators=[
        DataRequired(message='Selecione um instrumento')
    ], coerce=int)

    data_avaliacao = DateField('Data da Avaliação', validators=[
        DataRequired(message='Campo obrigatório')
    ], format='%Y-%m-%d')

    relacionamento_respondente = SelectField('Relacionamento do Respondente', validators=[
        DataRequired(message='Campo obrigatório')
    ], choices=[
        ('', 'Selecione...'),
        ('pai', 'Pai'),
        ('mae', 'Mãe'),
        ('responsavel_legal', 'Responsável Legal'),
        ('professor', 'Professor(a)'),
        ('terapeuta', 'Terapeuta'),
        ('outro', 'Outro')
    ])

    comentarios = TextAreaField('Comentários sobre comportamento e funcionamento', validators=[
        Optional()
    ])

    submit = SubmitField('Criar Avaliação')


class RespostaForm(FlaskForm):
    """Formulário para responder uma questão"""
    questao_id = HiddenField('Questão ID', validators=[DataRequired()])

    valor = RadioField('Resposta', validators=[
        DataRequired(message='Selecione uma opção')
    ], choices=[
        ('NUNCA', 'Nunca'),
        ('OCASIONAL', 'Ocasional'),
        ('FREQUENTE', 'Frequente'),
        ('SEMPRE', 'Sempre')
    ])

    submit = SubmitField('Próxima')
