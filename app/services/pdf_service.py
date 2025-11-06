"""
Serviço de Geração de PDFs
Cria relatórios em PDF usando ReportLab
"""
from io import BytesIO
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime


class PDFService:
    """Serviço para geração de relatórios PDF"""

    @staticmethod
    def gerar_relatorio_avaliacao(avaliacao):
        """
        Gera relatório completo de avaliação em PDF

        Args:
            avaliacao: Instância de Avaliacao

        Returns:
            BytesIO: Buffer com o PDF gerado
        """
        buffer = BytesIO()

        # Criar documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # Container para elementos
        story = []

        # Estilos
        styles = getSampleStyleSheet()

        # Estilo customizado para título
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        subtitulo_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=20
        )

        # Cabeçalho
        story.append(Paragraph("RELATÓRIO DE AVALIAÇÃO SPM", titulo_style))
        story.append(Paragraph("Sensory Processing Measure", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))

        # Informações do Paciente
        story.append(Paragraph("DADOS DO PACIENTE", subtitulo_style))

        anos, meses = avaliacao.paciente.calcular_idade(avaliacao.data_avaliacao)

        dados_paciente = [
            ['Nome:', avaliacao.paciente.nome],
            ['Data de Nascimento:', avaliacao.paciente.data_nascimento.strftime('%d/%m/%Y')],
            ['Idade:', f'{anos} anos, {meses} meses'],
            ['Sexo:', 'Masculino' if avaliacao.paciente.sexo == 'M' else 'Feminino'],
        ]

        if avaliacao.paciente.identificacao:
            dados_paciente.insert(1, ['Identificação:', avaliacao.paciente.identificacao])

        tabela_paciente = Table(dados_paciente, colWidths=[4*cm, 12*cm])
        tabela_paciente.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        story.append(tabela_paciente)
        story.append(Spacer(1, 0.5*cm))

        # Informações da Avaliação
        story.append(Paragraph("DADOS DA AVALIAÇÃO", subtitulo_style))

        dados_avaliacao = [
            ['Data da Avaliação:', avaliacao.data_avaliacao.strftime('%d/%m/%Y')],
            ['Instrumento:', avaliacao.instrumento.nome],
            ['Respondente:', avaliacao.relacionamento_respondente.capitalize()],
            ['Avaliador:', avaliacao.avaliador.nome_completo],
            ['Status:', 'Concluída' if avaliacao.status == 'concluida' else 'Em Andamento']
        ]

        tabela_avaliacao = Table(dados_avaliacao, colWidths=[4*cm, 12*cm])
        tabela_avaliacao.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        story.append(tabela_avaliacao)
        story.append(Spacer(1, 0.5*cm))

        if avaliacao.comentarios:
            story.append(Paragraph("<b>Comentários:</b>", styles['Normal']))
            story.append(Paragraph(avaliacao.comentarios, styles['Normal']))
            story.append(Spacer(1, 0.5*cm))

        # Resultados (se concluída)
        if avaliacao.status == 'concluida':
            story.append(PageBreak())
            story.append(Paragraph("RESULTADOS", subtitulo_style))

            # Tabela de escores
            dados_escores = [
                ['Domínio', 'Escore Bruto', 'T-Score', 'Classificação']
            ]

            dominios_info = [
                ('Participação Social', avaliacao.escore_soc, avaliacao.t_score_soc, avaliacao.classificacao_soc),
                ('Visão', avaliacao.escore_vis, avaliacao.t_score_vis, avaliacao.classificacao_vis),
                ('Audição', avaliacao.escore_hea, avaliacao.t_score_hea, avaliacao.classificacao_hea),
                ('Tato', avaliacao.escore_tou, avaliacao.t_score_tou, avaliacao.classificacao_tou),
                ('Consciência Corporal', avaliacao.escore_bod, avaliacao.t_score_bod, avaliacao.classificacao_bod),
                ('Equilíbrio e Movimento', avaliacao.escore_bal, avaliacao.t_score_bal, avaliacao.classificacao_bal),
                ('Planejamento e Ideação', avaliacao.escore_pla, avaliacao.t_score_pla, avaliacao.classificacao_pla),
            ]

            if avaliacao.escore_olf:
                dominios_info.insert(3, ('Olfato e Paladar', avaliacao.escore_olf,
                                        avaliacao.t_score_olf, avaliacao.classificacao_olf))

            for nome, escore, t_score, classificacao in dominios_info:
                if escore is not None:
                    class_texto = PDFService._classificacao_texto(classificacao)
                    dados_escores.append([
                        nome,
                        str(escore),
                        str(t_score) if t_score else 'N/A',
                        class_texto
                    ])

            # Linha total
            dados_escores.append(['TOTAL', str(avaliacao.escore_total), '', ''])

            tabela_escores = Table(dados_escores, colWidths=[6*cm, 3*cm, 3*cm, 4*cm])
            tabela_escores.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
            ]))

            story.append(tabela_escores)
            story.append(Spacer(1, 1*cm))

            # Interpretação
            story.append(Paragraph("INTERPRETAÇÃO DOS RESULTADOS", subtitulo_style))

            interpretacao = """
            Os escores obtidos na avaliação SPM refletem o padrão de processamento sensorial
            da criança em diferentes domínios. Escores mais altos indicam maior presença de
            dificuldades de processamento sensorial.
            """

            story.append(Paragraph(interpretacao, styles['Normal']))
            story.append(Spacer(1, 0.3*cm))

            # Legenda das classificações
            story.append(Paragraph("<b>Classificações:</b>", styles['Normal']))
            story.append(Spacer(1, 0.2*cm))

            legenda = [
                ['Típico', 'Processamento sensorial dentro da normalidade'],
                ['Provável Disfunção', 'Sugere possível disfunção, requer monitoramento'],
                ['Disfunção Definitiva', 'Indica disfunção clara, requer intervenção']
            ]

            tabela_legenda = Table(legenda, colWidths=[4*cm, 12*cm])
            tabela_legenda.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))

            story.append(tabela_legenda)

        # Rodapé
        story.append(Spacer(1, 1*cm))
        rodape = f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
        story.append(Paragraph(rodape, ParagraphStyle('Footer', parent=styles['Normal'],
                                                       fontSize=8, textColor=colors.grey,
                                                       alignment=TA_CENTER)))

        # Build PDF
        doc.build(story)

        buffer.seek(0)
        return buffer

    @staticmethod
    def _classificacao_texto(classificacao):
        """Retorna texto da classificação"""
        if classificacao == 'DISFUNCAO_DEFINITIVA':
            return 'Disfunção Definitiva'
        elif classificacao == 'PROVAVEL_DISFUNCAO':
            return 'Provável Disfunção'
        elif classificacao == 'TIPICO':
            return 'Típico'
        return 'N/A'
