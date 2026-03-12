"""
Simulateur Impôt sur le Revenu 2026 — Déclaration des revenus 2025
Interface tabulée : Foyer | Déductions | Enfant Majeur | Résultats | Export PDF
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
from calcul_impot import MoteurImpot, ScenarioEnfantMajeur, FraisReels
from rapport_pdf import GenererRapportPDF

# ─── Config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Simulateur Impôt 2026",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Marianne:wght@400;500;700&display=swap');
body,.stApp{background:#f5f7fa}
.main-header{background:linear-gradient(135deg,#003189 0%,#0052b4 60%,#ed2939 100%);
  padding:1.6rem 2rem;border-radius:14px;color:white;text-align:center;margin-bottom:1.5rem;
  box-shadow:0 4px 16px rgba(0,49,137,.25)}
.main-header h1{font-size:1.9rem;font-weight:700;margin:0}
.main-header p{font-size:.9rem;opacity:.9;margin:.3rem 0 0}
.card{background:white;border-radius:12px;padding:1.4rem;
  box-shadow:0 2px 8px rgba(0,0,0,.07);margin-bottom:1rem}
.metric-row{display:flex;gap:1rem;margin-bottom:1rem;flex-wrap:wrap}
.m-card{flex:1;min-width:140px;background:white;border-radius:10px;padding:1.1rem;
  text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.07)}
.m-val{font-size:1.7rem;font-weight:700}
.m-lbl{font-size:.75rem;color:#666;margin-top:.2rem}
.badge{display:inline-block;padding:.15rem .6rem;border-radius:20px;
  font-size:.72rem;font-weight:600;margin:.2rem}
.badge-blue{background:#dbeafe;color:#1e40af}
.badge-green{background:#dcfce7;color:#166534}
.badge-orange{background:#fef3c7;color:#92400e}
.badge-red{background:#fee2e2;color:#991b1b}
.verdict{border-radius:10px;padding:1.1rem 1.4rem;margin:1rem 0}
.verdict-A{background:#dbeafe;border-left:5px solid #1d4ed8}
.verdict-B{background:#dcfce7;border-left:5px solid #16a34a}
.conseil{background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;
  padding:.85rem 1rem;margin:.4rem 0}
.case-box{background:#f0f9ff;border:1px solid #bae6fd;border-radius:6px;
  padding:.3rem .6rem;font-family:monospace;font-size:.78rem;color:#0c4a6e;
  display:inline-block;margin:.15rem}
.source{background:#f8fafc;border-radius:6px;padding:.5rem .8rem;
  font-size:.75rem;color:#64748b;margin:.5rem 0}
.sep{border:none;border-top:1px solid #e5e7eb;margin:1.2rem 0}
div[data-testid="stTabs"] [data-baseweb="tab"]{font-size:.9rem;font-weight:500}
</style>
""", unsafe_allow_html=True)


# ─── Formatage français ───────────────────────────────────────────────
def fr(val, dec=0):
    """Format nombre style français : 1 234 567,50 €"""
    if val is None: return "—"
    if dec == 0:
        s = f"{abs(val):,.0f}".replace(",", "\u202f")
    else:
        s = f"{abs(val):,.{dec}f}"
        parts = s.split(".")
        s = parts[0].replace(",", "\u202f") + "," + parts[1]
    return ("−" if val < 0 else "") + s


moteur = MoteurImpot()

# ─── Header ───────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>🧮 Simulateur Impôt sur le Revenu 2026</h1>
  <p>Déclaration 2026 · Revenus 2025 · Barème officiel DGFiP (Brochure Pratique 2025)</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════
if 'profil' not in st.session_state:
    st.session_state.profil = {}
if 'profil_enfant' not in st.session_state:
    st.session_state.profil_enfant = {}
if 'comparaison_active' not in st.session_state:
    st.session_state.comparaison_active = False


# ═══════════════════════════════════════════════════════════════════════
# HELPER : Bloc frais réels
# ═══════════════════════════════════════════════════════════════════════
def saisie_frais_reels(prefix, salaire):
    """Retourne (frais_reels: bool, montant: float)"""
    mode = st.radio("Déduction des frais professionnels",
                    ["🔢 Forfait 10 % (automatique)", "📂 Frais réels justifiés"],
                    key=f"mode_fr_{prefix}", horizontal=True)
    if "Forfait" in mode:
        forfait = max(moteur.ABATTEMENT_SALAIRES_MIN,
                      min(salaire * 0.10, moteur.ABATTEMENT_SALAIRES_MAX))
        st.caption(f"Abattement forfaitaire : **{fr(forfait)} €**  ·  case **1AK / 1BK** à ne pas renseigner")
        return False, 0

    col1, col2 = st.columns(2)
    with col1:
        type_veh = st.selectbox("Véhicule", ["thermique", "electrique", "moto",
                                              "moto_electrique", "cyclo"],
            format_func=lambda x: {"thermique": "🚗 Voiture thermique/hybride",
                "electrique": "⚡ Voiture électrique", "moto": "🏍️ Moto thermique",
                "moto_electrique": "⚡ Moto électrique", "cyclo": "🛵 Cyclomoteur"}[x],
            key=f"tveh_{prefix}")
        cv = 5
        if type_veh in ("thermique", "electrique"):
            cv = st.select_slider("Puissance fiscale (CV)", [3,4,5,6,7], 5, key=f"cv_{prefix}")
        elif "moto" in type_veh:
            cv = st.selectbox("Cylindrée", [2,5,99],
                format_func=lambda x:{2:"1-2 CV",5:"3-5 CV",99:"> 5 CV"}[x],
                key=f"cv_m_{prefix}")
        km = st.number_input("Km professionnels / an", 0, 100000, 0, 500, key=f"km_{prefix}")
        fkm = 0
        if km > 0:
            fkm = FraisReels.calculer_bareme_km(km, cv, type_veh)
            st.info(f"🚗 Barème km : **{fr(fkm)} €**")

    with col2:
        nb_rep  = st.number_input("Repas pro / an", 0, 300, 0, key=f"rep_{prefix}")
        prix_rep = st.number_input("Prix moyen repas €", 0.0, 50.0, 10.0, 0.5, key=f"px_{prefix}")
        frep = max(0, (prix_rep - FraisReels.REPAS_VALEUR_FOYER) * nb_rep) if nb_rep else 0
        if nb_rep: st.info(f"🍽️ Frais repas : **{fr(frep)} €**")

        jtt = st.number_input("Jours télétravail", 0, 230, 0, key=f"tt_{prefix}")
        ftt = FraisReels.calculer_teletravail(jtt) if jtt else 0
        if jtt: st.info(f"💻 Télétravail : **{fr(ftt)} €**")

    dres = st.number_input("Double résidence €", 0, 30000, 0, 200, key=f"dr_{prefix}")
    form = st.number_input("Formation pro €", 0, 20000, 0, 100, key=f"fo_{prefix}")
    mat  = st.number_input("Matériel pro €", 0, 20000, 0, 100, key=f"ma_{prefix}")
    aut  = st.number_input("Autres frais €", 0, 20000, 0, 100, key=f"au_{prefix}")

    total = round(fkm + frep + ftt + dres + form + mat + aut)
    forfait = max(moteur.ABATTEMENT_SALAIRES_MIN,
                  min(salaire * 0.10, moteur.ABATTEMENT_SALAIRES_MAX))
    if total > 0:
        if total > forfait:
            st.success(f"✅ Frais réels ({fr(total)} €) > forfait ({fr(forfait)} €) → gain : +{fr(total-forfait)} €  ·  Case **1AK**")
            return True, total
        else:
            st.warning(f"⚠️ Frais réels ({fr(total)} €) inférieurs au forfait ({fr(forfait)} €). Forfait plus avantageux.")
            return False, 0
    return False, 0


# ═══════════════════════════════════════════════════════════════════════
# ONGLETS PRINCIPAUX
# ═══════════════════════════════════════════════════════════════════════
tab_foyer, tab_ded, tab_enfant, tab_res, tab_pdf = st.tabs([
    "👨‍👩‍👧 Mon Foyer",
    "💰 Déductions & Crédits",
    "🎓 Enfant Majeur",
    "📊 Résultats",
    "📄 Bilan PDF",
])


# ══════════════════════════════════════════════════════════════════════
# ONGLET 1 — FOYER FISCAL
# ══════════════════════════════════════════════════════════════════════
with tab_foyer:
    st.markdown("### 👨‍👩‍👧 Situation familiale")

    col_sit, col_enf = st.columns([1, 1])
    with col_sit:
        situation = st.selectbox("Statut matrimonial",
            ["Célibataire / Divorcé(e)", "Marié(e) / Pacsé(e)", "Veuf(ve)"],
            key="situation")
        invalide = st.checkbox("Carte d'invalidité ≥ 80 %  (+0,5 part)",
                               key="invalide")
    with col_enf:
        nb_enfants = st.number_input("Enfants mineurs à charge", 0, 10, 0, key="nb_enfants")
        parent_isole = False
        if situation in ("Célibataire / Divorcé(e)", "Veuf(ve)") and nb_enfants > 0:
            parent_isole = st.checkbox(
                "Parent isolé — case T  (+1 part pour le 1er enfant)",
                key="parent_isole")

    st.markdown('<hr class="sep">', unsafe_allow_html=True)
    st.markdown("### 💶 Revenus 2024 (montants bruts avant abattement)")

    # ─ Déclarant 1 ─
    st.markdown("**Déclarant 1**")
    c1a, c1b, c1c = st.columns(3)
    with c1a:
        sal1 = st.number_input("Salaires / Traitements €", 0, 500000, 45000, 500,
            help="Case 1AJ — montant net imposable avant abattement 10 %", key="sal1")
    with c1b:
        pen1 = st.number_input("Pensions / Retraites €", 0, 200000, 0, 200,
            help="Case 1AS — montant brut avant abattement 10 %", key="pen1")
    with c1c:
        hsup1 = st.number_input("dont Heures sup / complémentaires €", 0, 7500, 0, 100,
            help="Case 1GH — montant exonéré IR, inclus dans les salaires ci-dessus (plafond 7 500 €)",
            key="hsup1")
        if hsup1 > 0:
            st.caption(f"✅ Exonération IR : {fr(min(hsup1, 7500))} € (case 1GH)")

    with st.expander("🚗 Frais professionnels — Déclarant 1"):
        fr1, mfr1 = saisie_frais_reels("main_d1", sal1)

    # ─ Déclarant 2 (si couple) ─
    sal2 = pen2 = hsup2 = 0
    fr2 = False; mfr2 = 0
    if situation == "Marié(e) / Pacsé(e)":
        st.markdown("**Déclarant 2**")
        c2a, c2b, c2c = st.columns(3)
        with c2a:
            sal2 = st.number_input("Salaires / Traitements €", 0, 500000, 0, 500,
                help="Case 1BJ", key="sal2")
        with c2b:
            pen2 = st.number_input("Pensions / Retraites €", 0, 200000, 0, 200,
                help="Case 1BS", key="pen2")
        with c2c:
            hsup2 = st.number_input("dont Heures sup / complémentaires €", 0, 7500, 0, 100,
                help="Case 1HH", key="hsup2")
            if hsup2 > 0:
                st.caption(f"✅ Exonération IR : {fr(min(hsup2, 7500))} € (case 1HH)")
        with st.expander("🚗 Frais professionnels — Déclarant 2"):
            fr2, mfr2 = saisie_frais_reels("main_d2", sal2)

    st.markdown('<div class="source">📌 Revenus imposables = Salaires − Heures sup exonérées − Abattement 10 % (ou frais réels)</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# ONGLET 2 — DÉDUCTIONS & CRÉDITS
# ══════════════════════════════════════════════════════════════════════
with tab_ded:
    st.markdown("### 🎯 Déductions du revenu global")

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.markdown("**Plan Épargne Retraite (PER)**")
        per = st.number_input("Versements PER €", 0, 80000, 0, 500,
            help="Cases 6NS / 6NT / 6NU — Déductible dans la limite de 10 % des revenus (min 4 637 €, max 37 094 €)",
            key="per")
        pen_versee = st.number_input("Pension alimentaire versée €", 0, 20000, 0, 200,
            help="Case 6GI — Plafond légal 6 794 € pour un enfant majeur (hors foyer)",
            key="pen_versee")

    with d_col2:
        st.markdown("**Cotisations déductibles**")
        cot_synd = st.number_input("Cotisations syndicales €", 0, 2000, 0, 50,
            help="Case 7AC — Crédit d'impôt 66 %, plafond 1 % des salaires nets",
            key="cot_synd")

    st.markdown('<hr class="sep">', unsafe_allow_html=True)
    st.markdown("### 💝 Réductions d'impôt — Dons")

    r_col1, r_col2, r_col3 = st.columns(3)
    with r_col1:
        dons_75 = st.number_input("Dons 75 % (aide aux personnes) €", 0, 5000, 0, 50,
            help="Case 7UD — Dons aux associations d'aide aux personnes en difficulté. Réduction 75 %, plafond 1 000 €",
            key="dons_75")
    with r_col2:
        dons_mayo = st.number_input("Dons Mayotte urgence 75 % €", 0, 5000, 0, 50,
            help="Case 7UM — Cyclone Chido (14/12/2024 → 17/05/2025). Plafond spécifique 2 000 €",
            key="dons_mayo")
    with r_col3:
        dons_66 = st.number_input("Dons 66 % (associations) €", 0, 50000, 0, 50,
            help="Case 7VC — Dons aux associations d'intérêt général. Plafond 20 % du RNI",
            key="dons_66")

    st.markdown('<hr class="sep">', unsafe_allow_html=True)
    st.markdown("### 🏠 Crédits d'impôt")

    cr_col1, cr_col2 = st.columns(2)
    with cr_col1:
        st.markdown("**Garde d'enfants hors domicile**")
        nb_enf6 = st.number_input("Enfants de moins de 6 ans au 01/01/2024",
            0, 5, 0, key="nb_enf6",
            help="Nés en 2018 ou après")
        res_alt = False; frais_garde = 0
        if nb_enf6 > 0:
            res_alt = st.checkbox("Résidence alternée (plafond divisé par 2)", key="res_alt")
            frais_garde = st.number_input("Frais de garde (crèche, assistante maternelle) €",
                0, 15000, 0, 100, key="garde",
                help="Cases 7GA à 7GC — Crédit 50 %, plafond 3 500 € / enfant")
            plaf_g = (3500 / (2 if res_alt else 1)) * nb_enf6
            cr_g = min(frais_garde, plaf_g) * 0.5
            st.caption(f"Crédit estimé : **{fr(cr_g)} €** (plafond dépenses : {fr(plaf_g)} €)")

    with cr_col2:
        st.markdown("**Emploi à domicile**")
        prem_annee = st.checkbox("1ère année d'emploi salarié à domicile", key="prem_annee",
            help="Majoration du plafond à 15 000 €")
        emploi_dom = st.number_input("Total dépenses emploi à domicile €",
            0, 25000, 0, 200, key="emp_dom",
            help="Cases 7DB à 7DQ — Crédit 50 %, plafond 12 000 € (+ 1 500 €/enfant)")
        if emploi_dom > 0:
            plaf_e = (15000 if prem_annee else 12000) + nb_enfants * 1500
            plaf_e = min(plaf_e, 18000 if prem_annee else 15000)
            cr_e = min(emploi_dom, plaf_e) * 0.5
            st.caption(f"Crédit estimé : **{fr(cr_e)} €** (plafond dépenses : {fr(plaf_e)} €)")


# ══════════════════════════════════════════════════════════════════════
# ONGLET 3 — ENFANT MAJEUR
# ══════════════════════════════════════════════════════════════════════
profil_enfant = None
comparaison_active = False

with tab_enfant:
    st.markdown("### 🎓 Comparaison rattachement vs foyer fiscal indépendant")
    st.markdown("""
    Activez cette option pour **comparer** les deux scénarios :
    - **Scénario A** — L'enfant reste rattaché à votre foyer (ses revenus s'ajoutent aux vôtres, +½ part)
    - **Scénario B** — L'enfant dépose sa propre déclaration (vous pouvez lui verser une pension déductible)
    """)

    comparaison_active = st.toggle(
        "🔄 Activer la comparaison pour un enfant majeur",
        key="comp_active")

    if comparaison_active:
        st.markdown('<hr class="sep">', unsafe_allow_html=True)
        st.markdown("#### Renseignez la situation fiscale complète de votre enfant")
        st.caption("Remplissez comme si votre enfant déposait sa propre déclaration.")

        # ─ Sous-onglets pour structurer le profil enfant ─
        e_tab1, e_tab2, e_tab3 = st.tabs([
            "👤 Situation & Revenus",
            "💰 Déductions & Crédits",
            "🎓 Études & Pension"
        ])

        with e_tab1:
            ec1, ec2 = st.columns(2)
            with ec1:
                st.markdown("**Situation familiale de l'enfant**")
                sit_enf = st.selectbox("Statut matrimonial",
                    ["Célibataire / Divorcé(e)", "Marié(e) / Pacsé(e)", "Veuf(ve)"],
                    key="sit_enf")
                nb_enf_enf = st.number_input("Ses propres enfants à charge", 0, 10, 0, key="enf_enf")
                pi_enf = False
                if sit_enf in ("Célibataire / Divorcé(e)", "Veuf(ve)") and nb_enf_enf > 0:
                    pi_enf = st.checkbox("Parent isolé (case T)", key="pi_enf")
                inv_enf = st.checkbox("Invalide ≥ 80 %", key="inv_enf")

            with ec2:
                st.markdown("**Ses revenus 2024**")
                sal1_enf = st.number_input("Salaires / Traitements €", 0, 200000, 18000, 500,
                    help="Case 1AJ — peut être étudiant salarié, apprenti, alternant…", key="sal1_enf")
                pen1_enf = st.number_input("Pensions / Retraites €", 0, 100000, 0, 200,
                    help="Case 1AS", key="pen1_enf")
                hsup1_enf = st.number_input("dont Heures sup / complémentaires €", 0, 7500, 0, 100,
                    help="Case 1GH — exonéré IR, inclus dans salaires ci-dessus", key="hsup1_enf")

                sal2_enf = pen2_enf = hsup2_enf = 0
                fr1_enf = False; mfr1_enf = 0
                fr2_enf = False; mfr2_enf = 0

                if sit_enf == "Marié(e) / Pacsé(e)":
                    sal2_enf = st.number_input("Salaires conjoint(e) €", 0, 200000, 0, 500, key="sal2_enf")
                    pen2_enf = st.number_input("Pensions conjoint(e) €", 0, 100000, 0, 200, key="pen2_enf")
                    hsup2_enf = st.number_input("dont Heures sup conjoint(e) €", 0, 7500, 0, 100, key="hsup2_enf")

            with st.expander("🚗 Frais professionnels de l'enfant — Déclarant 1"):
                fr1_enf, mfr1_enf = saisie_frais_reels("enf_d1", sal1_enf)
            if sit_enf == "Marié(e) / Pacsé(e)" and sal2_enf > 0:
                with st.expander("🚗 Frais professionnels de l'enfant — Déclarant 2"):
                    fr2_enf, mfr2_enf = saisie_frais_reels("enf_d2", sal2_enf)

        with e_tab2:
            ed1, ed2 = st.columns(2)
            with ed1:
                st.markdown("**Déductions**")
                per_enf = st.number_input("PER €", 0, 20000, 0, 200,
                    help="Cases 6NS / 6NT / 6NU", key="per_enf")
                cot_synd_enf = st.number_input("Cotisations syndicales €", 0, 1000, 0, 50,
                    help="Case 7AC", key="synd_enf")
            with ed2:
                st.markdown("**Réductions & Crédits**")
                dons_75_enf = st.number_input("Dons 75 % €", 0, 2000, 0, 50, key="d75_enf")
                dons_66_enf = st.number_input("Dons 66 % €", 0, 10000, 0, 50, key="d66_enf")
                nb_enf6_enf = st.number_input("Ses enfants < 6 ans", 0, 5, 0, key="enf6_enf")
                garde_enf = 0
                if nb_enf6_enf > 0:
                    garde_enf = st.number_input("Frais garde €", 0, 10000, 0, 100, key="garde_enf")
                emploi_enf = st.number_input("Emploi à domicile €", 0, 15000, 0, 200, key="emp_enf")

        with e_tab3:
            et1, et2 = st.columns(2)
            with et1:
                st.markdown("**Niveau d'études** (pour scénario A — réduction scolarité)")
                niveau_enf = st.selectbox("Niveau d'études",
                    list(moteur.SCOLARITE.keys()), key="niv_enf")
                red_scol_est = moteur.SCOLARITE.get(niveau_enf, 183)
                st.info(f"📚 Réduction scolarité (Scénario A) : **{red_scol_est} €** (case 7EF/7EG/7EA)")
            with et2:
                st.markdown("**Pension alimentaire potentielle**")
                pension_enf = st.slider(
                    "Pension que vous pourriez verser €", 0, 6794, 6794, 100,
                    help="Déduite de votre revenu (case 6GI) · Imposable chez l'enfant (case 1AS) · Plafond 6 794 €",
                    key="pension_enf")
                st.caption(f"Chez vous : déductible → case **6GI**  ·  "
                           f"Chez l'enfant : imposable (pension) → case **1AS**")

        # ─ Construction du profil enfant ─
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
            'niveau_etude': niveau_enf,
            'pension_recue': pension_enf,
        }

    else:
        st.info("💡 Activez l'option ci-dessus pour simuler le rattachement ou le foyer indépendant d'un enfant majeur.")


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
res = moteur.calculer(profil)
conseils = moteur.generer_conseils(profil, res)

comparaison = None
res_enfant_seul = None
if comparaison_active and profil_enfant:
    pe_seul = {k: v for k, v in profil_enfant.items()
               if k not in ('niveau_etude', 'pension_recue')}
    res_enfant_seul = moteur.calculer(pe_seul)
    scenario = ScenarioEnfantMajeur(moteur)
    comparaison = scenario.comparer(profil, profil_enfant)


# ══════════════════════════════════════════════════════════════════════
# ONGLET 4 — RÉSULTATS
# ══════════════════════════════════════════════════════════════════════
with tab_res:
    st.markdown("### 📊 Votre simulation fiscale 2026")

    # ─ KPIs principaux ─
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="m-card">
            <div class="m-val" style="color:#003189">{fr(res['revenu_imposable'])} €</div>
            <div class="m-lbl">Revenu Net Imposable</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="m-card">
            <div class="m-val" style="color:#b45309">{fr(res['impot_brut'])} €</div>
            <div class="m-lbl">Impôt brut</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="m-card">
            <div class="m-val" style="color:#15803d">{fr(res['decote'])} €</div>
            <div class="m-lbl">Décote appliquée</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="m-card">
            <div class="m-val" style="color:#003189">{fr(res['impot_net'])} €</div>
            <div class="m-lbl">🎯 Impôt net à payer</div></div>""", unsafe_allow_html=True)

    st.markdown("")
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("Taux moyen", f"{res['taux_moyen']:.2f} %")
    with k2: st.metric("Taux marginal (TMI)", f"{res['taux_marginal']} %")
    with k3: st.metric("Parts fiscales", f"{res['nb_parts']:.1f}")
    with k4:
        hstot = hsup1 + hsup2
        if hstot > 0:
            st.metric("Heures sup exonérées", f"{fr(hstot)} €", delta="−IR (case 1GH)")
        else:
            st.metric("Abattement total", f"{fr(res['abattement_applique'])} €")

    st.markdown('<div class="source">📌 Barème 2024 officiel · Brochure DGFiP 2025 · Décote : 889 − 45,25 % × impôt (célibataire) · QF plafonné 1 791 €/½-part</div>',
                unsafe_allow_html=True)

    # ─ Détail calcul ─
    with st.expander("🔍 Détail complet du calcul", expanded=False):
        dcol1, dcol2 = st.columns(2)
        with dcol1:
            st.markdown("**Revenu Net Imposable**")
            rows = [["Salaires bruts D1", f"{fr(sal1)} €"]]
            if hsup1 > 0:
                rows.append(["dont Heures sup exonérées (case 1GH)", f"−{fr(hsup1)} €"])
            rows += [
                ["Abattement salaires D1", f"−{fr(res['abattement_salaires_1'])} €"],
                ["Pensions D1", f"{fr(pen1)} €"],
                ["Abattement pensions D1", f"−{fr(res['abattement_pensions_1'])} €"],
            ]
            if situation == "Marié(e) / Pacsé(e)":
                rows += [
                    ["Salaires D2", f"{fr(sal2)} €"],
                    ["Abattement D2", f"−{fr(res['abattement_salaires_2'])} €"],
                    ["Pensions D2", f"{fr(pen2)} €"],
                    ["Abattement pensions D2", f"−{fr(res['abattement_pensions_2'])} €"],
                ]
            rows += [
                ["Déduction PER", f"−{fr(res['deduction_per'])} €"],
                ["Pension alimentaire versée", f"−{fr(res['pension_versee_ded'])} €"],
                ["= Revenu Net Imposable", f"➡ {fr(res['revenu_imposable'])} €"],
            ]
            st.dataframe(pd.DataFrame(rows, columns=["Étape", "Montant"]),
                         hide_index=True, use_container_width=True)

        with dcol2:
            st.markdown("**Calcul de l'impôt**")
            rows2 = [
                [f"Quotient (RNI ÷ {res['nb_parts']:.1f} parts)",
                 f"{fr(res['quotient_familial'])} €"],
                ["Impôt sur 1 part", f"{fr(res['impot_une_part'])} €"],
                [f"× {res['nb_parts']:.1f} parts",
                 f"= {fr(res['impot_avant_plafond'])} €"],
                ["Plafonnement QF (1 791 €/½-part)",
                 f"−{fr(res['plafonnement_qf'])} €"],
                ["Impôt brut", f"{fr(res['impot_brut'])} €"],
                ["Décote (cst − 45,25 % × impôt)",
                 f"−{fr(res['decote'])} €"],
                ["Réductions dons 75 %", f"−{fr(res['reduction_dons_75'])} €"],
                ["Réductions dons 66 %", f"−{fr(res['reduction_dons_66'])} €"],
                ["Crédit frais de garde", f"−{fr(res['credit_garde'])} €"],
                ["Crédit emploi domicile", f"−{fr(res['credit_emploi'])} €"],
                ["Crédit cotisations syndicales", f"−{fr(res['credit_syndicat'])} €"],
                ["= IMPÔT NET", f"➡ {fr(res['impot_net'])} €"],
            ]
            st.dataframe(pd.DataFrame(rows2, columns=["Étape", "Montant"]),
                         hide_index=True, use_container_width=True)

    # ─ Graphiques ─
    g1, g2 = st.columns(2)
    with g1:
        tranches = [t for t in res['detail_tranches'] if t['impot_tranche'] > 0]
        if tranches:
            fig = go.Figure([go.Bar(
                x=[t['label'] for t in tranches],
                y=[t['impot_tranche'] for t in tranches],
                marker_color=['#bfdbfe','#93c5fd','#60a5fa','#2563eb','#1e3a8a'][:len(tranches)],
                text=[f"{fr(t['impot_tranche'])} €" for t in tranches],
                textposition='outside'
            )])
            fig.update_layout(title="Impôt par tranche", height=320,
                              plot_bgcolor='white', showlegend=False)
            fig.update_yaxes(gridcolor='#f0f0f0')
            st.plotly_chart(fig, use_container_width=True)

    with g2:
        total_brut = res['revenu_total_brut']
        if total_brut > 0:
            fig2 = go.Figure(go.Pie(
                labels=['Impôt net', 'Revenu disponible'],
                values=[res['impot_net'], max(0, total_brut - res['impot_net'])],
                hole=0.55,
                marker_colors=['#dc2626', '#1d4ed8'],
                textinfo='label+percent'
            ))
            fig2.update_layout(title="Répartition du revenu", height=320,
                annotations=[dict(text=f"{res['taux_moyen']:.1f} %<br>moyen",
                                  x=0.5, y=0.5, font_size=14, showarrow=False)])
            st.plotly_chart(fig2, use_container_width=True)

    # ─ Comparaison enfant majeur ─
    if comparaison_active and comparaison:
        st.markdown('<hr class="sep">', unsafe_allow_html=True)
        st.markdown("### 🎓 Résultats — Comparaison enfant majeur")

        sc_a = comparaison['scenario_a']
        sc_b = comparaison['scenario_b']
        meill = comparaison['meilleur_scenario']
        eco   = comparaison['economie']

        ca, cb = st.columns(2)
        with ca:
            best_a = "🏆 " if meill == "A" else ""
            st.markdown(f"""<div style="background:#eff6ff;border-radius:10px;
                padding:1.2rem;border:2px solid {'#1d4ed8' if meill=='A' else '#e5e7eb'}">
                <h4>{best_a}Scénario A — Rattachement</h4>
                <p>Parts foyer : <b>{sc_a['nb_parts']:.1f}</b><br>
                RNI après abattement rattachement : <b>{fr(sc_a['rni'])} €</b><br>
                Impôt brut : <b>{fr(sc_a['impot_brut'])} €</b><br>
                Décote : <b>−{fr(sc_a['decote'])} €</b><br>
                Réduction scolarité ({sc_a['niveau_etude']}) : <b>−{sc_a['reduction_scolarite']} €</b><br>
                <span style="font-size:1.2rem;font-weight:700;color:#1d4ed8">
                💰 {fr(sc_a['cout_total'])} €</span></p></div>""",
                unsafe_allow_html=True)

        with cb:
            best_b = "🏆 " if meill == "B" else ""
            pb = sc_b['parents']
            eb = sc_b['enfant']
            st.markdown(f"""<div style="background:#f0fdf4;border-radius:10px;
                padding:1.2rem;border:2px solid {'#16a34a' if meill=='B' else '#e5e7eb'}">
                <h4>{best_b}Scénario B — Foyer indépendant</h4>
                <p><b>Parents</b> (sans l'enfant) :<br>
                &nbsp;Pension versée déductible : −{fr(pb['pension_versee'])} €<br>
                &nbsp;IR parents : <b>{fr(pb['impot_net'])} €</b><br>
                <b>Enfant</b> (foyer propre) :<br>
                &nbsp;Parts : {eb['nb_parts']:.1f} · RNI : {fr(eb['revenu_imposable'])} €<br>
                &nbsp;IR enfant : <b>{fr(eb['impot_net'])} €</b><br>
                <span style="font-size:1.2rem;font-weight:700;color:#16a34a">
                💰 Total : {fr(sc_b['cout_total'])} €</span></p></div>""",
                unsafe_allow_html=True)

        cls = "verdict-A" if meill == "A" else "verdict-B"
        emoji = "📎" if meill == "A" else "📤"
        label = "Rattachement" if meill == "A" else "Foyer indépendant"
        st.markdown(f"""<div class="verdict {cls}">
            <h3>{emoji} Recommandation : Scénario {meill} — {label}</h3>
            <p>Cette option est plus avantageuse de <strong>{fr(eco)} €</strong> par rapport à l'autre scénario.</p>
        </div>""", unsafe_allow_html=True)

        # Graphique comparatif
        fig_c = go.Figure([
            go.Bar(name=f'A — Rattachement ({fr(sc_a["cout_total"])} €)',
                   x=['Coût fiscal total'], y=[sc_a['cout_total']],
                   marker_color='#3b82f6',
                   text=f"{fr(sc_a['cout_total'])} €", textposition='outside'),
            go.Bar(name=f'B — Indépendant ({fr(sc_b["cout_total"])} €)',
                   x=['Coût fiscal total'], y=[sc_b['cout_total']],
                   marker_color='#22c55e',
                   text=f"{fr(sc_b['cout_total'])} €", textposition='outside'),
        ])
        fig_c.update_layout(barmode='group', title="Coût fiscal global comparé",
                            height=280, plot_bgcolor='white')
        st.plotly_chart(fig_c, use_container_width=True)

    # ─ Conseils ─
    st.markdown('<hr class="sep">', unsafe_allow_html=True)
    st.markdown("### 💡 Conseils d'optimisation personnalisés")
    if conseils:
        for c in conseils:
            st.markdown(f"""<div class="conseil">
                <strong>{c['icone']} {c['titre']}</strong><br>
                <span style="color:#555">{c['detail']}</span></div>""",
                unsafe_allow_html=True)
    else:
        st.success("✅ Votre situation semble bien optimisée.")


# ══════════════════════════════════════════════════════════════════════
# ONGLET 5 — EXPORT PDF
# ══════════════════════════════════════════════════════════════════════
with tab_pdf:
    st.markdown("### 📄 Bilan fiscal personnalisé")
    st.markdown("""
    Le rapport PDF comprend :
    - ✅ Résumé complet de votre simulation
    - ✅ Détail tranche par tranche
    - ✅ Guide des **cases à renseigner** sur votre déclaration en ligne
    - ✅ Conseils d'optimisation personnalisés
    """)
    if comparaison_active and comparaison:
        st.info("📋 Le rapport inclura également la **comparaison enfant majeur** et le détail de sa déclaration.")

    if st.button("🖨️ Générer mon bilan fiscal PDF", type="primary"):
        with st.spinner("Génération en cours…"):
            try:
                gen = GenererRapportPDF()
                pdf_bytes = gen.generer(
                    profil, res, conseils, comparaison,
                    profil_enfant=profil_enfant,
                    res_enfant_seul=res_enfant_seul
                )
                b64 = base64.b64encode(pdf_bytes).decode()
                href = (f'<a href="data:application/pdf;base64,{b64}" '
                        f'download="bilan_fiscal_2026.pdf" '
                        f'style="display:inline-block;background:linear-gradient(135deg,#003189,#0052b4);'
                        f'color:white;padding:.8rem 2rem;border-radius:8px;'
                        f'text-decoration:none;font-weight:700;font-size:1rem;margin-top:.5rem">'
                        f'⬇️ Télécharger le rapport PDF</a>')
                st.markdown(href, unsafe_allow_html=True)
                st.success("✅ Rapport généré !")
            except Exception as e:
                st.error(f"Erreur génération PDF : {e}")
                raise

    st.markdown('<hr class="sep">', unsafe_allow_html=True)
    st.markdown("""<div style="color:#94a3b8;font-size:.75rem;text-align:center;padding:.5rem">
    🇫🇷 Simulateur basé sur la Brochure Pratique DGFiP 2025 (Revenus 2024) ·
    Pour information uniquement · Consultez <a href="https://www.impots.gouv.fr" target="_blank">impots.gouv.fr</a>
    </div>""", unsafe_allow_html=True)
