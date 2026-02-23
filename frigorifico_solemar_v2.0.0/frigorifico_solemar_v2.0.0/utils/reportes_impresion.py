"""
Generador de Reportes para Impresión - Frigorífico Solemar
Genera archivos PDF para impresión de tickets
"""

import os
from datetime import datetime

# Directorio para guardar los reportes
REPORTES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reportes")
if not os.path.exists(REPORTES_DIR):
    os.makedirs(REPORTES_DIR)

# Intentar importar reportlab, si no está disponible usar generación de texto
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib import colors
    REPORTLAB_DISPONIBLE = True
except ImportError:
    REPORTLAB_DISPONIBLE = False


def generar_ticket_pesaje_pdf(ticket_data, mostrar=True):
    """
    Genera un archivo con el ticket de pesaje (PDF o TXT según disponibilidad)
    
    Args:
        ticket_data: dict con los datos del ticket
        mostrar: si True, abre el archivo después de generar
    
    Returns:
        str: ruta del archivo generado
    """
    if REPORTLAB_DISPONIBLE:
        return _generar_ticket_pdf(ticket_data, mostrar)
    else:
        return _generar_ticket_txt(ticket_data, mostrar)


def _generar_ticket_txt(ticket_data, mostrar=True):
    """Genera un ticket en formato texto"""
    numero_ticket = ticket_data.get('numero_ticket', 'SIN-NUMERO')
    fecha = ticket_data.get('fecha', '')
    hora = ticket_data.get('hora', '')
    tipo = ticket_data.get('tipo_ticket', 'ingreso').upper()
    
    filename = f"ticket_{numero_ticket.replace('-', '_')}.txt"
    filepath = os.path.join(REPORTES_DIR, filename)
    
    peso_bruto = ticket_data.get('peso_bruto_kg') or ticket_data.get('peso_kg', 0)
    peso_tara = ticket_data.get('peso_tara_kg', 0)
    peso_neto = ticket_data.get('peso_neto_kg') or peso_bruto
    
    contenido = f"""
╔══════════════════════════════════════════════════════════════╗
║               FRIGORÍFICO SOLEMAR                           ║
║               TICKET DE {tipo:^20}                        ║
╠══════════════════════════════════════════════════════════════╣
║  TICKET N°: {numero_ticket:<20} FECHA: {fecha:<12}        ║
║  TIPO:      {tipo:<20} HORA:  {hora:<12}        ║
║  ESTADO:    {ticket_data.get('estado', 'abierto').upper():<20}                       ║
╠══════════════════════════════════════════════════════════════╣
║  DATOS DEL TRANSPORTE                                       ║
║  ─────────────────────────────────────────────────────────  ║
║  Patente Chasis:     {str(ticket_data.get('patente_chasis', '-') or '-'):<30}    ║
║  Patente Acoplado:   {str(ticket_data.get('patente_acoplado', '-') or '-'):<30}    ║
║  Transportista:      {str(ticket_data.get('transportista', '-') or '-')[:30]:<30}    ║
║  CUIT Transportista: {str(ticket_data.get('cuit_transportista', '-') or '-'):<30}    ║
║  Chofer:             {str(ticket_data.get('chofer', '-') or '-')[:30]:<30}    ║
║  DNI Chofer:         {str(ticket_data.get('dni_chofer', '-') or '-'):<30}    ║
╠══════════════════════════════════════════════════════════════╣
║  DATOS DE PESAJE                                            ║
║  ─────────────────────────────────────────────────────────  ║
║  Peso Bruto:     {peso_bruto:>15,.0f} kg                         ║
║  Peso Tara:      {peso_tara:>15,.0f} kg                         ║
║  ════════════════════════════════════════════════════════   ║
║  PESO NETO:      {peso_neto:>15,.0f} kg                         ║
╠══════════════════════════════════════════════════════════════╣
║  OTROS DATOS                                                ║
║  N° Habilitación: {str(ticket_data.get('num_habilitacion', '-') or '-'):<30}      ║
║  Precintos:       {str(ticket_data.get('precintos', '-') or '-'):<30}      ║
║  Observaciones:   {str(ticket_data.get('observaciones', '-') or '-')[:30]:<30}      ║
║  Operador:        {str(ticket_data.get('operador', '-') or '-'):<30}      ║
╠══════════════════════════════════════════════════════════════╣
║  Documento generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S'):<30}   ║
╠══════════════════════════════════════════════════════════════╣
║                                                             ║
║   ______________________          ______________________    ║
║        Firma Operador                 Firma Chofer          ║
╚══════════════════════════════════════════════════════════════╝
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    if mostrar:
        try:
            if os.name == 'nt':
                os.startfile(filepath)
            else:
                import subprocess
                subprocess.run(['xdg-open', filepath])
        except:
            pass
    
    return filepath


def _generar_ticket_pdf(ticket_data, mostrar=True):
    """Genera un ticket en formato PDF usando reportlab"""
    numero_ticket = ticket_data.get('numero_ticket', 'SIN-NUMERO')
    fecha = ticket_data.get('fecha', '')
    hora = ticket_data.get('hora', '')
    tipo = ticket_data.get('tipo_ticket', 'ingreso').upper()
    
    filename = f"ticket_{numero_ticket.replace('-', '_')}.pdf"
    filepath = os.path.join(REPORTES_DIR, filename)
    
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    styles = getSampleStyleSheet()
    
    elements = []
    
    # Estilos personalizados
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=10,
        textColor=colors.HexColor('#0066CC')
    )
    
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=15,
        textColor=colors.HexColor('#CC0000') if tipo == 'EGRESO' else colors.HexColor('#008800')
    )
    
    seccion_style = ParagraphStyle(
        'Seccion',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#0066CC')
    )
    
    # Encabezado
    elements.append(Paragraph("FRIGORÍFICO SOLEMAR", titulo_style))
    elements.append(Paragraph(f"TICKET DE {tipo}", subtitulo_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0066CC')))
    elements.append(Spacer(1, 15))
    
    # Datos del ticket
    info_data = [
        ['TICKET N°:', numero_ticket, 'FECHA:', fecha],
        ['TIPO:', tipo, 'HORA:', hora],
        ['ESTADO:', ticket_data.get('estado', 'abierto').upper(), 'OPERADOR:', str(ticket_data.get('operador', '-') or '-')],
    ]
    
    info_table = Table(info_data, colWidths=[2.5*cm, 5*cm, 2.5*cm, 5*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.gray),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.gray))
    elements.append(Spacer(1, 15))
    
    # Datos del transporte
    elements.append(Paragraph("DATOS DEL TRANSPORTE", seccion_style))
    elements.append(Spacer(1, 10))
    
    transporte_data = [
        ['Patente Chasis:', str(ticket_data.get('patente_chasis', '-') or '-')],
        ['Patente Acoplado:', str(ticket_data.get('patente_acoplado', '-') or '-')],
        ['Transportista:', str(ticket_data.get('transportista', '-') or '-')[:40]],
        ['CUIT Transportista:', str(ticket_data.get('cuit_transportista', '-') or '-')],
        ['Chofer:', str(ticket_data.get('chofer', '-') or '-')[:40]],
        ['DNI Chofer:', str(ticket_data.get('dni_chofer', '-') or '-')],
    ]
    
    trans_table = Table(transporte_data, colWidths=[4*cm, 11*cm])
    trans_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    elements.append(trans_table)
    elements.append(Spacer(1, 15))
    
    # Datos de pesaje
    elements.append(Paragraph("DATOS DE PESAJE", seccion_style))
    elements.append(Spacer(1, 10))
    
    peso_bruto = ticket_data.get('peso_bruto_kg') or ticket_data.get('peso_kg', 0)
    peso_tara = ticket_data.get('peso_tara_kg', 0)
    peso_neto = ticket_data.get('peso_neto_kg') or peso_bruto
    
    pesaje_data = [
        ['Peso Bruto:', f"{peso_bruto:,.0f} kg" if peso_bruto else '-'],
        ['Peso Tara:', f"{peso_tara:,.0f} kg" if peso_tara else '-'],
        ['PESO NETO:', f"{peso_neto:,.0f} kg" if peso_neto else '-'],
    ]
    
    pesaje_table = Table(pesaje_data, colWidths=[4*cm, 6*cm])
    pesaje_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, -1), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
        ('TEXTCOLOR', (1, -1), (1, -1), colors.HexColor('#008800')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F5E9')),
    ]))
    elements.append(pesaje_table)
    elements.append(Spacer(1, 15))
    
    # Otros datos
    elements.append(Paragraph("OTROS DATOS", seccion_style))
    elements.append(Spacer(1, 10))
    
    otros_data = [
        ['N° Habilitación:', str(ticket_data.get('num_habilitacion', '-') or '-')],
        ['Precintos:', str(ticket_data.get('precintos', '-') or '-')],
        ['Observaciones:', str(ticket_data.get('observaciones', '-') or '-')[:50]],
    ]
    
    otros_table = Table(otros_data, colWidths=[4*cm, 11*cm])
    otros_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    elements.append(otros_table)
    elements.append(Spacer(1, 20))
    
    # Pie
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0066CC')))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        ParagraphStyle('Pie', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.gray)
    ))
    
    # Espacio para firmas
    elements.append(Spacer(1, 30))
    firmas_data = [
        ['____________________', '', '____________________'],
        ['Firma Operador', '', 'Firma Chofer'],
    ]
    firmas_table = Table(firmas_data, colWidths=[6*cm, 3*cm, 6*cm])
    firmas_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.gray),
    ]))
    elements.append(firmas_table)
    
    doc.build(elements)
    
    if mostrar:
        try:
            if os.name == 'nt':
                os.startfile(filepath)
            else:
                import subprocess
                subprocess.run(['xdg-open', filepath])
        except:
            pass
    
    return filepath


def generar_reporte_pesajes_pdf(tickets, filtros=None):
    """
    Genera un reporte PDF con múltiples tickets de pesaje
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"reporte_pesajes_{timestamp}.txt" if not REPORTLAB_DISPONIBLE else f"reporte_pesajes_{timestamp}.pdf"
    filepath = os.path.join(REPORTES_DIR, filename)
    
    if not REPORTLAB_DISPONIBLE:
        return _generar_reporte_txt(tickets, filtros, filepath)
    
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Título
    elements.append(Paragraph("FRIGORÍFICO SOLEMAR", ParagraphStyle(
        'Titulo', parent=styles['Heading1'], fontSize=18, alignment=TA_CENTER, textColor=colors.HexColor('#0066CC')
    )))
    elements.append(Paragraph("REPORTE DE PESAJES", ParagraphStyle(
        'Subtitulo', parent=styles['Heading2'], fontSize=14, alignment=TA_CENTER, spaceAfter=15
    )))
    elements.append(Spacer(1, 10))
    
    # Filtros
    if filtros:
        filtro_text = f"Filtros: "
        if filtros.get('fecha_desde'):
            filtro_text += f"Desde {filtros['fecha_desde']} "
        if filtros.get('fecha_hasta'):
            filtro_text += f"Hasta {filtros['fecha_hasta']} "
        if filtros.get('patente'):
            filtro_text += f"Patente: {filtros['patente']} "
        elements.append(Paragraph(filtro_text, styles['Normal']))
    
    elements.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
    elements.append(Paragraph(f"Total: {len(tickets)} registros", styles['Normal']))
    elements.append(Spacer(1, 15))
    
    # Tabla
    header = ['Ticket', 'Fecha', 'Tipo', 'Patente', 'Transportista', 'Peso Neto', 'Estado']
    data = [header]
    
    for t in tickets:
        patente = f"{t.get('patente_chasis', '')} {t.get('patente_acoplado', '')}".strip()
        peso = t.get('peso_neto_kg') or t.get('peso_bruto_kg') or t.get('peso_kg', 0)
        data.append([
            t.get('numero_ticket', '-'),
            f"{t.get('fecha', '')} {t.get('hora', '')}",
            t.get('tipo_ticket', '-').upper(),
            patente[:15] if patente else '-',
            (t.get('transportista', '-') or '-')[:20],
            f"{peso:,.0f}" if peso else '-',
            t.get('estado', '-').upper()
        ])
    
    table = Table(data, colWidths=[2.5*cm, 3*cm, 1.5*cm, 2.5*cm, 4*cm, 2*cm, 1.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
    ]))
    elements.append(table)
    
    doc.build(elements)
    return filepath


def _generar_reporte_txt(tickets, filtros, filepath):
    """Genera un reporte en formato texto"""
    lineas = []
    lineas.append("=" * 80)
    lineas.append("FRIGORÍFICO SOLEMAR - REPORTE DE PESAJES")
    lineas.append("=" * 80)
    lineas.append(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    lineas.append(f"Total: {len(tickets)} registros")
    if filtros:
        lineas.append(f"Filtros: {filtros}")
    lineas.append("-" * 80)
    
    for t in tickets:
        patente = f"{t.get('patente_chasis', '')} {t.get('patente_acoplado', '')}".strip()
        peso = t.get('peso_neto_kg') or t.get('peso_bruto_kg') or t.get('peso_kg', 0)
        lineas.append(f"{t.get('numero_ticket', '-'):20} | {t.get('fecha', '')} {t.get('hora', ''):8} | "
                      f"{t.get('tipo_ticket', '-'):7} | {patente:15} | {peso:>10,.0f} kg | {t.get('estado', '-')}")
    
    lineas.append("=" * 80)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lineas))
    
    return filepath


def imprimir_archivo(filepath):
    """
    Envía un archivo a la impresora predeterminada del sistema
    """
    try:
        if os.name == 'nt':  # Windows
            os.startfile(filepath, 'print')
        elif os.name == 'posix':  # Linux/Mac
            import subprocess
            subprocess.run(['lp', filepath])
        return True
    except Exception as e:
        raise Exception(f"Error al imprimir: {e}")


def obtener_ruta_reportes():
    """Retorna la ruta del directorio de reportes"""
    return REPORTES_DIR
