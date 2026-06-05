"""
Planilha de Controle de Execução — Renovação Telemetria 4.0
Dados reais das estações ERP/ERD/SDV
"""
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from datetime import date

# ─── Paleta ─────────────────────────────────────────────────────────────────
C_AZUL_ESC   = "1F3864"; C_AZUL_MED  = "2E75B6"; C_AZUL_CL   = "BDD7EE"
C_CINZA_H    = "D6DCE4"; C_CINZA_L   = "F2F2F2"; C_BRANCO    = "FFFFFF"
C_VERDE      = "375623"; C_VERDE_CL  = "E2EFDA"; C_VERDE_MED = "70AD47"
C_AMAR       = "BF8F00"; C_AMAR_CL   = "FFF2CC"; C_AMAR_MED  = "FFD966"
C_VERM       = "C00000"; C_VERM_CL   = "FCE4D6"
C_LAR        = "C55A11"; C_LAR_CL    = "FCE4D6"
C_ROXO_CL    = "EAE3F5"; C_ROXO      = "7030A0"

def F(c):  return PatternFill("solid", fgColor=c)
def Fb(s=11, c=C_BRANCO): return Font(bold=True, size=s, color=c, name="Calibri")
def Fn(s=9,  c="000000"): return Font(size=s, color=c, name="Calibri")
def Ac(): return Alignment(horizontal="center", vertical="center", wrap_text=True)
def Al(): return Alignment(horizontal="left",   vertical="center", wrap_text=True)
def borda():
    t = Side(style="thin", color="BFBFBF")
    return Border(left=t, right=t, top=t, bottom=t)
def borda_m():
    m = Side(style="medium", color=C_AZUL_MED)
    return Border(left=m, right=m, top=m, bottom=m)

STATUS_COR = {
    "Concluído":     (C_VERDE,    C_VERDE_CL),
    "Em andamento":  (C_AZUL_MED, C_AZUL_CL),
    "Não iniciado":  (C_CINZA_H,  C_CINZA_L),
    "Atrasado":      (C_LAR,      C_LAR_CL),
    "Pendente":      (C_AMAR,     C_AMAR_CL),
}

# ─── DADOS REAIS ─────────────────────────────────────────────────────────────
#  Campos: id | programa | ordem | li_mec | li_tel | lat | lon
#          | pin | psai | pe1 | ps1 | pdt | shutoff | endereco | bairro
ESTACOES = [
  # ── CG_07  (Pin 17 bar) ───────────────────────────────────────────────────
  ("ERP070",       "renovação 4.0","52698733","CG_07_EST_ECP_ECP00273","CG_07_TEL_ERP070",      -23.54613713,-46.52902165, 17,  4,   25,10, 2,1,"",""),
  ("ERPCR2101",    "renovação 4.0","52698789","CG_07_EST_ECP_ECP00248","CG_07_TEL_ERPCR2101",    -22.60147974,-44.97030172, 17,  7,   25,10, 2,1,"",""),
  ("ERPLO2101",    "renovação 4.0","52698812","CG_07_EST_ECP_ECP00096","CG_07_TEL_ERPLO2101",    -22.75168006,-45.10520185, 17,  7,   25,10, 2,1,"",""),
  ("ERP303",       "renovação 4.0","52704379","CG_07_EST_ECP_ECP00320","CG_07_TEL_ECP00320",     -23.63252256, None,         17,  4,   25,10, None,1,"",""),
  # ── CG_07 SDV ─────────────────────────────────────────────────────────────
  ("SDV000002",    "renovação 4.0","52710348", None,                   "CG_07_TEL_VBSDV-002",    None,        None,         18, 18,   25,25, None,1,"",""),
  ("SDV000003",    "renovação 4.0","52710374", None,                   "CG_07_TEL_VBSDV-003",    None,        None,         18, 18,   25,25, None,1,"",""),
  # ── CG_08  (Pin 35 bar) ───────────────────────────────────────────────────
  ("ERPPR5101",    "renovação 4.0","52698802","CG_08_EST_ECP_ECP00029","CG_08_TEL_ERPPR5101",    -22.71263837,-47.63288796, 35,  7,   50,10, 2,1,"",""),
  ("ERPMM5101",    "renovação 4.0","52698839","CG_08_EST_ECP_ECP00079","CG_08_TEL_ERPMM5101",    -22.48323693,-46.97969425, 35,  7,   50,10, 2,1,"",""),
  ("ERPRC55501",   "renovação 4.0","52698842","CG_08_EST_ECP_ECP00043","CG_08_TEL_ERPRC55501",   -22.43588917,-47.57001734, 35,  4,   50,10, 2,1,"",""),
  ("ERPSG5102",    "renovação 4.0","52698847","CG_08_EST_ECP_ECP00023","CG_08_TEL_ERPSG5102",    -22.46786995,-47.51231674, 35,  7,   50,10, 2,1,"",""),
  ("ERPITN5101",   "renovação 4.0","52704425","CG_08_EST_ECP_ECP00108","CG_08_TEL_ERPITN55501",  -22.21957086,-47.77069950, 35,  7,   50,10, 2,1,"",""),
  # ── CG_06  (Pin 7 bar) ────────────────────────────────────────────────────
  ("ERPAM15501",   "renovação 4.0","52698818","CG_06_EST_ECP_ECP00022","CG_06_TEL_ERPAM15501",   -22.74309209,-47.32637041,  7,  4,   10,10, 2,1,"",""),
  ("ERPAM15502",   "renovação 4.0","52698826","CG_06_EST_ECP_ECP00023","CG_06_TEL_ERPAM15502",   -22.73759659,-47.32001076,  7,  4,   10,10, 2,1,"",""),
  ("ERPLM10502",   "renovação 4.0","52698833","CG_06_EST_ECP_ECP00027", None,                     0.0,          0.0,          7,0.35,  10, 0.6,2,1,"",""),
  # ── CG_05  ERD (Pin 4 bar) — com coordenadas ─────────────────────────────
  ("ERD181",       "renovação 4.0","52698862","CG_05_EST_ECD_ECD00283","CG_05_TEL_ECD_ECD00283", -23.55609706,-46.64952663,  4,0.35,  10,0.6, None,1,"","Bela Vista"),
  ("ERD184",       "renovação 4.0","52698865","CG_05_EST_ECD_ECD00287","CG_05_TEL_ECD_ECD00287", -23.57836671,-46.65096982,  4,0.35,  10,0.6, None,1,"R SIQUEIRA BUENO S/N",""),
  ("ERD028",       "renovação 4.0","52698869","CG_05_EST_ECD_ECD00185","CG_05_TEL_ERD028",        -23.54515810,-46.65747982,  4,0.35,  10,0.6, None,1,"AV ANGELICA S/N",""),
  ("ERD054",       "renovação 4.0","52698873","CG_05_EST_ECD_ECD00218","CG_05_TEL_ERD054",        -23.58629157,-46.64789650,  4,0.35,  10,0.6, None,1,"AV CONS RODRIGUES ALVES S/N","VILA MARIANA"),
  ("ERD110",       "renovação 4.0","52698883","CG_05_EST_ECD_ECD00238","CG_05_TEL_ECD00238",      -23.58209008,-46.58345346,  4,0.35,  10,0.6, None,1,"",""),
  ("ERD112",       "renovação 4.0","52698886","CG_05_EST_ECD_ECD00272","CG_05_TEL_ECD_ECD00272",  -23.55951437,-46.63115241,  4,0.35,  10,0.6, None,1,"",""),
  ("ERD168",       "renovação 4.0","52701400","CG_05_EST_ECD_ECD00253","CG_05_TEL_ECD_ECD00253",  -23.56758187,-46.63206222,  4,0.35,  10,0.6, None,1,"",""),
  ("ERD169",       "renovação 4.0","52702396","CG_05_EST_ECD_ECD00254","CG_05_TEL_ECD_ECD00254",  -23.57208939,-46.61074902,  4,0.35,  10,0.6, None,1,"",""),
  ("ERD177",       "renovação 4.0","52704294","CG_05_EST_ECD_ECD00264","CG_05_TEL_ECD_ECD00264",  -23.53408444,-46.67843151,  4,0.35,  10,0.6, None,1,"",""),
  ("ERD006",       "renovação 4.0","52704312","CG_05_EST_ECD_ECD00228","CG_05_TEL_ECD_ECD00241",  -23.54628320,-46.59185262,  4,0.35,  10,0.6, None,1,"RUA SIQUEIRA BUENO",""),
  ("ERD014",       "renovação 4.0","52704333","CG_05_EST_ECD_ECD00266","CG_05_TEL_ECD_ECD00266",  -23.53944089,-46.62927539,  4,0.35,  10,0.6, None,1,"",""),
  ("ERDITV550501", "renovação 4.0","52704346","CG_05_EST_ECD_ECD00261","CG_05_TEL_ECD_ECD00261",  -23.05820535,-47.06306169,  4,0.35,  10,0.6, None,1,"",""),
  ("ERDITV550502", "renovação 4.0","52704356","CG_05_EST_ECD_ECD00263","CG_05_TEL_ECD_ECD00263",  -23.05302448,-47.06814986,  4,0.35,  10,0.6, None,1,"",""),
  ("ERD179",       "renovação 4.0","52704369","CG_05_EST_ECD_ECD00267","CG_05_TEL_ECD_ECD00267",  -23.54079764,-46.64848926,  4,0.35,  10,0.6, None,1,"",""),
  ("ERD095",       "renovação 4.0","52704401","CG_05_EST_ECD_ECD00262","CG_05_TEL_ECD_ECD00262",  -23.55541983,-46.64068095,  4,0.35,  10,0.6, None,1,"R JACEGUAI S/N","BELA VISTA"),
  ("ERD114",       "renovação 4.0","52704416","CG_05_EST_ECD_ECD00274","CG_05_TEL_ECD_ECD00274",  -23.56977384,-46.63374193,  4,0.35,  10,0.6, None,1,"",""),
  ("ERD037",       "renovação 4.0","52704442","CG_05_EST_ECD_ECD00220","CG_05_TEL_ERD037",        -23.55536020,-46.64302773,  4,0.35,  10,0.6, None,1,"","Bela Vista"),
  # ── CG_05  ERDSJ (Pin 4 bar, Psai 1 bar) ────────────────────────────────
  ("ERDSJ551502",  "renovação 4.0","52704429","CG_05_EST_ECD_ECD00275","CG_05_TEL_ECD_ECD00275",  -23.19548479,-45.88893565,  4,  1,   10, 4, None,1,"",""),
  ("ERDSJ551503",  "renovação 4.0","52704436","CG_05_EST_ECD_ECD00276","CG_05_TEL_ECD_ECD00276",  -23.21350405,-45.90994678,  4,  1,   10, 4, None,1,"",""),
  # ── CG_05  ERD — sem dados de campo ──────────────────────────────────────
  ("ERD013",       "renovação 4.0", None,      None,                    None,                      None,        None,          4,0.35,  10,0.6, None,1,"",""),
  ("ERD020",       "renovação 4.0", None,      None,                    None,                      None,        None,          4,0.35,  10,0.6, None,1,"",""),
  ("ERD021",       "renovação 4.0", None,      None,                    None,                      None,        None,          4,0.35,  10,0.6, None,1,"",""),
  ("ERD040",       "renovação 4.0", None,      None,                    None,                      None,        None,          4,0.35,  10,0.6, None,1,"",""),
  ("ERD042",       "renovação 4.0", None,      None,                    None,                      None,        None,          4,0.35,  10,0.6, None,1,"",""),
  ("ERD061",       "renovação 4.0", None,      None,                    None,                      None,        None,          4,0.35,  10,0.6, None,1,"",""),
  ("ERD091",       "renovação 4.0", None,      None,                    None,                      None,        None,          4,0.35,  10,0.6, None,1,"",""),
  ("ERD092",       "renovação 4.0", None,      None,                    None,                      None,        None,          4,0.35,  10,0.6, None,1,"",""),
  ("ERD093",       "renovação 4.0", None,      None,                    None,                      None,        None,          4,0.35,  10,0.6, None,1,"",""),
  ("ERD099",       "renovação 4.0", None,      None,                    None,                      None,        None,          4,0.35,  10,0.6, None,1,"",""),
  ("ERD111",       "renovação 4.0", None,      None,                    None,                      None,        None,          4,0.35,  10,0.6, None,1,"",""),
  ("ERD125",       "renovação 4.0", None,      None,                    None,                      None,        None,          4,0.35,  10,0.6, None,1,"",""),
  ("ERD185",       "renovação 4.0", None,      None,                    None,                      None,        None,          4,0.35,  10,0.6, None,1,"",""),
  ("ERD186",       "renovação 4.0", None,      None,                    None,                      None,        None,          4,0.35,  10,0.6, None,1,"",""),
]

# ─── Funções auxiliares ──────────────────────────────────────────────────────
def tipo(eid):
    if eid.startswith("ERD"): return "ERD"
    if eid.startswith("ERP"): return "ERP"
    if eid.startswith("SDV"): return "SDV"
    return "—"

def grupo(li_mec):
    if not li_mec: return "—"
    for g in ["CG_05","CG_06","CG_07","CG_08"]:
        if g in li_mec: return g
    return "—"

def classe_pressao(pin):
    if pin is None: return "—"
    if pin <= 4:  return "4 bar"
    if pin <= 7:  return "7 bar"
    if pin <= 18: return "17/18 bar"
    return "35 bar"

def coord_ok(lat, lon):
    if lat is None or lon is None: return False
    if lat == 0.0 and lon == 0.0: return False
    return True

def lm_ok(v):  return bool(v)
def lt_ok(v):  return bool(v)

def pendencias_str(e):
    p = []
    if not lm_ok(e[3]):    p.append("LM")
    if not lt_ok(e[4]):    p.append("LT")
    if not coord_ok(e[5],e[6]): p.append("COORD")
    return " | ".join(p) if p else "OK"

# ─── Cabeçalhos e larguras ───────────────────────────────────────────────────
COLS_CTRL = [
    ("#",          4),  ("Estação",     14),  ("Tipo",     6),  ("CG",       8),
    ("Programa",  14),  ("Ordem OS",   12),  ("LI Mecânica",24),("LI Telemetria",24),
    ("Latitude",  13),  ("Longitude",  13),  ("Pin (bar)", 10), ("Psai (bar)",10),
    ("PE1 (bar)", 9),   ("PS1 (bar)",   9),  ("PDT (un)",  8),  ("Shutoff",   8),
    ("Caixa",     10),  ("Suporte",    10),  ("P.Solar (W)",11),("CDC",       9),
    ("Bat1 (Ah)", 9),   ("Bat2 (Ah)",   9),  ("Modem",    10),  ("Gateway",  10),
    ("Endereço",  28),  ("Bairro",     16),
    # Colunas de controle
    ("Pendências",14),  ("Status",     14),  ("Etapa Atual",18),
    ("Resp.",     18),  ("Dt. Prevista",13), ("Dt. Realizada",13),
    ("Observações",32),
]

COLS_PAINEL = [
    ("Indicador", 26), ("Valor", 12), ("Detalhes", 40),
]

# ════════════════════════════════════════════════════════════════════════════
# WORKBOOK
# ════════════════════════════════════════════════════════════════════════════
wb = openpyxl.Workbook()
wb.remove(wb.active)

# ════════════════════════════════════════════════════════════════════════════
# ABA 1: CONTROLE DE EXECUÇÃO (principal)
# ════════════════════════════════════════════════════════════════════════════
ws = wb.create_sheet("📋 Controle de Execução")
ws.sheet_view.showGridLines = False
ws.sheet_view.zoomScale = 85

# ── Cabeçalho ──
ncols = len(COLS_CTRL)
ws.merge_cells(f"A1:{get_column_letter(ncols)}1")
c = ws["A1"]
c.value = "CONTROLE DE EXECUÇÃO — RENOVAÇÃO TELEMETRIA 4.0 | ERP / ERD / SDV"
c.fill = F(C_AZUL_ESC); c.font = Fb(14); c.alignment = Ac()
ws.row_dimensions[1].height = 38

ws.merge_cells(f"A2:{get_column_letter(ncols)}2")
c = ws["A2"]
c.value = f"Atualizado em: {date.today().strftime('%d/%m/%Y')}   |   Total de estações: {len(ESTACOES)}"
c.fill = F(C_AZUL_MED); c.font = Fb(10); c.alignment = Ac()
ws.row_dimensions[2].height = 20

# ── Grupos de colunas (linha 3) ──
grupos = [
    (1,  4,  "IDENTIFICAÇÃO",       C_AZUL_ESC),
    (5,  8,  "DADOS DO SISTEMA",    C_AZUL_MED),
    (9,  12, "LOCALIZAÇÃO",         "2F5496"),
    (13, 16, "INSTRUMENTAÇÃO",      "375623"),
    (17, 24, "EQUIPAMENTOS FÍSICOS","BF8F00"),
    (25, 26, "ENDEREÇO",            "4472C4"),
    (27, 27, "PENDÊNCIAS",          C_VERM),
    (28, 33, "CONTROLE / STATUS",   C_ROXO),
]
for ci, cf, label, cor in grupos:
    ws.merge_cells(start_row=3, start_column=ci, end_row=3, end_column=cf)
    c = ws.cell(3, ci, label)
    c.fill = F(cor); c.font = Fb(8); c.alignment = Ac()
ws.row_dimensions[3].height = 22

# ── Sub-cabeçalho (linha 4) ──
for col_idx, (nome, larg) in enumerate(COLS_CTRL, 1):
    c = ws.cell(4, col_idx, nome)
    c.fill = F(C_CINZA_H); c.font = Fb(9, C_AZUL_ESC); c.alignment = Ac(); c.border = borda()
    ws.column_dimensions[get_column_letter(col_idx)].width = larg
ws.row_dimensions[4].height = 38

# ── Validações ──
dv_status = DataValidation(type="list",
    formula1='"Não iniciado,Em andamento,Concluído,Atrasado,Cancelado"')
dv_etapa = DataValidation(type="list",
    formula1='"Levantamento de campo,Elaboração de projeto,Aprovação,Aquisição,Recebimento,Configuração,Instalação,Comissionamento,Integração SCADA,Calibração,Entrega"')
ws.add_data_validation(dv_status)
ws.add_data_validation(dv_etapa)

# ── Dados ──
for row_i, e in enumerate(ESTACOES, start=5):
    eid,prog,ordem,li_mec,li_tel,lat,lon,pin,psai,pe1,ps1,pdt,shutoff,end,bairro = e

    par = row_i % 2 == 0
    bg = C_CINZA_L if par else C_BRANCO

    # Pendências automáticas
    pend = pendencias_str(e)
    pend_cor = C_VERM_CL if pend != "OK" else C_VERDE_CL
    pend_font_cor = C_VERM if pend != "OK" else C_VERDE

    # Valores das colunas
    valores = [
        row_i - 4,                          # #
        eid,                                 # Estação
        tipo(eid),                           # Tipo
        grupo(li_mec),                       # CG
        prog,                                # Programa
        ordem or "—",                        # Ordem
        li_mec or "⚠ Sem LI Mec.",           # LI Mec
        li_tel or "⚠ Sem LI Tel.",           # LI Tel
        lat if coord_ok(lat,lon) else "⚠ N/D", # Lat
        lon if coord_ok(lat,lon) else "⚠ N/D", # Lon
        pin,                                 # Pin
        psai,                                # Psai
        pe1,                                 # PE1
        ps1,                                 # PS1
        pdt or "—",                          # PDT
        shutoff,                             # Shutoff
        "","","","","","","","",              # físicos (em branco p/ preenchimento)
        end or "",                           # Endereço
        bairro or "",                        # Bairro
        pend,                                # Pendências
        "Não iniciado",                      # Status
        "Levantamento de campo",             # Etapa
        "",                                  # Resp
        "",                                  # Dt Prevista
        "",                                  # Dt Realizada
        "",                                  # Obs
    ]

    for col_i, val in enumerate(valores, 1):
        c = ws.cell(row_i, col_i, val)
        c.border = borda()
        c.font = Fn(9)
        c.alignment = Al() if col_i in (2,7,8,25,26,33) else Ac()

        # Cores especiais
        if col_i == 2:   # Estação
            c.font = Fb(9, C_AZUL_ESC); c.fill = F(C_AZUL_CL if par else C_BRANCO)
        elif col_i == 27:  # Pendências
            c.fill = F(pend_cor); c.font = Fb(9, pend_font_cor)
        elif col_i == 28:  # Status
            ct, cb = STATUS_COR.get(val, (C_CINZA_H, C_CINZA_L))
            c.fill = F(cb); c.font = Fb(9, ct)
        elif col_i in (7,8) and (not li_mec or not li_tel):
            c.fill = F(C_AMAR_CL); c.font = Fn(9, C_AMAR)
        elif col_i in (9,10) and not coord_ok(lat,lon):
            c.fill = F(C_AMAR_CL); c.font = Fn(9, C_AMAR)
        else:
            c.fill = F(bg)

        # Validações
        if col_i == 28: dv_status.add(c)
        if col_i == 29: dv_etapa.add(c)

    ws.row_dimensions[row_i].height = 20

ws.freeze_panes = "B5"
ws.auto_filter.ref = f"A4:{get_column_letter(ncols)}{4 + len(ESTACOES)}"

# ════════════════════════════════════════════════════════════════════════════
# ABA 2: PAINEL GERAL
# ════════════════════════════════════════════════════════════════════════════
wp = wb.create_sheet("📊 Painel Geral")
wp.sheet_view.showGridLines = False
wp.sheet_view.zoomScale = 90

wp.merge_cells("A1:I1")
c = wp["A1"]
c.value = "PAINEL GERAL — RENOVAÇÃO TELEMETRIA 4.0"
c.fill = F(C_AZUL_ESC); c.font = Fb(15); c.alignment = Ac()
wp.row_dimensions[1].height = 42

wp.merge_cells("A2:I2")
c = wp["A2"]
c.value = f"Gerado em {date.today().strftime('%d/%m/%Y')}  |  Responsável: Francisco Silva"
c.fill = F(C_AZUL_MED); c.font = Fb(10); c.alignment = Ac()
wp.row_dimensions[2].height = 22

# ── Contadores ──
total     = len(ESTACOES)
n_erp     = sum(1 for e in ESTACOES if tipo(e[0]) == "ERP")
n_erd     = sum(1 for e in ESTACOES if tipo(e[0]) == "ERD")
n_sdv     = sum(1 for e in ESTACOES if tipo(e[0]) == "SDV")
n_sem_lm  = sum(1 for e in ESTACOES if not e[3])
n_sem_lt  = sum(1 for e in ESTACOES if not e[4])
n_sem_coo = sum(1 for e in ESTACOES if not coord_ok(e[5],e[6]))
n_pend    = sum(1 for e in ESTACOES if pendencias_str(e) != "OK")

# ── KPI cards (linha 4 e 5) ──
wp.row_dimensions[3].height = 14
kpis = [
    ("TOTAL ERPs", total,   C_AZUL_ESC),
    ("ERP",        n_erp,   C_AZUL_MED),
    ("ERD",        n_erd,   "375623"),
    ("SDV",        n_sdv,   "4472C4"),
    ("⚠ Sem LM",  n_sem_lm, C_AMAR),
    ("⚠ Sem LT",  n_sem_lt, C_AMAR),
    ("⚠ Sem Coord",n_sem_coo,C_LAR),
    ("Com Pendência",n_pend, C_VERM),
]
col_kpi = [1,2,3,4,5,6,7,8]
for i, (lbl, val, cor) in enumerate(kpis):
    col = i + 1
    wp.column_dimensions[get_column_letter(col)].width = 16
    c_lbl = wp.cell(4, col, lbl)
    c_lbl.fill = F(cor); c_lbl.font = Fb(9); c_lbl.alignment = Ac()
    c_val = wp.cell(5, col, val)
    c_val.fill = F(cor); c_val.font = Fb(22); c_val.alignment = Ac()
    wp.row_dimensions[4].height = 26
    wp.row_dimensions[5].height = 44

wp.row_dimensions[6].height = 14

# ── Bloco: por classe de pressão ──
wp.merge_cells("A7:D7")
c = wp["A7"]
c.value = "POR CLASSE DE PRESSÃO (Pin)"
c.fill = F(C_AZUL_MED); c.font = Fb(10); c.alignment = Ac()
wp.row_dimensions[7].height = 22

classes_h = ["Classe", "Qtd. Estações", "Tipo"]
for col, h in enumerate(classes_h, 1):
    c = wp.cell(8, col, h)
    c.fill = F(C_CINZA_H); c.font = Fb(9, C_AZUL_ESC); c.alignment = Ac(); c.border = borda()

classes = [
    ("4 bar",     [e for e in ESTACOES if e[7] == 4],  "ERD"),
    ("7 bar",     [e for e in ESTACOES if e[7] == 7],  "ERP CG_06"),
    ("17/18 bar", [e for e in ESTACOES if e[7] in (17,18)], "ERP/SDV CG_07"),
    ("35 bar",    [e for e in ESTACOES if e[7] == 35], "ERP CG_08"),
]
for ri, (cls, lst, tp) in enumerate(classes, 9):
    bg = C_CINZA_L if ri % 2 == 0 else C_BRANCO
    for ci, val in enumerate([cls, len(lst), tp], 1):
        c = wp.cell(ri, ci, val)
        c.fill = F(bg); c.font = Fn(10); c.alignment = Ac(); c.border = borda()
    wp.row_dimensions[ri].height = 20

# ── Bloco: inventário de transmissores ──
wp.row_dimensions[13].height = 14
wp.merge_cells("A14:D14")
c = wp["A14"]
c.value = "INVENTÁRIO DE TRANSMISSORES"
c.fill = F("375623"); c.font = Fb(10); c.alignment = Ac()
wp.row_dimensions[14].height = 22

h_trans = ["Tipo / Faixa", "PE1 (entradas)", "PS1 (saídas)", "Total"]
for col, h in enumerate(h_trans, 1):
    c = wp.cell(15, col, h)
    c.fill = F(C_CINZA_H); c.font = Fb(9, C_AZUL_ESC); c.alignment = Ac(); c.border = borda()

# Conta transmissores
pe1_ranges = {}; ps1_ranges = {}
for e in ESTACOES:
    pe = str(e[9]).replace(".", ",") + " bar"
    ps = str(e[10]).replace(".", ",") + " bar"
    pe1_ranges[pe] = pe1_ranges.get(pe,0) + 1
    ps1_ranges[ps] = ps1_ranges.get(ps,0) + 1

all_ranges = sorted(set(list(pe1_ranges.keys()) + list(ps1_ranges.keys())))
for ri, rng in enumerate(all_ranges, 16):
    bg = C_CINZA_L if ri % 2 == 0 else C_BRANCO
    pe_q = pe1_ranges.get(rng, 0)
    ps_q = ps1_ranges.get(rng, 0)
    for ci, val in enumerate([rng, pe_q or "—", ps_q or "—", pe_q+ps_q], 1):
        c = wp.cell(ri, ci, val)
        c.fill = F(C_VERDE_CL if ci == 4 else bg)
        c.font = Fb(9, C_VERDE) if ci == 4 else Fn(10)
        c.alignment = Ac(); c.border = borda()
    wp.row_dimensions[ri].height = 20

# Totais PDT e Shutoff
pdt_total  = sum(e[12] for e in ESTACOES if isinstance(e[12], (int,float)))
shut_total = sum(e[13] for e in ESTACOES if isinstance(e[13], (int,float)))
for ri, (lbl, val) in enumerate([(f"PDT (un.)", pdt_total), (f"Shutoff (un.)", shut_total)], 16+len(all_ranges)):
    for ci, v in enumerate([lbl, "—", "—", val], 1):
        c = wp.cell(ri, ci, v)
        c.fill = F(C_ROXO_CL if ci == 4 else C_CINZA_L)
        c.font = Fb(9, C_ROXO) if ci == 4 else Fn(10)
        c.alignment = Ac(); c.border = borda()
    wp.row_dimensions[ri].height = 20

# Larguras
for i in range(1,10):
    wp.column_dimensions[get_column_letter(i)].width = 16

# ════════════════════════════════════════════════════════════════════════════
# ABA 3: PENDÊNCIAS
# ════════════════════════════════════════════════════════════════════════════
wpen = wb.create_sheet("⚠️ Pendências")
wpen.sheet_view.showGridLines = False

wpen.merge_cells("A1:H1")
c = wpen["A1"]
c.value = "ESTAÇÕES COM PENDÊNCIAS DE DADOS — AÇÃO REQUERIDA ANTES DA EXECUÇÃO"
c.fill = F(C_VERM); c.font = Fb(13); c.alignment = Ac()
wpen.row_dimensions[1].height = 36

# 3 sub-blocos: sem LM / sem LT / sem coordenadas
def bloco_pendencia(ws_p, row_start, titulo, estacoes_filtradas, cor):
    n = len(estacoes_filtradas)
    ws_p.merge_cells(f"A{row_start}:H{row_start}")
    c = ws_p.cell(row_start, 1, f"{titulo} ({n} estação{'s' if n>1 else ''})")
    c.fill = F(cor); c.font = Fb(10); c.alignment = Ac()
    ws_p.row_dimensions[row_start].height = 22

    hdrs = ["Estação","Tipo","CG","Ordem OS","LI Mecânica","LI Telemetria","Lat","Lon"]
    for ci, h in enumerate(hdrs, 1):
        c = ws_p.cell(row_start+1, ci, h)
        c.fill = F(C_CINZA_H); c.font = Fb(9, C_AZUL_ESC); c.alignment = Ac(); c.border = borda()
    ws_p.row_dimensions[row_start+1].height = 28

    for ri, e in enumerate(estacoes_filtradas, row_start+2):
        eid,_,ordem,li_mec,li_tel,lat,lon = e[0],e[1],e[2],e[3],e[4],e[5],e[6]
        vals = [eid, tipo(eid), grupo(li_mec), ordem or "—",
                li_mec or "⚠ FALTANTE", li_tel or "⚠ FALTANTE",
                lat if coord_ok(lat,lon) else "⚠ N/D",
                lon if coord_ok(lat,lon) else "⚠ N/D"]
        bg = C_CINZA_L if ri % 2 == 0 else C_BRANCO
        for ci, val in enumerate(vals, 1):
            c = ws_p.cell(ri, ci, val)
            c.border = borda(); c.font = Fn(9); c.alignment = Ac()
            if isinstance(val,str) and "⚠" in val:
                c.fill = F(C_AMAR_CL); c.font = Fn(9, C_AMAR)
            else:
                c.fill = F(bg)
        ws_p.row_dimensions[ri].height = 20
    return row_start + 2 + len(estacoes_filtradas) + 1

sem_lm   = [e for e in ESTACOES if not e[3]]
sem_lt   = [e for e in ESTACOES if not e[4]]
sem_coo  = [e for e in ESTACOES if not coord_ok(e[5], e[6])]

r = bloco_pendencia(wpen, 2,  "⚠ SEM LI MECÂNICA",  sem_lm,  C_LAR)
r = bloco_pendencia(wpen, r,  "⚠ SEM LI TELEMETRIA", sem_lt,  C_AMAR)
r = bloco_pendencia(wpen, r,  "⚠ SEM COORDENADAS",   sem_coo, C_VERM)

largs_pen = [14,8,10,12,26,26,14,14]
for i,l in enumerate(largs_pen,1):
    wpen.column_dimensions[get_column_letter(i)].width = l

# ════════════════════════════════════════════════════════════════════════════
# ABA 4: RESUMO DE MATERIAIS
# ════════════════════════════════════════════════════════════════════════════
wm = wb.create_sheet("📦 Resumo de Materiais")
wm.sheet_view.showGridLines = False

wm.merge_cells("A1:F1")
c = wm["A1"]
c.value = "RESUMO DE MATERIAIS — TRANSMISSORES E COMPONENTES POR ESTAÇÃO"
c.fill = F(C_AZUL_ESC); c.font = Fb(13); c.alignment = Ac()
wm.row_dimensions[1].height = 36

hdrs_m = ["Estação","Tipo","CG","Pressão Entrada (bar)","PE1 (faixa bar)","PS1 (faixa bar)","PDT (un.)","Shutoff (un.)","Caixa","Suporte","P.Solar (W)","Modem","Gateway"]
widths_m = [14,6,8,14,12,12,9,9,10,10,12,12,12]
for ci,(h,w) in enumerate(zip(hdrs_m,widths_m),1):
    c = wm.cell(2, ci, h)
    c.fill = F(C_AZUL_MED); c.font = Fb(9); c.alignment = Ac(); c.border = borda()
    wm.column_dimensions[get_column_letter(ci)].width = w
wm.row_dimensions[2].height = 36

# Subtotais por faixa PE1 e PS1
totais_pe1 = {}; totais_ps1 = {}; total_pdt = 0; total_shut = 0
for ri, e in enumerate(ESTACOES, 3):
    eid,_,ordem,li_mec,li_tel,lat,lon,pin,psai,pe1,ps1,pdt,shutoff = e[:13]
    bg = C_CINZA_L if ri % 2 == 0 else C_BRANCO
    vals = [eid, tipo(eid), grupo(li_mec), pin, pe1, ps1,
            pdt or 0, shutoff or 0, "","","","",""]
    for ci,val in enumerate(vals,1):
        c = wm.cell(ri, ci, val)
        c.fill = F(bg); c.font = Fn(9); c.alignment = Ac(); c.border = borda()
    wm.row_dimensions[ri].height = 18

    totais_pe1[pe1] = totais_pe1.get(pe1,0) + 1
    totais_ps1[ps1] = totais_ps1.get(ps1,0) + 1
    if pdt: total_pdt += pdt
    if shutoff: total_shut += shutoff

# Linha de totais
row_tot = 3 + len(ESTACOES)
wm.row_dimensions[row_tot].height = 14
row_tot += 1

wm.merge_cells(f"A{row_tot}:D{row_tot}")
c = wm.cell(row_tot, 1, "TOTAIS")
c.fill = F(C_AZUL_ESC); c.font = Fb(11); c.alignment = Ac()

pe1_desc = " | ".join([f"{int(k) if k==int(k) else k} bar: {v} un." for k,v in sorted(totais_pe1.items())])
ps1_desc = " | ".join([f"{int(k) if k==int(k) else k} bar: {v} un." for k,v in sorted(totais_ps1.items())])

row_tot2 = row_tot + 1
vals_tot = ["TOTAL","","","", pe1_desc, ps1_desc, total_pdt, total_shut,"","","","",""]
for ci, val in enumerate(vals_tot,1):
    c = wm.cell(row_tot2, ci, val)
    c.fill = F(C_VERDE_CL); c.font = Fb(9, C_VERDE); c.alignment = Al(); c.border = borda()
wm.row_dimensions[row_tot2].height = 28

wm.freeze_panes = "A3"

# ════════════════════════════════════════════════════════════════════════════
# Salvar
# ════════════════════════════════════════════════════════════════════════════
saida = "/home/user/nodered-heroku/utils/Renovacao_Telemetria_4.0_Controle.xlsx"
wb.save(saida)
print(f"OK → {saida}")
