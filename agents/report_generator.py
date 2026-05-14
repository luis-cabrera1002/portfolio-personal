import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable)
from config import REPORTS_DIR, TICKER_NAMES
from agents.ai_client import get_ai_response

os.makedirs(REPORTS_DIR, exist_ok=True)


def _s(val, fmt=None):
    try:
        if val is None: return "N/A"
        if fmt == "pct": return f"{float(val):.2%}"
        if fmt == "2f":  return f"{float(val):.2f}"
        return str(val)
    except Exception:
        return "N/A"


def generate_investment_memo(data):
    prompt = f"""Escribe un memo de inversión profesional de 400-500 palabras basado en estos datos de portafolio:

{str(data)[:3000]}

El memo debe incluir:
- Resumen ejecutivo
- Análisis de mercado actual
- Análisis del portafolio
- Riesgos identificados
- Recomendaciones específicas
- Conclusión

Tono profesional, en español, dirigido a un inversor sofisticado."""
    return get_ai_response(prompt, max_tokens=1200)


def generate_pdf_report(portfolio_data, filename=None):
    if filename is None:
        filename = f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = os.path.join(REPORTS_DIR, filename)
    doc = SimpleDocTemplate(path, pagesize=letter,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    title_s = ParagraphStyle("T", parent=styles["Title"], fontSize=22,
                              textColor=colors.HexColor("#1a3a5c"), spaceAfter=6)
    h2_s    = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14,
                              textColor=colors.HexColor("#1a3a5c"), spaceBefore=14, spaceAfter=4)
    body_s  = ParagraphStyle("B", parent=styles["Normal"], fontSize=9, leading=13, spaceAfter=4)
    disc_s  = ParagraphStyle("D", parent=styles["Normal"], fontSize=7,
                              textColor=colors.gray, leading=10)

    story = []
    now = datetime.now().strftime("%d %b %Y  %H:%M")

    story += [Spacer(1, 0.4*inch),
              Paragraph("Portfolio Intelligence Suite", title_s),
              Paragraph("Reporte Ejecutivo de Inversiones", styles["Heading3"]),
              Paragraph(f"Generado: {now}", styles["Normal"]),
              HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a3a5c")),
              Spacer(1, 0.2*inch)]

    # Holdings
    story.append(Paragraph("1. Asignación del Portfolio", h2_s))
    alloc   = portfolio_data.get("strategy", {}).get("allocation", {}) or {}
    weights = alloc.get("weights", {})
    if weights:
        tbl_data = [["Ticker", "Nombre", "Peso (%)"]]
        for t, w in sorted(weights.items(), key=lambda x: -x[1]):
            if w > 0.0005:
                tbl_data.append([t, TICKER_NAMES.get(t, t), f"{w*100:.1f}%"])
        tbl = Table(tbl_data, colWidths=[1.2*inch, 2.5*inch, 1.2*inch])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,0), colors.HexColor("#1a3a5c")),
            ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
            ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0),(-1,-1), 9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, colors.HexColor("#eef2f7")]),
            ("GRID",       (0,0),(-1,-1), 0.3, colors.lightgrey),
            ("ALIGN",      (2,0),(2,-1),  "CENTER"),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(
            f"Retorno esperado: {_s(alloc.get('expected_return'),'pct')} | "
            f"Volatilidad: {_s(alloc.get('volatility'),'pct')} | "
            f"Sharpe: {_s(alloc.get('sharpe_ratio'),'2f')}", body_s))

    # Risk
    story.append(Paragraph("2. Métricas de Riesgo", h2_s))
    pm = portfolio_data.get("risk", {}).get("portfolio_metrics", {})
    if pm:
        rd = [["Métrica", "Valor"],
              ["VaR 95% (1d)", _s(pm.get("var_95"), "pct")],
              ["VaR 99% (1d)", _s(pm.get("var_99"), "pct")],
              ["CVaR 95%",     _s(pm.get("cvar_95"), "pct")],
              ["Volatilidad Anual", _s(pm.get("annual_volatility"), "pct")],
              ["Concentración HHI", _s(pm.get("hhi_concentration"), "2f")]]
        rt = Table(rd, colWidths=[2.5*inch, 2*inch])
        rt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#c0392b")),
            ("TEXTCOLOR", (0,0),(-1,0), colors.white),
            ("FONTNAME",  (0,0),(-1,0), "Helvetica-Bold"),
            ("FONTSIZE",  (0,0),(-1,-1), 9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, colors.HexColor("#fdecea")]),
            ("GRID",(0,0),(-1,-1), 0.3, colors.lightgrey),
        ]))
        story.append(rt)

    # ESG
    story.append(Paragraph("3. Resumen ESG", h2_s))
    esg = portfolio_data.get("esg", {})
    if esg:
        ed = [["Ticker","E","S","G","Total","Semáforo"]]
        for t, info in list(esg.items())[:10]:
            lm = {"verde":"✓ Verde","amarillo":"~ Amarillo","rojo":"✗ Rojo"}
            ed.append([t, _s(info.get("environmental_score")), _s(info.get("social_score")),
                       _s(info.get("governance_score")), _s(info.get("total_score")),
                       lm.get(info.get("traffic_light",""), "N/A")])
        et = Table(ed, colWidths=[0.9*inch]*5+[1.1*inch])
        et.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#27ae60")),
            ("TEXTCOLOR", (0,0),(-1,0), colors.white),
            ("FONTNAME",  (0,0),(-1,0), "Helvetica-Bold"),
            ("FONTSIZE",  (0,0),(-1,-1), 8),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#eafaf1")]),
            ("GRID",(0,0),(-1,-1), 0.3, colors.lightgrey),
            ("ALIGN",(1,0),(-1,-1),"CENTER"),
        ]))
        story.append(et)

    # AI Memo
    story.append(Paragraph("4. Análisis del Analista IA", h2_s))
    memo = generate_investment_memo(portfolio_data)
    for para in memo.split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip(), body_s))
            story.append(Spacer(1, 0.05*inch))

    # Disclaimer
    story += [Spacer(1, 0.3*inch),
              HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey),
              Spacer(1, 0.05*inch),
              Paragraph(
                  "DISCLAIMER: Reporte generado automáticamente. No constituye asesoramiento de inversión. "
                  "Consulte con un asesor financiero certificado antes de tomar decisiones.", disc_s)]

    doc.build(story)
    return path
