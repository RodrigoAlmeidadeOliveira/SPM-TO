"""
Serviço para geração de relatórios PDF do PEI
"""
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime


class PeiPDFService:
    """Serviço para geração de relatórios PDF do PEI"""

    @staticmethod
    def gerar_relatorio_pei(avaliacao, itens_pei):
        """
        Gera relatório PDF do Plano Educacional Individualizado

        Args:
            avaliacao: Instância de Avaliacao
            itens_pei: Lista de PlanoItem selecionados

        Returns:
            BytesIO: Buffer com o PDF gerado
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # Estilos
        styles = getSampleStyleSheet()

        # Estilo customizado para título
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#0d6efd'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        # Estilo para subtítulo
        subtitulo_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#495057'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )

        # Estilo para texto normal
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceBefore=6,
            spaceAfter=6
        )

        # Estilo para itens do PEI
        item_style = ParagraphStyle(
            'ItemPEI',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=0.5*cm,
            spaceBefore=8,
            spaceAfter=8,
            bulletIndent=0.25*cm
        )

        # Container dos elementos
        elements = []

        # ===== CABEÇALHO =====
        elements.append(Paragraph('PLANO EDUCACIONAL INDIVIDUALIZADO (PEI)', titulo_style))
        elements.append(Spacer(1, 0.5*cm))

        # ===== DADOS DO PACIENTE =====
        paciente = avaliacao.paciente
        idade_anos, idade_meses = paciente.calcular_idade()

        dados_paciente = [
            ['<b>Nome:</b>', paciente.nome],
            ['<b>Identificação:</b>', paciente.identificacao],
            ['<b>Data de Nascimento:</b>', paciente.data_nascimento.strftime('%d/%m/%Y')],
            ['<b>Idade:</b>', f'{idade_anos} anos e {idade_meses} meses'],
            ['<b>Sexo:</b>', paciente.get_sexo_display()],
        ]

        tabela_paciente = Table(dados_paciente, colWidths=[4*cm, 12*cm])
        tabela_paciente.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (0, -1), 0),
        ]))

        elements.append(tabela_paciente)
        elements.append(Spacer(1, 0.5*cm))

        # ===== DADOS DA AVALIAÇÃO =====
        elements.append(Paragraph('INFORMAÇÕES DA AVALIAÇÃO', subtitulo_style))

        dados_avaliacao = [
            ['<b>Instrumento:</b>', avaliacao.instrumento.nome],
            ['<b>Data da Avaliação:</b>', avaliacao.data_avaliacao.strftime('%d/%m/%Y')],
            ['<b>Avaliador:</b>', avaliacao.avaliador.nome_completo],
            ['<b>Respondente:</b>', avaliacao.relacionamento_respondente or 'Não informado'],
        ]

        tabela_avaliacao = Table(dados_avaliacao, colWidths=[4*cm, 12*cm])
        tabela_avaliacao.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (0, -1), 0),
        ]))

        elements.append(tabela_avaliacao)
        elements.append(Spacer(1, 0.8*cm))

        # ===== RESULTADOS DA AVALIAÇÃO =====
        elements.append(Paragraph('RESULTADOS DA AVALIAÇÃO SPM', subtitulo_style))
        elements.append(Spacer(1, 0.3*cm))

        # Classificações por domínio
        dominios_info = [
            ('SOC', 'Participação Social', avaliacao.classificacao_soc, avaliacao.t_score_soc),
            ('VIS', 'Visão', avaliacao.classificacao_vis, avaliacao.t_score_vis),
            ('HEA', 'Audição', avaliacao.classificacao_hea, avaliacao.t_score_hea),
            ('TOU', 'Tato', avaliacao.classificacao_tou, avaliacao.t_score_tou),
            ('BOD', 'Consciência Corporal', avaliacao.classificacao_bod, avaliacao.t_score_bod),
            ('BAL', 'Equilíbrio', avaliacao.classificacao_bal, avaliacao.t_score_bal),
            ('PLA', 'Planejamento', avaliacao.classificacao_pla, avaliacao.t_score_pla),
        ]

        # Se for SPM-P, incluir OLF
        if avaliacao.instrumento.codigo == 'SPM_P':
            dominios_info.append(('OLF', 'Olfato/Paladar', avaliacao.classificacao_olf, avaliacao.t_score_olf))

        # Criar tabela de resultados
        dados_resultados = [['<b>Domínio</b>', '<b>T-Score</b>', '<b>Classificação</b>']]

        for codigo, nome, classificacao, t_score in dominios_info:
            if classificacao:
                class_texto = PeiPDFService._formatar_classificacao(classificacao)
                dados_resultados.append([nome, str(t_score) if t_score else '-', class_texto])

        if len(dados_resultados) > 1:  # Se houver dados
            tabela_resultados = Table(dados_resultados, colWidths=[8*cm, 3*cm, 5*cm])
            tabela_resultados.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e9ecef')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            elements.append(tabela_resultados)
            elements.append(Spacer(1, 0.8*cm))

        # ===== ITENS DO PEI =====
        elements.append(PageBreak())
        elements.append(Paragraph('OBJETIVOS E ESTRATÉGIAS DO PEI', subtitulo_style))
        elements.append(Spacer(1, 0.3*cm))

        elements.append(Paragraph(
            'Com base nos resultados da avaliação SPM, os seguintes objetivos e estratégias '
            'são recomendados para o desenvolvimento do aluno:',
            normal_style
        ))
        elements.append(Spacer(1, 0.5*cm))

        # Agrupar itens por domínio
        itens_por_dominio = {}
        for item in itens_pei:
            dominio_nome = item.template_item.dominio_nome
            if dominio_nome not in itens_por_dominio:
                itens_por_dominio[dominio_nome] = []
            itens_por_dominio[dominio_nome].append(item)

        # Renderizar itens agrupados
        contador = 1
        for dominio_nome in sorted(itens_por_dominio.keys()):
            # Título do domínio
            elements.append(Paragraph(
                f'<b>{dominio_nome}</b>',
                ParagraphStyle('DominioTitle', parent=subtitulo_style, fontSize=11, textColor=colors.HexColor('#0d6efd'))
            ))
            elements.append(Spacer(1, 0.2*cm))

            # Itens do domínio
            for item in itens_por_dominio[dominio_nome]:
                texto_item = f'<b>{contador}.</b> {item.template_item.texto}'
                elements.append(Paragraph(texto_item, item_style))

                # Se houver observações
                if item.observacoes:
                    obs_style = ParagraphStyle(
                        'Observacoes',
                        parent=normal_style,
                        fontSize=9,
                        leftIndent=1*cm,
                        textColor=colors.HexColor('#6c757d'),
                        italic=True
                    )
                    elements.append(Paragraph(f'<i>Observações: {item.observacoes}</i>', obs_style))

                contador += 1

            elements.append(Spacer(1, 0.4*cm))

        # ===== RODAPÉ =====
        elements.append(Spacer(1, 1*cm))
        elements.append(Paragraph(
            f'<i>Relatório gerado em {datetime.now().strftime("%d/%m/%Y às %H:%M")}</i>',
            ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))

        # Construir PDF
        doc.build(elements)

        buffer.seek(0)
        return buffer

    @staticmethod
    def _formatar_classificacao(classificacao):
        """Formata texto da classificação para exibição"""
        mapa = {
            'TIPICO': 'Típico',
            'PROVAVEL_DISFUNCAO': 'Provável Disfunção',
            'DISFUNCAO_DEFINITIVA': 'Disfunção Definitiva'
        }
        return mapa.get(classificacao, classificacao)
