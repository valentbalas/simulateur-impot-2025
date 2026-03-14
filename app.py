"""
Simulateur Impot sur le Revenu 2026 — Dark theme complet
3e declarant | Autres revenus | Conseils personnalises | Dirigeant PDF
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
from calcul_impot import MoteurImpot, ScenarioEnfantMajeur, FraisReels
from rapport_pdf import GenererRapportPDF
from dirigeant import MoteurDirigeant
from autres_revenus import AutresRevenus

st.set_page_config(page_title="Simulateur IR 2026", page_icon="🧮",
                   layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
.stApp,[data-testid="stAppViewContainer"]{background:#0f172a !important;color:#e2e8f0}
[data-testid="stHeader"]{background:#0f172a !important}
section[data-testid="stSidebar"]{background:#1e293b !important}
.stSelectbox>div>div,.stNumberInput>div>div>input,.stTextInput>div>div>input
  {background:#1e293b !important;color:#e2e8f0 !important;border-color:#334155 !important}
.stCheckbox label,.stRadio label,.stToggle label{color:#e2e8f0 !important}
div[data-testid="stTabs"] [data-baseweb="tab-list"]
  {background:#1e293b;border-radius:10px;padding:.3rem;gap:.2rem}
div[data-testid="stTabs"] [data-baseweb="tab"]
  {color:#94a3b8;border-radius:8px;padding:.4rem 1rem;font-weight:500}
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
.card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:1.2rem;margin-bottom:.8rem}
.card h4{color:#93c5fd;margin:0 0 .6rem 0;font-size:1rem}
.kpi{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:1rem;text-align:center}
.kpi-val{font-size:1.6rem;font-weight:700}
.kpi-lbl{font-size:.72rem;color:#94a3b8;margin-top:.2rem}
.verdict-a{background:#1e3a5f;border-left:4px solid #3b82f6;border-radius:0 8px 8px 0;padding:1rem;margin:.7rem 0}
.verdict-b{background:#14532d;border-left:4px solid #22c55e;border-radius:0 8px 8px 0;padding:1rem;margin:.7rem 0}
.conseil{background:#1c1a09;border:1px solid #854d0e;border-radius:8px;padding:.8rem 1rem;margin:.35rem 0;color:#fef9c3}
.conseil-priority{border-left:4px solid;border-radius:0 8px 8px 0;padding:.9rem 1.1rem;margin:.4rem 0}
.src{background:#1e293b;border-radius:6px;padding:.4rem .8rem;font-size:.74rem;color:#64748b;margin:.4rem 0}
.opt-card{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:1rem;margin:.4rem 0}
.opt-card h5{margin:0 0 .4rem 0;font-size:.92rem}
.badge{display:inline-block;padding:.15rem .55rem;border-radius:12px;font-size:.72rem;font-weight:600;margin:.1rem}
</style>""", unsafe_allow_html=True)

st.markdown("""
<div style="background:linear-gradient(135deg,#003189 0%,#1d4ed8 55%,#ed2939 100%);
  padding:1.4rem 2rem;border-radius:14px;color:white;text-align:center;
  margin-bottom:1.2rem;box-shadow:0 4px 20px rgba(29,78,216,.4)">
  <h1 style="margin:0;font-size:1.85rem;font-weight:700">Simulateur Impot sur le Revenu 2026</h1>
  <p style="margin:.3rem 0 0;opacity:.9;font-size:.9rem">
    Declaration 2026 &bull; Revenus 2025 &bull; Bareme officiel DGFiP (Brochure Pratique 2025)</p>
</div>""", unsafe_allow_html=True)

moteur   = MoteurImpot()
dm       = MoteurDirigeant()
ar_engine = AutresRevenus()


def fr(val, dec=0):
    if val is None: return "-"
    if dec == 0:
        s = f"{abs(val):,.0f}".replace(",", "\u202f")
    else:
        s = f"{abs(val):,.{dec}f}"
        p = s.split("."); s = p[0].replace(",", "\u202f") + "," + p[1]
    return ("-\u202f" if val < 0 else "") + s


def kpi(label, val, color="#93c5fd"):
    return (f'<div class="kpi"><div class="kpi-val" style="color:{color}">{val}</div>'
            f'<div class="kpi-lbl">{label}</div></div>')


def impact_color(imp):
    return {"Tres eleve": "#f59e0b", "Eleve": "#3b82f6",
            "A evaluer": "#8b5cf6", "Moyen": "#6b7280"}.get(imp, "#6b7280")


def saisie_frais_reels(prefix, salaire):
    mode = st.radio("Mode deduction", ["Forfait 10 % (auto)", "Frais reels justifies"],
                    key=f"mode_{prefix}", horizontal=True)
    if "Forfait" in mode:
        f10 = max(moteur.ABATTEMENT_SALAIRES_MIN, min(salaire * .10, moteur.ABATTEMENT_SALAIRES_MAX))
        st.caption(f"Forfait : **{fr(f10)} EUR** (cases 1AK/1BK non renseignees)")
        return False, 0
    c1, c2 = st.columns(2)
    with c1:
        tveh = st.selectbox("Vehicule",
            ["thermique","electrique","moto","moto_electrique","cyclo"],
            format_func=lambda x: {"thermique":"Voiture thermique","electrique":"Voiture electrique",
                "moto":"Moto","moto_electrique":"Moto electrique","cyclo":"Cyclomoteur"}[x],
            key=f"tveh_{prefix}")
        cv = 5
        if tveh in ("thermique","electrique"):
            cv = st.select_slider("CV fiscaux",[3,4,5,6,7],5,key=f"cv_{prefix}")
        elif "moto" in tveh:
            cv = st.selectbox("Cylindree",[2,5,99],
                format_func=lambda x:{2:"1-2 CV",5:"3-5 CV",99:"> 5 CV"}[x], key=f"cvm_{prefix}")
        km = st.number_input("Km pro/an",0,100000,0,500,key=f"km_{prefix}")
        fkm = FraisReels.calculer_bareme_km(km,cv,tveh) if km else 0
        if km: st.info(f"Km : **{fr(fkm)} EUR**")
    with c2:
        nbr = st.number_input("Repas pro/an",0,300,0,key=f"rep_{prefix}")
        pxr = st.number_input("Prix repas EUR",0.0,50.0,10.0,.5,key=f"px_{prefix}")
        frep = max(0,(pxr-FraisReels.REPAS_VALEUR_FOYER)*nbr) if nbr else 0
        if nbr: st.info(f"Repas : **{fr(frep)} EUR**")
        jtt = st.number_input("Jours teletravail",0,230,0,key=f"tt_{prefix}")
        ftt = FraisReels.calculer_teletravail(jtt) if jtt else 0
        if jtt: st.info(f"Teletravail : **{fr(ftt)} EUR**")
    dr = st.number_input("Double residence EUR",0,30000,0,200,key=f"dr_{prefix}")
    fo = st.number_input("Formation EUR",0,20000,0,100,key=f"fo_{prefix}")
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


# ══════════════════════════════════════════════════════════════════════
# CHOIX DU MODE
# ══════════════════════════════════════════════════════════════════════
st.markdown("### Que souhaitez-vous simuler ?")
mode = st.radio("", [
    "Simulation du foyer familial",
    "Comparaison avec un enfant majeur (rattachement vs foyer independant)",
    "Revenus de dirigeant / Revenus professionnels complexes",
], key="mode_global")
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════
# MODE DIRIGEANT
# ══════════════════════════════════════════════════════════════════════
if mode == "Revenus de dirigeant / Revenus professionnels complexes":
    tab_dir, tab_opt, tab_dir_pdf = st.tabs([
        "🏢  Revenus & Statuts TNS",
        "🎯  Optimisation Fiscale",
        "📄  Rapport PDF Dirigeant",
    ])

    with tab_dir:
        st.markdown("### Parametres generaux")
        pg1, pg2 = st.columns(2)
        with pg1:
            tmi_dir = st.select_slider("TMI",[0,11,30,41,45],30,key="tmi_dir")
            statut_dir = st.selectbox("Statut social",
                list(dm.TNS_COTISATIONS.keys()),
                format_func=lambda x: dm.TNS_COTISATIONS[x]['label'],
                key="statut_dir")
        with pg2:
            remun_comp = st.number_input("Remuneration de reference EUR",
                0, 500000, 80000, 5000, key="remun_comp")
            if remun_comp:
                cmp = dm.comparer_statuts(remun_comp, tmi_dir)
                df_cmp = pd.DataFrame([{
                    "Statut": r['label'].split('(')[0].strip(),
                    "Charges": f"{r['taux_charges']} %",
                    "Cotisations": f"{fr(r['cotisations'])} EUR",
                    "IR estime": f"{fr(r['ir_estime'])} EUR",
                    "Net final": f"{fr(r['net_final'])} EUR",
                } for r in cmp])
                st.dataframe(df_cmp, hide_index=True, use_container_width=True)

        st.markdown("---")
        dt1, dt2, dt3, dt4, dt5 = st.tabs([
            "👤 TNS & Remuneration", "🏦 IS & Dividendes",
            "🛒 BIC / BNC", "🏠 Immobilier", "🎯 Strategie remun/div"])

        with dt1:
            t1a, t1b = st.columns(2)
            with t1a:
                rem_ts = st.number_input("Remuneration brute EUR",0,500000,60000,1000,key="rem_ts")
                fr_ts  = st.checkbox("Frais reels",key="fr_ts")
                mfr_ts = st.number_input("Montant frais reels EUR",0,30000,0,500,key="mfr_ts") if fr_ts else 0
            with t1b:
                if rem_ts:
                    ab_ts = mfr_ts if fr_ts and mfr_ts else max(moteur.ABATTEMENT_SALAIRES_MIN,
                        min(rem_ts*.10, moteur.ABATTEMENT_SALAIRES_MAX))
                    imp_ts = max(0, rem_ts-ab_ts)
                    cot_ts = dm.calculer_cotisations_tns(rem_ts, statut_dir)
                    st.markdown(f"""<div class="card">
                    <h4>Remuneration de gerance (case 1AJ)</h4>
                    Brute : <b>{fr(rem_ts)} EUR</b> | Abatt. : -{fr(ab_ts)} EUR<br>
                    Imposable IR : <b>{fr(imp_ts)} EUR</b> => IR estime : <b>{fr(int(imp_ts*tmi_dir/100))} EUR</b><br>
                    <hr style="border-color:#334155;margin:.5rem 0">
                    Cotisations ({cot_ts['statut'][:30]}) : <b style="color:#f87171">{fr(cot_ts['cotisations'])} EUR</b><br>
                    Net avant IR : <b style="color:#4ade80">{fr(cot_ts['net_avant_ir'])} EUR</b>
                    </div>""", unsafe_allow_html=True)
            if rem_ts:
                c_t1, c_t2, c_t3 = st.columns(3)
                cot_data = dm.calculer_cotisations_tns(rem_ts, statut_dir)
                with c_t1:
                    det_html = "".join(f"<tr><td style='color:#94a3b8;padding:.12rem .4rem'>{k}</td>"
                        f"<td style='padding:.12rem .4rem'><b>{v}</b></td></tr>"
                        for k,v in cot_data['detail'].items())
                    st.markdown(f"""<div class="card"><h4>Detail cotisations</h4>
                    <table style="width:100%;font-size:.82rem">{det_html}</table></div>""",
                    unsafe_allow_html=True)
                with c_t2:
                    avt = "".join(f"<li style='color:#4ade80;font-size:.82rem'>{a}</li>"
                                  for a in cot_data['avantages'])
                    st.markdown(f"""<div class="card"><h4>Avantages</h4>
                    <ul style="margin:.3rem 0 0 1rem">{avt}</ul></div>""",unsafe_allow_html=True)
                with c_t3:
                    inc = "".join(f"<li style='color:#f87171;font-size:.82rem'>{i}</li>"
                                  for i in cot_data['inconvenients'])
                    st.markdown(f"""<div class="card"><h4>Points de vigilance</h4>
                    <ul style="margin:.3rem 0 0 1rem">{inc}</ul></div>""",unsafe_allow_html=True)
                # Graphique
                cmpg = dm.comparer_statuts(rem_ts, tmi_dir)
                fig_t = go.Figure([
                    go.Bar(name="Cotisations",
                           x=[r['label'].split('(')[0][:22] for r in cmpg],
                           y=[r['cotisations'] for r in cmpg],
                           marker_color="#f87171",
                           text=[f"{fr(r['cotisations'])} EUR" for r in cmpg],
                           textposition='outside', textfont=dict(color='#e2e8f0')),
                    go.Bar(name="Net final apres IR",
                           x=[r['label'].split('(')[0][:22] for r in cmpg],
                           y=[r['net_final'] for r in cmpg],
                           marker_color="#4ade80",
                           text=[f"{fr(r['net_final'])} EUR" for r in cmpg],
                           textposition='outside', textfont=dict(color='#e2e8f0')),
                ])
                fig_t.update_layout(barmode='group', height=310,
                    plot_bgcolor='#1e293b', paper_bgcolor='#1e293b',
                    font=dict(color='#e2e8f0'), xaxis_tickfont=dict(size=8))
                fig_t.update_yaxes(gridcolor='#334155')
                st.plotly_chart(fig_t, use_container_width=True)

        with dt2:
            i2a, i2b = st.columns(2)
            with i2a:
                res_fisc = st.number_input("Resultat fiscal EUR",-500000,5000000,80000,1000,key="res_fisc")
                if res_fisc > 0:
                    is_d = dm.calculer_is(res_fisc)
                    st.markdown(f"""<div class="card"><h4>Calcul IS 2024</h4>
                    Base 15 % : {fr(is_d['base_reduit'])} EUR => IS : {fr(is_d['is_reduit'])} EUR<br>
                    Base 25 % : {fr(is_d['base_normal'])} EUR => IS : {fr(is_d['is_normal'])} EUR<br>
                    <b style="color:#f87171">IS total : {fr(is_d['is_total'])} EUR</b>
                    ({is_d['taux_effectif']:.2f} %)<br>
                    <b style="color:#4ade80">Benefice net : {fr(is_d['benefice_net'])} EUR</b>
                    </div>""", unsafe_allow_html=True)
            with i2b:
                div_b = st.number_input("Dividendes bruts EUR",0,2000000,50000,1000,key="div_b")
                if div_b:
                    d_d = dm.calculer_dividendes(div_b, tmi_dir)
                    for lbl, opt, cm in [
                        ("PFU 30 %", d_d['pfu'], "#60a5fa" if d_d['meilleur']=="PFU" else "#475569"),
                        (f"Bareme {tmi_dir} % + abatt 40 %", d_d['bareme'], "#4ade80" if d_d['meilleur']=="Bareme" else "#475569")]:
                        best = "Recommande" if (lbl.startswith("PFU") and d_d['meilleur']=="PFU") or (lbl.startswith("Bareme") and d_d['meilleur']=="Bareme") else ""
                        st.markdown(f"""<div class="card" style="border-color:{cm}">
                        <h4 style="color:{cm}">{'🏆 ' if best else ''}{lbl}</h4>
                        IR : {fr(opt.get('ir',0))} EUR | PS : {fr(opt.get('ps',0))} EUR<br>
                        <b>Total : {fr(opt['total_imposition'])} EUR | Net : {fr(opt['net_percu'])} EUR</b>
                        </div>""", unsafe_allow_html=True)

        with dt3:
            btype = st.selectbox("Regime", [
                "BIC micro - ventes","BIC micro - services","BIC reel",
                "BNC micro","BNC reel (2035)"], key="btype")
            bb1, bb2 = st.columns(2)
            with bb1:
                ca_b = st.number_input("CA / Recettes EUR",0,5000000,60000,1000,key="ca_b")
                ch_b = am_b = 0
                if "reel" in btype:
                    ch_b = st.number_input("Charges EUR",0,5000000,40000,1000,key="ch_b")
                    if "BIC" in btype:
                        am_b = st.number_input("Amortissements EUR",0,500000,0,1000,key="am_b")
            with bb2:
                if "ventes" in btype: r_b = dm.calculer_bic_micro(ca_b,'vente')
                elif "services" in btype and "BIC" in btype: r_b = dm.calculer_bic_micro(ca_b,'services')
                elif "BIC reel" in btype: r_b = dm.calculer_bic_reel(ca_b,ch_b,am_b)
                elif "BNC micro" in btype: r_b = dm.calculer_bnc_micro(ca_b)
                else: r_b = dm.calculer_bnc_reel(ca_b,ch_b)
                imposable = r_b.get('benefice_imposable',r_b.get('imposable',0))
                deficit = r_b.get('deficit',0)
                col_v = "#4ade80" if imposable >= 0 else "#f87171"
                abatt_l = (f"Abattement {r_b['abattement_pct']} % : -{fr(r_b.get('abattement_montant',0))} EUR<br>"
                           if 'abattement_pct' in r_b else f"Charges : -{fr(r_b.get('charges',0))} EUR<br>")
                st.markdown(f"""<div class="card"><h4>{r_b.get('type',btype)}</h4>
                {abatt_l}
                <b style="color:{col_v}">Imposable : {fr(imposable)} EUR</b><br>
                {"Deficit : <b>"+fr(deficit)+" EUR</b><br>" if deficit else ""}
                IR estime (TMI {tmi_dir} %) : <b>{fr(int(imposable*tmi_dir/100))} EUR</b>
                </div>""", unsafe_allow_html=True)

        with dt4:
            itype = st.selectbox("Type", [
                "Micro-foncier (30 %)","Foncier reel (2044)",
                "LMNP Micro-BIC","LMNP Reel","LMP",
                "SCI a l'IR","SCI a l'IS"], key="itype")
            im1, im2 = st.columns(2)
            with im1:
                rfb = st.number_input("Revenus / Recettes / Resultat EUR",-100000,5000000,15000,500,key="rfb")
                int_e=ch_f=trav=tf_f=fg_f=ch_lmnp=am_lmnp=ch_lmp=am_lmp=aut_rev=sci_qp=lmnp_cl=0
                if "reels" in itype or "Reel" in itype:
                    if "Foncier" in itype:
                        int_e   = st.number_input("Interets emprunt EUR",0,200000,5000,200,key="int_e")
                        ch_f    = st.number_input("Charges courantes EUR",0,100000,2000,100,key="ch_f")
                        trav    = st.number_input("Travaux EUR",0,500000,0,500,key="trav")
                        tf_f    = st.number_input("Taxe fonciere EUR",0,20000,1000,100,key="tf_f")
                        fg_f    = st.number_input("Frais gestion EUR",0,20000,500,100,key="fg_f")
                    elif "LMNP" in itype:
                        ch_lmnp = st.number_input("Charges EUR",0,200000,5000,500,key="ch_lmnp")
                        am_lmnp = st.number_input("Amortissements EUR",0,200000,4000,500,key="am_lmnp")
                    elif "LMP" in itype:
                        ch_lmp  = st.number_input("Charges EUR",0,500000,8000,500,key="ch_lmp")
                        am_lmp  = st.number_input("Amortissements EUR",0,300000,6000,500,key="am_lmp")
                        aut_rev = st.number_input("Autres revenus pro EUR",0,500000,45000,1000,key="aut_rev")
                elif "SCI a l'IS" in itype:
                    sci_qp = st.slider("Quote-part (%)",1,100,100,1,key="sci_qp") / 100
                elif "Micro" in itype and "LMNP" in itype:
                    lmnp_cl = st.checkbox("Bien classe",key="lmnp_cl")

            with im2:
                if "Micro-foncier" in itype:
                    r_im = dm.calculer_foncier_micro(rfb)
                    col_r = "#4ade80" if rfb >= 0 else "#f87171"
                    elig = "OK Eligible" if r_im['eligible'] else f"Depasse seuil {fr(r_im['seuil'])} EUR"
                    st.markdown(f"""<div class="card"><h4>Micro-foncier</h4>
                    Abattement 30 % : -{fr(r_im['abattement_montant'])} EUR<br>
                    <b style="color:{col_r}">Imposable : {fr(r_im['imposable'])} EUR</b><br>
                    IR estime : {fr(int(r_im['imposable']*tmi_dir/100))} EUR | PS : {fr(int(r_im['imposable']*.172))} EUR<br>
                    {elig}</div>""", unsafe_allow_html=True)
                elif "Foncier reel" in itype:
                    r_im = dm.calculer_foncier_reel(rfb,int_e,ch_f,trav,tf_f,fg_f)
                    col_r = "#4ade80" if r_im['resultat']>=0 else "#f87171"
                    def_html=""
                    if r_im['deficit_total']:
                        def_html=(f"Imputable RNG (plafond 10 700 EUR) : <b>{fr(r_im['deficit_imputable_rng'])} EUR</b><br>"
                                  f"Report foncier 10 ans : <b>{fr(r_im['deficit_report_foncier'])} EUR</b><br>")
                    st.markdown(f"""<div class="card"><h4>Foncier reel (2044)</h4>
                    Charges totales : {fr(r_im['total_charges'])} EUR<br>
                    <b style="color:{col_r}">Resultat : {fr(r_im['resultat'])} EUR</b><br>
                    {def_html}IR estime : {fr(int(r_im['imposable']*tmi_dir/100))} EUR</div>""",unsafe_allow_html=True)
                elif "LMNP Micro" in itype:
                    r_im = dm.calculer_lmnp(rfb,lmnp_cl,'micro')
                    elig = "OK" if r_im['eligible'] else f"Depasse {fr(r_im['seuil'])} EUR"
                    st.markdown(f"""<div class="card"><h4>LMNP Micro-BIC — {r_im['type_bien']}</h4>
                    Abattement {r_im['abattement_pct']} % : -{fr(rfb-r_im['imposable'])} EUR<br>
                    <b>Imposable : {fr(r_im['imposable'])} EUR</b><br>
                    IR : {fr(int(r_im['imposable']*tmi_dir/100))} EUR | PS : {fr(r_im['ps'])} EUR | {elig}
                    </div>""",unsafe_allow_html=True)
                elif "LMNP Reel" in itype:
                    r_im = dm.calculer_lmnp(rfb,False,'reel',ch_lmnp,am_lmnp)
                    col_r = "#4ade80" if r_im['benefice']>=0 else "#f87171"
                    st.markdown(f"""<div class="card"><h4>LMNP Reel</h4>
                    Charges : {fr(ch_lmnp)} | Amort. : {fr(am_lmnp)} EUR<br>
                    <b style="color:{col_r}">Benefice : {fr(r_im['imposable'])} EUR</b><br>
                    {"Deficit reportable 10 ans : "+fr(r_im['deficit'])+" EUR<br>" if r_im['deficit'] else ""}
                    IR estime : {fr(int(r_im['imposable']*tmi_dir/100))} EUR</div>""",unsafe_allow_html=True)
                elif "LMP" in itype:
                    r_im = dm.calculer_lmp(rfb,ch_lmp,am_lmp,aut_rev)
                    col_r = "#4ade80" if r_im['benefice']>=0 else "#f87171"
                    avts = "".join(f"<li style='font-size:.82rem'>{a}</li>" for a in r_im['avantages'])
                    st.markdown(f"""<div class="card"><h4>LMP</h4>
                    Statut LMP : <b style="color:{'#4ade80' if r_im['statut_lmp'] else '#f87171'}">{'Atteint' if r_im['statut_lmp'] else 'Non atteint'}</b><br>
                    <b style="color:{col_r}">Benefice : {fr(r_im['imposable'])} EUR</b><br>
                    {"Deficit imputable : "+fr(r_im['deficit'])+" EUR<br>" if r_im['deficit'] and r_im['statut_lmp'] else ""}
                    <ul style="margin:.4rem 0 0 1rem;color:#94a3b8">{avts}</ul></div>""",unsafe_allow_html=True)
                elif "SCI a l'IR" in itype:
                    r_im = dm.calculer_sci_ir(rfb)
                    col_r = "#4ade80" if rfb>=0 else "#f87171"
                    def_s = (f"Deficit imputable RNG : {fr(r_im['deficit_imputable_rng'])} EUR<br>" if r_im['deficit'] else "")
                    st.markdown(f"""<div class="card"><h4>SCI a l'IR</h4>
                    <b style="color:{col_r}">Resultat : {fr(rfb)} EUR</b><br>
                    {def_s}IR estime : {fr(int(r_im['imposable']*tmi_dir/100))} EUR | PS : {fr(r_im['ps'])} EUR<br>
                    <i style="color:#64748b">{r_im['note']}</i></div>""",unsafe_allow_html=True)
                else:  # SCI IS
                    r_im = dm.calculer_sci_is(rfb,sci_qp)
                    st.markdown(f"""<div class="card"><h4>SCI a l'IS</h4>
                    IS : <b style="color:#f87171">{fr(r_im['is_total'])} EUR</b> ({r_im['taux_effectif']:.2f} %)<br>
                    Benefice net : {fr(r_im['benefice_net'])} EUR<br>
                    Dividende potentiel ({int(sci_qp*100)} %) : <b>{fr(r_im['dividende_potentiel'])} EUR</b><br>
                    <i style="color:#64748b">{r_im['note']}</i></div>""",unsafe_allow_html=True)

        with dt5:
            sg1, sg2 = st.columns(2)
            with sg1:
                ben_avo = st.number_input("Benefice avant IS EUR",0,5000000,120000,5000,key="ben_avo")
                rem_sg  = st.number_input("Remuneration (strategie A) EUR",0,500000,70000,5000,key="rem_sg")
            with sg2:
                if ben_avo:
                    r_sg = dm.simuler_remuneration_vs_dividendes(ben_avo,rem_sg,tmi_dir)
                    sa = r_sg['strategie_a']; sb = r_sg['strategie_b']; ms = r_sg['meilleure']
                    for lbl, s, c in [("A — Remuneration", sa, "#60a5fa" if ms=="A" else "#475569"),
                                       ("B — Dividendes PFU", sb, "#4ade80" if ms=="B" else "#475569")]:
                        best = "🏆 " if (ms=="A" and "A" in lbl) or (ms=="B" and "B" in lbl) else ""
                        st.markdown(f"""<div class="card" style="border-color:{c}">
                        <h4 style="color:{c}">{best}{lbl}</h4>
                        IS societe : {fr(s['is_societe'])} EUR | IR/PFU : {fr(s.get('ir_personnel',s.get('pfu',0)))} EUR<br>
                        <b>Cout total : {fr(s['cout_total'])} EUR | Net percu : {fr(s['net_percu'])} EUR</b>
                        </div>""", unsafe_allow_html=True)
                    st.success(f"Recommandation Strategie **{ms}** — economie : **{fr(r_sg['economie'])} EUR**")

    # ── OPTIMISATION FISCALE ─────────────────────────────────────────
    with tab_opt:
        st.markdown("### Optimisation fiscale avancee pour dirigeant")
        st.markdown("Obtenez des recommandations personnalisees basees sur votre situation.")
        op1, op2 = st.columns(2)
        with op1:
            ben_opt = st.number_input("Benefice annuel de la societe EUR",0,5000000,150000,5000,key="ben_opt")
            rem_opt_in = st.number_input("Remuneration actuelle EUR",0,500000,70000,5000,key="rem_opt_in")
            ca_opt = st.number_input("Chiffre d'affaires EUR",0,10000000,300000,10000,key="ca_opt")
        with op2:
            tmi_opt = st.select_slider("Votre TMI",[0,11,30,41,45],30,key="tmi_opt")
            stat_opt = st.selectbox("Statut actuel",
                ["sarl_tns","president_sas","ae_bic","ae_bnc","tns_reel"],
                format_func={"sarl_tns":"SARL (Gerant majoritaire TNS)",
                    "president_sas":"SAS/SASU (President assimile salarie)",
                    "ae_bic":"Auto-entrepreneur BIC","ae_bnc":"Auto-entrepreneur BNC",
                    "tns_reel":"TNS regime reel (EI/EURL)"}.get,
                key="stat_opt")
            type_act_opt = st.selectbox("Type d'activite",
                ["services","vente","mixte"], key="type_act_opt")

        if ben_opt > 0 and st.button("Analyser et generer les recommandations", type="primary"):
            opts = dm.optimisation_fiscale({
                'benefice': ben_opt, 'remuneration': rem_opt_in,
                'tmi': tmi_opt, 'statut_actuel': stat_opt,
                'ca': ca_opt, 'type_activite': type_act_opt,
            })
            st.markdown(f"#### {len(opts)} recommandations identifiees")
            for i, opt in enumerate(opts, 1):
                ic = impact_color(opt['impact'])
                pour_html = "".join(f"<li style='color:#4ade80;font-size:.82rem'>{p}</li>" for p in opt['pour'])
                contre_html = "".join(f"<li style='color:#f87171;font-size:.82rem'>{c}</li>" for c in opt['contre'])
                gain_str = (f" — Gain estime : <b style='color:#f59e0b'>{fr(opt['gain_estime'])} EUR</b>"
                            if opt['gain_estime'] > 0 else "")
                st.markdown(f"""<div class="opt-card" style="border-left:4px solid {ic}">
                <h5 style="color:{ic}">{i}. {opt['titre']}
                <span class="badge" style="background:{ic}22;color:{ic}">{opt['impact']}</span>
                {gain_str}</h5>
                <p style="color:#94a3b8;font-size:.85rem;margin:.3rem 0">{opt['detail']}</p>
                <p style="color:#60a5fa;font-size:.82rem;margin:.2rem 0"><b>Action :</b> {opt['action']}</p>
                <div style="display:flex;gap:2rem;margin-top:.4rem">
                <div><b style="color:#4ade80;font-size:.8rem">Pour</b><ul style="margin:.2rem 0 0 1rem">{pour_html}</ul></div>
                <div><b style="color:#f87171;font-size:.8rem">Contre</b><ul style="margin:.2rem 0 0 1rem">{contre_html}</ul></div>
                </div></div>""", unsafe_allow_html=True)

        st.markdown("""<div class="src">Sources : BOI-BIC, BOI-BNC, BOI-RFPI, BOI-RPPM | CGI art. 219, 200A, 163 quinquies D | Calculs indicatifs — Consultez un expert-comptable.</div>""",
                    unsafe_allow_html=True)

    # ── PDF DIRIGEANT ─────────────────────────────────────────────────
    with tab_dir_pdf:
        st.markdown("### Rapport PDF — Revenus de dirigeant")
        st.markdown("""
        Le rapport inclura :
        - Votre statut social et comparaison des charges par statut
        - Calcul IS, fiscalite dividendes
        - BIC / BNC / Revenus immobiliers renseignes
        - Recommandations d'optimisation
        """)
        if st.button("Generer le rapport dirigeant PDF", type="primary"):
            with st.spinner("Generation..."):
                try:
                    from rapport_pdf import GenererRapportDirigeantPDF
                    gen_d = GenererRapportDirigeantPDF()
                    profil_dir = {
                        'statut': stat_opt if 'stat_opt' in dir() else statut_dir,
                        'remuneration': rem_ts if 'rem_ts' in dir() else 0,
                        'tmi': tmi_dir,
                        'benefice': res_fisc if 'res_fisc' in dir() else 0,
                        'dividendes': div_b if 'div_b' in dir() else 0,
                    }
                    pdf_bytes = gen_d.generer(profil_dir, dm)
                    b64 = base64.b64encode(pdf_bytes).decode()
                    href = (f'<a href="data:application/pdf;base64,{b64}" '
                            f'download="rapport_dirigeant_2026.pdf" '
                            f'style="display:inline-block;background:#1d4ed8;color:white;'
                            f'padding:.8rem 2rem;border-radius:8px;text-decoration:none;'
                            f'font-weight:700">Telecharger le rapport dirigeant PDF</a>')
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("Rapport genere !")
                except Exception as e:
                    st.error(f"Erreur : {e}")
                    raise

# ══════════════════════════════════════════════════════════════════════
# MODE IRPP (foyer seul ou comparaison)
# ══════════════════════════════════════════════════════════════════════
else:
    comp_mode = (mode == "Comparaison avec un enfant majeur (rattachement vs foyer independant)")

    if comp_mode:
        tabs_irpp = st.tabs(["👨\u200d👩\u200d👧  Mon Foyer","💰  Deductions","🎓  Enfant Majeur","💡  Conseils","📊  Resultats","📄  PDF"])
    else:
        tabs_irpp = st.tabs(["👨\u200d👩\u200d👧  Mon Foyer","💰  Deductions","💡  Conseils","📊  Resultats","📄  PDF"])
        tabs_irpp = list(tabs_irpp)
        tabs_irpp.insert(2, None)

    tab_foyer, tab_ded, tab_enf, tab_conseils, tab_res, tab_pdf = tabs_irpp

    # ── FOYER ────────────────────────────────────────────────────────
    with tab_foyer:
        st.markdown("### Situation familiale")
        f1, f2 = st.columns(2)
        with f1:
            situation = st.selectbox("Statut matrimonial",
                ["Celibataire / Divorce(e)","Marie(e) / Pacse(e)","Veuf(ve)"], key="situation")
            invalide = st.checkbox("Carte d'invalidite >= 80 % (+0,5 part)", key="invalide")
        with f2:
            nb_enfants = st.number_input("Enfants mineurs a charge", 0, 10, 0, key="nb_enfants")
            parent_isole = False
            if situation in ("Celibataire / Divorce(e)","Veuf(ve)") and nb_enfants > 0:
                parent_isole = st.checkbox("Parent isole (case T) +1 part 1er enfant", key="parent_isole")

        st.markdown("---")
        st.markdown("### Revenus 2024 — montants bruts avant abattement")

        # D1
        st.markdown("**Declarant 1**")
        r1a, r1b, r1c = st.columns(3)
        with r1a:
            sal1 = st.number_input("Salaires EUR",0,500000,45000,500,help="Case 1AJ",key="sal1")
        with r1b:
            pen1 = st.number_input("Pensions EUR",0,200000,0,200,help="Case 1AS",key="pen1")
        with r1c:
            hsup1 = st.number_input("dont Heures sup EUR",0,7500,0,100,help="Case 1GH",key="hsup1")
        with st.expander("Frais pro — Declarant 1"):
            fr1, mfr1 = saisie_frais_reels("d1", sal1)

        # D2
        sal2 = pen2 = hsup2 = 0; fr2 = False; mfr2 = 0
        if situation == "Marie(e) / Pacse(e)":
            st.markdown("**Declarant 2**")
            r2a, r2b, r2c = st.columns(3)
            with r2a: sal2 = st.number_input("Salaires EUR",0,500000,0,500,help="Case 1BJ",key="sal2")
            with r2b: pen2 = st.number_input("Pensions EUR",0,200000,0,200,help="Case 1BS",key="pen2")
            with r2c: hsup2 = st.number_input("dont Heures sup EUR",0,7500,0,100,help="Case 1HH",key="hsup2")
            with st.expander("Frais pro — Declarant 2"):
                fr2, mfr2 = saisie_frais_reels("d2", sal2)

        # D3+ : Enfants majeurs rattaches
        st.markdown("---")
        st.markdown("### Enfants majeurs rattaches au foyer (Declarants 3+)")
        st.caption("Un enfant majeur rattache voit ses revenus integres au foyer (+0,5 part / +abattement 6 794 EUR).")
        nb_rat = st.number_input("Nombre d'enfants majeurs rattaches au foyer",0,3,0,key="nb_rat")
        enfants_rattaches_data = []
        for i in range(int(nb_rat)):
            with st.expander(f"Enfant majeur rattache n°{i+1}"):
                era, erb = st.columns(2)
                with era:
                    sal_r = st.number_input(f"Salaires EUR",0,200000,0,500,key=f"sal_rat_{i}")
                    pen_r = st.number_input(f"Pensions EUR",0,100000,0,200,key=f"pen_rat_{i}")
                    hs_r  = st.number_input(f"Heures sup EUR",0,7500,0,100,key=f"hs_rat_{i}")
                with erb:
                    etud_r = st.checkbox("Etudiant (exo. 5 301 EUR)", key=f"etud_rat_{i}")
                    exo_r  = min(sal_r, moteur.JOBS_ETUDIANTS_EXONERATION) if etud_r else 0
                    fr_r   = st.checkbox("Frais reels", key=f"fr_rat_{i}")
                    mfr_r  = st.number_input("Montant FR EUR",0,20000,0,500,key=f"mfr_rat_{i}") if fr_r else 0
                    if etud_r and exo_r:
                        st.info(f"Exoneration : {fr(exo_r)} EUR")
                enfants_rattaches_data.append({
                    'salaire': sal_r, 'pension': pen_r, 'heures_sup': hs_r,
                    'exoneration_etudiant': exo_r, 'frais_reels': fr_r, 'montant_fr': mfr_r,
                })

        # Autres revenus (placements)
        st.markdown("---")
        autres_rev_on = st.checkbox("J'ai d'autres types de revenus (placements financiers, assurance vie, PEA...)", key="autres_rev_on")
        ar_data = {}
        if autres_rev_on:
            st.markdown("#### Revenus de placements financiers")
            ar1, ar2, ar3 = st.columns(3)
            with ar1:
                st.markdown("**Assurance Vie**")
                av_gain = st.number_input("Gains sur rachats EUR",0,500000,0,500,key="av_gain")
                av_duree = st.number_input("Duree contrat (annees)",0,50,9,1,key="av_duree")
                av_vers = st.number_input("Versements totaux EUR",0,1000000,50000,5000,key="av_vers")
            with ar2:
                st.markdown("**PEA**")
                pea_gain = st.number_input("Gains PEA EUR",0,500000,0,500,key="pea_gain")
                pea_age  = st.number_input("Age du PEA (annees)",0,40,6,1,key="pea_age")
                pea_clot = st.checkbox("Cloture du PEA",key="pea_clot")
            with ar3:
                st.markdown("**Compte-Titres (CTO)**")
                cto_pv  = st.number_input("Plus-values EUR",0,500000,0,500,key="cto_pv")
                cto_div = st.number_input("Dividendes EUR",0,200000,0,200,key="cto_div")
            ar_data = {'av_gain': av_gain, 'av_duree': av_duree, 'av_vers': av_vers,
                       'pea_gain': pea_gain, 'pea_age': pea_age, 'pea_clot': pea_clot,
                       'cto_pv': cto_pv, 'cto_div': cto_div}

    # ── DEDUCTIONS ───────────────────────────────────────────────────
    with tab_ded:
        st.markdown("### Deductions du revenu global")
        da, db = st.columns(2)
        with da:
            per = st.number_input("Versements PER EUR",0,80000,0,500,
                help="Cases 6NS/6NT/6NU",key="per")
            pen_versee = st.number_input("Pension alimentaire versee EUR",0,20000,0,200,
                help="Case 6GI — plafond 6 794 EUR",key="pen_versee")
        with db:
            cot_synd = st.number_input("Cotisations syndicales EUR",0,2000,0,50,
                help="Case 7AC — credit 66 %, plafond 1 % salaires",key="cot_synd")
        st.markdown("---")
        st.markdown("### Dons")
        dc, dd, de = st.columns(3)
        with dc: dons_75 = st.number_input("Dons 75 % EUR",0,5000,0,50,help="Case 7UD",key="dons_75")
        with dd: dons_mayo = st.number_input("Dons Mayotte 75 % EUR",0,5000,0,50,help="Case 7UM",key="dons_mayo")
        with de: dons_66 = st.number_input("Dons 66 % EUR",0,50000,0,50,help="Case 7VC",key="dons_66")
        st.markdown("---")
        st.markdown("### Credits d'impot")
        df2, dg2 = st.columns(2)
        with df2:
            nb_enf6 = st.number_input("Enfants < 6 ans au 01/01/2024",0,5,0,key="nb_enf6")
            res_alt = False; frais_garde = 0
            if nb_enf6 > 0:
                res_alt = st.checkbox("Residence alternee",key="res_alt")
                frais_garde = st.number_input("Frais garde EUR",0,15000,0,100,
                    help="Cases 7GA-7GC — credit 50 %",key="garde")
        with dg2:
            prem_annee = st.checkbox("1ere annee emploi domicile",key="prem_annee")
            emploi_dom = st.number_input("Emploi domicile EUR",0,25000,0,200,
                help="Cases 7DB/7DQ — credit 50 %",key="emp_dom")

    # ── ENFANT MAJEUR ────────────────────────────────────────────────
    profil_enfant = None; comparaison = None; res_enfant_seul = None
    etudiant_enf = False; exo_etud_enf = 0

    if comp_mode and tab_enf is not None:
        with tab_enf:
            st.markdown("### Profil fiscal de l'enfant majeur")
            st.markdown("**Scenario A** = ses revenus integres dans votre foyer (+0,5 part)  |  **Scenario B** = sa propre declaration independante")
            et1, et2, et3 = st.tabs(["Situation & Revenus","Deductions & Credits","Statut & Pension"])
            with et1:
                ea, eb_c = st.columns(2)
                with ea:
                    sit_enf = st.selectbox("Statut matrimonial",
                        ["Celibataire / Divorce(e)","Marie(e) / Pacse(e)","Veuf(ve)"],key="sit_enf")
                    nb_enf_enf = st.number_input("Ses propres enfants",0,10,0,key="enf_enf")
                    pi_enf = False
                    if sit_enf in ("Celibataire / Divorce(e)","Veuf(ve)") and nb_enf_enf > 0:
                        pi_enf = st.checkbox("Parent isole",key="pi_enf")
                    inv_enf = st.checkbox("Invalide >= 80 %",key="inv_enf")
                with eb_c:
                    sal1_enf = st.number_input("Salaires EUR",0,200000,18000,500,help="Case 1AJ",key="sal1_enf")
                    pen1_enf = st.number_input("Pensions EUR",0,100000,0,200,help="Case 1AS",key="pen1_enf")
                    hsup1_enf= st.number_input("Heures sup EUR",0,7500,0,100,help="Case 1GH",key="hsup1_enf")
                    sal2_enf = pen2_enf = hsup2_enf = 0
                    if sit_enf == "Marie(e) / Pacse(e)":
                        sal2_enf = st.number_input("Salaires conj. EUR",0,200000,0,500,key="sal2_enf")
                        pen2_enf = st.number_input("Pensions conj. EUR",0,100000,0,200,key="pen2_enf")
                        hsup2_enf= st.number_input("Heures sup conj. EUR",0,7500,0,100,key="hsup2_enf")
                with st.expander("Frais pro — Enfant D1"):
                    fr1_enf, mfr1_enf = saisie_frais_reels("enf_d1", sal1_enf)
                fr2_enf = False; mfr2_enf = 0
                if sit_enf == "Marie(e) / Pacse(e)" and sal2_enf > 0:
                    with st.expander("Frais pro — Enfant D2"):
                        fr2_enf, mfr2_enf = saisie_frais_reels("enf_d2", sal2_enf)
            with et2:
                ec1, ec2 = st.columns(2)
                with ec1:
                    per_enf = st.number_input("PER EUR",0,20000,0,200,key="per_enf")
                    cot_synd_enf = st.number_input("Syndicales EUR",0,1000,0,50,key="synd_enf")
                    dons_75_enf = st.number_input("Dons 75 % EUR",0,2000,0,50,key="d75_enf")
                    dons_66_enf = st.number_input("Dons 66 % EUR",0,10000,0,50,key="d66_enf")
                with ec2:
                    nb_enf6_enf = st.number_input("Ses enfants < 6 ans",0,5,0,key="enf6_enf")
                    garde_enf = st.number_input("Frais garde EUR",0,10000,0,100,key="garde_enf") if nb_enf6_enf > 0 else 0
                    emploi_enf = st.number_input("Emploi domicile EUR",0,15000,0,200,key="emp_enf")
            with et3:
                eg1, eg2 = st.columns(2)
                with eg1:
                    etudiant_enf = st.checkbox("Enfant etudiant (< 26 ans)",key="etudiant_enf",
                        help="Exoneration 5 301 EUR sur emplois etudiants, art. 81 bis CGI")
                    if etudiant_enf:
                        niveau_enf = st.selectbox("Niveau d'etudes",list(moteur.SCOLARITE.keys()),key="niv_enf")
                        st.success(f"Exoneration emploi etudiant : {fr(min(sal1_enf,5301))} EUR | Reduction scolarite (Scenario A) : {moteur.SCOLARITE.get(niveau_enf,183)} EUR")
                    else:
                        niveau_enf = list(moteur.SCOLARITE.keys())[-1]
                with eg2:
                    pension_enf = st.slider("Pension potentielle EUR",0,6794,6794,100,key="pension_enf",
                        help="Deductible chez vous (6GI) — Imposable chez l'enfant (1AS)")
                    st.markdown("- Chez vous : deductible **case 6GI**\n- Chez l'enfant : imposable **case 1AS**\n- Plafond legal : **6 794 EUR**")

            exo_etud_enf = min(sal1_enf, moteur.JOBS_ETUDIANTS_EXONERATION) if etudiant_enf else 0
            profil_enfant = {
                'situation': sit_enf, 'nb_enfants': nb_enf_enf,
                'invalide_declarant': inv_enf, 'parent_isole': pi_enf,
                'revenu_salaire_declarant': sal1_enf, 'revenu_pension_declarant': pen1_enf,
                'revenu_salaire_conjoint': sal2_enf, 'revenu_pension_conjoint': pen2_enf,
                'heures_sup_declarant': hsup1_enf, 'heures_sup_conjoint': hsup2_enf,
                'frais_reels': fr1_enf, 'montant_frais_reels_1': mfr1_enf,
                'frais_reels_2': fr2_enf, 'montant_frais_reels_2': mfr2_enf,
                'versement_per': per_enf, 'cotisations_syndicales': cot_synd_enf,
                'dons_60_75': dons_75_enf, 'dons_mayotte': 0, 'dons_60': dons_66_enf,
                'nb_enfants_moins_6': nb_enf6_enf, 'residence_alternee': False,
                'frais_garde': garde_enf, 'premiere_annee_emploi': False,
                'emploi_domicile': emploi_enf,
                'etudiant': etudiant_enf, 'exoneration_emploi_etudiant': exo_etud_enf,
                'niveau_etude': niveau_enf, 'pension_recue': pension_enf,
            }
    else:
        sit_enf="Celibataire / Divorce(e)"; nb_enf_enf=0; pi_enf=inv_enf=False
        sal1_enf=pen1_enf=sal2_enf=pen2_enf=0; hsup1_enf=hsup2_enf=0
        fr1_enf=fr2_enf=False; mfr1_enf=mfr2_enf=0
        per_enf=cot_synd_enf=dons_75_enf=dons_66_enf=0
        nb_enf6_enf=garde_enf=emploi_enf=0
        niveau_enf=list(moteur.SCOLARITE.keys())[-1]; pension_enf=6794

    # ── CALCUL PRINCIPAL ─────────────────────────────────────────────
    profil = {
        'situation': situation, 'nb_enfants': nb_enfants,
        'invalide_declarant': invalide, 'parent_isole': parent_isole,
        'revenu_salaire_declarant': sal1, 'revenu_pension_declarant': pen1,
        'revenu_salaire_conjoint': sal2, 'revenu_pension_conjoint': pen2,
        'heures_sup_declarant': hsup1, 'heures_sup_conjoint': hsup2,
        'frais_reels': fr1, 'montant_frais_reels_1': mfr1,
        'frais_reels_2': fr2, 'montant_frais_reels_2': mfr2,
        'versement_per': per, 'cotisations_syndicales': cot_synd,
        'pension_alimentaire_versee': pen_versee,
        'dons_60_75': dons_75, 'dons_mayotte': dons_mayo, 'dons_60': dons_66,
        'nb_enfants_moins_6': nb_enf6, 'residence_alternee': res_alt,
        'frais_garde': frais_garde, 'premiere_annee_emploi': prem_annee,
        'emploi_domicile': emploi_dom,
        'enfants_rattaches': enfants_rattaches_data,
    }
    res      = moteur.calculer(profil)
    conseils = moteur.generer_conseils(profil, res)

    if comp_mode and profil_enfant:
        pe_seul = {k:v for k,v in profil_enfant.items() if k not in ('niveau_etude','pension_recue','etudiant')}
        pe_seul['exoneration_emploi_etudiant'] = exo_etud_enf
        res_enfant_seul = moteur.calculer(pe_seul)
        sc_obj      = ScenarioEnfantMajeur(moteur)
        comparaison = sc_obj.comparer(profil, profil_enfant)

    # Calcul autres revenus
    ar_resultats = {}
    if autres_rev_on and ar_data:
        tmi_foyer = res['taux_marginal'] or 11
        if ar_data.get('av_gain',0) > 0:
            ar_resultats['av'] = ar_engine.calculer_assurance_vie(
                ar_data['av_gain'], ar_data['av_duree'],
                ar_data['av_vers'], situation, tmi_foyer)
        if ar_data.get('pea_gain',0) > 0:
            ar_resultats['pea'] = ar_engine.calculer_pea(
                ar_data['pea_gain'], ar_data['pea_age'], ar_data['pea_clot'])
        if ar_data.get('cto_pv',0) > 0 or ar_data.get('cto_div',0) > 0:
            ar_resultats['cto'] = ar_engine.calculer_cto(
                ar_data.get('cto_pv',0), ar_data.get('cto_div',0), tmi_foyer)

    # ── CONSEILS ─────────────────────────────────────────────────────
    with tab_conseils:
        st.markdown("### Conseils fiscaux personnalises")
        tmi_foyer = res['taux_marginal']
        rni_foyer = res['revenu_imposable']
        inet_foyer = res['impot_net']
        total_b   = sal1 + pen1 + sal2 + pen2

        st.markdown(f"""
        Votre situation : TMI **{tmi_foyer} %** | RNI **{fr(rni_foyer)} EUR** | Impot net **{fr(inet_foyer)} EUR** | Taux moyen **{res['taux_moyen']:.2f} %**
        """)

        # ─ Actions rapides ─
        st.markdown("#### Actions rapides — Impact immediat")
        actions = []

        reste_per = res['plafond_per'] - per
        if reste_per > 500 and tmi_foyer >= 30:
            eco_per = reste_per * tmi_foyer / 100
            actions.append({'icone':'💰','prio':'Tres eleve','col':'#f59e0b',
                'titre':f"PER : {fr(reste_per)} EUR disponibles => economie {fr(eco_per)} EUR",
                'detail':f"Votre plafond PER est de {fr(res['plafond_per'])} EUR. "
                          f"A TMI {tmi_foyer} %, chaque euro verse reduit votre impot de {tmi_foyer/100:.0%}. "
                          f"Cases 6NS/6NT/6NU.",
                'case':'6NS'})

        if not fr1 and sal1 > 20000:
            forfait = res['abattement_salaires_1'] + res['abattement_salaires_2']
            actions.append({'icone':'📋','prio':'Moyen','col':'#3b82f6',
                'titre':f"Verifier les frais reels (forfait actuel : {fr(forfait)} EUR)",
                'detail':"Si vos frais reels (km, repas, formation, teletravail) depassent ce montant, "
                          "vous pouvez opter pour les frais reels. Utilisez le calculateur dans Mon Foyer.",
                'case':'1AK'})

        if dons_75 == 0 and dons_66 == 0 and inet_foyer > 0:
            plaf_d = rni_foyer * 0.20
            actions.append({'icone':'❤️','prio':'Facile','col':'#ec4899',
                'titre':f"Dons : reduction jusqu'a {fr(plaf_d*.66)} EUR possible",
                'detail':f"Plafond dons 66 % : {fr(plaf_d)} EUR de dons => {fr(plaf_d*.66)} EUR de reduction. "
                          "Case 7VC. Pour 100 EUR donnes, votre impot baisse de 66 EUR.",
                'case':'7VC'})

        if emploi_dom == 0:
            actions.append({'icone':'🏠','prio':'Facile','col':'#8b5cf6',
                'titre':"Emploi domicile : credit d'impot 50 % sur 12 000 EUR",
                'detail':"Menage, jardinage, garde, soutien scolaire, assistante de vie... "
                          "50 % des sommes versees en credit d'impot. Max 6 000 EUR de credit. Cases 7DB/7DQ.",
                'case':'7DB'})

        if nb_enf6 > 0 and frais_garde == 0:
            actions.append({'icone':'👶','prio':'Facile','col':'#06b6d4',
                'titre':"Frais de garde : credit 50 % sur 3 500 EUR par enfant",
                'detail':f"Vous avez {nb_enf6} enfant(s) de moins de 6 ans. Credit d'impot 50 % "
                          "sur les frais de creche, assistante maternelle. Cases 7GA-7GC.",
                'case':'7GA'})

        if tmi_foyer == 30:
            surplus = res['quotient_familial'] - 29315
            if 0 < surplus < 10000:
                eco_t = surplus * res['nb_parts']
                actions.append({'icone':'📉','prio':'Eleve','col':'#3b82f6',
                    'titre':f"Repasser en tranche 11 % : versement PER de {fr(eco_t)} EUR",
                    'detail':f"Votre quotient est a {fr(surplus)} EUR au-dessus du seuil 11 %. "
                              f"Un versement PER de {fr(eco_t)} EUR vous ferait economiser {fr(eco_t*0.19)} EUR. Case 6NS.",
                    'case':'6NS'})

        if cot_synd == 0 and (sal1+sal2) > 5000:
            actions.append({'icone':'🤝','prio':'Facile','col':'#6b7280',
                'titre':"Cotisations syndicales : credit 66 %",
                'detail':f"Si vous versez des cotisations, 66 % sont deductibles. "
                          f"Plafond : {fr((sal1+sal2)*0.01)} EUR (1 % des salaires). Case 7AC.",
                'case':'7AC'})

        if nb_rat > 0:
            actions.append({'icone':'🎓','prio':'A verifier','col':'#8b5cf6',
                'titre':f"Enfants majeurs rattaches : verifiez l'interet du rattachement",
                'detail':f"Vous avez {nb_rat} enfant(s) rattache(s). "
                          "Utilisez le mode 'Comparaison enfant majeur' pour simuler les deux scenarios.",
                'case':'D'})

        for a in actions:
            st.markdown(f"""<div class="conseil-priority" style="background:{a['col']}11;border-color:{a['col']}">
            <b style="color:{a['col']}">{a['icone']} [{a['prio']}] {a['titre']}</b>
            <span class="badge" style="background:{a['col']}33;color:{a['col']};float:right">Case {a['case']}</span><br>
            <span style="color:#cbd5e1;font-size:.85rem">{a['detail']}</span>
            </div>""", unsafe_allow_html=True)

        if not actions:
            st.success("Votre situation semble deja bien optimisee !")

        # ─ Conseils patrimoniaux ─
        if autres_rev_on or total_b > 60000:
            st.markdown("---")
            st.markdown("#### Conseils patrimoniaux")
            age_est = st.slider("Votre age (pour conseils personnalises)", 20, 80, 45, key="age_c")
            cp = ar_engine.conseils_patrimoine(tmi_foyer, age_est, situation)
            for c in cp:
                ic2 = {"Eleve":"#3b82f6","Moyen":"#6b7280","Tres facile":"#4ade80","Facile":"#22c55e"}.get(c['facilite'],"#3b82f6")
                st.markdown(f"""<div class="conseil">
                <b>{c['titre']}</b>
                <span class="badge" style="background:{ic2}22;color:{ic2}">Impact : {c['impact']}</span>
                <span class="badge" style="background:#33415522;color:#94a3b8">{c['facilite']}</span><br>
                <span style="color:#fbbf24;font-size:.85rem">{c['detail']}</span></div>""",
                    unsafe_allow_html=True)

        # ─ Autres revenus ─
        if ar_resultats:
            st.markdown("---")
            st.markdown("#### Fiscalite de vos placements financiers")
            if 'av' in ar_resultats:
                av = ar_resultats['av']
                st.markdown(f"""<div class="card"><h4>Assurance Vie — {av['regime']}</h4>
                Gain : {fr(av['gain'])} EUR | Abattement : {fr(av['abattement_applicable'])} EUR<br>
                <b>PFU : {fr(av['pfu']['total'])} EUR (net {fr(av['pfu']['net'])} EUR)</b> |
                <b>Bareme : {fr(av['bareme']['total'])} EUR (net {fr(av['bareme']['net'])} EUR)</b><br>
                Recommande : <b style="color:#f59e0b">{av['meilleur']}</b> — economie : {fr(av['economie'])} EUR<br>
                <i style="color:#64748b;font-size:.82rem">{av['note']}</i></div>""",
                    unsafe_allow_html=True)
            if 'pea' in ar_resultats:
                pea = ar_resultats['pea']
                st.markdown(f"""<div class="card"><h4>PEA — {pea['regime']}</h4>
                Gain : {fr(pea['gain'])} EUR | IR : {fr(pea['ir'])} EUR | PS : {fr(pea['ps'])} EUR<br>
                <b style="color:#4ade80">Net : {fr(pea['net'])} EUR | Taux effectif : {pea['taux_effectif']} %</b><br>
                <i style="color:#64748b;font-size:.82rem">{pea['note']}</i></div>""",
                    unsafe_allow_html=True)
            if 'cto' in ar_resultats:
                cto = ar_resultats['cto']
                st.markdown(f"""<div class="card"><h4>Compte-Titres (CTO)</h4>
                PV : {fr(ar_data['cto_pv'])} EUR | Div : {fr(ar_data['cto_div'])} EUR<br>
                PFU : {fr(cto['pfu']['total'])} EUR (net {fr(cto['pfu']['net'])} EUR) |
                Bareme : {fr(cto['bareme']['total'])} EUR (net {fr(cto['bareme']['net'])} EUR)<br>
                Recommande : <b style="color:#f59e0b">{cto['meilleur']}</b> — economie : {fr(cto['economie'])} EUR<br>
                <i style="color:#64748b;font-size:.82rem">{cto['note']}</i></div>""",
                    unsafe_allow_html=True)

    # ── RESULTATS ─────────────────────────────────────────────────────
    with tab_res:
        st.markdown("### Votre simulation fiscale 2026")
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(kpi("Revenu Net Imposable",f"{fr(res['revenu_imposable'])} EUR","#93c5fd"),unsafe_allow_html=True)
        with k2: st.markdown(kpi("Impot brut",f"{fr(res['impot_brut'])} EUR","#f87171"),unsafe_allow_html=True)
        with k3: st.markdown(kpi("Decote",f"-{fr(res['decote'])} EUR","#4ade80"),unsafe_allow_html=True)
        with k4: st.markdown(kpi("IMPOT NET A PAYER",f"{fr(res['impot_net'])} EUR","#60a5fa"),unsafe_allow_html=True)

        st.markdown("")
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Taux moyen",f"{res['taux_moyen']:.2f} %")
        with m2: st.metric("TMI",f"{res['taux_marginal']} %")
        with m3: st.metric("Parts fiscales",f"{res['nb_parts']:.1f}")
        with m4:
            hstot = hsup1 + hsup2
            rat_tot = sum(e.get('salaire',0)+e.get('pension',0) for e in enfants_rattaches_data)
            if hstot: st.metric("Heures sup exonerees",f"{fr(hstot)} EUR")
            elif rat_tot: st.metric(f"{nb_rat} enfant(s) rattache(s)",f"{fr(rat_tot)} EUR integres")
            else: st.metric("Abattement total",f"{fr(res['abattement_applique'])} EUR")

        if nb_rat > 0:
            st.info(f"{nb_rat} enfant(s) majeur(s) rattache(s) : revenus integres = {fr(rat_tot)} EUR | abattement rattachement = {fr(nb_rat * 6794)} EUR | parts suppl. = +{nb_rat*0.5:.1f}")

        st.markdown('<div class="src">Bareme 2024 — DGFiP 2025 — Decote : 889 - 45,25 % x impot (cel.) — QF plafonne 1 791 EUR/demi-part</div>',unsafe_allow_html=True)

        with st.expander("Detail complet du calcul"):
            d1, d2 = st.columns(2)
            with d1:
                rows = [["Salaires bruts D1",f"{fr(sal1)} EUR"]]
                if hsup1: rows.append(["dont Heures sup D1",f"-{fr(hsup1)} EUR"])
                rows += [
                    ["Abattement salaires D1",f"-{fr(res['abattement_salaires_1'])} EUR"],
                    ["Pensions D1",f"{fr(pen1)} EUR"],
                ]
                if situation == "Marie(e) / Pacse(e)":
                    rows += [["Salaires D2",f"{fr(sal2)} EUR"],
                             ["Abattement D2",f"-{fr(res['abattement_salaires_2'])} EUR"]]
                for i,e in enumerate(enfants_rattaches_data):
                    rows.append([f"Enfant rattache {i+1} (sal+pen)",
                        f"{fr(e.get('salaire',0)+e.get('pension',0))} EUR"])
                rows += [
                    ["Deduction PER",f"-{fr(res['deduction_per'])} EUR"],
                    ["Abattement rattachement",f"-{fr(nb_rat*6794)} EUR"] if nb_rat else ["",""],
                    ["= RNI",f"{fr(res['revenu_imposable'])} EUR"],
                ]
                st.dataframe(pd.DataFrame([r for r in rows if r[1]], columns=["Etape","Montant"]),
                             hide_index=True, use_container_width=True)
            with d2:
                rows2=[
                    [f"Quotient (RNI / {res['nb_parts']:.1f} parts)",f"{fr(res['quotient_familial'])} EUR"],
                    ["Impot avant plafonnement",f"{fr(res['impot_avant_plafond'])} EUR"],
                    ["Plafonnement QF",f"-{fr(res['plafonnement_qf'])} EUR"],
                    ["Impot brut",f"{fr(res['impot_brut'])} EUR"],
                    ["Decote",f"-{fr(res['decote'])} EUR"],
                    ["Reductions & Credits",f"-{fr(res['reduction_dons_75']+res['reduction_dons_66']+res['credit_garde']+res['credit_emploi']+res['credit_syndicat'])} EUR"],
                    ["= IMPOT NET",f"{fr(res['impot_net'])} EUR"],
                ]
                st.dataframe(pd.DataFrame(rows2, columns=["Etape","Montant"]),
                             hide_index=True, use_container_width=True)

        g1, g2 = st.columns(2)
        with g1:
            tr = [t for t in res['detail_tranches'] if t['impot_tranche'] > 0]
            if tr:
                fig = go.Figure([go.Bar(
                    x=[t['label'] for t in tr], y=[t['impot_tranche'] for t in tr],
                    marker_color=['#1e3a5f','#1d4ed8','#3b82f6','#60a5fa','#93c5fd'][:len(tr)],
                    text=[f"{fr(t['impot_tranche'])} EUR" for t in tr],
                    textposition='outside', textfont=dict(color='#e2e8f0'))])
                fig.update_layout(title="Impot par tranche",height=300,
                    plot_bgcolor='#1e293b',paper_bgcolor='#1e293b',
                    font=dict(color='#e2e8f0'),showlegend=False)
                fig.update_yaxes(gridcolor='#334155')
                fig.update_xaxes(tickfont=dict(size=8))
                st.plotly_chart(fig, use_container_width=True)
        with g2:
            tb = res['revenu_total_brut']
            if tb > 0:
                fig2 = go.Figure(go.Pie(
                    labels=['Impot net','Revenu disponible'],
                    values=[res['impot_net'], max(0, tb-res['impot_net'])],
                    hole=0.55, marker_colors=['#dc2626','#1d4ed8'],
                    textfont=dict(color='#e2e8f0')))
                fig2.update_layout(title="Repartition",height=300,
                    plot_bgcolor='#1e293b',paper_bgcolor='#1e293b',
                    font=dict(color='#e2e8f0'),
                    annotations=[dict(text=f"{res['taux_moyen']:.1f} %<br>moyen",
                                      x=0.5,y=0.5,font_size=13,font=dict(color='#e2e8f0'),showarrow=False)])
                st.plotly_chart(fig2, use_container_width=True)

        # Comparaison
        if comp_mode and comparaison:
            st.markdown("---")
            st.markdown("### Comparaison enfant majeur")
            sc_a=comparaison['scenario_a']; sc_b=comparaison['scenario_b']
            meill=comparaison['meilleur_scenario']; eco=comparaison['economie']
            etud=comparaison.get('etudiant',False)
            pb=sc_b['parents']; eb=sc_b['enfant']

            ca_c, cb_c = st.columns(2)
            with ca_c:
                bc_a="#1d4ed8" if meill=="A" else "#334155"
                lignes_a=[
                    f"Parts foyer avec enfant : <b>{sc_a['nb_parts']:.1f}</b>",
                    f"Revenus enfant integres : <b>{fr(sc_a['revenus_enfant_integres'])} EUR</b>",
                ]
                if etud and sc_a.get('exoneration_etudiant',0):
                    lignes_a.append(f"Exoneration emploi etudiant : <b>-{fr(sc_a['exoneration_etudiant'])} EUR</b>")
                lignes_a += [
                    f"RNI foyer combine : <b>{fr(sc_a['rni'])} EUR</b>",
                    f"IR foyer avant reduction scol. : <b>{fr(sc_a['impot_net_avant_scol'])} EUR</b>",
                ]
                if etud:
                    lignes_a.append(f"Reduction scolarite ({sc_a['niveau_etude']}) : <b>-{sc_a['reduction_scolarite']} EUR</b>")
                st.markdown(f"""<div class="card" style="border-color:{bc_a}">
                <h4 style="color:#93c5fd">{'🏆 ' if meill=='A' else ''}Scenario A — Rattachement</h4>
                {"<br>".join(lignes_a)}<br><br>
                <span style="font-size:1.3rem;font-weight:700;color:#60a5fa">Impot net : {fr(sc_a['cout_total'])} EUR</span>
                </div>""", unsafe_allow_html=True)

            with cb_c:
                bc_b="#16a34a" if meill=="B" else "#334155"
                lignes_b_p=[
                    f"Parts parents (inchangees) : <b>{pb['nb_parts']:.1f}</b>",
                    f"Pension versee deductible (6GI) : <b>-{fr(pb.get('pension_versee',0))} EUR</b>",
                    f"IR parents : <b>{fr(pb['impot_net'])} EUR</b>",
                ]
                lignes_b_e=[f"Parts : <b>{eb['nb_parts']:.1f}</b>"]
                if etud and eb.get('exoneration_etudiant',0):
                    lignes_b_e.append(f"Exoneration emploi etudiant : <b>-{fr(eb['exoneration_etudiant'])} EUR</b>")
                lignes_b_e += [
                    f"Pension recue imposable (1AS) : <b>{fr(eb.get('pension_recue',0))} EUR</b>",
                    f"RNI enfant : <b>{fr(eb['revenu_imposable'])} EUR</b>",
                    f"TMI enfant : <b>{eb.get('taux_marginal',0)} %</b>",
                    f"IR enfant : <b>{fr(eb['impot_net'])} EUR</b>",
                ]
                st.markdown(f"""<div class="card" style="border-color:{bc_b}">
                <h4 style="color:#4ade80">{'🏆 ' if meill=='B' else ''}Scenario B — Foyer independant</h4>
                <b style="color:#94a3b8">Parents :</b><br>{"<br>".join(lignes_b_p)}<br><br>
                <b style="color:#94a3b8">Enfant :</b><br>{"<br>".join(lignes_b_e)}<br><br>
                <span style="font-size:1.3rem;font-weight:700;color:#4ade80">Total : {fr(sc_b['cout_total'])} EUR</span>
                </div>""", unsafe_allow_html=True)

            cls="verdict-a" if meill=="A" else "verdict-b"
            lab="Scenario A — Rattachement" if meill=="A" else "Scenario B — Foyer independant"
            col="#60a5fa" if meill=="A" else "#4ade80"
            st.markdown(f"""<div class="{cls}">
            <h3 style="color:{col};margin:0">Recommandation : {lab}</h3>
            <p style="margin:.4rem 0 0">Economie : <b>{fr(eco)} EUR</b></p></div>""",
                unsafe_allow_html=True)

            fig_c = go.Figure([
                go.Bar(name=f"A — Rattachement",x=["Cout fiscal"],y=[sc_a['cout_total']],
                       marker_color='#1d4ed8',text=f"{fr(sc_a['cout_total'])} EUR",
                       textposition='outside',textfont=dict(color='#e2e8f0')),
                go.Bar(name=f"B — Independant",x=["Cout fiscal"],y=[sc_b['cout_total']],
                       marker_color='#16a34a',text=f"{fr(sc_b['cout_total'])} EUR",
                       textposition='outside',textfont=dict(color='#e2e8f0')),
            ])
            fig_c.update_layout(barmode='group',height=260,
                plot_bgcolor='#1e293b',paper_bgcolor='#1e293b',font=dict(color='#e2e8f0'))
            st.plotly_chart(fig_c, use_container_width=True)

    # ── PDF ──────────────────────────────────────────────────────────
    with tab_pdf:
        st.markdown("### Bilan fiscal PDF")
        st.markdown("""
        - Resume de simulation + detail par tranche
        - **Guide des cases a renseigner** sur impots.gouv.fr
        - Conseils personnalises
        """ + ("- Comparaison enfant majeur incluse" if comp_mode and comparaison else ""))

        if st.button("Generer le bilan fiscal PDF", type="primary"):
            with st.spinner("Generation..."):
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
                            f'padding:.8rem 2rem;border-radius:8px;text-decoration:none;font-weight:700">'
                            f'Telecharger le rapport PDF</a>')
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("Rapport genere !")
                except Exception as e:
                    st.error(f"Erreur : {e}")
                    raise

        st.markdown('<div class="src" style="margin-top:1rem">Simulateur base sur Brochure Pratique DGFiP 2025 (Revenus 2024) | Pour information uniquement | <a href="https://www.impots.gouv.fr" target="_blank" style="color:#3b82f6">impots.gouv.fr</a></div>',unsafe_allow_html=True)
