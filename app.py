"""
Simulateur Impot sur le Revenu 2026 — Dark theme
Mode : Foyer familial | Comparaison enfant majeur
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
from calcul_impot import MoteurImpot, ScenarioEnfantMajeur, FraisReels
from rapport_pdf import GenererRapportPDF
from dirigeant import MoteurDirigeant

st.set_page_config(
    page_title="Simulateur IR 2026",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CSS dark ─────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp,[data-testid="stAppViewContainer"]{background:#0f172a !important;color:#e2e8f0}
[data-testid="stHeader"]{background:#0f172a !important}
section[data-testid="stSidebar"]{background:#1e293b !important}
.stSelectbox>div>div,.stNumberInput>div>div>input,
.stTextInput>div>div>input,.stTextArea textarea
  {background:#1e293b !important;color:#e2e8f0 !important;border-color:#334155 !important}
.stCheckbox label,.stRadio label{color:#e2e8f0 !important}
.stRadio>div>label>div{color:#e2e8f0 !important}
div[data-testid="stTabs"] [data-baseweb="tab-list"]
  {background:#1e293b;border-radius:10px;padding:.3rem;gap:.2rem}
div[data-testid="stTabs"] [data-baseweb="tab"]
  {color:#94a3b8;border-radius:8px;padding:.4rem 1.1rem;font-weight:500}
div[data-testid="stTabs"] [aria-selected="true"]
  {background:#1d4ed8 !important;color:white !important}
.stButton>button{background:#1d4ed8;color:white;border:none;
  border-radius:8px;font-weight:600;padding:.55rem 1.4rem}
.stButton>button:hover{background:#2563eb}
[data-testid="stMetric"]{background:#1e293b;border-radius:8px;padding:.7rem 1rem}
[data-testid="stMetricLabel"]{color:#94a3b8}
[data-testid="stMetricValue"]{color:#e2e8f0}
.streamlit-expanderHeader{background:#1e293b !important;color:#e2e8f0 !important;border-radius:8px}
.streamlit-expanderContent{background:#1e293b !important}
.stAlert{background:#1e293b !important;border-color:#334155 !important}
.stDataFrame{background:#1e293b}
/* Custom components */
.card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:1.2rem;margin-bottom:.8rem}
.card h4{color:#93c5fd;margin:0 0 .6rem 0;font-size:1rem}
.kpi{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:1rem;text-align:center}
.kpi-val{font-size:1.6rem;font-weight:700}
.kpi-lbl{font-size:.72rem;color:#94a3b8;margin-top:.2rem}
.verdict-a{background:#1e3a5f;border-left:4px solid #3b82f6;border-radius:0 8px 8px 0;padding:1rem;margin:.7rem 0}
.verdict-b{background:#14532d;border-left:4px solid #22c55e;border-radius:0 8px 8px 0;padding:1rem;margin:.7rem 0}
.conseil{background:#1c1a09;border:1px solid #854d0e;border-radius:8px;padding:.8rem 1rem;margin:.35rem 0;color:#fef9c3}
.src{background:#1e293b;border-radius:6px;padding:.4rem .8rem;font-size:.74rem;color:#64748b;margin:.4rem 0}
.tns-card{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:1rem;height:100%}
.tns-card h5{color:#34d399;margin:0 0 .4rem 0;font-size:.9rem}
.mode-badge{display:inline-block;padding:.3rem .9rem;border-radius:20px;font-weight:600;font-size:.85rem}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:linear-gradient(135deg,#003189 0%,#1d4ed8 55%,#ed2939 100%);
  padding:1.4rem 2rem;border-radius:14px;color:white;text-align:center;
  margin-bottom:1.2rem;box-shadow:0 4px 20px rgba(29,78,216,.4)">
  <h1 style="margin:0;font-size:1.85rem;font-weight:700">Simulateur Impot sur le Revenu 2026</h1>
  <p style="margin:.3rem 0 0;opacity:.9;font-size:.9rem">
    Declaration 2026 &bull; Revenus 2025 &bull; Bareme officiel DGFiP (Brochure Pratique 2025)</p>
</div>
""", unsafe_allow_html=True)

moteur   = MoteurImpot()
dirigeant_m = MoteurDirigeant()


def fr(val, dec=0):
    if val is None: return "-"
    if dec == 0:
        s = f"{abs(val):,.0f}".replace(",", "\u202f")
    else:
        s = f"{abs(val):,.{dec}f}"
        p = s.split(".")
        s = p[0].replace(",", "\u202f") + "," + p[1]
    return ("-\u202f" if val < 0 else "") + s


def kpi(label, val, color="#93c5fd"):
    return f'<div class="kpi"><div class="kpi-val" style="color:{color}">{val}</div><div class="kpi-lbl">{label}</div></div>'


def saisie_frais_reels(prefix, salaire):
    mode = st.radio("Mode deduction", ["Forfait 10 % (auto)", "Frais reels justifies"],
                    key=f"mode_{prefix}", horizontal=True)
    if "Forfait" in mode:
        f10 = max(moteur.ABATTEMENT_SALAIRES_MIN, min(salaire * .10, moteur.ABATTEMENT_SALAIRES_MAX))
        st.caption(f"Abattement forfaitaire : **{fr(f10)} EUR** — cases 1AK/1BK non renseignees")
        return False, 0
    c1, c2 = st.columns(2)
    with c1:
        tveh = st.selectbox("Vehicule",
            ["thermique","electrique","moto","moto_electrique","cyclo"],
            format_func=lambda x:{"thermique":"Voiture thermique/hybride",
                "electrique":"Voiture electrique","moto":"Moto thermique",
                "moto_electrique":"Moto electrique","cyclo":"Cyclomoteur"}[x],
            key=f"tveh_{prefix}")
        cv = 5
        if tveh in ("thermique","electrique"):
            cv = st.select_slider("CV fiscaux",[3,4,5,6,7],5,key=f"cv_{prefix}")
        elif "moto" in tveh:
            cv = st.selectbox("Cylindree",[2,5,99],
                format_func=lambda x:{2:"1-2 CV",5:"3-5 CV",99:"> 5 CV"}[x],
                key=f"cvm_{prefix}")
        km = st.number_input("Km pro / an",0,100000,0,500,key=f"km_{prefix}")
        fkm = FraisReels.calculer_bareme_km(km,cv,tveh) if km else 0
        if km: st.info(f"Bareme km : **{fr(fkm)} EUR**")
    with c2:
        nbr = st.number_input("Repas pro / an",0,300,0,key=f"rep_{prefix}")
        pxr = st.number_input("Prix moyen repas EUR",0.0,50.0,10.0,.5,key=f"px_{prefix}")
        frep = max(0,(pxr - FraisReels.REPAS_VALEUR_FOYER)*nbr) if nbr else 0
        if nbr: st.info(f"Frais repas : **{fr(frep)} EUR**")
        jtt = st.number_input("Jours teletravail",0,230,0,key=f"tt_{prefix}")
        ftt = FraisReels.calculer_teletravail(jtt) if jtt else 0
        if jtt: st.info(f"Teletravail : **{fr(ftt)} EUR**")
    dr = st.number_input("Double residence EUR",0,30000,0,200,key=f"dr_{prefix}")
    fo = st.number_input("Formation pro EUR",0,20000,0,100,key=f"fo_{prefix}")
    ma = st.number_input("Materiel EUR",0,20000,0,100,key=f"ma_{prefix}")
    au = st.number_input("Autres EUR",0,20000,0,100,key=f"au_{prefix}")
    total = round(fkm+frep+ftt+dr+fo+ma+au)
    f10 = max(moteur.ABATTEMENT_SALAIRES_MIN, min(salaire*.10, moteur.ABATTEMENT_SALAIRES_MAX))
    if total > 0:
        if total > f10:
            st.success(f"Frais reels ({fr(total)} EUR) > forfait ({fr(f10)} EUR) => +{fr(total-f10)} EUR")
            return True, total
        else:
            st.warning(f"Frais reels ({fr(total)} EUR) < forfait ({fr(f10)} EUR). Forfait conseille.")
            return False, 0
    return False, 0


# ══════════════════════════════════════════════════════════════════════
# CHOIX DU MODE — en haut, avant les onglets
# ══════════════════════════════════════════════════════════════════════
st.markdown("### Que souhaitez-vous simuler ?")
mode = st.radio(
    "",
    ["Simulation du foyer familial",
     "Comparaison avec un enfant majeur (rattachement vs foyer independant)",
     "Revenus de dirigeant / Revenus professionnels complexes"],
    key="mode_global", horizontal=False,
    help="Choisissez votre simulation. Vous pourrez remplir toutes les informations dans les onglets correspondants."
)
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# ONGLETS
# ══════════════════════════════════════════════════════════════════════
if mode == "Revenus de dirigeant / Revenus professionnels complexes":
    # ── DIRIGEANT uniquement ──────────────────────────────────────────
    tab_dir, tab_dir_pdf = st.tabs(["🏢  Revenus Dirigeant & TNS", "📄  Rapport Dirigeant PDF"])

    with tab_dir:
        st.markdown("### Revenus de dirigeant — Simulation et optimisation")

        c_haut1, c_haut2 = st.columns([1, 2])
        with c_haut1:
            st.markdown("#### Parametres generaux")
            tmi_dir = st.select_slider(
                "TMI (taux marginal d'imposition)",
                [0, 11, 30, 41, 45], 30, key="tmi_dir")
            statut_dir = st.selectbox(
                "Statut social",
                list(dirigeant_m.TNS_COTISATIONS.keys()),
                format_func=lambda x: dirigeant_m.TNS_COTISATIONS[x]['label'],
                key="statut_dir")

        with c_haut2:
            st.markdown("#### Comparaison des statuts sociaux")
            remun_comp = st.number_input(
                "Remuneration de reference pour comparaison EUR",
                0, 500000, 80000, 5000, key="remun_comp")
            if remun_comp > 0:
                comparatif = dirigeant_m.comparer_statuts(remun_comp, tmi_dir)
                rows_c = []
                for r in comparatif:
                    rows_c.append({
                        "Statut": r['label'],
                        "Charges (%)": f"{r['taux_charges']} %",
                        "Cotisations": f"{fr(r['cotisations'])} EUR",
                        "IR estime": f"{fr(r['ir_estime'])} EUR",
                        "Net final": f"{fr(r['net_final'])} EUR",
                    })
                df_c = pd.DataFrame(rows_c)
                st.dataframe(df_c, hide_index=True, use_container_width=True)

        st.markdown("---")

        # ─ Sous-onglets dirigeant ─────────────────────────────────────
        dt1, dt2, dt3, dt4, dt5 = st.tabs([
            "👤 TNS & Statut social",
            "🏦 IS & Dividendes",
            "🛒 BIC / BNC",
            "🏠 Immobilier",
            "🎯 Strategie globale"
        ])

        # ── TNS ──────────────────────────────────────────────────────
        with dt1:
            st.markdown("#### Traitement & Salaires — Remuneration de dirigeant")
            t1a, t1b = st.columns(2)
            with t1a:
                rem_ts = st.number_input("Remuneration brute EUR", 0, 500000, 60000, 1000, key="rem_ts")
                fr_ts  = st.checkbox("Frais reels justifies", key="fr_ts")
                mfr_ts = st.number_input("Montant frais reels EUR", 0, 30000, 0, 500,
                                         key="mfr_ts") if fr_ts else 0
            with t1b:
                if rem_ts:
                    from calcul_impot import MoteurImpot as _M
                    _m = _M()
                    ab_ts = mfr_ts if fr_ts and mfr_ts else max(_m.ABATTEMENT_SALAIRES_MIN,
                        min(rem_ts*.10, _m.ABATTEMENT_SALAIRES_MAX))
                    imp_ts = max(0, rem_ts - ab_ts)
                    ir_ts  = imp_ts * tmi_dir / 100
                    st.markdown(f"""<div class="card">
                    <h4>Traitement & Salaires (cat. TS)</h4>
                    Remuneration brute : <b>{fr(rem_ts)} EUR</b><br>
                    Abattement ({'frais reels' if fr_ts else 'forfait 10 %'}) : <b>-{fr(ab_ts)} EUR</b><br>
                    Imposable (case 1AJ) : <b>{fr(imp_ts)} EUR</b><br>
                    IR estime (TMI {tmi_dir} %) : <b>{fr(ir_ts)} EUR</b><br>
                    <i style="color:#64748b">Deductible IS si SARL/SAS</i>
                    </div>""", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### Cotisations sociales selon le statut")
            if rem_ts > 0:
                cot_data = dirigeant_m.calculer_cotisations_tns(rem_ts, statut_dir)
                c_t1, c_t2, c_t3 = st.columns(3)
                with c_t1:
                    st.markdown(f"""<div class="card">
                    <h4>Charges sociales</h4>
                    Statut : <b style="color:#34d399">{cot_data['statut']}</b><br>
                    Remuneration : <b>{fr(rem_ts)} EUR</b><br>
                    Taux global : <b>{int(cot_data['taux_global']*100)} %</b><br>
                    Cotisations : <b style="color:#f87171">{fr(cot_data['cotisations'])} EUR</b><br>
                    Net avant IR : <b style="color:#4ade80">{fr(cot_data['net_avant_ir'])} EUR</b>
                    </div>""", unsafe_allow_html=True)
                with c_t2:
                    detail_html = "".join(
                        f"<tr><td style='color:#94a3b8;padding:.15rem .5rem'>{k}</td>"
                        f"<td style='padding:.15rem .5rem'><b>{v}</b></td></tr>"
                        for k, v in cot_data['detail'].items())
                    st.markdown(f"""<div class="card">
                    <h4>Detail des cotisations</h4>
                    <table style="width:100%;font-size:.85rem">{detail_html}</table>
                    </div>""", unsafe_allow_html=True)
                with c_t3:
                    avt_html = "".join(f"<li style='color:#4ade80;font-size:.82rem'>{a}</li>"
                                       for a in cot_data['avantages'])
                    inc_html = "".join(f"<li style='color:#f87171;font-size:.82rem'>{i}</li>"
                                       for i in cot_data['inconvenients'])
                    st.markdown(f"""<div class="card">
                    <h4>Points cles</h4>
                    <b style="color:#4ade80">Avantages</b>
                    <ul style="margin:.3rem 0 .6rem 1rem">{avt_html}</ul>
                    <b style="color:#f87171">Points de vigilance</b>
                    <ul style="margin:.3rem 0 0 1rem">{inc_html}</ul>
                    </div>""", unsafe_allow_html=True)

                # Graphique comparatif charges
                statuts_g = [r['label'].split('(')[0].strip() for r in dirigeant_m.comparer_statuts(rem_ts, tmi_dir)]
                cotis_g   = [r['cotisations'] for r in dirigeant_m.comparer_statuts(rem_ts, tmi_dir)]
                net_g     = [r['net_final']   for r in dirigeant_m.comparer_statuts(rem_ts, tmi_dir)]
                fig_t = go.Figure([
                    go.Bar(name="Cotisations", x=statuts_g, y=cotis_g,
                           marker_color="#f87171",
                           text=[f"{fr(v)} EUR" for v in cotis_g], textposition='outside',
                           textfont=dict(color='#e2e8f0')),
                    go.Bar(name="Net final apres IR", x=statuts_g, y=net_g,
                           marker_color="#4ade80",
                           text=[f"{fr(v)} EUR" for v in net_g], textposition='outside',
                           textfont=dict(color='#e2e8f0')),
                ])
                fig_t.update_layout(barmode='group', title="Comparaison statuts sociaux",
                    height=320, plot_bgcolor='#1e293b', paper_bgcolor='#1e293b',
                    font=dict(color='#e2e8f0'), xaxis_tickfont=dict(size=9))
                fig_t.update_yaxes(gridcolor='#334155')
                st.plotly_chart(fig_t, use_container_width=True)

        # ── IS & Dividendes ──────────────────────────────────────────
        with dt2:
            st.markdown("#### Impot sur les Societes & Dividendes")
            i2a, i2b = st.columns(2)
            with i2a:
                st.markdown("**Calcul IS**")
                res_fisc = st.number_input("Resultat fiscal EUR", -500000, 5000000, 80000, 1000, key="res_fisc")
                st.caption("Taux reduit 15 % <= 42 500 EUR | Taux normal 25 % au-dela")
                if res_fisc > 0:
                    is_data = dirigeant_m.calculer_is(res_fisc)
                    st.markdown(f"""<div class="card">
                    <h4>Calcul IS 2024</h4>
                    Base taux reduit 15 % : <b>{fr(is_data['base_reduit'])} EUR</b> => IS : <b>{fr(is_data['is_reduit'])} EUR</b><br>
                    Base taux normal 25 % : <b>{fr(is_data['base_normal'])} EUR</b> => IS : <b>{fr(is_data['is_normal'])} EUR</b><br>
                    <b style="color:#f87171">IS total : {fr(is_data['is_total'])} EUR</b><br>
                    Taux effectif : <b>{is_data['taux_effectif']:.2f} %</b><br>
                    <b style="color:#4ade80">Benefice net disponible : {fr(is_data['benefice_net'])} EUR</b>
                    </div>""", unsafe_allow_html=True)
            with i2b:
                st.markdown("**Dividendes**")
                div_bruts = st.number_input("Dividendes bruts EUR", 0, 2000000, 50000, 1000, key="div_bruts")
                if div_bruts > 0:
                    d_data = dirigeant_m.calculer_dividendes(div_bruts, tmi_dir)
                    pfu = d_data['pfu']
                    bar = d_data['bareme']
                    meill_d = d_data['meilleur']
                    for opt_lbl, opt, color in [
                        ("PFU - Flat Tax 30 %", pfu, "#60a5fa" if meill_d=="PFU" else "#475569"),
                        (f"Option bareme {tmi_dir} % + abatt. 40 %", bar, "#4ade80" if meill_d=="Bareme" else "#475569")
                    ]:
                        best = "🏆 " if (meill_d=="PFU" and "PFU" in opt_lbl) or (meill_d=="Bareme" and "bareme" in opt_lbl) else ""
                        ir_v = opt.get('ir', 0)
                        ps_v = opt.get('ps', 0)
                        st.markdown(f"""<div class="card" style="border-color:{color}">
                        <h4 style="color:{color}">{best}{opt_lbl}</h4>
                        IR : <b>{fr(ir_v)} EUR</b> | PS 17,2 % : <b>{fr(ps_v)} EUR</b><br>
                        Total prelevements : <b>{fr(opt['total_imposition'])} EUR</b><br>
                        Net percu : <b style="color:{color}">{fr(opt['net_percu'])} EUR</b>
                        </div>""", unsafe_allow_html=True)
                    st.success(f"Recommandation : **{meill_d}** — economie : {fr(d_data['economie'])} EUR")

        # ── BIC / BNC ────────────────────────────────────────────────
        with dt3:
            st.markdown("#### BIC / BNC — Regimes micro et reel")
            regime_type = st.selectbox("Type d'activite", [
                "BIC micro — ventes/commerce",
                "BIC micro — services/prestations",
                "BIC reel simplifie (declaration 2031)",
                "BNC micro — liberale",
                "BNC reel — declaration controlee (2035)",
            ], key="regime_type")

            b1, b2 = st.columns(2)
            with b1:
                if "micro" in regime_type:
                    ca_b = st.number_input("Chiffre d'affaires / Recettes EUR",
                        0, 2000000, 60000, 1000, key="ca_b")
                else:
                    ca_b = st.number_input("CA / Recettes EUR", 0, 5000000, 150000, 1000, key="ca_b")
                    ch_b = st.number_input("Charges deductibles EUR", 0, 5000000, 90000, 1000, key="ch_b")
                    am_b = st.number_input("Amortissements EUR", 0, 500000, 0, 1000, key="am_b") if "BIC" in regime_type else 0

            with b2:
                if "ventes" in regime_type:
                    r_b = dirigeant_m.calculer_bic_micro(ca_b, 'vente')
                elif "services" in regime_type and "BIC" in regime_type:
                    r_b = dirigeant_m.calculer_bic_micro(ca_b, 'services')
                elif "BIC reel" in regime_type:
                    r_b = dirigeant_m.calculer_bic_reel(ca_b, ch_b, am_b)
                elif "BNC micro" in regime_type:
                    r_b = dirigeant_m.calculer_bnc_micro(ca_b)
                else:
                    r_b = dirigeant_m.calculer_bnc_reel(ca_b, ch_b)

                imposable = r_b.get('benefice_imposable', r_b.get('imposable', 0))
                deficit   = r_b.get('deficit', 0)
                col_v     = "#4ade80" if imposable >= 0 else "#f87171"
                abatt_info = ""
                if 'abattement_pct' in r_b:
                    abatt_info = f"Abattement {r_b['abattement_pct']} % : -{fr(r_b.get('abattement_montant',0))} EUR<br>"
                elif 'charges' in r_b:
                    abatt_info = f"Charges : -{fr(r_b['charges'])} EUR<br>"

                seuil_info = ""
                if 'eligible' in r_b:
                    ok = "OK" if r_b['eligible'] else "Depasse - regime reel obligatoire"
                    seuil_info = f"Seuil micro : {fr(r_b.get('seuil_regime', r_b.get('seuil', 0)))} EUR — {ok}<br>"

                ir_est = int(imposable * tmi_dir / 100)
                st.markdown(f"""<div class="card">
                <h4>{r_b.get('type', regime_type)}</h4>
                CA / Recettes : <b>{fr(ca_b)} EUR</b><br>
                {abatt_info}
                <b style="color:{col_v}">Benefice imposable : {fr(imposable)} EUR</b><br>
                {"Deficit : <b>" + fr(deficit) + " EUR</b><br>" if deficit else ""}
                {seuil_info}
                IR estime (TMI {tmi_dir} %) : <b>{fr(ir_est)} EUR</b><br>
                Cotisations TNS ({int(dirigeant_m.TNS_COTISATIONS.get(statut_dir,{}).get('taux_global',0.43)*100)} %) : <b>{fr(int(imposable * dirigeant_m.TNS_COTISATIONS.get(statut_dir,{'taux_global':.43})['taux_global']))} EUR</b>
                </div>""", unsafe_allow_html=True)

        # ── Immobilier ───────────────────────────────────────────────
        with dt4:
            st.markdown("#### Revenus immobiliers — Foncier, LMNP, LMP, SCI")
            immo_type = st.selectbox("Type de revenu", [
                "Micro-foncier (abattement 30 %)",
                "Revenus fonciers reels (declaration 2044)",
                "LMNP — Micro-BIC",
                "LMNP — Regime reel",
                "LMP — Location Meublee Professionnelle",
                "SCI a l'IR (transparent)",
                "SCI a l'IS",
            ], key="immo_type")

            im1, im2 = st.columns(2)
            with im1:
                if "Micro-foncier" in immo_type:
                    rfb = st.number_input("Revenus fonciers bruts EUR", 0, 500000, 10000, 500, key="rfb")
                elif "reels" in immo_type:
                    rfb = st.number_input("Revenus bruts EUR", 0, 1000000, 20000, 500, key="rfb")
                    int_e = st.number_input("Interets emprunt EUR", 0, 200000, 5000, 200, key="int_e")
                    ch_fon = st.number_input("Charges courantes EUR", 0, 100000, 2000, 100, key="ch_fon")
                    trav = st.number_input("Travaux EUR", 0, 500000, 0, 500, key="trav")
                    tf_fon = st.number_input("Taxe fonciere EUR", 0, 20000, 1000, 100, key="tf_fon")
                    fg_fon = st.number_input("Frais gestion EUR", 0, 20000, 500, 100, key="fg_fon")
                elif "LMNP" in immo_type:
                    rfb = st.number_input("Recettes LMNP EUR", 0, 500000, 18000, 500, key="rfb")
                    lmnp_cl = st.checkbox("Bien classe (tourisme classe)", key="lmnp_cl") if "Micro" in immo_type else False
                    if "reel" in immo_type:
                        ch_lmnp = st.number_input("Charges EUR", 0, 200000, 6000, 500, key="ch_lmnp")
                        am_lmnp = st.number_input("Amortissements EUR", 0, 200000, 5000, 500, key="am_lmnp")
                elif "LMP" in immo_type:
                    rfb = st.number_input("Recettes LMP EUR", 0, 1000000, 35000, 1000, key="rfb")
                    ch_lmp = st.number_input("Charges EUR", 0, 500000, 10000, 500, key="ch_lmp")
                    am_lmp = st.number_input("Amortissements EUR", 0, 300000, 8000, 500, key="am_lmp")
                    aut_rev = st.number_input("Autres revenus pro foyer EUR", 0, 500000, 45000, 1000, key="aut_rev")
                elif "SCI a l'IR" in immo_type:
                    rfb = st.number_input("Quote-part resultat SCI EUR", -100000, 500000, 5000, 500, key="rfb")
                else:  # SCI IS
                    rfb = st.number_input("Resultat fiscal SCI EUR", 0, 5000000, 60000, 1000, key="rfb")
                    sci_qp = st.slider("Votre quote-part (%)", 1, 100, 100, 1, key="sci_qp") / 100

            with im2:
                if "Micro-foncier" in immo_type:
                    r_im = dirigeant_m.calculer_foncier_micro(rfb)
                    st.markdown(f"""<div class="card">
                    <h4>Micro-foncier (abattement 30 %)</h4>
                    Revenus bruts : {fr(rfb)} EUR<br>
                    Abattement 30 % : -{fr(r_im['abattement_montant'])} EUR<br>
                    <b>Imposable : {fr(r_im['imposable'])} EUR</b><br>
                    IR estime (TMI {tmi_dir} %) : <b>{fr(int(r_im['imposable']*tmi_dir/100))} EUR</b><br>
                    PS 17,2 % : <b>{fr(int(r_im['imposable']*.172))} EUR</b><br>
                    {"OK Eligible" if r_im['eligible'] else "Depasse seuil " + fr(r_im['seuil']) + " EUR"}
                    </div>""", unsafe_allow_html=True)

                elif "reels" in immo_type:
                    r_im = dirigeant_m.calculer_foncier_reel(rfb, int_e, ch_fon, trav, tf_fon, fg_fon)
                    col_f = "#4ade80" if r_im['resultat'] >= 0 else "#f87171"
                    def_html = ""
                    if r_im['deficit_total'] > 0:
                        def_html = (f"Deficit total : <b>{fr(r_im['deficit_total'])} EUR</b><br>"
                                    f"Imputable sur RNG (plafond 10 700 EUR) : <b>{fr(r_im['deficit_imputable_rng'])} EUR</b><br>"
                                    f"Reportable foncier 10 ans : <b>{fr(r_im['deficit_report_foncier'])} EUR</b><br>")
                    st.markdown(f"""<div class="card">
                    <h4>Foncier reel (declaration 2044)</h4>
                    Revenus bruts : {fr(rfb)} EUR — Charges totales : {fr(r_im['total_charges'])} EUR<br>
                    <b style="color:{col_f}">Resultat : {fr(r_im['resultat'])} EUR</b><br>
                    {def_html}
                    IR estime sur benefice : <b>{fr(int(r_im['imposable']*tmi_dir/100))} EUR</b>
                    </div>""", unsafe_allow_html=True)

                elif "LMNP" in immo_type:
                    if "Micro" in immo_type:
                        r_im = dirigeant_m.calculer_lmnp(rfb, lmnp_cl, 'micro')
                        st.markdown(f"""<div class="card">
                        <h4>LMNP Micro-BIC — {r_im['type_bien']}</h4>
                        Recettes : {fr(rfb)} EUR<br>
                        Abattement {r_im['abattement_pct']} % : -{fr(rfb - r_im['imposable'])} EUR<br>
                        <b>Imposable : {fr(r_im['imposable'])} EUR</b><br>
                        IR estime : <b>{fr(int(r_im['imposable']*tmi_dir/100))} EUR</b><br>
                        PS 17,2 % : <b>{fr(r_im['ps'])} EUR</b><br>
                        {"OK Eligible" if r_im['eligible'] else "Depasse seuil " + fr(r_im['seuil']) + " EUR"}
                        </div>""", unsafe_allow_html=True)
                    else:
                        r_im = dirigeant_m.calculer_lmnp(rfb, False, 'reel', ch_lmnp, am_lmnp)
                        col_lr = "#4ade80" if r_im['benefice'] >= 0 else "#f87171"
                        def_lr = f"Deficit reportable 10 ans : <b>{fr(r_im['deficit'])} EUR</b><br>" if r_im['deficit'] else ""
                        st.markdown(f"""<div class="card">
                        <h4>LMNP Reel</h4>
                        Recettes : {fr(rfb)} — Charges : {fr(ch_lmnp)} — Amort. : {fr(am_lmnp)} EUR<br>
                        <b style="color:{col_lr}">Benefice imposable : {fr(r_im['imposable'])} EUR</b><br>
                        {def_lr}
                        IR estime : <b>{fr(int(r_im['imposable']*tmi_dir/100))} EUR</b>
                        </div>""", unsafe_allow_html=True)

                elif "LMP" in immo_type:
                    r_im = dirigeant_m.calculer_lmp(rfb, ch_lmp, am_lmp, aut_rev)
                    col_lp = "#4ade80" if r_im['benefice'] >= 0 else "#f87171"
                    avts = "".join(f"<li style='font-size:.82rem'>{a}</li>" for a in r_im['avantages'])
                    st.markdown(f"""<div class="card">
                    <h4>LMP — Location Meublee Professionnelle</h4>
                    Statut LMP : <b style="color:{'#4ade80' if r_im['statut_lmp'] else '#f87171'}">{'Atteint' if r_im['statut_lmp'] else 'Non atteint'}</b><br>
                    <b style="color:{col_lp}">Benefice : {fr(r_im['imposable'])} EUR</b><br>
                    {"Deficit imputable sans limite : <b>" + fr(r_im['deficit']) + " EUR</b><br>" if r_im['deficit'] and r_im['statut_lmp'] else ""}
                    <ul style="margin:.4rem 0 0 1rem;color:#94a3b8">{avts}</ul>
                    </div>""", unsafe_allow_html=True)

                elif "SCI a l'IR" in immo_type:
                    r_im = dirigeant_m.calculer_sci_ir(rfb)
                    col_s = "#4ade80" if rfb >= 0 else "#f87171"
                    def_s = ""
                    if r_im['deficit']:
                        def_s = (f"Deficit imputable RNG : <b>{fr(r_im['deficit_imputable_rng'])} EUR</b>"
                                 f" (plafond 10 700 EUR)<br>")
                    st.markdown(f"""<div class="card">
                    <h4>SCI a l'IR — Transparent fiscalement</h4>
                    Quote-part resultat : <b style="color:{col_s}">{fr(rfb)} EUR</b><br>
                    {def_s}
                    Imposable (revenus fonciers) : <b>{fr(r_im['imposable'])} EUR</b><br>
                    IR estime (TMI {tmi_dir} %) : <b>{fr(int(r_im['imposable']*tmi_dir/100))} EUR</b><br>
                    PS 17,2 % : <b>{fr(r_im['ps'])} EUR</b><br>
                    <i style="color:#64748b">{r_im['note']}</i>
                    </div>""", unsafe_allow_html=True)

                else:  # SCI IS
                    r_im = dirigeant_m.calculer_sci_is(rfb, sci_qp)
                    st.markdown(f"""<div class="card">
                    <h4>SCI a l'IS</h4>
                    Resultat fiscal : {fr(rfb)} EUR<br>
                    IS : <b style="color:#f87171">{fr(r_im['is_total'])} EUR</b>
                    (taux effectif : {r_im['taux_effectif']:.2f} %)<br>
                    Benefice net : <b>{fr(r_im['benefice_net'])} EUR</b><br>
                    Dividende potentiel (quote-part {int(sci_qp*100)} %) : <b>{fr(r_im['dividende_potentiel'])} EUR</b><br>
                    <i style="color:#64748b">{r_im['note']}</i>
                    </div>""", unsafe_allow_html=True)
                    if r_im['dividende_potentiel'] > 0:
                        dv2 = dirigeant_m.calculer_dividendes(r_im['dividende_potentiel'], tmi_dir)
                        st.info(f"Si distribues => PFU : **{fr(dv2['pfu']['total_imposition'])} EUR** | "
                                f"Bareme : **{fr(dv2['bareme']['total_imposition'])} EUR** "
                                f"=> **{dv2['meilleur']}** conseille")

        # ── Strategie globale ────────────────────────────────────────
        with dt5:
            st.markdown("#### Optimisation : Remuneration vs Dividendes")
            sg1, sg2 = st.columns(2)
            with sg1:
                ben_avo = st.number_input("Benefice avant IS et remuneration EUR",
                    0, 5000000, 120000, 5000, key="ben_avo")
                rem_sg = st.number_input("Remuneration (strategie remuneration) EUR",
                    0, 500000, 70000, 5000, key="rem_sg")
            with sg2:
                if ben_avo > 0:
                    r_sg = dirigeant_m.simuler_remuneration_vs_dividendes(ben_avo, rem_sg, tmi_dir)
                    sa = r_sg['strategie_a']
                    sb = r_sg['strategie_b']
                    meill_sg = r_sg['meilleure']
                    col_a = "#60a5fa" if meill_sg == "A" else "#475569"
                    col_b = "#4ade80" if meill_sg == "B" else "#475569"
                    st.markdown(f"""<div class="card" style="border-color:{col_a}">
                    <h4 style="color:{col_a}">{'🏆 ' if meill_sg=='A' else ''}A — Tout en remuneration</h4>
                    IS societe : {fr(sa['is_societe'])} EUR<br>
                    IR personnel : {fr(sa['ir_personnel'])} EUR<br>
                    <b>Cout total : {fr(sa['cout_total'])} EUR | Net percu : {fr(sa['net_percu'])} EUR</b>
                    </div>""", unsafe_allow_html=True)
                    st.markdown(f"""<div class="card" style="border-color:{col_b}">
                    <h4 style="color:{col_b}">{'🏆 ' if meill_sg=='B' else ''}B — Dividendes PFU 30 %</h4>
                    IS societe : {fr(sb['is_societe'])} EUR<br>
                    PFU dividendes : {fr(sb['pfu'])} EUR<br>
                    <b>Cout total : {fr(sb['cout_total'])} EUR | Net percu : {fr(sb['net_percu'])} EUR</b>
                    </div>""", unsafe_allow_html=True)
                    st.success(f"Recommandation : Strategie **{meill_sg}** — economie : **{fr(r_sg['economie'])} EUR**")

            st.markdown("""<div class="src">
            Sources : BOI-BIC, BOI-BNC, BOI-RFPI, BOI-RPPM | Art. 219, 200A, 32, 50-0, 102ter CGI | Calculs indicatifs — Consultez un expert-comptable.
            </div>""", unsafe_allow_html=True)

    # ── PDF Dirigeant ─────────────────────────────────────────────────
    with tab_dir_pdf:
        st.markdown("### Rapport PDF — Revenus de dirigeant")
        st.info("Le rapport PDF pour les revenus de dirigeant sera genere a partir des parametres saisis dans l'onglet precedent.")
        st.markdown("""
        Le rapport comprendra :
        - Synthese du statut social et comparaison des charges
        - Calcul IS et strategie dividendes
        - BIC / BNC / Revenus immobiliers
        - Recommandations personnalisees
        """)
        if st.button("Generer le rapport dirigeant PDF", type="primary"):
            st.info("Fonctionnalite en cours de developpement. Utilisez l'onglet IRPP pour le rapport PDF complet.")

else:
    # ══════════════════════════════════════════════════════════════════
    # MODE IRPP — Foyer seul OU Comparaison enfant majeur
    # ══════════════════════════════════════════════════════════════════
    comp_mode = (mode == "Comparaison avec un enfant majeur (rattachement vs foyer independant)")

    if comp_mode:
        st.markdown("""<div class="mode-badge" style="background:#1e3a5f;color:#93c5fd">
        Mode actif : Comparaison enfant majeur — Rattachement vs Foyer independant
        </div>""", unsafe_allow_html=True)
        tabs_irpp = st.tabs([
            "👨\u200d👩\u200d👧  Mon Foyer",
            "💰  Deductions & Credits",
            "🎓  Enfant Majeur",
            "📊  Resultats & Comparaison",
            "📄  Export PDF",
        ])
    else:
        st.markdown("""<div class="mode-badge" style="background:#1e293b;color:#4ade80">
        Mode actif : Simulation du foyer familial
        </div>""", unsafe_allow_html=True)
        tabs_irpp = st.tabs([
            "👨\u200d👩\u200d👧  Mon Foyer",
            "💰  Deductions & Credits",
            "📊  Resultats",
            "📄  Export PDF",
        ])
        # Dummy tab ref for enfant — not shown
        tabs_irpp = list(tabs_irpp)
        tabs_irpp.insert(2, None)

    tab_foyer, tab_ded, tab_enf, tab_res, tab_pdf = tabs_irpp

    # ── ONGLET FOYER ─────────────────────────────────────────────────
    with tab_foyer:
        st.markdown("### Situation familiale")
        f1, f2 = st.columns(2)
        with f1:
            situation = st.selectbox("Statut matrimonial",
                ["Celibataire / Divorce(e)","Marie(e) / Pacse(e)","Veuf(ve)"],
                key="situation")
            invalide = st.checkbox("Carte d'invalidite >= 80 % (+0,5 part)", key="invalide")
        with f2:
            nb_enfants = st.number_input("Enfants mineurs a charge", 0, 10, 0, key="nb_enfants")
            parent_isole = False
            if situation in ("Celibataire / Divorce(e)","Veuf(ve)") and nb_enfants > 0:
                parent_isole = st.checkbox("Parent isole (case T) +1 part pour le 1er enfant",
                                           key="parent_isole")

        st.markdown("---")
        st.markdown("### Revenus 2024 — montants bruts avant abattement")
        st.markdown("**Declarant 1**")
        r1a, r1b, r1c = st.columns(3)
        with r1a:
            sal1 = st.number_input("Salaires / Traitements EUR", 0, 500000, 45000, 500,
                help="Case 1AJ", key="sal1")
        with r1b:
            pen1 = st.number_input("Pensions / Retraites EUR", 0, 200000, 0, 200,
                help="Case 1AS", key="pen1")
        with r1c:
            hsup1 = st.number_input("dont Heures sup exonerees EUR", 0, 7500, 0, 100,
                help="Case 1GH — inclus dans salaires, plafond 7 500 EUR", key="hsup1")
            if hsup1: st.caption(f"Exoneration IR : {fr(min(hsup1,7500))} EUR")
        with st.expander("Frais professionnels — Declarant 1"):
            fr1, mfr1 = saisie_frais_reels("d1", sal1)

        sal2 = pen2 = hsup2 = 0
        fr2 = False; mfr2 = 0
        if situation == "Marie(e) / Pacse(e)":
            st.markdown("**Declarant 2**")
            r2a, r2b, r2c = st.columns(3)
            with r2a:
                sal2 = st.number_input("Salaires EUR", 0, 500000, 0, 500, help="Case 1BJ", key="sal2")
            with r2b:
                pen2 = st.number_input("Pensions EUR", 0, 200000, 0, 200, help="Case 1BS", key="pen2")
            with r2c:
                hsup2 = st.number_input("dont Heures sup EUR", 0, 7500, 0, 100, help="Case 1HH", key="hsup2")
            with st.expander("Frais professionnels — Declarant 2"):
                fr2, mfr2 = saisie_frais_reels("d2", sal2)

        st.markdown('<div class="src">Revenus imposables = Salaires - Heures sup exonerees - Abattement 10 % (ou frais reels)</div>',
                    unsafe_allow_html=True)

    # ── ONGLET DEDUCTIONS ────────────────────────────────────────────
    with tab_ded:
        st.markdown("### Deductions du revenu global")
        da, db = st.columns(2)
        with da:
            per = st.number_input("Versements PER EUR", 0, 80000, 0, 500,
                help="Cases 6NS/6NT/6NU — 10 % revenus, min 4 637 EUR", key="per")
            pen_versee = st.number_input("Pension alimentaire versee EUR", 0, 20000, 0, 200,
                help="Case 6GI — plafond legal 6 794 EUR pour enfant majeur", key="pen_versee")
        with db:
            cot_synd = st.number_input("Cotisations syndicales EUR", 0, 2000, 0, 50,
                help="Case 7AC — credit 66 %, plafond 1 % salaires", key="cot_synd")
        st.markdown("---")
        st.markdown("### Reductions — Dons")
        dc, dd, de = st.columns(3)
        with dc:
            dons_75 = st.number_input("Dons 75 % (aide personnes) EUR", 0, 5000, 0, 50,
                help="Case 7UD — plafond 1 000 EUR", key="dons_75")
        with dd:
            dons_mayo = st.number_input("Dons Mayotte 75 % EUR", 0, 5000, 0, 50,
                help="Case 7UM — cyclone Chido, plafond 2 000 EUR", key="dons_mayo")
        with de:
            dons_66 = st.number_input("Dons 66 % (assoc.) EUR", 0, 50000, 0, 50,
                help="Case 7VC — plafond 20 % du RNI", key="dons_66")
        st.markdown("---")
        st.markdown("### Credits d'impot")
        df_col, dg_col = st.columns(2)
        with df_col:
            st.markdown("**Garde d'enfants hors domicile**")
            nb_enf6 = st.number_input("Enfants < 6 ans au 01/01/2024", 0, 5, 0, key="nb_enf6")
            res_alt = False; frais_garde = 0
            if nb_enf6 > 0:
                res_alt = st.checkbox("Residence alternee (plafond / 2)", key="res_alt")
                frais_garde = st.number_input("Frais garde EUR", 0, 15000, 0, 100,
                    help="Cases 7GA-7GC — credit 50 %, plafond 3 500 EUR/enfant", key="garde")
                plaf_g = (3500 / (2 if res_alt else 1)) * nb_enf6
                st.caption(f"Credit estime : **{fr(min(frais_garde, plaf_g) * .5)} EUR**")
        with dg_col:
            st.markdown("**Emploi a domicile**")
            prem_annee = st.checkbox("1ere annee emploi domicile", key="prem_annee")
            emploi_dom = st.number_input("Depenses EUR", 0, 25000, 0, 200,
                help="Cases 7DB/7DQ — credit 50 %, plafond 12 000 EUR + 1 500 EUR/enfant", key="emp_dom")
            if emploi_dom:
                plaf_e = (15000 if prem_annee else 12000) + nb_enfants * 1500
                st.caption(f"Credit estime : **{fr(min(emploi_dom, min(plaf_e,18000 if prem_annee else 15000)) * .5)} EUR**")

    # ── ONGLET ENFANT MAJEUR (seulement si mode comparaison) ─────────
    profil_enfant   = None
    comparaison     = None
    res_enfant_seul = None
    etudiant_enf    = False
    exo_etud_enf    = 0

    if comp_mode and tab_enf is not None:
        with tab_enf:
            st.markdown("### Profil fiscal complet de l'enfant majeur")
            st.markdown("""
            Renseignez la situation comme s'il **declarait seul** (Scenario B).
            Pour le **Scenario A** (rattachement), ses revenus seront automatiquement integres dans votre foyer.
            """)
            et1, et2, et3 = st.tabs(["Situation & Revenus", "Deductions & Credits", "Statut etudiant & Pension"])

            with et1:
                ea, eb_c = st.columns(2)
                with ea:
                    sit_enf = st.selectbox("Statut matrimonial",
                        ["Celibataire / Divorce(e)","Marie(e) / Pacse(e)","Veuf(ve)"],
                        key="sit_enf")
                    nb_enf_enf = st.number_input("Ses propres enfants a charge", 0, 10, 0, key="enf_enf")
                    pi_enf = False
                    if sit_enf in ("Celibataire / Divorce(e)","Veuf(ve)") and nb_enf_enf > 0:
                        pi_enf = st.checkbox("Parent isole (case T)", key="pi_enf")
                    inv_enf = st.checkbox("Invalide >= 80 %", key="inv_enf")
                with eb_c:
                    sal1_enf  = st.number_input("Salaires EUR", 0, 200000, 18000, 500,
                        help="Case 1AJ — etudiant, alternant, salarie...", key="sal1_enf")
                    pen1_enf  = st.number_input("Pensions EUR", 0, 100000, 0, 200, help="Case 1AS", key="pen1_enf")
                    hsup1_enf = st.number_input("dont Heures sup EUR", 0, 7500, 0, 100, help="Case 1GH", key="hsup1_enf")
                    sal2_enf = pen2_enf = hsup2_enf = 0
                    if sit_enf == "Marie(e) / Pacse(e)":
                        sal2_enf  = st.number_input("Salaires conjoint(e) EUR", 0, 200000, 0, 500, key="sal2_enf")
                        pen2_enf  = st.number_input("Pensions conjoint(e) EUR", 0, 100000, 0, 200, key="pen2_enf")
                        hsup2_enf = st.number_input("Heures sup conjoint(e) EUR", 0, 7500, 0, 100, key="hsup2_enf")
                with st.expander("Frais professionnels — Enfant (Declarant 1)"):
                    fr1_enf, mfr1_enf = saisie_frais_reels("enf_d1", sal1_enf)
                fr2_enf = False; mfr2_enf = 0
                if sit_enf == "Marie(e) / Pacse(e)" and sal2_enf > 0:
                    with st.expander("Frais professionnels — Enfant (Declarant 2)"):
                        fr2_enf, mfr2_enf = saisie_frais_reels("enf_d2", sal2_enf)

            with et2:
                ec1, ec2 = st.columns(2)
                with ec1:
                    per_enf       = st.number_input("PER EUR", 0, 20000, 0, 200, key="per_enf")
                    cot_synd_enf  = st.number_input("Cotisations syndicales EUR", 0, 1000, 0, 50, key="synd_enf")
                    dons_75_enf   = st.number_input("Dons 75 % EUR", 0, 2000, 0, 50, key="d75_enf")
                    dons_66_enf   = st.number_input("Dons 66 % EUR", 0, 10000, 0, 50, key="d66_enf")
                with ec2:
                    nb_enf6_enf = st.number_input("Ses enfants < 6 ans", 0, 5, 0, key="enf6_enf")
                    garde_enf   = st.number_input("Frais garde EUR", 0, 10000, 0, 100,
                        key="garde_enf") if nb_enf6_enf > 0 else 0
                    emploi_enf  = st.number_input("Emploi domicile EUR", 0, 15000, 0, 200, key="emp_enf")

            with et3:
                eg1, eg2 = st.columns(2)
                with eg1:
                    st.markdown("**Statut etudiant**")
                    etudiant_enf = st.checkbox(
                        "L'enfant est etudiant (moins de 26 ans)", key="etudiant_enf",
                        help="Exoneration jobs etudiants : 5 301 EUR max (3 x SMIC mensuel 2024, art. 81 bis CGI)")
                    if etudiant_enf:
                        st.success(f"Exoneration emploi etudiant applicable : jusqu'a **5 301 EUR** exoneres dans les 2 scenarios.")
                        niveau_enf = st.selectbox("Niveau d'etudes (reduction scolarite Scenario A)",
                            list(moteur.SCOLARITE.keys()), key="niv_enf")
                        red_scol_est = moteur.SCOLARITE.get(niveau_enf, 183)
                        st.caption(f"Reduction scolarite applicable en Scenario A uniquement : **{red_scol_est} EUR** (cases 7EF/7EG/7EA)")
                    else:
                        niveau_enf = list(moteur.SCOLARITE.keys())[-1]
                with eg2:
                    st.markdown("**Pension alimentaire potentielle**")
                    pension_enf = st.slider(
                        "Pension que vous pourriez verser EUR", 0, 6794, 6794, 100, key="pension_enf",
                        help="Deductible chez vous (6GI) — Imposable chez l'enfant (1AS) — Plafond 6 794 EUR")
                    st.markdown(f"""
                    - Chez vous : deductible case **6GI**
                    - Chez l'enfant : imposable case **1AS** (comme pension)
                    - Plafond legal : **6 794 EUR**
                    """)

            exo_etud_enf = min(sal1_enf, moteur.JOBS_ETUDIANTS_EXONERATION) if etudiant_enf else 0
            profil_enfant = {
                'situation': sit_enf, 'nb_enfants': nb_enf_enf,
                'invalide_declarant': inv_enf, 'parent_isole': pi_enf,
                'revenu_salaire_declarant': sal1_enf, 'revenu_pension_declarant': pen1_enf,
                'revenu_salaire_conjoint': sal2_enf,  'revenu_pension_conjoint': pen2_enf,
                'heures_sup_declarant': hsup1_enf, 'heures_sup_conjoint': hsup2_enf,
                'frais_reels': fr1_enf, 'montant_frais_reels_1': mfr1_enf,
                'frais_reels_2': fr2_enf, 'montant_frais_reels_2': mfr2_enf,
                'versement_per': per_enf, 'cotisations_syndicales': cot_synd_enf,
                'dons_60_75': dons_75_enf, 'dons_mayotte': 0, 'dons_60': dons_66_enf,
                'nb_enfants_moins_6': nb_enf6_enf, 'residence_alternee': False,
                'frais_garde': garde_enf, 'premiere_annee_emploi': False,
                'emploi_domicile': emploi_enf,
                'etudiant': etudiant_enf,
                'exoneration_emploi_etudiant': exo_etud_enf,
                'niveau_etude': niveau_enf,
                'pension_recue': pension_enf,
            }
    else:
        # Valeurs par defaut si pas de comparaison
        sit_enf = "Celibataire / Divorce(e)"
        nb_enf_enf = 0
        pi_enf = inv_enf = False
        sal1_enf = pen1_enf = sal2_enf = pen2_enf = 0
        hsup1_enf = hsup2_enf = 0
        fr1_enf = fr2_enf = False
        mfr1_enf = mfr2_enf = 0
        per_enf = cot_synd_enf = 0
        dons_75_enf = dons_66_enf = 0
        nb_enf6_enf = garde_enf = emploi_enf = 0
        niveau_enf = list(moteur.SCOLARITE.keys())[-1]
        pension_enf = 6794

    # ── CALCUL ───────────────────────────────────────────────────────
    profil = {
        'situation': situation, 'nb_enfants': nb_enfants,
        'invalide_declarant': invalide, 'parent_isole': parent_isole,
        'revenu_salaire_declarant': sal1, 'revenu_pension_declarant': pen1,
        'revenu_salaire_conjoint': sal2,  'revenu_pension_conjoint': pen2,
        'heures_sup_declarant': hsup1,   'heures_sup_conjoint': hsup2,
        'frais_reels': fr1, 'montant_frais_reels_1': mfr1,
        'frais_reels_2': fr2, 'montant_frais_reels_2': mfr2,
        'versement_per': per, 'cotisations_syndicales': cot_synd,
        'pension_alimentaire_versee': pen_versee,
        'dons_60_75': dons_75, 'dons_mayotte': dons_mayo, 'dons_60': dons_66,
        'nb_enfants_moins_6': nb_enf6, 'residence_alternee': res_alt,
        'frais_garde': frais_garde, 'premiere_annee_emploi': prem_annee,
        'emploi_domicile': emploi_dom,
    }
    res     = moteur.calculer(profil)
    conseils = moteur.generer_conseils(profil, res)

    if comp_mode and profil_enfant:
        pe_seul = {k: v for k, v in profil_enfant.items()
                   if k not in ('niveau_etude','pension_recue','etudiant')}
        pe_seul['exoneration_emploi_etudiant'] = exo_etud_enf
        res_enfant_seul = moteur.calculer(pe_seul)
        sc_obj      = ScenarioEnfantMajeur(moteur)
        comparaison = sc_obj.comparer(profil, profil_enfant)

    # ── ONGLET RESULTATS ─────────────────────────────────────────────
    with tab_res:
        st.markdown("### Votre simulation fiscale 2026")
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(kpi("Revenu Net Imposable", f"{fr(res['revenu_imposable'])} EUR","#93c5fd"),unsafe_allow_html=True)
        with k2: st.markdown(kpi("Impot brut", f"{fr(res['impot_brut'])} EUR","#f87171"),unsafe_allow_html=True)
        with k3: st.markdown(kpi("Decote", f"-{fr(res['decote'])} EUR","#4ade80"),unsafe_allow_html=True)
        with k4: st.markdown(kpi("IMPOT NET A PAYER", f"{fr(res['impot_net'])} EUR","#60a5fa"),unsafe_allow_html=True)

        st.markdown("")
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Taux moyen", f"{res['taux_moyen']:.2f} %")
        with m2: st.metric("TMI", f"{res['taux_marginal']} %")
        with m3: st.metric("Parts fiscales", f"{res['nb_parts']:.1f}")
        with m4:
            hstot = hsup1 + hsup2
            if hstot: st.metric("Heures sup exonerees", f"{fr(hstot)} EUR")
            else: st.metric("Abattement total", f"{fr(res['abattement_applique'])} EUR")

        st.markdown('<div class="src">Bareme 2024 — DGFiP 2025 — Decote : 889 - 45,25 % x impot (cel.) — QF plafonne 1 791 EUR/demi-part</div>', unsafe_allow_html=True)

        with st.expander("Detail complet du calcul"):
            d1, d2 = st.columns(2)
            with d1:
                rows = [["Salaires bruts D1", f"{fr(sal1)} EUR"]]
                if hsup1: rows.append(["dont Heures sup D1", f"-{fr(hsup1)} EUR"])
                rows += [
                    ["Abattement salaires D1", f"-{fr(res['abattement_salaires_1'])} EUR"],
                    ["Pensions D1", f"{fr(pen1)} EUR"],
                    ["Abattement pensions D1", f"-{fr(res['abattement_pensions_1'])} EUR"],
                ]
                if situation == "Marie(e) / Pacse(e)":
                    rows += [["Salaires D2", f"{fr(sal2)} EUR"],
                             ["Abattement D2", f"-{fr(res['abattement_salaires_2'])} EUR"]]
                rows += [
                    ["Deduction PER", f"-{fr(res['deduction_per'])} EUR"],
                    ["Pension versee", f"-{fr(res['pension_versee_ded'])} EUR"],
                    ["= RNI", f"{fr(res['revenu_imposable'])} EUR"],
                ]
                st.dataframe(pd.DataFrame(rows, columns=["Etape","Montant"]),
                             hide_index=True, use_container_width=True)
            with d2:
                rows2 = [
                    [f"Quotient RNI / {res['nb_parts']:.1f} parts", f"{fr(res['quotient_familial'])} EUR"],
                    ["x parts", f"{fr(res['impot_avant_plafond'])} EUR"],
                    ["Plafonnement QF", f"-{fr(res['plafonnement_qf'])} EUR"],
                    ["Impot brut", f"{fr(res['impot_brut'])} EUR"],
                    ["Decote", f"-{fr(res['decote'])} EUR"],
                    ["Reductions / Credits", f"-{fr(res['reduction_dons_75']+res['reduction_dons_66']+res['credit_garde']+res['credit_emploi']+res['credit_syndicat'])} EUR"],
                    ["= IMPOT NET", f"{fr(res['impot_net'])} EUR"],
                ]
                st.dataframe(pd.DataFrame(rows2, columns=["Etape","Montant"]),
                             hide_index=True, use_container_width=True)

        # Graphiques
        g1, g2 = st.columns(2)
        with g1:
            tr = [t for t in res['detail_tranches'] if t['impot_tranche'] > 0]
            if tr:
                fig = go.Figure([go.Bar(
                    x=[t['label'] for t in tr], y=[t['impot_tranche'] for t in tr],
                    marker_color=['#1e3a5f','#1d4ed8','#3b82f6','#60a5fa','#93c5fd'][:len(tr)],
                    text=[f"{fr(t['impot_tranche'])} EUR" for t in tr],
                    textposition='outside', textfont=dict(color='#e2e8f0'))])
                fig.update_layout(title="Impot par tranche", height=300,
                    plot_bgcolor='#1e293b', paper_bgcolor='#1e293b',
                    font=dict(color='#e2e8f0'), showlegend=False)
                fig.update_yaxes(gridcolor='#334155')
                fig.update_xaxes(tickfont=dict(size=8))
                st.plotly_chart(fig, use_container_width=True)
        with g2:
            tb = res['revenu_total_brut']
            if tb > 0:
                fig2 = go.Figure(go.Pie(
                    labels=['Impot net','Revenu disponible'],
                    values=[res['impot_net'], max(0, tb - res['impot_net'])],
                    hole=0.55, marker_colors=['#dc2626','#1d4ed8'],
                    textfont=dict(color='#e2e8f0')))
                fig2.update_layout(title="Repartition du revenu", height=300,
                    plot_bgcolor='#1e293b', paper_bgcolor='#1e293b',
                    font=dict(color='#e2e8f0'),
                    annotations=[dict(text=f"{res['taux_moyen']:.1f} %<br>moyen",
                                      x=0.5, y=0.5, font_size=13,
                                      font=dict(color='#e2e8f0'), showarrow=False)])
                st.plotly_chart(fig2, use_container_width=True)

        # ── COMPARAISON (si mode actif) ──────────────────────────────
        if comp_mode and comparaison:
            st.markdown("---")
            st.markdown("### Comparaison enfant majeur — Rattachement vs Foyer independant")

            sc_a  = comparaison['scenario_a']
            sc_b  = comparaison['scenario_b']
            meill = comparaison['meilleur_scenario']
            eco   = comparaison['economie']
            etud  = comparaison.get('etudiant', False)
            pb    = sc_b['parents']
            eb    = sc_b['enfant']

            # ── Scenario A ──
            ca_c, cb_c = st.columns(2)
            with ca_c:
                best_a = "🏆 " if meill == "A" else ""
                bc_a   = "#1d4ed8" if meill == "A" else "#334155"

                # Construire les lignes proprement (pas de HTML conditionnel inline)
                lignes_a = [
                    f"Parts foyer avec enfant rattache : <b>{sc_a['nb_parts']:.1f}</b>",
                    f"Revenus enfant integres : <b>{fr(sc_a['revenus_enfant_integres'])} EUR</b>",
                ]
                if etud and sc_a.get('exoneration_etudiant', 0) > 0:
                    lignes_a.append(f"Exoneration emploi etudiant : <b>-{fr(sc_a['exoneration_etudiant'])} EUR</b>")
                lignes_a += [
                    f"RNI foyer combine : <b>{fr(sc_a['rni'])} EUR</b>",
                    f"Impot brut : <b>{fr(sc_a['impot_brut'])} EUR</b>",
                    f"IR foyer avant reduction scol. : <b>{fr(sc_a['impot_net_avant_scol'])} EUR</b>",
                ]
                if etud:
                    lignes_a.append(f"Reduction scolarite ({sc_a['niveau_etude']}) : <b>-{sc_a['reduction_scolarite']} EUR</b>")

                body_a = "<br>".join(lignes_a)
                st.markdown(f"""<div class="card" style="border-color:{bc_a}">
                <h4 style="color:#93c5fd">{best_a}Scenario A — Rattachement</h4>
                {body_a}<br><br>
                <span style="font-size:1.3rem;font-weight:700;color:#60a5fa">
                Impot net total : {fr(sc_a['cout_total'])} EUR</span>
                </div>""", unsafe_allow_html=True)

            with cb_c:
                best_b = "🏆 " if meill == "B" else ""
                bc_b   = "#16a34a" if meill == "B" else "#334155"

                lignes_b_parents = [
                    f"Parts parents (inchangees) : <b>{pb['nb_parts']:.1f}</b>",
                    f"Pension versee deductible (case 6GI) : <b>-{fr(pb.get('pension_versee',0))} EUR</b>",
                    f"IR parents : <b>{fr(pb['impot_net'])} EUR</b>",
                ]
                lignes_b_enfant = [
                    f"Parts enfant : <b>{eb['nb_parts']:.1f}</b>",
                ]
                if etud and eb.get('exoneration_etudiant', 0) > 0:
                    lignes_b_enfant.append(f"Exoneration emploi etudiant : <b>-{fr(eb['exoneration_etudiant'])} EUR</b>")
                lignes_b_enfant += [
                    f"Pension recue imposable (case 1AS) : <b>{fr(eb.get('pension_recue',0))} EUR</b>",
                    f"RNI enfant : <b>{fr(eb['revenu_imposable'])} EUR</b>",
                    f"TMI enfant : <b>{eb.get('taux_marginal',0)} %</b>",
                    f"IR enfant : <b>{fr(eb['impot_net'])} EUR</b>",
                ]

                bp_html = "<br>".join(lignes_b_parents)
                be_html = "<br>".join(lignes_b_enfant)
                st.markdown(f"""<div class="card" style="border-color:{bc_b}">
                <h4 style="color:#4ade80">{best_b}Scenario B — Foyer independant</h4>
                <b style="color:#94a3b8">Parents :</b><br>{bp_html}<br><br>
                <b style="color:#94a3b8">Enfant :</b><br>{be_html}<br><br>
                <span style="font-size:1.3rem;font-weight:700;color:#4ade80">
                Total (parents + enfant) : {fr(sc_b['cout_total'])} EUR</span>
                </div>""", unsafe_allow_html=True)

            # Verdict
            cls  = "verdict-a" if meill == "A" else "verdict-b"
            lab  = "Scenario A — Rattachement" if meill == "A" else "Scenario B — Foyer independant"
            col  = "#60a5fa" if meill == "A" else "#4ade80"
            st.markdown(f"""<div class="{cls}">
            <h3 style="color:{col};margin:0">Recommandation : {lab}</h3>
            <p style="margin:.4rem 0 0">Economie : <b>{fr(eco)} EUR</b> par rapport a l'autre scenario.</p>
            </div>""", unsafe_allow_html=True)

            # Graphique
            fig_c = go.Figure([
                go.Bar(name=f"A — Rattachement", x=["Cout fiscal total"], y=[sc_a['cout_total']],
                       marker_color='#1d4ed8',
                       text=f"{fr(sc_a['cout_total'])} EUR", textposition='outside',
                       textfont=dict(color='#e2e8f0')),
                go.Bar(name=f"B — Independant", x=["Cout fiscal total"], y=[sc_b['cout_total']],
                       marker_color='#16a34a',
                       text=f"{fr(sc_b['cout_total'])} EUR", textposition='outside',
                       textfont=dict(color='#e2e8f0')),
            ])
            fig_c.update_layout(barmode='group', title="Cout fiscal global compare",
                height=280, plot_bgcolor='#1e293b', paper_bgcolor='#1e293b',
                font=dict(color='#e2e8f0'))
            st.plotly_chart(fig_c, use_container_width=True)

        # Conseils
        st.markdown("---")
        st.markdown("### Conseils d'optimisation")
        if conseils:
            icones = {'PER':'💰','FR':'📋','DONS':'❤️','DOM':'🏠','TMI':'📉','SYND':'🤝','HS':'⏰'}
            for c in conseils:
                ic = icones.get(c['icone'], '💡')
                st.markdown(f"""<div class="conseil">
                <b>{ic} {c['titre']}</b><br>
                <span style="color:#fbbf24">{c['detail']}</span></div>""",
                            unsafe_allow_html=True)
        else:
            st.success("Votre situation semble bien optimisee.")

    # ── ONGLET PDF ───────────────────────────────────────────────────
    with tab_pdf:
        st.markdown("### Bilan fiscal PDF personnalise")
        st.markdown("""
        - Resume complet de votre simulation
        - Detail du calcul tranche par tranche
        - **Guide des cases a renseigner** sur votre declaration (impots.gouv.fr)
        - Conseils d'optimisation personnalises
        """)
        if comp_mode and comparaison:
            st.info("Le rapport inclura la comparaison enfant majeur et la declaration detaillee de l'enfant.")

        if st.button("Generer mon bilan fiscal PDF", type="primary"):
            with st.spinner("Generation en cours..."):
                try:
                    gen = GenererRapportPDF()
                    pdf_bytes = gen.generer(
                        profil, res, conseils,
                        comparaison if comp_mode else None,
                        profil_enfant=profil_enfant if comp_mode else None,
                        res_enfant_seul=res_enfant_seul if comp_mode else None
                    )
                    b64 = base64.b64encode(pdf_bytes).decode()
                    href = (f'<a href="data:application/pdf;base64,{b64}" '
                            f'download="bilan_fiscal_2026.pdf" '
                            f'style="display:inline-block;background:#1d4ed8;color:white;'
                            f'padding:.8rem 2rem;border-radius:8px;text-decoration:none;'
                            f'font-weight:700;font-size:1rem;margin-top:.5rem">'
                            f'Telecharger le rapport PDF</a>')
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("Rapport genere !")
                except Exception as e:
                    st.error(f"Erreur generation PDF : {e}")
                    raise

        st.markdown("---")
        st.markdown("""<div style="color:#475569;font-size:.74rem;text-align:center;padding:.5rem">
        Simulateur base sur Brochure Pratique DGFiP 2025 (Revenus 2024) |
        Pour information uniquement |
        <a href="https://www.impots.gouv.fr" target="_blank" style="color:#3b82f6">impots.gouv.fr</a>
        </div>""", unsafe_allow_html=True)
