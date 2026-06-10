import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

# ─────────────────────────────────────────────
# Configuração da página
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PrintPrice 3D – Orçamentos",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS customizado
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border-left: 5px solid #e94560;
    }
    .main-header h1 { color: #ffffff; margin: 0; font-size: 2rem; }
    .main-header p  { color: #a0aec0; margin: 0.4rem 0 0; font-size: 0.95rem; }

    .section-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
    }
    .section-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        color: #1a202c;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .price-box {
        background: linear-gradient(135deg, #0f3460, #e94560);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        text-align: center;
        color: white;
        margin: 1rem 0;
    }
    .price-box .label { font-size: 0.85rem; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.1em; }
    .price-box .value { font-size: 2.4rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif; }

    .cost-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #e2e8f0;
        font-size: 0.9rem;
        color: #4a5568;
    }
    .cost-row:last-child { border-bottom: none; }
    .cost-row .cost-label { font-weight: 500; }
    .cost-row .cost-value { font-weight: 600; color: #2d3748; }

    .color-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.15rem;
    }
    .badge-mono  { background: #ebf4ff; color: #2b6cb0; border: 1px solid #bee3f8; }
    .badge-multi { background: #faf5ff; color: #6b46c1; border: 1px solid #e9d8fd; }

    .orcamento-header {
        background: #1a1a2e;
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px 10px 0 0;
    }
    .orcamento-body  { background: white; padding: 1.5rem 2rem; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 10px 10px; }

    .stButton>button {
        background: linear-gradient(135deg, #0f3460, #e94560) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
    }
    .stButton>button:hover { opacity: 0.9 !important; }

    .stSelectbox label, .stNumberInput label, .stTextInput label, .stTextArea label {
        font-weight: 500;
        color: #2d3748;
        font-size: 0.88rem;
    }

    div[data-testid="metric-container"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.8rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Cabeçalho
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🖨️ PrintPrice 3D</h1>
    <p>Sistema de precificação e geração de orçamentos para impressão 3D</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar – Configurações de custo
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configurações de Custo")
    st.caption("Parâmetros base da sua impressora e negócio")

    with st.expander("💡 Custos de Energia e Máquina", expanded=True):
        custo_energia_kwh   = st.number_input("Custo energia (R$/kWh)", value=0.80, step=0.01, format="%.2f")
        potencia_impressora = st.number_input("Potência da impressora (W)", value=200, step=10)
        custo_hora_maquina  = st.number_input("Custo hora/máquina (R$)", value=5.00, step=0.50, format="%.2f",
                                               help="Depreciação, manutenção, etc.")

    with st.expander("🧵 Filamento", expanded=True):
        custo_filamento_kg = st.number_input("Custo do filamento (R$/kg)", value=120.00, step=5.0, format="%.2f")
        desperdicio_pct    = st.number_input("Desperdício estimado (%)", value=10.0, step=1.0, format="%.1f")

    with st.expander("💼 Custos Indiretos", expanded=False):
        custo_operador_hora = st.number_input("Mão de obra (R$/h)", value=20.00, step=1.0, format="%.2f")
        overhead_pct        = st.number_input("Overhead / fixos (%)", value=15.0, step=1.0, format="%.1f")
        margem_lucro_pct    = st.number_input("Margem de lucro (%)", value=30.0, step=1.0, format="%.1f")

    st.divider()
    st.caption("💡 Esses parâmetros são usados em todos os cálculos. Ajuste conforme seus custos reais.")

# ─────────────────────────────────────────────
# Conteúdo principal – Abas
# ─────────────────────────────────────────────
aba_preco, aba_historico = st.tabs(["📐 Calcular Orçamento", "📋 Histórico de Orçamentos"])

# ══════════════════════════════════════════════
# ABA 1: CALCULAR ORÇAMENTO
# ══════════════════════════════════════════════
with aba_preco:

    col_form, col_resultado = st.columns([1.1, 0.9], gap="large")

    # ──────────────────────────────────────────
    # COLUNA ESQUERDA – Dados do produto
    # ──────────────────────────────────────────
    with col_form:

        # Dados do cliente
        st.markdown('<div class="section-title">👤 Dados do Cliente</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            nome_cliente = st.text_input("Nome / Empresa", placeholder="João Silva")
        with c2:
            contato_cliente = st.text_input("E-mail ou WhatsApp", placeholder="joao@email.com")

        st.divider()

        # Dados do produto
        st.markdown('<div class="section-title">📦 Produto a Imprimir</div>', unsafe_allow_html=True)
        nome_produto  = st.text_input("Nome do produto", placeholder="Ex: Suporte de mesa articulado")
        descricao     = st.text_area("Descrição / observações", height=80, placeholder="Detalhes adicionais...")

        c1, c2, c3 = st.columns(3)
        with c1:
            peso_peca_g  = st.number_input("Peso da peça (g)", value=50.0, step=1.0, format="%.1f")
        with c2:
            tempo_horas  = st.number_input("Tempo de impressão (h)", value=3.0, step=0.5, format="%.1f")
        with c3:
            quantidade   = st.number_input("Quantidade", value=1, step=1, min_value=1)

        st.divider()

        # ── SELEÇÃO DE COR ──────────────────────
        st.markdown('<div class="section-title">🎨 Configuração de Cor</div>', unsafe_allow_html=True)

        modo_cor = st.radio(
            "Modo de impressão",
            options=["Monocor (1 cor)", "Multicolorido (2+ cores)"],
            horizontal=True,
        )

        if "Monocor" in modo_cor:
            st.markdown('<span class="color-badge badge-mono">🖤 Monocor</span>', unsafe_allow_html=True)
            cor_principal = st.selectbox(
                "Cor do filamento",
                ["Preto", "Branco", "Cinza", "Vermelho", "Azul", "Verde", "Amarelo", "Laranja",
                 "Rosa", "Roxo", "Transparente", "Outra"],
            )
            cores_config = [{"cor": cor_principal, "percentual": 100.0}]
            adicional_troca_cor = 0.0

        else:
            st.markdown('<span class="color-badge badge-multi">🌈 Multicolorido</span>', unsafe_allow_html=True)

            num_cores = st.slider("Número de cores", min_value=2, max_value=8, value=2)
            adicional_troca_cor = st.number_input(
                "Custo adicional por troca de cor (R$)",
                value=5.00, step=0.50, format="%.2f",
                help="Tempo de pausa, purga de filamento, etc.",
            )

            st.caption("Distribua a proporção de cada cor (deve somar 100%)")
            cores_config   = []
            lista_cores    = ["Preto", "Branco", "Cinza", "Vermelho", "Azul", "Verde",
                              "Amarelo", "Laranja", "Rosa", "Roxo", "Transparente", "Outra"]
            total_pct      = 0.0
            cols_cores     = st.columns(min(num_cores, 4))

            for i in range(num_cores):
                with cols_cores[i % 4]:
                    cor = st.selectbox(f"Cor {i+1}", lista_cores, key=f"cor_{i}",
                                       index=i % len(lista_cores))
                    pct = st.number_input(f"% Cor {i+1}", min_value=0.0, max_value=100.0,
                                         value=round(100.0 / num_cores, 1), step=1.0,
                                         key=f"pct_{i}", format="%.1f")
                    cores_config.append({"cor": cor, "percentual": pct})
                    total_pct += pct

            # Alerta se percentual não fecha 100%
            if abs(total_pct - 100.0) > 0.5:
                st.warning(f"⚠️ A soma dos percentuais é {total_pct:.1f}%. Ajuste para totalizar 100%.")
            else:
                st.success(f"✅ Distribuição OK — {total_pct:.1f}%")

        st.divider()

        # Acabamento
        st.markdown('<div class="section-title">🔧 Acabamento e Pós-processamento</div>', unsafe_allow_html=True)
        acabamentos = st.multiselect(
            "Selecione os acabamentos desejados",
            ["Lixamento", "Pintura", "Primer", "Montagem", "Embalagem personalizada", "Entrega"],
        )
        custo_acabamento_manual = {
            "Lixamento": 8.0, "Pintura": 15.0, "Primer": 7.0,
            "Montagem": 10.0, "Embalagem personalizada": 12.0, "Entrega": 15.0,
        }
        custo_acabamentos = sum(custo_acabamento_manual[a] for a in acabamentos)

        if acabamentos:
            st.caption(f"Acabamentos selecionados: R$ {custo_acabamentos:.2f}")

        # Desconto
        desconto_pct = st.number_input("Desconto ao cliente (%)", value=0.0, step=1.0,
                                        min_value=0.0, max_value=50.0, format="%.1f")

        calcular = st.button("💰 Calcular Orçamento", use_container_width=True)

    # ──────────────────────────────────────────
    # COLUNA DIREITA – Resultado
    # ──────────────────────────────────────────
    with col_resultado:
        st.markdown("### 💲 Resultado do Orçamento")

        if calcular or st.session_state.get("ultimo_orcamento"):

            # ── CÁLCULO ──────────────────────────
            # Custo do filamento
            peso_total_g         = peso_peca_g * quantidade
            peso_com_desperdicio = peso_total_g * (1 + desperdicio_pct / 100)
            custo_filamento      = (peso_com_desperdicio / 1000) * custo_filamento_kg

            # Custo de energia
            energia_kwh          = (potencia_impressora / 1000) * tempo_horas * quantidade
            custo_energia        = energia_kwh * custo_energia_kwh

            # Custo máquina
            custo_maquina        = custo_hora_maquina * tempo_horas * quantidade

            # Mão de obra (estimativa: 15% do tempo de impressão em monitoramento)
            custo_mao_obra       = custo_operador_hora * tempo_horas * 0.15 * quantidade

            # Custo troca de cor
            trocas = (len(cores_config) - 1) if "Monocor" not in modo_cor else 0
            custo_cor_extra = adicional_troca_cor * trocas * quantidade

            # Subtotal antes do overhead
            subtotal_direto = (custo_filamento + custo_energia + custo_maquina +
                               custo_mao_obra + custo_cor_extra + custo_acabamentos)

            # Overhead
            custo_overhead = subtotal_direto * (overhead_pct / 100)
            custo_total    = subtotal_direto + custo_overhead

            # Margem de lucro
            lucro          = custo_total * (margem_lucro_pct / 100)
            preco_sem_desc = custo_total + lucro

            # Desconto
            valor_desconto = preco_sem_desc * (desconto_pct / 100)
            preco_final    = preco_sem_desc - valor_desconto
            preco_unitario = preco_final / quantidade if quantidade > 0 else 0.0

            # Salva no estado da sessão
            st.session_state["ultimo_orcamento"] = {
                "cliente": nome_cliente, "contato": contato_cliente,
                "produto": nome_produto, "descricao": descricao,
                "peso_g": peso_peca_g, "tempo_h": tempo_horas,
                "quantidade": quantidade, "modo_cor": modo_cor,
                "cores": cores_config, "acabamentos": acabamentos,
                "custo_filamento": custo_filamento, "custo_energia": custo_energia,
                "custo_maquina": custo_maquina, "custo_mao_obra": custo_mao_obra,
                "custo_cor_extra": custo_cor_extra, "custo_acabamentos": custo_acabamentos,
                "custo_overhead": custo_overhead, "custo_total": custo_total,
                "lucro": lucro, "desconto_pct": desconto_pct,
                "valor_desconto": valor_desconto,
                "preco_sem_desc": preco_sem_desc,
                "preco_final": preco_final, "preco_unitario": preco_unitario,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }

            orc = st.session_state["ultimo_orcamento"]

            # ── EXIBIÇÃO ─────────────────────────
            st.markdown(f"""
            <div class="price-box">
                <div class="label">Preço Total</div>
                <div class="value">R$ {orc['preco_final']:,.2f}</div>
                <div style="opacity:0.8; font-size:0.85rem; margin-top:0.4rem">
                    {orc['quantidade']}× peça(s) · R$ {orc['preco_unitario']:,.2f}/un
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Métricas resumidas
            m1, m2, m3 = st.columns(3)
            m1.metric("Custo de produção", f"R$ {orc['custo_total']:.2f}")
            m2.metric("Lucro", f"R$ {orc['lucro']:.2f}")
            m3.metric("Desconto", f"R$ {orc['valor_desconto']:.2f}")

            # Detalhamento de custos
            st.markdown("**📊 Detalhamento de custos**")
            itens_custo = [
                ("🧵 Filamento", orc["custo_filamento"]),
                ("⚡ Energia elétrica", orc["custo_energia"]),
                ("🔩 Hora/máquina", orc["custo_maquina"]),
                ("👷 Mão de obra", orc["custo_mao_obra"]),
                ("🎨 Troca de cores", orc["custo_cor_extra"]),
                ("✂️ Acabamentos", orc["custo_acabamentos"]),
                ("📦 Overhead", orc["custo_overhead"]),
            ]
            detalhe_html = ""
            for label, valor in itens_custo:
                if valor > 0:
                    detalhe_html += f'<div class="cost-row"><span class="cost-label">{label}</span><span class="cost-value">R$ {valor:.2f}</span></div>'

            st.markdown(f'<div class="section-card">{detalhe_html}</div>', unsafe_allow_html=True)

            # Cores usadas
            st.markdown("**🎨 Configuração de cor**")
            badges = ""
            for c in orc["cores"]:
                cls = "badge-mono" if "Monocor" in orc["modo_cor"] else "badge-multi"
                pct_str = f" — {c['percentual']:.0f}%" if "Monocor" not in orc["modo_cor"] else ""
                badges += f'<span class="color-badge {cls}">{c["cor"]}{pct_str}</span>'
            st.markdown(badges, unsafe_allow_html=True)

            st.divider()

            # Botões de ação
            ba1, ba2 = st.columns(2)
            with ba1:
                if st.button("📋 Gerar Orçamento PDF", use_container_width=True):
                    st.session_state["gerar_orcamento"] = True

            with ba2:
                if st.button("💾 Salvar no Histórico", use_container_width=True):
                    if "historico" not in st.session_state:
                        st.session_state["historico"] = []
                    entrada = orc.copy()
                    entrada["id"] = len(st.session_state["historico"]) + 1
                    st.session_state["historico"].append(entrada)
                    st.success("✅ Orçamento salvo no histórico!")

            # Gerar orçamento texto formatado
            if st.session_state.get("gerar_orcamento"):
                st.session_state["gerar_orcamento"] = False
                cores_str = ", ".join(
                    [f"{c['cor']} ({c['percentual']:.0f}%)" if "Monocor" not in orc["modo_cor"]
                     else c["cor"] for c in orc["cores"]]
                )
                orcamento_txt = f"""
╔══════════════════════════════════════════════╗
       ORÇAMENTO DE IMPRESSÃO 3D
       PrintPrice 3D
══════════════════════════════════════════════╝

DATA: {orc['data']}

CLIENTE
  Nome/Empresa : {orc['cliente'] or 'Não informado'}
  Contato      : {orc['contato'] or 'Não informado'}

PRODUTO
  Descrição    : {orc['produto'] or 'Não informado'}
  Obs.         : {orc['descricao'] or '—'}
  Quantidade   : {orc['quantidade']} un.
  Peso unitário: {orc['peso_g']:.1f} g
  Tempo aprox. : {orc['tempo_h']:.1f} h por peça
  Cores        : {orc['modo_cor']} — {cores_str}
  Acabamentos  : {', '.join(orc['acabamentos']) if orc['acabamentos'] else 'Nenhum'}

CUSTOS (total para {orc['quantidade']} peça(s))
  Filamento       : R$ {orc['custo_filamento']:.2f}
  Energia         : R$ {orc['custo_energia']:.2f}
  Hora/máquina    : R$ {orc['custo_maquina']:.2f}
  Mão de obra     : R$ {orc['custo_mao_obra']:.2f}
  Troca de cor    : R$ {orc['custo_cor_extra']:.2f}
  Acabamentos     : R$ {orc['custo_acabamentos']:.2f}
  Overhead ({orc['custo_overhead']/max(orc['custo_total']-orc['custo_overhead'],0.01)*100:.0f}%): R$ {orc['custo_overhead']:.2f}
  ─────────────────────────────────────────
  Custo total     : R$ {orc['custo_total']:.2f}
  Margem de lucro : R$ {orc['lucro']:.2f}
  Desconto        : R$ {orc['valor_desconto']:.2f} ({orc['desconto_pct']:.1f}%)

  ══════════════════════════════════════════
  PREÇO FINAL     : R$ {orc['preco_final']:.2f}
  Preço unitário  : R$ {orc['preco_unitario']:.2f}/un
  ══════════════════════════════════════════

Validade deste orçamento: 15 dias.
Obrigado pela preferência!
"""
                st.download_button(
                    "⬇️ Baixar orçamento (.txt)",
                    data=orcamento_txt.encode("utf-8"),
                    file_name=f"orcamento_{orc['cliente'] or 'cliente'}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

        else:
            st.info("👈 Preencha os dados do produto e clique em **Calcular Orçamento**.")

# ══════════════════════════════════════════════
# ABA 2: HISTÓRICO
# ══════════════════════════════════════════════
with aba_historico:
    st.markdown("### 📋 Histórico de Orçamentos")

    if "historico" not in st.session_state or not st.session_state["historico"]:
        st.info("Nenhum orçamento salvo ainda. Calcule e salve orçamentos na aba anterior.")
    else:
        historico = st.session_state["historico"]

        # Tabela resumida
        df_hist = pd.DataFrame([{
            "Nº": h["id"],
            "Data": h["data"],
            "Cliente": h["cliente"] or "—",
            "Produto": h["produto"] or "—",
            "Qtd": h["quantidade"],
            "Modo": "Multicolorido" if "Multi" in h["modo_cor"] else "Monocor",
            "Preço Total (R$)": f"{h['preco_final']:.2f}",
            "Unitário (R$)": f"{h['preco_unitario']:.2f}",
        } for h in historico])

        st.dataframe(df_hist, use_container_width=True, hide_index=True)

        # Estatísticas
        st.divider()
        st.markdown("**📈 Resumo**")
        valores = [h["preco_final"] for h in historico]
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Total de orçamentos", len(historico))
        s2.metric("Faturamento total", f"R$ {sum(valores):,.2f}")
        s3.metric("Ticket médio", f"R$ {sum(valores)/len(valores):,.2f}")
        s4.metric("Maior orçamento", f"R$ {max(valores):,.2f}")

        # Exportar histórico
        csv_data = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Exportar histórico (.csv)",
            data=csv_data,
            file_name=f"historico_orcamentos_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
        if st.button("🗑️ Limpar histórico"):
            st.session_state["historico"] = []
            st.rerun()
