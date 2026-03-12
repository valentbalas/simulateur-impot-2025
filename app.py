"""
Simulateur Impot sur le Revenu 2026 - Declaration revenus 2025
Dark theme | 6 onglets | IRPP complet | Dirigeants / Societes
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

# ─── Dark theme CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
/* Base dark */
.stApp,[data-testid="stAppViewContainer"]
  {background:#0f172a !important;color:#e2e8f0}
[data-testid="stHeader"]{background:#0f172a !important}
section[data-testid="stSidebar"]{background:#1e293b !important}

/* Inputs */
.stSelectbox>div>div, .stNumberInput>div>div>input,
.stTextInput>div>div>input, .stTextArea textarea
  {background:#1e293b !important;color:#e2e8f0 !important;
   border-color:#334155 !important}
.stCheckbox label{color:#e2e8f0 !important}
.stRadio label{color:#e2e8f0 !important}

/* Cards custom */
.card{background:#1e293b;border:1px solid #334155;border-radius:12px;
  padding:1.3rem;margin-bottom:.8rem}
.card h4{color:#93c5fd;margin:0 0 .6rem 0}

/* KPI box */
.kpi{background:#1e293b;border:1px solid #334155;border-radius:10px;
  padding:1rem;text-align:center}
.kpi-val{font-size:1.65rem;font-weight:700}
.kpi-lbl{font-size:.73rem;color:#94a3b8;margin-top:.2rem}

/* Tabs */
div[data-testid="stTabs"] [data-baseweb="tab-list"]
  {background:#1e293b;border-radius:10px;padding:.3rem}
div[data-testid="stTabs"] [data-baseweb="tab"]
  {color:#94a3b8;border-radius:8px;padding:.4rem 1rem;font-weight:500}
div[data-testid="stTabs"] [aria-selected="true"]
  {background:#1d4ed8 !important;color:white !important}

/* Tables */
.stDataFrame{background:#1e293b}
[data-testid="stTable"]{background:#1e293b}

/* Buttons */
.stButton>button{background:#1d4ed8;color:white;border:none;
  border-radius:8px;font-weight:600;padding:.55rem 1.4rem}
.stButton>button:hover{background:#2563eb}

/* Metrics */
[data-testid="stMetric"]{background:#1e293b;border-radius:8px;padding:.7rem 1rem}
[data-testid="stMetricLabel"]{color:#94a3b8}
[data-testid="stMetricValue"]{color:#e2e8f0}

/* Expanders */
.streamlit-expanderHeader{background:#1e293b !important;color:#e2e8f0 !important;
  border-radius:8px}
.streamlit-expanderContent{background:#1e293b !important}

/* Verdict boxes */
.verdict-a{background:#1e3a5f;border-left:4px solid #3b82f6;
  border-radius:0 8px 8px 0;padding:1rem;margin:.7rem 0}
.verdict-b{background:#14532d;border-left:4px solid #22c55e;
  border-radius:0 8px 8px 0;padding:1rem;margin:.7rem 0}

/* Conseil box */
.conseil{background:#1c1a09;border:1px solid #854d0e;border-radius:8px;
  padding:.8rem 1rem;margin:.35rem 0;color:#fef9c3}

/* Case badge */
.case-badge{background:#1e3a5f;color:#93c5fd;font-family:monospace;
  padding:.15rem .5rem;border-radius:4px;font-size:.78rem;
  display:inline-block;margin:.15rem}

/* Info/success overrides */
.stAlert{background:#1e293b !important;border-color:#334155 !important}

/* Source note */
.src{background:#1e293b;border-radius:6px;padding:.4rem .8rem;
  font-size:.74rem;color:#64748b;margin:.4rem 0}

/* Dividers */
hr{border-color:#334155}

/* Plotly bg */
.js-plotly-plot .plotly .bg{fill:#1e293b !important}
</style>
""", unsafe_allow_html=True)


# ─── Header ───────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#003189 0%,#1d4ed8 55%,#ed2939 100%);
  padding:1.4rem 2rem;border-radius:14px;color:white;text-align:center;
  margin-bottom:1.2rem;box-shadow:0 4px 20px rgba(29,78,216,.4)">
  <h1 style="margin:0;font-size:1.85rem;font-weight:700">
    🧮 Simulateur Impot sur le Revenu 2026</h1>
  <p style="margin:.3rem 0 0;opacity:.9;font-size:.9rem">
    Declaration 2026 &bull; Revenus 2025 &bull; Bareme officiel DGFiP (Brochure Pratique 2025)</p>
</div>
""", unsafe_allow_html=True)

# ─── Helpers ──────────────────────────────────────────────────────────
moteur   = MoteurImpot()
dirigeant_m = MoteurDirigeant()


def fr(val, dec=0):
    """Formatage nombre francais : separateur milliers espace, decimale virgule."""
    if val is None: return "-"
    if dec == 0:
        s = f"{abs(val):,.0f}".replace(",", "\u202f")
    else:
        s = f"{abs(val):,.{dec}f}"
        p = s.split(".")
        s = p[0].replace(",", "\u202f") + "," + p[1]
    return ("-\u202f" if val < 0 else "") + s


def kpi(label, val, color="#93c5fd"):
    return f"""<div class="kpi">
      <div class="kpi-val" style="color:{color}">{val}</div>
      <div class="kpi-lbl">{label}</div></div>"""


def saisie_frais_reels(prefix, salaire):
    """Retourne (frais_reels: bool, montant: float)"""
    mode = st.radio(
        "Mode deduction frais professionnels",
        ["Forfait 10 % (automatique)", "Frais reels justifies"],
        key=f"mode_{prefix}", horizontal=True)
    if "Forfait" in mode:
        forfait = max(moteur.ABATTEMENT_SALAIRES_MIN,
                      min(salaire * 0.10, moteur.ABATTEMENT_SALAIRES_MAX))
        st.caption(f"Abattement forfaitaire : **{fr(forfait)} EUR** (cases 1AK/1BK non renseignees)")
        return False, 0

    c1, c2 = st.columns(2)
    with c1:
        tveh = st.selectbox("Vehicule", ["thermique","electrique","moto","moto_electrique","cyclo"],
            format_func=lambda x:{"thermique":"Voiture thermique/hybride",
                "electrique":"Voiture electrique","moto":"Moto thermique",
                "moto_electrique":"Moto electrique","cyclo":"Cyclomoteur"}[x],
            key=f"tveh_{prefix}")
        cv = 5
        if tveh in ("thermique","electrique"):
            cv = st.select_slider("CV fiscaux", [3,4,5,6,7], 5, key=f"cv_{prefix}")
        elif "moto" in tveh:
            cv = st.selectbox("Cylindree", [2,5,99],
                format_func=lambda x:{2:"1-2 CV",5:"3-5 CV",99:"> 5 CV"}[x],
                key=f"cvm_{prefix}")
        km  = st.number_input("Km pro / an", 0, 100000, 0, 500, key=f"km_{prefix}")
        fkm = 0
        if km > 0:
            fkm = FraisReels.calculer_bareme_km(km, cv, tveh)
            st.info(f"Bareme km : **{fr(fkm)} EUR**")
    with c2:
        nb_rep   = st.number_input("Repas pro / an", 0, 300, 0, key=f"rep_{prefix}")
        prix_rep = st.number_input("Prix moyen repas EUR", 0.0, 50.0, 10.0, 0.5, key=f"px_{prefix}")
        frep     = max(0, (prix_rep - FraisReels.REPAS_VALEUR_FOYER) * nb_rep) if nb_rep else 0
        if nb_rep: st.info(f"Frais repas : **{fr(frep)} EUR**")
        jtt  = st.number_input("Jours teletravail", 0, 230, 0, key=f"tt_{prefix}")
        ftt  = FraisReels.calculer_teletravail(jtt) if jtt else 0
        if jtt: st.info(f"Teletravail : **{fr(ftt)} EUR**")

    dres = st.number_input("Double residence EUR", 0, 30000, 0, 200, key=f"dr_{prefix}")
    form = st.number_input("Formation pro EUR", 0, 20000, 0, 100, key=f"fo_{prefix}")
    mat  = st.number_input("Materiel pro EUR", 0, 20000, 0, 100, key=f"ma_{prefix}")
    aut  = st.number_input("Autres frais EUR", 0, 20000, 0, 100, key=f"au_{prefix}")

    total   = round(fkm + frep + ftt + dres + form + mat + aut)
    forfait = max(moteur.ABATTEMENT_SALAIRES_MIN,
                  min(salaire * 0.10, moteur.ABATTEMENT_SALAIRES_MAX))
    if total > 0:
        if total > forfait:
            st.success(f"Frais reels ({fr(total)} EUR) > forfait ({fr(forfait)} EUR) => gain : +{fr(total-forfait)} EUR")
            return True, total
        else:
            st.warning(f"Frais reels ({fr(total)} EUR) inferieurs au forfait ({fr(forfait)} EUR). Conservez le forfait.")
            return False, 0
    return False, 0


# ══════════════════════════════════════════════════════════════════════
# ONGLETS
# ══════════════════════════════════════════════════════════════════════
(tab_foyer, tab_ded, tab_enfant,
 tab_res, tab_dir, tab_pdf) = st.tabs([
    "👨‍👩‍👧  Mon Foyer",
    "💰  Deductions & Credits",
    "🎓  Enfant Majeur",
    "📊  Resultats IRPP",
    "🏢  Revenus Dirigeant",
    "📄  Export PDF",
])


# ══════════════════════════════════════════════════════════════════════
# ONGLET 1 — MON FOYER
# ══════════════════════════════════════════════════════════════════════
with tab_foyer:
    st.markdown("### Situation familiale")
    c1, c2 = st.columns(2)
    with c1:
        situation = st.selectbox("Statut matrimonial",
            ["Celibataire / Divorce(e)","Marie(e) / Pacse(e)","Veuf(ve)"],
            key="situation")
        invalide = st.checkbox("Carte d'invalidite >= 80 % (+0,5 part)", key="invalide")
    with c2:
        nb_enfants = st.number_input("Enfants mineurs a charge", 0, 10, 0, key="nb_enfants")
        parent_isole = False
        if situation in ("Celibataire / Divorce(e)","Veuf(ve)") and nb_enfants > 0:
            parent_isole = st.checkbox("Parent isole (case T) - +1 part pour le 1er enfant",
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
            help="Case 1GH — inclus dans salaires ci-dessus, plafond 7 500 EUR", key="hsup1")
        if hsup1:
            st.caption(f"Exoneration IR : {fr(min(hsup1,7500))} EUR")

    with st.expander("Frais professionnels reels — Declarant 1"):
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
            hsup2 = st.number_input("dont Heures sup EUR", 0, 7500, 0, 100,
                help="Case 1HH", key="hsup2")
        with st.expander("Frais professionnels reels — Declarant 2"):
            fr2, mfr2 = saisie_frais_reels("d2", sal2)

    st.markdown('<div class="src">Revenus imposables = Salaires - Heures sup exonerees - Abattement 10 % (ou frais reels)</div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# ONGLET 2 — DEDUCTIONS & CREDITS
# ══════════════════════════════════════════════════════════════════════
with tab_ded:
    st.markdown("### Deductions du revenu global")
    da, db = st.columns(2)
    with da:
        per = st.number_input("Versements PER EUR", 0, 80000, 0, 500,
            help="Cases 6NS/6NT/6NU — 10 % revenus, min 4 637 EUR, max 37 094 EUR", key="per")
        pen_versee = st.number_input("Pension alimentaire versee EUR", 0, 20000, 0, 200,
            help="Case 6GI — plafond legal 6 794 EUR pour enfant majeur hors foyer", key="pen_versee")
    with db:
        cot_synd = st.number_input("Cotisations syndicales EUR", 0, 2000, 0, 50,
            help="Case 7AC — credit 66 %, plafond 1 % salaires", key="cot_synd")

    st.markdown("---")
    st.markdown("### Reductions d'impot — Dons")
    dc, dd, de = st.columns(3)
    with dc:
        dons_75 = st.number_input("Dons 75 % (aide personnes) EUR", 0, 5000, 0, 50,
            help="Case 7UD — plafond 1 000 EUR", key="dons_75")
    with dd:
        dons_mayo = st.number_input("Dons Mayotte urgence 75 % EUR", 0, 5000, 0, 50,
            help="Case 7UM — cyclone Chido, plafond 2 000 EUR", key="dons_mayo")
    with de:
        dons_66 = st.number_input("Dons 66 % (associations) EUR", 0, 50000, 0, 50,
            help="Case 7VC — plafond 20 % du RNI", key="dons_66")

    st.markdown("---")
    st.markdown("### Credits d'impot")
    df, dg = st.columns(2)
    with df:
        st.markdown("**Garde d'enfants hors domicile**")
        nb_enf6 = st.number_input("Enfants < 6 ans au 01/01/2024", 0, 5, 0, key="nb_enf6")
        res_alt = False; frais_garde = 0
        if nb_enf6 > 0:
            res_alt = st.checkbox("Residence alternee (plafond / 2)", key="res_alt")
            frais_garde = st.number_input("Frais garde EUR", 0, 15000, 0, 100,
                help="Cases 7GA-7GC — credit 50 %, plafond 3 500 EUR/enfant", key="garde")
            plaf_g = (3500 / (2 if res_alt else 1)) * nb_enf6
            cr_g = min(frais_garde, plaf_g) * 0.5
            st.caption(f"Credit estime : **{fr(cr_g)} EUR**")
    with dg:
        st.markdown("**Emploi a domicile**")
        prem_annee = st.checkbox("1ere annee emploi domicile (+3 000 EUR plafond)", key="prem_annee")
        emploi_dom = st.number_input("Depenses emploi domicile EUR", 0, 25000, 0, 200,
            help="Cases 7DB/7DQ — credit 50 %, plafond 12 000 EUR + 1 500 EUR/enfant", key="emp_dom")
        if emploi_dom:
            plaf_e = (15000 if prem_annee else 12000) + nb_enfants * 1500
            cr_e = min(emploi_dom, min(plaf_e, 18000 if prem_annee else 15000)) * 0.5
            st.caption(f"Credit estime : **{fr(cr_e)} EUR**")


# ══════════════════════════════════════════════════════════════════════
# ONGLET 3 — ENFANT MAJEUR
# ══════════════════════════════════════════════════════════════════════
profil_enfant    = None
comparaison      = None
res_enfant_seul  = None
comparaison_active = False

with tab_enfant:
    st.markdown("### Comparaison : Rattachement vs Foyer fiscal independant")
    st.markdown("""
    **Scenario A** — L'enfant reste rattache : ses revenus s'ajoutent aux votres (+0,5 part).
    Si etudiant : exoneration jobs etudiants (5 301 EUR) + reduction scolarite.

    **Scenario B** — L'enfant fait sa propre declaration. Vous pouvez lui verser une pension
    deductible (case 6GI). L'enfant declare la pension recue comme revenu imposable (case 1AS).
    """)

    comparaison_active = st.toggle(
        "Activer la comparaison pour un enfant majeur", key="comp_active")

    if comparaison_active:
        st.markdown("---")

        # ─ Sous-onglets enfant ─
        et1, et2, et3 = st.tabs([
            "Situation & Revenus", "Deductions & Credits", "Etudes & Pension"])

        with et1:
            ea, eb_col = st.columns(2)
            with ea:
                st.markdown("**Situation familiale de l'enfant**")
                sit_enf = st.selectbox("Statut matrimonial",
                    ["Celibataire / Divorce(e)","Marie(e) / Pacse(e)","Veuf(ve)"],
                    key="sit_enf")
                nb_enf_enf = st.number_input("Ses propres enfants a charge", 0, 10, 0, key="enf_enf")
                pi_enf = False
                if sit_enf in ("Celibataire / Divorce(e)","Veuf(ve)") and nb_enf_enf > 0:
                    pi_enf = st.checkbox("Parent isole (case T)", key="pi_enf")
                inv_enf = st.checkbox("Invalide >= 80 %", key="inv_enf")

            with eb_col:
                st.markdown("**Ses revenus 2024**")
                sal1_enf = st.number_input("Salaires EUR", 0, 200000, 18000, 500,
                    help="Case 1AJ — etudiant, alternant, salarie...", key="sal1_enf")
                pen1_enf = st.number_input("Pensions / Retraites EUR", 0, 100000, 0, 200,
                    help="Case 1AS", key="pen1_enf")
                hsup1_enf = st.number_input("dont Heures sup EUR", 0, 7500, 0, 100,
                    help="Case 1GH — exonere IR, inclus dans salaires", key="hsup1_enf")
                sal2_enf = pen2_enf = hsup2_enf = 0
                if sit_enf == "Marie(e) / Pacse(e)":
                    sal2_enf = st.number_input("Salaires conjoint(e) EUR", 0, 200000, 0, 500, key="sal2_enf")
                    pen2_enf = st.number_input("Pensions conjoint(e) EUR", 0, 100000, 0, 200, key="pen2_enf")
                    hsup2_enf = st.number_input("Heures sup conjoint(e) EUR", 0, 7500, 0, 100, key="hsup2_enf")

            with st.expander("Frais professionnels — Declarant 1 enfant"):
                fr1_enf, mfr1_enf = saisie_frais_reels("enf_d1", sal1_enf)
            fr2_enf = False; mfr2_enf = 0
            if sit_enf == "Marie(e) / Pacse(e)" and sal2_enf > 0:
                with st.expander("Frais professionnels — Declarant 2 enfant"):
                    fr2_enf, mfr2_enf = saisie_frais_reels("enf_d2", sal2_enf)

        with et2:
            ec1, ec2 = st.columns(2)
            with ec1:
                per_enf      = st.number_input("PER EUR", 0, 20000, 0, 200, key="per_enf")
                cot_synd_enf = st.number_input("Cotisations syndicales EUR", 0, 1000, 0, 50, key="synd_enf")
                dons_75_enf  = st.number_input("Dons 75 % EUR", 0, 2000, 0, 50, key="d75_enf")
                dons_66_enf  = st.number_input("Dons 66 % EUR", 0, 10000, 0, 50, key="d66_enf")
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
                    "L'enfant est encore etudiant (< 26 ans)",
                    key="etudiant_enf",
                    help="Exoneration jobs etudiants : 5 301 EUR (3 x SMIC mensuel 2024, art. 81 bis CGI)")
                if etudiant_enf:
                    st.info(
                        f"Exoneration emploi etudiant : jusqu'a **5 301 EUR** de ses salaires "
                        f"seront exoneres d'IR dans les 2 scenarios.")
                    niveau_enf = st.selectbox("Niveau d'etudes",
                        list(moteur.SCOLARITE.keys()), key="niv_enf")
                    red_scol_est = moteur.SCOLARITE.get(niveau_enf, 183)
                    st.caption(f"Reduction scolarite (Scenario A uniquement) : **{red_scol_est} EUR** — case 7EF/7EG/7EA")
                else:
                    niveau_enf = list(moteur.SCOLARITE.keys())[-1]
            with eg2:
                st.markdown("**Pension alimentaire potentielle**")
                pension_enf = st.slider(
                    "Pension que vous pourriez verser EUR",
                    0, 6794, 6794, 100, key="pension_enf",
                    help="Deductible chez vous (6GI) — Imposable chez l'enfant (1AS) — Plafond 6 794 EUR")
                st.caption("Chez vous : case **6GI** (deductible RNI)")
                st.caption("Chez l'enfant : case **1AS** (imposable comme pension)")

        # ─ Profil enfant ─
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
        st.info("Activez l'option ci-dessus pour comparer le rattachement et le foyer independant.")
        etudiant_enf = False
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
        exo_etud_enf = 0


# ══════════════════════════════════════════════════════════════════════
# CALCUL GLOBAL
# ══════════════════════════════════════════════════════════════════════
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

if comparaison_active and profil_enfant:
    pe_seul = {k: v for k, v in profil_enfant.items()
               if k not in ('niveau_etude','pension_recue','etudiant')}
    pe_seul['exoneration_emploi_etudiant'] = exo_etud_enf
    res_enfant_seul = moteur.calculer(pe_seul)
    sc_obj    = ScenarioEnfantMajeur(moteur)
    comparaison = sc_obj.comparer(profil, profil_enfant)


# ══════════════════════════════════════════════════════════════════════
# ONGLET 4 — RESULTATS IRPP
# ══════════════════════════════════════════════════════════════════════
with tab_res:
    st.markdown("### Votre simulation fiscale 2026")

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(kpi("Revenu Net Imposable",
                        f"{fr(res['revenu_imposable'])} EUR", "#93c5fd"),
                    unsafe_allow_html=True)
    with k2:
        st.markdown(kpi("Impot brut",
                        f"{fr(res['impot_brut'])} EUR", "#f87171"),
                    unsafe_allow_html=True)
    with k3:
        st.markdown(kpi("Decote",
                        f"-{fr(res['decote'])} EUR", "#4ade80"),
                    unsafe_allow_html=True)
    with k4:
        st.markdown(kpi("IMPOT NET A PAYER",
                        f"{fr(res['impot_net'])} EUR", "#60a5fa"),
                    unsafe_allow_html=True)

    st.markdown("")
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Taux moyen", f"{res['taux_moyen']:.2f} %")
    with m2: st.metric("TMI", f"{res['taux_marginal']} %")
    with m3: st.metric("Parts fiscales", f"{res['nb_parts']:.1f}")
    with m4:
        hstot = hsup1 + hsup2
        if hstot:
            st.metric("Heures sup exonerees", f"{fr(hstot)} EUR")
        elif exo_etud_enf and comparaison_active:
            st.metric("Exo. etudiant (enfant)", f"{fr(exo_etud_enf)} EUR")
        else:
            st.metric("Abattement total", f"{fr(res['abattement_applique'])} EUR")

    st.markdown('<div class="src">Bareme 2024 — Brochure DGFiP 2025 — Decote : 889 - 45,25 % x impot (cel.) — QF plafonne 1 791 EUR/demi-part</div>',
                unsafe_allow_html=True)

    # Détail
    with st.expander("Detail complet du calcul"):
        d1, d2 = st.columns(2)
        with d1:
            st.markdown("**Revenus => RNI**")
            rows = [["Salaires bruts D1", f"{fr(sal1)} EUR"]]
            if hsup1: rows.append(["dont Heures sup D1", f"-{fr(hsup1)} EUR"])
            rows += [
                ["Abattement salaires D1", f"-{fr(res['abattement_salaires_1'])} EUR"],
                ["Pensions D1", f"{fr(pen1)} EUR"],
                ["Abattement pensions D1", f"-{fr(res['abattement_pensions_1'])} EUR"],
            ]
            if situation == "Marie(e) / Pacse(e)":
                rows += [
                    ["Salaires D2", f"{fr(sal2)} EUR"],
                    ["Abattement D2", f"-{fr(res['abattement_salaires_2'])} EUR"],
                ]
            rows += [
                ["Deduction PER", f"-{fr(res['deduction_per'])} EUR"],
                ["Pension versee", f"-{fr(res['pension_versee_ded'])} EUR"],
                ["= RNI", f"{fr(res['revenu_imposable'])} EUR"],
            ]
            st.dataframe(pd.DataFrame(rows, columns=["Etape","Montant"]),
                         hide_index=True, use_container_width=True)
        with d2:
            st.markdown("**Calcul impot**")
            rows2 = [
                [f"Quotient (RNI / {res['nb_parts']:.1f} parts)", f"{fr(res['quotient_familial'])} EUR"],
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
                x=[t['label'] for t in tr],
                y=[t['impot_tranche'] for t in tr],
                marker_color=['#1e3a5f','#1d4ed8','#3b82f6','#60a5fa','#93c5fd'][:len(tr)],
                text=[f"{fr(t['impot_tranche'])} EUR" for t in tr],
                textposition='outside', textfont=dict(color='#e2e8f0')
            )])
            fig.update_layout(title="Impot par tranche", height=300,
                plot_bgcolor='#1e293b', paper_bgcolor='#1e293b',
                font=dict(color='#e2e8f0'), showlegend=False)
            fig.update_yaxes(gridcolor='#334155')
            fig.update_xaxes(tickfont=dict(size=9))
            st.plotly_chart(fig, use_container_width=True)

    with g2:
        total_b = res['revenu_total_brut']
        if total_b > 0:
            fig2 = go.Figure(go.Pie(
                labels=['Impot net','Revenu disponible'],
                values=[res['impot_net'], max(0, total_b - res['impot_net'])],
                hole=0.55,
                marker_colors=['#dc2626','#1d4ed8'],
                textfont=dict(color='#e2e8f0')
            ))
            fig2.update_layout(
                title="Repartition du revenu", height=300,
                plot_bgcolor='#1e293b', paper_bgcolor='#1e293b',
                font=dict(color='#e2e8f0'),
                annotations=[dict(text=f"{res['taux_moyen']:.1f} %<br>moyen",
                                  x=0.5, y=0.5, font_size=13,
                                  font=dict(color='#e2e8f0'), showarrow=False)])
            st.plotly_chart(fig2, use_container_width=True)

    # ─ Comparaison enfant majeur ─
    if comparaison_active and comparaison:
        st.markdown("---")
        st.markdown("### Comparaison enfant majeur")

        sc_a = comparaison['scenario_a']
        sc_b = comparaison['scenario_b']
        meill = comparaison['meilleur_scenario']
        eco   = comparaison['economie']
        pb    = sc_b['parents']
        eb    = sc_b['enfant']
        etud  = comparaison.get('etudiant', False)

        ca_col, cb_col = st.columns(2)
        with ca_col:
            best = "🏆 " if meill == "A" else ""
            st.markdown(f"""<div class="card">
            <h4>{best}Scenario A — Rattachement</h4>
            Parts foyer (avec enfant) : <b>{sc_a['nb_parts']:.1f}</b><br>
            Revenus enfant integres : <b>{fr(sc_a['revenus_enfant_integres'])} EUR</b><br>
            {"Exoneration emploi etudiant : <b>-" + fr(sc_a['exoneration_etudiant']) + " EUR</b><br>" if etud and sc_a['exoneration_etudiant'] else ""}
            RNI foyer combine : <b>{fr(sc_a['rni'])} EUR</b><br>
            Impot brut : <b>{fr(sc_a['impot_brut'])} EUR</b><br>
            IR foyer avant reduction scol. : <b>{fr(sc_a['impot_net_avant_scol'])} EUR</b><br>
            {"Reduction scolarite (" + sc_a['niveau_etude'] + ") : <b>-" + str(sc_a['reduction_scolarite']) + " EUR</b><br>" if etud else ""}
            <br><span style="font-size:1.3rem;font-weight:700;color:#60a5fa">
            Impot net : {fr(sc_a['cout_total'])} EUR</span>
            </div>""", unsafe_allow_html=True)

        with cb_col:
            best = "🏆 " if meill == "B" else ""
            st.markdown(f"""<div class="card">
            <h4>{best}Scenario B — Foyer independant</h4>
            <b>Parents</b> (sans enfant rattache) :<br>
            &nbsp;Parts parents : {pb['nb_parts']:.1f}<br>
            &nbsp;Pension versee deductible : -{fr(pb.get('pension_versee',0))} EUR<br>
            &nbsp;<b>IR parents : {fr(pb['impot_net'])} EUR</b><br><br>
            <b>Enfant</b> (propre declaration) :<br>
            &nbsp;Parts : {eb['nb_parts']:.1f} — RNI : {fr(eb['revenu_imposable'])} EUR<br>
            {"&nbsp;Exoneration etudiant : -" + fr(eb.get('exoneration_etudiant',0)) + " EUR<br>" if etud and eb.get('exoneration_etudiant',0) else ""}
            &nbsp;Pension recue imposable : {fr(eb.get('pension_recue',0))} EUR<br>
            &nbsp;TMI enfant : {eb.get('taux_marginal',0)} %<br>
            &nbsp;<b>IR enfant : {fr(eb['impot_net'])} EUR</b><br><br>
            <span style="font-size:1.3rem;font-weight:700;color:#4ade80">
            Total : {fr(sc_b['cout_total'])} EUR</span>
            </div>""", unsafe_allow_html=True)

        cls  = "verdict-a" if meill == "A" else "verdict-b"
        lab  = "Rattachement (A)" if meill == "A" else "Foyer independant (B)"
        col  = "#60a5fa" if meill == "A" else "#4ade80"
        st.markdown(f"""<div class="{cls}">
        <h3 style="color:{col};margin:0">Recommandation : {lab}</h3>
        <p style="margin:.4rem 0 0">Economie : <b>{fr(eco)} EUR</b> par rapport a l'autre scenario.</p>
        </div>""", unsafe_allow_html=True)

        fig_c = go.Figure([
            go.Bar(name=f"A - Rattachement ({fr(sc_a['cout_total'])} EUR)",
                   x=["Cout fiscal total"], y=[sc_a['cout_total']],
                   marker_color='#1d4ed8',
                   text=f"{fr(sc_a['cout_total'])} EUR", textposition='outside',
                   textfont=dict(color='#e2e8f0')),
            go.Bar(name=f"B - Independant ({fr(sc_b['cout_total'])} EUR)",
                   x=["Cout fiscal total"], y=[sc_b['cout_total']],
                   marker_color='#16a34a',
                   text=f"{fr(sc_b['cout_total'])} EUR", textposition='outside',
                   textfont=dict(color='#e2e8f0')),
        ])
        fig_c.update_layout(barmode='group', title="Cout fiscal global compare",
                            height=280, plot_bgcolor='#1e293b', paper_bgcolor='#1e293b',
                            font=dict(color='#e2e8f0'))
        st.plotly_chart(fig_c, use_container_width=True)

    # ─ Conseils ─
    st.markdown("---")
    st.markdown("### Conseils d'optimisation")
    if conseils:
        for c in conseils:
            icones = {'PER':'💰','FR':'📋','DONS':'❤️','DOM':'🏠',
                      'TMI':'📉','SYND':'🤝','HS':'⏰'}
            ic = icones.get(c['icone'], '💡')
            st.markdown(f"""<div class="conseil">
            <b>{ic} {c['titre']}</b><br>
            <span style="color:#fbbf24">{c['detail']}</span></div>""",
                        unsafe_allow_html=True)
    else:
        st.success("Votre situation semble bien optimisee.")


# ══════════════════════════════════════════════════════════════════════
# ONGLET 5 — REVENUS DIRIGEANT
# ══════════════════════════════════════════════════════════════════════
with tab_dir:
    st.markdown("### Revenus de dirigeant / Revenus complexes")
    st.markdown("""
    Simulez vos revenus professionnels et immobiliers : BIC, BNC, revenus fonciers,
    LMNP, LMP, SCI, dividendes, remuneration de gerance et calcul de l'IS.
    """)

    tmi_dir = st.select_slider(
        "Votre TMI (taux marginal pour calcul option bareme dividendes)",
        [0, 11, 30, 41, 45], 30, key="tmi_dir")

    dir_tabs = st.tabs([
        "🏦 IS Societe", "💶 Dividendes",
        "🛒 BIC / BNC",  "🏠 Foncier / LMNP / LMP",
        "🏢 Gerance & Strategie"
    ])

    # ─ IS Societe ─
    with dir_tabs[0]:
        st.markdown("#### Calcul de l'Impot sur les Societes (IS)")
        is_col1, is_col2 = st.columns(2)
        with is_col1:
            res_fisc = st.number_input("Resultat fiscal de la societe EUR",
                -500000, 5000000, 80000, 1000, key="res_fisc")
            st.caption("Taux reduit 15 % jusqu'a 42 500 EUR puis 25 % au-dela")
        with is_col2:
            if res_fisc > 0:
                is_data = dirigeant_m.calculer_is(res_fisc)
                st.markdown(f"""<div class="card">
                <h4>Resultat IS 2024</h4>
                Base taux reduit (15 %) : <b>{fr(is_data['base_reduit'])} EUR</b><br>
                IS taux reduit : <b>{fr(is_data['is_reduit'])} EUR</b><br>
                Base taux normal (25 %) : <b>{fr(is_data['base_normal'])} EUR</b><br>
                IS taux normal : <b>{fr(is_data['is_normal'])} EUR</b><br>
                <hr style="border-color:#334155">
                <b>IS total : {fr(is_data['is_total'])} EUR</b><br>
                Taux effectif : <b>{is_data['taux_effectif']:.2f} %</b><br>
                Benefice net disponible : <b>{fr(is_data['benefice_net'])} EUR</b>
                </div>""", unsafe_allow_html=True)
            else:
                st.info("Saisissez un resultat fiscal positif pour calculer l'IS.")

    # ─ Dividendes ─
    with dir_tabs[1]:
        st.markdown("#### Comparaison PFU vs Option bareme — Dividendes")
        dv1, dv2 = st.columns(2)
        with dv1:
            div_bruts = st.number_input("Dividendes bruts a distribuer EUR",
                0, 2000000, 50000, 1000, key="div_bruts")
        with dv2:
            st.info(f"Votre TMI : **{tmi_dir} %** (modifiable en haut de page)")

        if div_bruts > 0:
            d_data = dirigeant_m.calculer_dividendes(div_bruts, tmi_dir)
            pfu  = d_data['pfu']
            bar  = d_data['bareme']
            meill_d = d_data['meilleur']

            dc1, dc2 = st.columns(2)
            with dc1:
                best_d = "🏆 " if meill_d == "PFU" else ""
                c_d = "#60a5fa" if meill_d == "PFU" else "#94a3b8"
                st.markdown(f"""<div class="card" style="border-color:{c_d}">
                <h4>{best_d}PFU — Flat Tax 30 %</h4>
                IR (12,8 %) : <b>{fr(pfu['ir'])} EUR</b><br>
                Prelevements sociaux (17,2 %) : <b>{fr(pfu['ps'])} EUR</b><br>
                <b>Total prelevements : {fr(pfu['total_imposition'])} EUR</b><br>
                Net percu : <b>{fr(pfu['net_percu'])} EUR</b>
                </div>""", unsafe_allow_html=True)
            with dc2:
                best_d = "🏆 " if meill_d == "Bareme" else ""
                c_d = "#4ade80" if meill_d == "Bareme" else "#94a3b8"
                st.markdown(f"""<div class="card" style="border-color:{c_d}">
                <h4>{best_d}Option bareme + abattement 40 %</h4>
                Base imposable (apres abatt. 40 %) : <b>{fr(bar['base_imposable'])} EUR</b><br>
                IR ({tmi_dir} %) : <b>{fr(bar['ir'])} EUR</b><br>
                Prelevements sociaux (17,2 %) : <b>{fr(bar['ps'])} EUR</b><br>
                <b>Total : {fr(bar['total_imposition'])} EUR</b><br>
                Net percu : <b>{fr(bar['net_percu'])} EUR</b>
                </div>""", unsafe_allow_html=True)

            lab_d = "PFU (Flat Tax)" if meill_d == "PFU" else "Option bareme"
            st.success(f"Recommandation : **{lab_d}** — economie : {fr(d_data['economie'])} EUR")

            # Graphique
            fig_d = go.Figure([
                go.Bar(name='IR', x=['PFU','Bareme'], y=[pfu['ir'], bar['ir']],
                       marker_color='#3b82f6'),
                go.Bar(name='Prel. sociaux', x=['PFU','Bareme'],
                       y=[pfu['ps'], bar['ps']], marker_color='#f87171'),
            ])
            fig_d.update_layout(barmode='stack', title="Comparaison prelevements",
                height=280, plot_bgcolor='#1e293b', paper_bgcolor='#1e293b',
                font=dict(color='#e2e8f0'))
            st.plotly_chart(fig_d, use_container_width=True)

    # ─ BIC / BNC ─
    with dir_tabs[2]:
        st.markdown("#### BIC / BNC — Regimes micro et reel")
        bic_type = st.selectbox("Type de regime",
            ["BIC micro (ventes)","BIC micro (services)","BIC reel",
             "BNC micro","BNC reel (declaration 2035)"], key="bic_type")

        if "BIC micro" in bic_type:
            act = "vente" if "ventes" in bic_type else "services"
            ca_bic = st.number_input("Chiffre d'affaires EUR", 0, 2000000, 60000, 1000, key="ca_bic")
            if ca_bic:
                r_bic = dirigeant_m.calculer_bic_micro(ca_bic, act)
                ok = "✅" if r_bic['eligible'] else "⚠️"
                st.markdown(f"""<div class="card">
                <h4>{r_bic['label']}</h4>
                CA : <b>{fr(r_bic['ca'])} EUR</b><br>
                Abattement {r_bic['abattement_pct']} % : <b>-{fr(r_bic['abattement_montant'])} EUR</b><br>
                <b>Benefice imposable : {fr(r_bic['benefice_imposable'])} EUR</b><br>
                IR estime (TMI {tmi_dir} %) : <b>{fr(int(r_bic['benefice_imposable'] * tmi_dir / 100))} EUR</b><br>
                {ok} Seuil regime micro : {fr(r_bic['seuil_regime'])} EUR
                {'— Eligible' if r_bic['eligible'] else '— Depasse : regime reel obligatoire'}
                </div>""", unsafe_allow_html=True)

        elif bic_type == "BIC reel":
            bc1, bc2, bc3 = st.columns(3)
            with bc1: ca_r = st.number_input("CA EUR", 0, 5000000, 150000, 1000, key="ca_r")
            with bc2: ch_r = st.number_input("Charges deductibles EUR", 0, 5000000, 100000, 1000, key="ch_r")
            with bc3: am_r = st.number_input("Amortissements EUR", 0, 500000, 0, 1000, key="am_r")
            r_bic_r = dirigeant_m.calculer_bic_reel(ca_r, ch_r, am_r)
            col_b = "#4ade80" if r_bic_r['benefice'] >= 0 else "#f87171"
            st.markdown(f"""<div class="card">
            <h4>BIC Reel simplifie (declaration 2031)</h4>
            CA : {fr(ca_r)} EUR — Charges : {fr(ch_r)} EUR — Amortissements : {fr(am_r)} EUR<br>
            <b style="color:{col_b}">Benefice imposable : {fr(r_bic_r['benefice_imposable'])} EUR</b><br>
            {"<b>Deficit BIC : " + fr(r_bic_r['deficit']) + " EUR</b><br>" if r_bic_r['deficit'] else ""}
            IR estime (TMI {tmi_dir} %) : <b>{fr(int(r_bic_r['benefice_imposable'] * tmi_dir / 100))} EUR</b>
            </div>""", unsafe_allow_html=True)

        elif bic_type == "BNC micro":
            rec_bnc = st.number_input("Recettes EUR", 0, 500000, 50000, 1000, key="rec_bnc")
            if rec_bnc:
                r_bnc = dirigeant_m.calculer_bnc_micro(rec_bnc)
                ok = "✅" if r_bnc['eligible'] else "⚠️"
                st.markdown(f"""<div class="card">
                <h4>BNC Micro — Abattement 34 %</h4>
                Recettes : {fr(r_bnc['recettes'])} EUR<br>
                Abattement 34 % : -{fr(r_bnc['abattement_montant'])} EUR<br>
                <b>Benefice imposable : {fr(r_bnc['benefice_imposable'])} EUR</b><br>
                IR estime (TMI {tmi_dir} %) : <b>{fr(int(r_bnc['benefice_imposable'] * tmi_dir / 100))} EUR</b><br>
                {ok} Seuil : {fr(r_bnc['seuil_regime'])} EUR
                </div>""", unsafe_allow_html=True)

        else:  # BNC reel
            rr1, rr2 = st.columns(2)
            with rr1: rec_r = st.number_input("Recettes EUR", 0, 2000000, 80000, 1000, key="rec_r")
            with rr2: ch_bnc = st.number_input("Charges deductibles EUR", 0, 2000000, 40000, 1000, key="ch_bnc")
            r_bnc_r = dirigeant_m.calculer_bnc_reel(rec_r, ch_bnc)
            st.markdown(f"""<div class="card">
            <h4>BNC Reel — Declaration 2035</h4>
            Recettes : {fr(rec_r)} EUR — Charges : {fr(ch_bnc)} EUR<br>
            <b>Benefice imposable : {fr(r_bnc_r['benefice_imposable'])} EUR</b><br>
            {"Deficit : " + fr(r_bnc_r['deficit']) + " EUR<br>" if r_bnc_r['deficit'] else ""}
            IR estime (TMI {tmi_dir} %) : <b>{fr(int(r_bnc_r['benefice_imposable'] * tmi_dir / 100))} EUR</b>
            </div>""", unsafe_allow_html=True)

    # ─ Foncier / LMNP / LMP ─
    with dir_tabs[3]:
        st.markdown("#### Revenus immobiliers")
        immo_type = st.selectbox("Type de revenu immobilier",
            ["Revenus fonciers — Micro-foncier",
             "Revenus fonciers — Regime reel (declaration 2044)",
             "LMNP — Micro-BIC",
             "LMNP — Regime reel",
             "LMP — Location Meublee Professionnelle",
             "SCI a l'IR",
             "SCI a l'IS"], key="immo_type")

        if "Micro-foncier" in immo_type:
            rf_b = st.number_input("Revenus fonciers bruts EUR", 0, 500000, 10000, 500, key="rf_b")
            if rf_b:
                r_f = dirigeant_m.calculer_foncier_micro(rf_b)
                ok = "✅" if r_f['eligible'] else "⚠️"
                st.markdown(f"""<div class="card">
                <h4>Micro-foncier — Abattement 30 %</h4>
                Revenus bruts : {fr(rf_b)} EUR<br>
                Abattement 30 % : -{fr(r_f['abattement_montant'])} EUR<br>
                <b>Imposable : {fr(r_f['imposable'])} EUR</b><br>
                IR estime (TMI {tmi_dir} %) : <b>{fr(int(r_f['imposable'] * tmi_dir / 100))} EUR</b><br>
                Prel. sociaux (17,2 %) : <b>{fr(int(r_f['imposable'] * 0.172))} EUR</b><br>
                {ok} Seuil : {fr(r_f['seuil'])} EUR
                </div>""", unsafe_allow_html=True)

        elif "Regime reel" in immo_type and "foncier" in immo_type.lower():
            fr_r1, fr_r2 = st.columns(2)
            with fr_r1:
                rfr_b = st.number_input("Revenus bruts EUR", 0, 1000000, 20000, 500, key="rfr_b")
                int_emp = st.number_input("Interets d'emprunt EUR", 0, 200000, 5000, 200, key="int_emp")
                charg_c = st.number_input("Charges courantes EUR", 0, 100000, 2000, 100, key="charg_c")
            with fr_r2:
                travaux = st.number_input("Travaux EUR", 0, 500000, 0, 500, key="travaux")
                tf = st.number_input("Taxe fonciere EUR", 0, 20000, 1000, 100, key="tf")
                frais_g = st.number_input("Frais gestion / assurances EUR", 0, 20000, 500, 100, key="frais_g")
            r_fr = dirigeant_m.calculer_foncier_reel(rfr_b, int_emp, charg_c, travaux, tf, frais_g)
            col_f = "#4ade80" if r_fr['resultat'] >= 0 else "#f87171"
            st.markdown(f"""<div class="card">
            <h4>Revenus fonciers — Regime reel (declaration 2044)</h4>
            Revenus bruts : {fr(rfr_b)} EUR — Total charges : {fr(r_fr['total_charges'])} EUR<br>
            <b style="color:{col_f}">Resultat : {fr(r_fr['resultat'])} EUR</b><br>
            {"<b>Deficit total : " + fr(r_fr['deficit_total']) + " EUR</b><br>"
             + "Dont imputable sur revenu global : <b>" + fr(r_fr['deficit_imputable_rng']) + " EUR</b> (plafond 10 700 EUR)<br>"
             + "Dont reportable sur foncier (10 ans) : <b>" + fr(r_fr['deficit_report_foncier']) + " EUR</b><br>"
             if r_fr['deficit_total'] > 0 else ""}
            IR estime (TMI {tmi_dir} %) sur benefice : <b>{fr(int(r_fr['imposable'] * tmi_dir / 100))} EUR</b>
            </div>""", unsafe_allow_html=True)

        elif "LMNP — Micro" in immo_type:
            lc1, lc2 = st.columns(2)
            with lc1:
                lmnp_rec = st.number_input("Recettes LMNP EUR", 0, 500000, 15000, 500, key="lmnp_rec")
                lmnp_cl  = st.checkbox("Bien classe (tourisme / meuble classe)", key="lmnp_cl")
            r_lmnp = dirigeant_m.calculer_lmnp(lmnp_rec, lmnp_cl, 'micro')
            ok = "✅" if r_lmnp['eligible'] else "⚠️"
            st.markdown(f"""<div class="card">
            <h4>LMNP Micro-BIC — {r_lmnp['type_bien']}</h4>
            Recettes : {fr(lmnp_rec)} EUR<br>
            Abattement {r_lmnp['abattement_pct']} % : -{fr(lmnp_rec - r_lmnp['imposable'])} EUR<br>
            <b>Imposable : {fr(r_lmnp['imposable'])} EUR</b><br>
            IR estime (TMI {tmi_dir} %) : <b>{fr(int(r_lmnp['imposable'] * tmi_dir / 100))} EUR</b><br>
            Prel. sociaux : <b>{fr(r_lmnp['ps'])} EUR</b><br>
            {ok} Seuil : {fr(r_lmnp['seuil'])} EUR
            </div>""", unsafe_allow_html=True)

        elif "LMNP — Regime reel" in immo_type:
            lr1, lr2, lr3 = st.columns(3)
            with lr1: lmnp_r_rec = st.number_input("Recettes EUR", 0, 500000, 25000, 500, key="lr_rec")
            with lr2: lmnp_r_ch  = st.number_input("Charges EUR", 0, 200000, 8000, 500, key="lr_ch")
            with lr3: lmnp_r_am  = st.number_input("Amortissements EUR", 0, 200000, 6000, 500, key="lr_am")
            r_lr = dirigeant_m.calculer_lmnp(lmnp_r_rec, False, 'reel',
                                               lmnp_r_ch, lmnp_r_am)
            col_lr = "#4ade80" if r_lr['benefice'] >= 0 else "#f87171"
            st.markdown(f"""<div class="card">
            <h4>LMNP Regime reel</h4>
            Recettes : {fr(lmnp_r_rec)} EUR — Charges : {fr(lmnp_r_ch)} EUR — Amort. : {fr(lmnp_r_am)} EUR<br>
            <b style="color:{col_lr}">Benefice imposable : {fr(r_lr['imposable'])} EUR</b><br>
            {"Deficit reportable 10 ans : <b>" + fr(r_lr['deficit']) + " EUR</b><br>" if r_lr['deficit'] else ""}
            IR estime (TMI {tmi_dir} %) : <b>{fr(int(r_lr['imposable'] * tmi_dir / 100))} EUR</b>
            </div>""", unsafe_allow_html=True)

        elif "LMP" in immo_type:
            lp1, lp2 = st.columns(2)
            with lp1:
                lmp_rec = st.number_input("Recettes LMP EUR", 0, 1000000, 30000, 1000, key="lmp_rec")
                lmp_ch  = st.number_input("Charges EUR", 0, 500000, 10000, 500, key="lmp_ch")
            with lp2:
                lmp_am  = st.number_input("Amortissements EUR", 0, 300000, 8000, 500, key="lmp_am")
                autres_rev = st.number_input("Autres revenus pro du foyer EUR", 0, 500000, 45000, 1000, key="lmp_aut")
            r_lmp = dirigeant_m.calculer_lmp(lmp_rec, lmp_ch, lmp_am, autres_rev)
            st.markdown(f"""<div class="card">
            <h4>LMP — Location Meublee Professionnelle</h4>
            Statut LMP atteint : <b>{'Oui' if r_lmp['statut_lmp'] else 'Non (recettes < 23 000 EUR ou < autres revenus pro)'}</b><br>
            Benefice imposable : <b>{fr(r_lmp['imposable'])} EUR</b><br>
            {"Deficit imputable sans limite sur RNG : <b>" + fr(r_lmp['deficit']) + " EUR</b><br>" if r_lmp['deficit'] and r_lmp['statut_lmp'] else ""}
            <ul style="margin:.4rem 0 0 1rem;color:#94a3b8">
            {"".join(f"<li>{a}</li>" for a in r_lmp['avantages'])}</ul>
            </div>""", unsafe_allow_html=True)

        elif "SCI a l'IR" in immo_type:
            sci_qp = st.number_input("Quote-part resultat foncier EUR", -100000, 500000, 5000, 500, key="sci_qp")
            r_sci_ir = dirigeant_m.calculer_sci_ir(sci_qp)
            st.markdown(f"""<div class="card">
            <h4>SCI a l'IR — Revenus fonciers (declaration 2044)</h4>
            Quote-part resultat : <b>{fr(sci_qp)} EUR</b><br>
            Imposable (revenus fonciers) : <b>{fr(r_sci_ir['imposable'])} EUR</b><br>
            IR estime (TMI {tmi_dir} %) : <b>{fr(int(r_sci_ir['imposable'] * tmi_dir / 100))} EUR</b><br>
            Prel. sociaux (17,2 %) : <b>{fr(int(r_sci_ir['imposable'] * 0.172))} EUR</b><br>
            <i>{r_sci_ir['note']}</i>
            </div>""", unsafe_allow_html=True)

        else:  # SCI IS
            si1, si2 = st.columns(2)
            with si1:
                sci_rf = st.number_input("Resultat fiscal SCI EUR", 0, 5000000, 60000, 1000, key="sci_rf")
            with si2:
                sci_part = st.slider("Votre quote-part (%)", 1, 100, 100, 1, key="sci_part") / 100
            r_sci_is = dirigeant_m.calculer_sci_is(sci_rf, sci_part)
            st.markdown(f"""<div class="card">
            <h4>SCI a l'IS</h4>
            Resultat fiscal : {fr(sci_rf)} EUR<br>
            IS total : <b>{fr(r_sci_is['is_total'])} EUR</b> (taux effectif : {r_sci_is['taux_effectif']:.2f} %)<br>
            Benefice net : <b>{fr(r_sci_is['benefice_net'])} EUR</b><br>
            Dividende potentiel (votre quote-part {int(sci_part*100)} %) : <b>{fr(r_sci_is['dividende_potentiel'])} EUR</b><br>
            <i>=> Soumis au PFU 30 % ou option bareme si distribue</i>
            </div>""", unsafe_allow_html=True)
            if r_sci_is['dividende_potentiel'] > 0:
                d2_data = dirigeant_m.calculer_dividendes(r_sci_is['dividende_potentiel'], tmi_dir)
                st.markdown(f"Imposition si distribution : PFU = **{fr(d2_data['pfu']['total_imposition'])} EUR** | "
                            f"Option bareme = **{fr(d2_data['bareme']['total_imposition'])} EUR** "
                            f"=> Recommande : **{d2_data['meilleur']}**")

    # ─ Gerance & Strategie ─
    with dir_tabs[4]:
        st.markdown("#### Remuneration de gerance & Optimisation remuneration / dividendes")

        st.markdown("**Remuneration de gerant**")
        ger1, ger2 = st.columns(2)
        with ger1:
            ger_rem = st.number_input("Remuneration brute du gerant EUR", 0, 500000, 60000, 1000, key="ger_rem")
            ger_fr  = st.checkbox("Frais reels gerant", key="ger_fr")
            ger_mfr = st.number_input("Montant frais reels EUR", 0, 30000, 0, 500, key="ger_mfr") if ger_fr else 0
        with ger2:
            if ger_rem:
                r_ger = dirigeant_m.calculer_gerance(ger_rem, ger_fr, ger_mfr)
                st.markdown(f"""<div class="card">
                <h4>Remuneration de gerance</h4>
                Remuneration brute : {fr(ger_rem)} EUR<br>
                Abattement ({r_ger['type_abattement']}) : -{fr(r_ger['abattement'])} EUR<br>
                <b>Imposable (cat. TS) : {fr(r_ger['imposable'])} EUR</b><br>
                IR estime (TMI {tmi_dir} %) : <b>{fr(int(r_ger['imposable'] * tmi_dir / 100))} EUR</b><br>
                <i style="color:#64748b">{r_ger['note']}</i>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Optimisation : Remuneration vs Dividendes**")
        st.markdown("Comparez le cout global selon que vous sortez le resultat en salaire ou en dividendes.")
        so1, so2 = st.columns(2)
        with so1:
            ben_avo = st.number_input("Benefice avant IS et remuneration EUR",
                0, 5000000, 120000, 1000, key="ben_avo")
            rem_strat = st.number_input("Remuneration envisagee (strategie A) EUR",
                0, 500000, 70000, 1000, key="rem_strat")
        with so2:
            if ben_avo > 0:
                r_strat = dirigeant_m.simuler_remuneration_vs_dividendes(
                    ben_avo, rem_strat, tmi_dir)
                sa = r_strat['strategie_a']
                sb = r_strat['strategie_b']
                meill_s = r_strat['meilleure']
                st.markdown(f"""<div class="card">
                <h4>Comparaison strategique</h4>
                <b>A — Tout en remuneration</b><br>
                IS societe : {fr(sa['is_societe'])} EUR<br>
                IR personnel estime : {fr(sa['ir_personnel'])} EUR<br>
                Cout total : <b>{fr(sa['cout_total'])} EUR</b> | Net percu : {fr(sa['net_percu'])} EUR<br><br>
                <b>B — Dividendes (PFU 30 %)</b><br>
                IS societe : {fr(sb['is_societe'])} EUR<br>
                PFU dividendes : {fr(sb['pfu'])} EUR<br>
                Cout total : <b>{fr(sb['cout_total'])} EUR</b> | Net percu : {fr(sb['net_percu'])} EUR<br><br>
                <b style="color:{'#60a5fa' if meill_s == 'A' else '#4ade80'}">
                Recommandation : Strategie {meill_s} (economie : {fr(r_strat['economie'])} EUR)</b>
                </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="src">
    Sources : BOI-BIC-CHAMP, BOI-BNC, BOI-RFPI, BOI-RPPM | Art. 219, 200A, 32, 50-0, 102ter CGI |
    Calculs indicatifs — Consultez un expert-comptable pour votre situation specifique.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# ONGLET 6 — EXPORT PDF
# ══════════════════════════════════════════════════════════════════════
with tab_pdf:
    st.markdown("### Bilan fiscal PDF personnalise")
    st.markdown("""
    Le rapport comprend :
    - Resume complet de votre simulation IRPP
    - Detail du calcul tranche par tranche
    - **Guide des cases a renseigner** sur votre declaration en ligne (impots.gouv.fr)
    - Conseils d'optimisation personnalises
    """)
    if comparaison_active and comparaison:
        st.info("Le rapport inclura la comparaison enfant majeur et le detail de sa declaration.")

    if st.button("Generer mon bilan fiscal PDF", type="primary"):
        with st.spinner("Generation en cours..."):
            try:
                gen = GenererRapportPDF()
                pdf_bytes = gen.generer(
                    profil, res, conseils, comparaison,
                    profil_enfant=profil_enfant,
                    res_enfant_seul=res_enfant_seul
                )
                b64 = base64.b64encode(pdf_bytes).decode()
                href = (
                    f'<a href="data:application/pdf;base64,{b64}" '
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
    Simulateur base sur la Brochure Pratique DGFiP 2025 (Revenus 2024) |
    Pour information uniquement |
    <a href="https://www.impots.gouv.fr" target="_blank" style="color:#3b82f6">impots.gouv.fr</a>
    </div>""", unsafe_allow_html=True)
