"""
Gerador de Planilha de Controle de Renovação de Telemetria
Estações de Redução de Pressão de Gás Natural
"""

import openpyxl
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side, GradientFill
)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.series import DataPoint
from datetime import date, timedelta
import os

# ── Paleta de cores ──────────────────────────────────────────────────────────
COR_AZUL_ESCURO   = "1F3864"
COR_AZUL_MEDIO    = "2E75B6"
COR_AZUL_CLARO    = "BDD7EE"
COR_CINZA_HEADER  = "D6DCE4"
COR_CINZA_LINHA   = "F2F2F2"
COR_VERDE         = "70AD47"
COR_VERDE_CLARO   = "E2EFDA"
COR_AMARELO       = "FFD966"
COR_AMARELO_CLARO = "FFF2CC"
COR_VERMELHO      = "FF0000"
COR_VERMELHO_CLARO= "FCE4D6"
COR_LARANJA       = "ED7D31"
COR_BRANCO        = "FFFFFF"

# ── Helpers de estilo ────────────────────────────────────────────────────────
def fill(cor):
    return PatternFill("solid", fgColor=cor)

def bold(size=11, color=COR_BRANCO, name="Calibri"):
    return Font(bold=True, size=size, color=color, name=name)

def normal(size=10, color="000000", name="Calibri"):
    return Font(size=size, color=color, name=name)

def center():
    return Alignment(horizontal="center", vertical="center", wrap_text=True)

def left():
    return Alignment(horizontal="left", vertical="center", wrap_text=True)

def borda_fina():
    lado = Side(style="thin", color="BFBFBF")
    return Border(left=lado, right=lado, top=lado, bottom=lado)

def borda_media():
    lado = Side(style="medium", color=COR_AZUL_MEDIO)
    return Border(left=lado, right=lado, top=lado, bottom=lado)

def aplicar_header(ws, linha, colunas_dados, titulo_aba):
    """Cabeçalho visual por aba."""
    ws.merge_cells(start_row=linha, start_column=1, end_row=linha, end_column=len(colunas_dados))
    c = ws.cell(linha, 1, titulo_aba)
    c.fill = fill(COR_AZUL_ESCURO)
    c.font = bold(14)
    c.alignment = center()
    ws.row_dimensions[linha].height = 32

def aplicar_subheader(ws, linha, colunas_dados):
    """Linha de subtítulo dos campos."""
    for col, (label, largura) in enumerate(colunas_dados, 1):
        c = ws.cell(linha, col, label)
        c.fill = fill(COR_AZUL_MEDIO)
        c.font = bold(10)
        c.alignment = center()
        c.border = borda_fina()
        ws.column_dimensions[get_column_letter(col)].width = largura
    ws.row_dimensions[linha].height = 40

def cor_status(status):
    mapa = {
        "Concluído":    (COR_VERDE,         COR_VERDE_CLARO),
        "Em andamento": (COR_AZUL_MEDIO,    COR_AZUL_CLARO),
        "Pendente":     (COR_AMARELO,        COR_AMARELO_CLARO),
        "Atrasado":     (COR_LARANJA,        COR_VERMELHO_CLARO),
        "Cancelado":    ("808080",           COR_CINZA_LINHA),
        "Não iniciado": (COR_CINZA_HEADER,   COR_CINZA_LINHA),
    }
    return mapa.get(status, ("000000", COR_BRANCO))

# ── Dados de exemplo ─────────────────────────────────────────────────────────
ESTACOES = [
    {"id": "ERP-001", "nome": "ERP Alto da Serra",    "municipio": "São Paulo",    "uf": "SP", "regional": "Sul",    "categoria": "Primária",    "prioridade": "Alta",   "status_geral": "Em andamento", "perc": 65},
    {"id": "ERP-002", "nome": "ERP Vale do Rio Doce", "municipio": "Governador Valadares","uf": "MG","regional": "Leste","categoria": "Secundária","prioridade": "Alta",  "status_geral": "Pendente",    "perc": 20},
    {"id": "ERP-003", "nome": "ERP Cabine Norte",     "municipio": "Campinas",     "uf": "SP", "regional": "Sul",    "categoria": "Primária",    "prioridade": "Média",  "status_geral": "Concluído",   "perc": 100},
    {"id": "ERP-004", "nome": "ERP Planalto Central", "municipio": "Brasília",     "uf": "DF", "regional": "Centro", "categoria": "Primária",    "prioridade": "Alta",   "status_geral": "Atrasado",    "perc": 40},
    {"id": "ERP-005", "nome": "ERP Litoral Sul",      "municipio": "Santos",       "uf": "SP", "regional": "Sul",    "categoria": "Secundária",  "prioridade": "Baixa",  "status_geral": "Não iniciado","perc": 0},
    {"id": "ERP-006", "nome": "ERP Zona Industrial",  "municipio": "Porto Alegre", "uf": "RS", "regional": "Sul",    "categoria": "Primária",    "prioridade": "Média",  "status_geral": "Em andamento","perc": 55},
    {"id": "ERP-007", "nome": "ERP Serra Gaúcha",     "municipio": "Caxias do Sul","uf": "RS", "regional": "Sul",    "categoria": "Secundária",  "prioridade": "Baixa",  "status_geral": "Concluído",   "perc": 100},
    {"id": "ERP-008", "nome": "ERP Polo Petroquímico","municipio": "Camaçari",     "uf": "BA", "regional": "Norte",  "categoria": "Primária",    "prioridade": "Alta",   "status_geral": "Em andamento","perc": 75},
]

FASES = [
    "Levantamento de Campo",
    "Elaboração de Projeto",
    "Aprovação do Projeto",
    "Aquisição de Equipamentos",
    "Recebimento de Equipamentos",
    "Configuração / Programação",
    "Remoção do Sistema Antigo",
    "Instalação do Sistema Novo",
    "Comissionamento",
    "Testes de Comunicação",
    "Integração SCADA",
    "Calibração e Certificação",
    "Aprovação Operacional",
    "Entrega e Documentação",
]

EQUIPAMENTOS = [
    ("Transmissor de Pressão Upstream",  "Bar (manométrico)",  "0–100",    "4–20 mA HART"),
    ("Transmissor de Pressão Downstream","Bar (manométrico)",  "0–50",     "4–20 mA HART"),
    ("Transmissor de Temperatura",       "°C",                 "-10 a 60", "4–20 mA HART"),
    ("Medidor de Vazão (Ultrassônico)",  "m³/h",               "0–5000",   "RS-485 Modbus"),
    ("Analisador de Qualidade de Gás",   "BTU/m³, %CH4",       "—",        "RS-232"),
    ("RTU / PLC",                        "—",                  "—",        "Multi-protocolo"),
    ("Modem de Comunicação",             "—",                  "—",        "4G/GPRS"),
    ("Painel Solar + Bateria",           "W / Ah",             "—",        "12/24 VDC"),
    ("Antena Externa",                   "—",                  "—",        "SMA/N-Type"),
    ("Sensor de Abertura de Porta",      "—",                  "—",        "Digital"),
]

PROBLEMAS_EXEMPLO = [
    ("ERP-001", "ERP Alto da Serra",    "Técnico",     "Alta",   "Compatibilidade do protocolo HART com RTU legado",                 "Aberto",   "João Silva",   "2026-05-10", "2026-05-25", "Aguardando firmware do fornecedor"),
    ("ERP-004", "ERP Planalto Central", "Logística",   "Alta",   "Atraso na entrega do medidor de vazão (prazo: 45 dias corridos)",  "Aberto",   "Maria Lima",   "2026-05-18", "2026-06-02", "Solicitado acompanhamento junto ao fornecedor"),
    ("ERP-006", "ERP Zona Industrial",  "Operacional", "Média",  "Interferência de sinal GSM no local — necessário antena direcional","Em análise","Carlos Souza", "2026-05-20", "2026-06-10", "Realizando levantamento de sinal in loco"),
    ("ERP-003", "ERP Cabine Norte",     "Qualidade",   "Baixa",  "Divergência de 0,3% na calibração do transmissor de pressão",      "Fechado",  "Ana Costa",    "2026-04-05", "2026-04-12", "Recalibrado e certificado pelo INMETRO"),
]

CHECKLIST_COMISSIONAMENTO = [
    ("ELÉTRICA",         "Verificar tensão de alimentação (12/24 VDC)",                   "Sim/Não"),
    ("ELÉTRICA",         "Verificar aterramento do painel",                                "Sim/Não"),
    ("ELÉTRICA",         "Verificar fusíveis e disjuntores",                               "Sim/Não"),
    ("ELÉTRICA",         "Testar carga da bateria / painel solar",                         "Medição (V)"),
    ("INSTRUMENTAÇÃO",   "Confirmar range dos transmissores conforme projeto",              "Sim/Não"),
    ("INSTRUMENTAÇÃO",   "Verificar loop 4–20 mA em todos os pontos",                      "Sim/Não"),
    ("INSTRUMENTAÇÃO",   "Confirmar endereçamento HART",                                   "Sim/Não"),
    ("INSTRUMENTAÇÃO",   "Testar sensor de abertura de porta",                             "Sim/Não"),
    ("COMUNICAÇÃO",      "Confirmar nível de sinal GSM/4G (mín. -90 dBm)",                 "Medição (dBm)"),
    ("COMUNICAÇÃO",      "Realizar teste de ping com o servidor SCADA",                    "Sim/Não"),
    ("COMUNICAÇÃO",      "Verificar envio de alarmes por SMS/email",                       "Sim/Não"),
    ("RTU / PLC",        "Confirmar firmware atualizado",                                  "Versão"),
    ("RTU / PLC",        "Verificar banco de tags mapeado conforme IED-List",              "Sim/Não"),
    ("RTU / PLC",        "Testar watchdog e auto-restart",                                 "Sim/Não"),
    ("SCADA",            "Confirmar visualização de todos os pontos no SCADA",             "Sim/Não"),
    ("SCADA",            "Verificar histórico de dados sendo gravado",                     "Sim/Não"),
    ("SCADA",            "Testar alarmes de pressão alta/baixa no supervisório",           "Sim/Não"),
    ("CALIBRAÇÃO",       "Certificado de calibração do transmissor de pressão UP anexado","Sim/Não"),
    ("CALIBRAÇÃO",       "Certificado de calibração do transmissor de pressão DOWN anexado","Sim/Não"),
    ("CALIBRAÇÃO",       "Certificado de calibração do medidor de vazão anexado",          "Sim/Não"),
    ("DOCUMENTAÇÃO",     "As-built atualizado e assinado",                                 "Sim/Não"),
    ("DOCUMENTAÇÃO",     "Manual dos equipamentos entregue à operação",                    "Sim/Não"),
    ("DOCUMENTAÇÃO",     "Termo de entrega assinado pelo responsável operacional",         "Sim/Não"),
]

# ── Criação do workbook ───────────────────────────────────────────────────────
wb = openpyxl.Workbook()
wb.remove(wb.active)  # Remove aba padrão

# ════════════════════════════════════════════════════════════════════════════
# ABA 1: PAINEL GERAL
# ════════════════════════════════════════════════════════════════════════════
ws1 = wb.create_sheet("📊 Painel Geral")
ws1.sheet_view.showGridLines = False
ws1.sheet_view.zoomScale = 90

# Título principal
ws1.merge_cells("A1:P1")
c = ws1["A1"]
c.value = "CONTROLE DE RENOVAÇÃO DE TELEMETRIA — ESTAÇÕES DE REDUÇÃO DE PRESSÃO (ERP)"
c.fill = fill(COR_AZUL_ESCURO)
c.font = bold(16)
c.alignment = center()
ws1.row_dimensions[1].height = 45

# Subtítulo
ws1.merge_cells("A2:P2")
c = ws1["A2"]
c.value = f"Gerado em: {date.today().strftime('%d/%m/%Y')}  |  Responsável: Francisco Silva  |  Empresa: —"
c.fill = fill(COR_AZUL_MEDIO)
c.font = bold(10)
c.alignment = center()
ws1.row_dimensions[2].height = 22

# ── Indicadores resumo ────────────────────────────────────────────────────────
ws1.row_dimensions[3].height = 18
ws1.row_dimensions[4].height = 28
ws1.row_dimensions[5].height = 40
ws1.row_dimensions[6].height = 20

total     = len(ESTACOES)
concluido = sum(1 for e in ESTACOES if e["status_geral"] == "Concluído")
andamento = sum(1 for e in ESTACOES if e["status_geral"] == "Em andamento")
pendente  = sum(1 for e in ESTACOES if e["status_geral"] == "Pendente")
atrasado  = sum(1 for e in ESTACOES if e["status_geral"] == "Atrasado")
nao_inic  = sum(1 for e in ESTACOES if e["status_geral"] == "Não iniciado")
perc_medio= round(sum(e["perc"] for e in ESTACOES) / total)

indicadores = [
    ("TOTAL DE ERPs",     total,      COR_AZUL_ESCURO),
    ("CONCLUÍDAS",        concluido,  COR_VERDE),
    ("EM ANDAMENTO",      andamento,  COR_AZUL_MEDIO),
    ("PENDENTES",         pendente,   COR_AMARELO),
    ("ATRASADAS",         atrasado,   COR_LARANJA),
    ("NÃO INICIADAS",     nao_inic,   "808080"),
    ("PROGRESSO MÉDIO",   f"{perc_medio}%", COR_AZUL_MEDIO),
]

col_starts = [1, 3, 5, 7, 9, 11, 13]
for idx, (label, valor, cor) in enumerate(indicadores):
    cs = col_starts[idx]
    ws1.merge_cells(start_row=4, start_column=cs, end_row=4, end_column=cs+1)
    ws1.merge_cells(start_row=5, start_column=cs, end_row=5, end_column=cs+1)
    cl = ws1.cell(4, cs, label)
    cl.fill = fill(cor)
    cl.font = bold(9)
    cl.alignment = center()
    cv = ws1.cell(5, cs, valor)
    cv.fill = fill(cor)
    cv.font = bold(22)
    cv.alignment = center()

# ── Tabela de estações ────────────────────────────────────────────────────────
cols_painel = [
    ("ID",           8), ("Estação",         28), ("Município",   16), ("UF", 5),
    ("Regional",    10), ("Categoria",        12), ("Prioridade",  10),
    ("Status Geral",15), ("Progresso (%)",    12), ("Barra",       22),
]

linha_header = 7
aplicar_header(ws1, linha_header, cols_painel, "MAPA DE STATUS DAS ESTAÇÕES")
aplicar_subheader(ws1, linha_header+1, cols_painel)

for row_idx, est in enumerate(ESTACOES, start=linha_header+2):
    cor_txt, cor_bg = cor_status(est["status_geral"])
    linha_par = row_idx % 2 == 0
    bg_linha = COR_CINZA_LINHA if linha_par else COR_BRANCO

    dados = [
        est["id"], est["nome"], est["municipio"], est["uf"],
        est["regional"], est["categoria"], est["prioridade"],
        est["status_geral"], est["perc"],
    ]
    for col_idx, valor in enumerate(dados, 1):
        c = ws1.cell(row_idx, col_idx, valor)
        c.border = borda_fina()
        c.alignment = center() if col_idx != 2 else left()
        c.font = normal(10)
        if col_idx == 8:
            c.fill = fill(cor_bg)
            c.font = bold(10, cor_txt)
        else:
            c.fill = fill(bg_linha)

    # Barra de progresso textual
    perc = est["perc"]
    blocos = round(perc / 5)
    barra = "█" * blocos + "░" * (20 - blocos)
    cb = ws1.cell(row_idx, 10, f"{barra} {perc}%")
    cb.alignment = left()
    cb.border = borda_fina()
    cb.fill = fill(COR_VERDE_CLARO if perc == 100 else COR_AMARELO_CLARO if perc > 0 else COR_CINZA_LINHA)
    cb.font = normal(9, COR_VERDE if perc == 100 else "000000")

    ws1.row_dimensions[row_idx].height = 22

# Larguras
larguras_p = [8, 28, 16, 5, 10, 12, 10, 15, 12, 28]
for i, l in enumerate(larguras_p, 1):
    ws1.column_dimensions[get_column_letter(i)].width = l

# Congelar
ws1.freeze_panes = "A9"

# ════════════════════════════════════════════════════════════════════════════
# ABA 2: CRONOGRAMA DE EXECUÇÃO
# ════════════════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet("📅 Cronograma de Execução")
ws2.sheet_view.showGridLines = False
ws2.sheet_view.zoomScale = 80

# Cabeçalho
ws2.merge_cells(f"A1:{get_column_letter(4 + len(FASES)*3)}1")
c = ws2["A1"]
c.value = "CRONOGRAMA DE EXECUÇÃO — FASES DE RENOVAÇÃO DE TELEMETRIA POR ESTAÇÃO"
c.fill = fill(COR_AZUL_ESCURO)
c.font = bold(13)
c.alignment = center()
ws2.row_dimensions[1].height = 38

# Linha de fase (cabeçalhos grupos)
for i, fase in enumerate(FASES):
    col_ini = 5 + i * 3
    ws2.merge_cells(start_row=2, start_column=col_ini, end_row=2, end_column=col_ini+2)
    c = ws2.cell(2, col_ini, fase)
    c.fill = fill(COR_AZUL_MEDIO if i % 2 == 0 else COR_AZUL_ESCURO)
    c.font = bold(8)
    c.alignment = center()

# Colunas fixas header
fixos = [("ID", 8), ("Estação", 28), ("Regional", 10), ("Prioridade", 10)]
for col_idx, (nome, larg) in enumerate(fixos, 1):
    c = ws2.cell(2, col_idx, nome)
    c.fill = fill(COR_AZUL_ESCURO)
    c.font = bold(9)
    c.alignment = center()
    ws2.column_dimensions[get_column_letter(col_idx)].width = larg
ws2.row_dimensions[2].height = 45

# Sub-headers por fase
sub_fase = ["Prev.", "Real", "Status"]
for i in range(len(FASES)):
    for j, sub in enumerate(sub_fase):
        col = 5 + i * 3 + j
        c = ws2.cell(3, col, sub)
        c.fill = fill(COR_CINZA_HEADER)
        c.font = bold(8, COR_AZUL_ESCURO)
        c.alignment = center()
        c.border = borda_fina()
        ws2.column_dimensions[get_column_letter(col)].width = 10
ws2.row_dimensions[3].height = 25

# Merge das colunas fixas nas linhas 2-3
for col_idx in range(1, 5):
    ws2.merge_cells(start_row=2, start_column=col_idx, end_row=3, end_column=col_idx)
    ws2.cell(2, col_idx).alignment = center()

# Dados de exemplo
status_fases_exemplo = {
    "ERP-001": ["Concluído","Concluído","Concluído","Concluído","Concluído","Concluído","Concluído","Em andamento","Pendente","Pendente","Pendente","Pendente","Pendente","Pendente"],
    "ERP-002": ["Concluído","Em andamento","Pendente","Pendente","Pendente","Pendente","Pendente","Pendente","Pendente","Pendente","Pendente","Pendente","Pendente","Pendente"],
    "ERP-003": ["Concluído","Concluído","Concluído","Concluído","Concluído","Concluído","Concluído","Concluído","Concluído","Concluído","Concluído","Concluído","Concluído","Concluído"],
    "ERP-004": ["Concluído","Concluído","Concluído","Atrasado","Atrasado","Pendente","Pendente","Pendente","Pendente","Pendente","Pendente","Pendente","Pendente","Pendente"],
    "ERP-005": ["Não iniciado"]*14,
    "ERP-006": ["Concluído","Concluído","Concluído","Concluído","Concluído","Concluído","Em andamento","Em andamento","Pendente","Pendente","Pendente","Pendente","Pendente","Pendente"],
    "ERP-007": ["Concluído"]*14,
    "ERP-008": ["Concluído","Concluído","Concluído","Concluído","Concluído","Concluído","Concluído","Concluído","Concluído","Em andamento","Pendente","Pendente","Pendente","Pendente"],
}

data_base = date(2026, 3, 1)
for row_idx, est in enumerate(ESTACOES, start=4):
    bg = COR_CINZA_LINHA if row_idx % 2 == 0 else COR_BRANCO
    dados_fix = [est["id"], est["nome"], est["regional"], est["prioridade"]]
    for col_idx, val in enumerate(dados_fix, 1):
        c = ws2.cell(row_idx, col_idx, val)
        c.fill = fill(bg)
        c.font = normal(9)
        c.alignment = left() if col_idx == 2 else center()
        c.border = borda_fina()

    status_list = status_fases_exemplo.get(est["id"], ["Pendente"]*14)
    for f_idx, st in enumerate(status_list):
        col_ini = 5 + f_idx * 3
        dt_prev = data_base + timedelta(weeks=f_idx * 2 + row_idx - 4)
        dt_real = dt_prev + timedelta(days=3) if st == "Concluído" else None
        cor_txt, cor_bg = cor_status(st)

        c_prev = ws2.cell(row_idx, col_ini, dt_prev.strftime("%d/%m/%y"))
        c_prev.fill = fill(bg)
        c_prev.font = normal(8)
        c_prev.alignment = center()
        c_prev.border = borda_fina()

        c_real = ws2.cell(row_idx, col_ini+1, dt_real.strftime("%d/%m/%y") if dt_real else "—")
        c_real.fill = fill(bg)
        c_real.font = normal(8)
        c_real.alignment = center()
        c_real.border = borda_fina()

        c_st = ws2.cell(row_idx, col_ini+2, st)
        c_st.fill = fill(cor_bg)
        c_st.font = bold(8, cor_txt)
        c_st.alignment = center()
        c_st.border = borda_fina()

    ws2.row_dimensions[row_idx].height = 22

ws2.freeze_panes = "E4"

# ════════════════════════════════════════════════════════════════════════════
# ABA 3: INVENTÁRIO DE EQUIPAMENTOS
# ════════════════════════════════════════════════════════════════════════════
ws3 = wb.create_sheet("🔧 Inventário de Equipamentos")
ws3.sheet_view.showGridLines = False

cols_inv = [
    ("ID ERP", 10), ("Estação", 28), ("Equipamento", 32), ("Unid. Eng.", 12),
    ("Faixa", 12), ("Protocolo", 14), ("Tag", 14), ("Qtd. Prev.", 10),
    ("Qtd. Rec.", 10), ("Fabricante", 16), ("Modelo", 18),
    ("Nº Série", 16), ("Cert. Calibração", 16), ("Status", 14), ("Observações", 30),
]

aplicar_header(ws3, 1, cols_inv, "INVENTÁRIO DE EQUIPAMENTOS DE TELEMETRIA POR ESTAÇÃO")
aplicar_subheader(ws3, 2, cols_inv)

row3 = 3
for est in ESTACOES:
    for eq in EQUIPAMENTOS:
        nome_eq, unid, faixa, protocolo = eq
        bg = COR_CINZA_LINHA if row3 % 2 == 0 else COR_BRANCO
        status_eq = "Instalado" if est["status_geral"] == "Concluído" else ("Em instalação" if est["status_geral"] in ("Em andamento",) else "Aguardando")
        cor_txt_e, cor_bg_e = cor_status("Concluído" if status_eq == "Instalado" else ("Em andamento" if status_eq == "Em instalação" else "Pendente"))
        dados = [
            est["id"], est["nome"], nome_eq, unid, faixa, protocolo,
            f"TLM-{est['id'][-3:]}-{nome_eq[:3].upper()}",
            1, 1 if status_eq == "Instalado" else 0,
            "—", "—", "—",
            "Sim" if status_eq == "Instalado" else "Não",
            status_eq, "",
        ]
        for col_idx, val in enumerate(dados, 1):
            c = ws3.cell(row3, col_idx, val)
            c.border = borda_fina()
            c.alignment = center() if col_idx not in (2, 3, 15) else left()
            c.font = normal(9)
            if col_idx == 14:
                c.fill = fill(cor_bg_e)
                c.font = bold(9, cor_txt_e)
            else:
                c.fill = fill(bg)
        ws3.row_dimensions[row3].height = 20
        row3 += 1

ws3.freeze_panes = "A3"

# ════════════════════════════════════════════════════════════════════════════
# ABA 4: CHECKLIST DE COMISSIONAMENTO
# ════════════════════════════════════════════════════════════════════════════
ws4 = wb.create_sheet("✅ Checklist Comissionamento")
ws4.sheet_view.showGridLines = False

cols_ck = [
    ("ID ERP", 10), ("Estação", 28), ("Área", 18), ("Item de Verificação", 55),
    ("Tipo Resposta", 14), ("Resultado", 16), ("Conforme?", 11),
    ("Responsável", 20), ("Data", 12), ("Observações", 30),
]

aplicar_header(ws4, 1, cols_ck, "CHECKLIST DE COMISSIONAMENTO — RENOVAÇÃO DE TELEMETRIA")
aplicar_subheader(ws4, 2, cols_ck)

# Validação dropdown Conforme
dv_sim_nao = DataValidation(type="list", formula1='"Sim,Não,N/A"', allow_blank=False)
dv_sim_nao.error = "Valor inválido. Use: Sim, Não ou N/A"
dv_sim_nao.errorTitle = "Entrada inválida"
ws4.add_data_validation(dv_sim_nao)

row4 = 3
area_atual = ""
for est in ESTACOES[:3]:  # Exemplo com 3 estações
    for area, item, tipo in CHECKLIST_COMISSIONAMENTO:
        bg = COR_CINZA_LINHA if row4 % 2 == 0 else COR_BRANCO
        area_fill = COR_AZUL_CLARO if area != area_atual else bg
        area_atual = area
        dados = [est["id"], est["nome"], area, item, tipo, "", "", "", "", ""]
        for col_idx, val in enumerate(dados, 1):
            c = ws4.cell(row4, col_idx, val)
            c.border = borda_fina()
            c.font = normal(9)
            c.alignment = left() if col_idx in (3, 4, 10) else center()
            if col_idx == 3:
                c.fill = fill(area_fill)
                c.font = bold(9, COR_AZUL_ESCURO)
            else:
                c.fill = fill(bg)
        dv_sim_nao.add(ws4.cell(row4, 7))
        ws4.row_dimensions[row4].height = 20
        row4 += 1

ws4.freeze_panes = "D3"

# ════════════════════════════════════════════════════════════════════════════
# ABA 5: REGISTRO DE PROBLEMAS
# ════════════════════════════════════════════════════════════════════════════
ws5 = wb.create_sheet("⚠️ Registro de Problemas")
ws5.sheet_view.showGridLines = False

cols_prob = [
    ("Nº", 6), ("ID ERP", 10), ("Estação", 24), ("Categoria", 14),
    ("Severidade", 12), ("Descrição do Problema", 50), ("Status", 14),
    ("Responsável", 18), ("Data Abertura", 13), ("Prazo Resolução", 14),
    ("Ação Tomada / Resolução", 40),
]

aplicar_header(ws5, 1, cols_prob, "REGISTRO DE PROBLEMAS E NÃO-CONFORMIDADES")
aplicar_subheader(ws5, 2, cols_prob)

# Validações
dv_status_prob = DataValidation(type="list", formula1='"Aberto,Em análise,Em resolução,Fechado,Cancelado"')
dv_sev = DataValidation(type="list", formula1='"Alta,Média,Baixa"')
ws5.add_data_validation(dv_status_prob)
ws5.add_data_validation(dv_sev)

row5 = 3
for i, prob in enumerate(PROBLEMAS_EXEMPLO, 1):
    id_erp, nome, cat, sev, desc, st, resp, dt_ab, dt_pz, acao = prob
    bg = COR_CINZA_LINHA if row5 % 2 == 0 else COR_BRANCO
    cor_txt_s, cor_bg_s = cor_status(st if st in ("Concluído","Em andamento","Pendente","Atrasado","Não iniciado") else ("Concluído" if st == "Fechado" else "Em andamento" if st == "Em análise" else "Pendente"))
    cor_sev = COR_VERMELHO_CLARO if sev == "Alta" else COR_AMARELO_CLARO if sev == "Média" else COR_VERDE_CLARO

    dados = [i, id_erp, nome, cat, sev, desc, st, resp, dt_ab, dt_pz, acao]
    for col_idx, val in enumerate(dados, 1):
        c = ws5.cell(row5, col_idx, val)
        c.border = borda_fina()
        c.font = normal(9)
        c.alignment = left() if col_idx in (6, 11, 3) else center()
        if col_idx == 5:
            c.fill = fill(cor_sev)
            c.font = bold(9)
        elif col_idx == 7:
            c.fill = fill(cor_bg_s)
            c.font = bold(9, cor_txt_s)
        else:
            c.fill = fill(bg)
    dv_status_prob.add(ws5.cell(row5, 7))
    dv_sev.add(ws5.cell(row5, 5))
    ws5.row_dimensions[row5].height = 36
    row5 += 1

# Linhas em branco para novos problemas
for _ in range(15):
    for col_idx in range(1, len(cols_prob)+1):
        c = ws5.cell(row5, col_idx, "")
        c.border = borda_fina()
        c.fill = fill(COR_BRANCO)
    dv_status_prob.add(ws5.cell(row5, 7))
    dv_sev.add(ws5.cell(row5, 5))
    ws5.row_dimensions[row5].height = 22
    row5 += 1

ws5.freeze_panes = "A3"

# ════════════════════════════════════════════════════════════════════════════
# ABA 6: CADASTRO DE ESTAÇÕES
# ════════════════════════════════════════════════════════════════════════════
ws6 = wb.create_sheet("🏭 Cadastro de Estações")
ws6.sheet_view.showGridLines = False

cols_cad = [
    ("ID ERP", 10), ("Nome da Estação", 30), ("Município", 18), ("UF", 6),
    ("Regional", 12), ("Categoria", 13), ("Prioridade", 11),
    ("Endereço / Localização", 35), ("Latitude", 12), ("Longitude", 12),
    ("Responsável Operacional", 22), ("Contato", 18),
    ("Pressão Montante (bar)", 16), ("Pressão Jusante (bar)", 16),
    ("Vazão Máx. (m³/h)", 14), ("Status Geral", 14), ("Observações", 30),
]

aplicar_header(ws6, 1, cols_cad, "CADASTRO DE ESTAÇÕES DE REDUÇÃO DE PRESSÃO (ERP)")
aplicar_subheader(ws6, 2, cols_cad)

dv_prior = DataValidation(type="list", formula1='"Alta,Média,Baixa"')
dv_categ = DataValidation(type="list", formula1='"Primária,Secundária,Terciária"')
ws6.add_data_validation(dv_prior)
ws6.add_data_validation(dv_categ)

for row_idx, est in enumerate(ESTACOES, start=3):
    bg = COR_CINZA_LINHA if row_idx % 2 == 0 else COR_BRANCO
    cor_txt_st, cor_bg_st = cor_status(est["status_geral"])
    dados = [
        est["id"], est["nome"], est["municipio"], est["uf"],
        est["regional"], est["categoria"], est["prioridade"],
        "—", "—", "—", "—", "—", "—", "—", "—",
        est["status_geral"], "",
    ]
    for col_idx, val in enumerate(dados, 1):
        c = ws6.cell(row_idx, col_idx, val)
        c.border = borda_fina()
        c.font = normal(9)
        c.alignment = left() if col_idx in (2, 8, 17) else center()
        if col_idx == 16:
            c.fill = fill(cor_bg_st)
            c.font = bold(9, cor_txt_st)
        else:
            c.fill = fill(bg)
    dv_prior.add(ws6.cell(row_idx, 7))
    dv_categ.add(ws6.cell(row_idx, 6))
    ws6.row_dimensions[row_idx].height = 22

ws6.freeze_panes = "A3"

# ════════════════════════════════════════════════════════════════════════════
# ABA 7: INSTRUÇÕES DE USO
# ════════════════════════════════════════════════════════════════════════════
ws7 = wb.create_sheet("ℹ️ Instruções de Uso")
ws7.sheet_view.showGridLines = False
ws7.sheet_view.zoomScale = 90

ws7.merge_cells("A1:H1")
c = ws7["A1"]
c.value = "MANUAL DE USO — PLANILHA DE CONTROLE DE RENOVAÇÃO DE TELEMETRIA"
c.fill = fill(COR_AZUL_ESCURO)
c.font = bold(14)
c.alignment = center()
ws7.row_dimensions[1].height = 40

instrucoes = [
    ("ABA",                       "PARA QUÊ USAR",                                                     "FREQUÊNCIA DE ATUALIZAÇÃO"),
    ("📊 Painel Geral",           "Visão executiva do status de todas as ERPs. Não editar diretamente — é alimentado pelas outras abas.", "Automático (leitura)"),
    ("📅 Cronograma de Execução", "Registre as datas planejadas/realizadas e o status de cada fase por estação.",                         "Semanal"),
    ("🔧 Inventário de Equip.",   "Controle de todos os equipamentos de telemetria por estação: tags, nº série, calibração, status.",    "A cada recebimento / instalação"),
    ("✅ Checklist Comiss.",       "Execute o checklist item a item antes de considerar a estação como 'Concluída'. Assine com nome e data.","A cada comissionamento"),
    ("⚠️ Registro de Problemas",  "Registre qualquer não-conformidade, desvio ou problema encontrado durante a execução.",               "Imediatamente ao detectar"),
    ("🏭 Cadastro de Estações",   "Dados cadastrais de cada ERP: localização, responsável, pressão operacional, categoria.",             "Quando houver mudança cadastral"),
]

ws7.row_dimensions[2].height = 18
ws7.row_dimensions[3].height = 22

for idx, (aba, uso, freq) in enumerate(instrucoes, start=3):
    is_header = idx == 3
    bg = COR_AZUL_MEDIO if is_header else (COR_CINZA_LINHA if idx % 2 == 0 else COR_BRANCO)
    fnt = bold(10) if is_header else normal(10)

    ws7.merge_cells(start_row=idx, start_column=1, end_row=idx, end_column=2)
    ws7.merge_cells(start_row=idx, start_column=3, end_row=idx, end_column=6)
    ws7.merge_cells(start_row=idx, start_column=7, end_row=idx, end_column=8)

    for col, val in [(1, aba), (3, uso), (7, freq)]:
        c = ws7.cell(idx, col, val)
        c.fill = fill(bg)
        c.font = fnt
        c.alignment = left()
        c.border = borda_fina()
    ws7.row_dimensions[idx].height = 36

ws7.merge_cells("A11:H11")
ws7.row_dimensions[11].height = 18

ws7.merge_cells("A12:H14")
nota = ws7["A12"]
nota.value = (
    "CONVENÇÃO DE STATUS:\n"
    "  ■ Concluído = todas as atividades da fase executadas, documentadas e aprovadas\n"
    "  ■ Em andamento = fase iniciada mas não finalizada\n"
    "  ■ Pendente = fase ainda não iniciada mas já agendada\n"
    "  ■ Atrasado = prazo ultrapassado sem conclusão\n"
    "  ■ Não iniciado = sem data definida ainda"
)
nota.fill = fill(COR_AMARELO_CLARO)
nota.font = normal(10, COR_AZUL_ESCURO)
nota.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
nota.border = borda_media()
ws7.row_dimensions[12].height = 18
ws7.row_dimensions[13].height = 18
ws7.row_dimensions[14].height = 60

for i in range(1, 9):
    ws7.column_dimensions[get_column_letter(i)].width = [12, 12, 20, 20, 20, 20, 16, 16][i-1]

# ════════════════════════════════════════════════════════════════════════════
# Ordenação das abas
# ════════════════════════════════════════════════════════════════════════════
ordem = [
    "📊 Painel Geral", "📅 Cronograma de Execução", "🔧 Inventário de Equipamentos",
    "✅ Checklist Comissionamento", "⚠️ Registro de Problemas",
    "🏭 Cadastro de Estações", "ℹ️ Instruções de Uso",
]
for i, nome in enumerate(ordem):
    wb._sheets.sort(key=lambda s: ordem.index(s.title) if s.title in ordem else 99)

# ════════════════════════════════════════════════════════════════════════════
# Salvar
# ════════════════════════════════════════════════════════════════════════════
saida = "/home/user/nodered-heroku/utils/Controle_Renovacao_Telemetria_ERP.xlsx"
wb.save(saida)
print(f"Planilha gerada: {saida}")
