"""
Simulateur d'Impôt sur le Revenu 2025 (Revenus 2024)
Application Streamlit — Barème officiel DGFiP
Source : Brochure Pratique 2025, Direction Générale des Finances Publiques
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64
from calcul_impot import MoteurImpot, ScenarioEnfantMajeur, FraisReels
from rapport_pdf import GenererRapportPDF

# ─── Configuration ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Simulateur Impôt 2025 (Revenus 2024)",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  .main-header{background:linear-gradient(135deg,#003189 0%,#0052b4 50%,#ed2939 100%);
    padding:1.8rem;border-radius:12px;color:white;text-align:center;margin-bottom:1.5rem}
  .metric-card{background:#f8f9ff;border:1px solid #e0e4ff;border-radius:10px;
    padding:1.2rem;text-align:center;margin:0.3rem 0}
  .metric-value{font-size:1.8rem;font-weight:700;color:#003189}
  .metric-label{font-size:0.8rem;color:#666;margin-top:0.3rem}
  .verdict-green{background:#e8f5e9;border-left:4px solid #2e7d32;padding:1rem;
    border-radius:0 8px 8px 0;margin:1rem 0}
  .verdict-blue{background:#e3f2fd;border-left:4px solid #1565c0;padding:1rem;
    border-radius:0 8px 8px 0;margin:1rem 0}
  .conseil-box{background:#fff8e1;border:1px solid #f9a825;border-radius:8px;
    padding:0.9rem;margin:0.4rem 0}
  .source-note{background:#f3f4f6;border-radius:6px;padding:0.6rem;
    font-size:0.78rem;color:#555;margin:0.5rem 0}
  .stButton>button{background:linear-gradient(135deg,#003189,#0052b4);color:white;
    border:none;border-radius:8px;padding:0.6rem 1.5rem;font-weight:600;width:100%}
</style>
""", unsafe_allow_html=True)

# ─── En-tête ─────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>🧮 Simulateur Impôt sur le Revenu 2025</h1>
  <p>Déclaration 2025 · Revenus 2024 · Barème officiel DGFiP · Brochure Pratique 2025</p>
</div>
""", unsafe_allow_html=True)

moteur = MoteurImpot()
fr_calc = FraisReels()

# ═════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📋 Votre situation fiscale")

    # ─── Situation familiale ───────────────────────────────────────
    st.markdown("### 👨‍👩‍👧 Foyer fiscal")
    situation = st.selectbox(
        "Statut matrimonial",
        ["Célibataire / Divorcé(e)", "Marié(e) / Pacsé(e)", "Veuf(ve)"]
    )
    nb_enfants = st.number_input(
        "Enfants mineurs à charge", min_value=0, max_value=10, value=0, step=1
    )
    parent_isole = False
    if situation in ("Célibataire / Divorcé(e)", "Veuf(ve)") and nb_enfants > 0:
        parent_isole = st.checkbox(
            "Parent isolé (case T) — vivant seul avec enfant(s)",
            help="Donne droit à 1 part entière pour le 1er enfant (au lieu de 0,5)"
        )
    invalide = st.checkbox(
        "Carte d'invalidité ≥ 80% (déclarant ou conjoint)",
        help="+0,5 part par personne invalide"
    )

    # ─── Revenus 2024 ─────────────────────────────────────────────
    st.markdown("### 💰 Revenus 2024")
    st.caption("Indiquez les montants bruts AVANT abattement 10%")

    tab_rev1, tab_rev2 = st.tabs(["Déclarant 1", "Déclarant 2"])
    with tab_rev1:
        sal1 = st.number_input("Salaires / Revenus assimilés €", 0, 500000, 45000, 500, key="sal1")
        pen1 = st.number_input("Pensions / Retraites / Rentes €", 0, 200000, 0, 200, key="pen1")
    with tab_rev2:
        sal2 = pen2 = 0
        if situation == "Marié(e) / Pacsé(e)":
            sal2 = st.number_input("Salaires / Revenus assimilés €", 0, 500000, 0, 500, key="sal2")
            pen2 = st.number_input("Pensions / Retraites / Rentes €", 0, 200000, 0, 200, key="pen2")
        else:
            st.info("Non applicable (imposition individuelle)")

    # ─── Frais professionnels ─────────────────────────────────────
    st.markdown("### 🚗 Frais professionnels")
    mode_frais = st.radio(
        "Mode de déduction — Déclarant 1",
        ["Forfait 10% (automatique)", "Frais réels justifiés"],
        help="Le choix s'applique à l'ensemble des revenus salariaux du déclarant"
    )
    frais_reels_1 = (mode_frais == "Frais réels justifiés")
    montant_fr1 = 0

    if frais_reels_1:
        st.markdown("**Calculateur frais réels**")
        with st.expander("🚗 Transport domicile–travail", expanded=True):
            type_veh = st.selectbox("Type de véhicule",
                ["thermique", "electrique", "moto", "moto_electrique", "cyclo"],
                format_func=lambda x: {
                    "thermique": "🚗 Voiture thermique/hybride",
                    "electrique": "⚡ Voiture électrique",
                    "moto": "🏍️ Moto thermique",
                    "moto_electrique": "⚡ Moto électrique",
                    "cyclo": "🛵 Cyclomoteur"
                }[x], key="type_veh"
            )
            cv = 5
            if type_veh in ("thermique", "electrique"):
                cv = st.slider("Puissance administrative (CV)", 3, 7, 5)
            elif type_veh in ("moto", "moto_electrique"):
                cv = st.selectbox("Puissance (CV)", [2, 5, 99],
                                   format_func=lambda x: {2:"1-2 CV", 5:"3-5 CV", 99:"> 5 CV"}[x])
            km_pro = st.number_input("Km professionnels annuels", 0, 100000, 8000, 500)
            frais_km = FraisReels.calculer_bareme_km(km_pro, cv, type_veh) if km_pro > 0 else 0
            if km_pro > 0:
                st.success(f"Indemnités kilométriques : **{frais_km:,.0f} €**")

        with st.expander("🍽️ Frais de repas supplémentaires"):
            nb_repas = st.number_input("Nombre de repas professionnels / an", 0, 300, 0, 10)
            prix_repas_moyen = st.number_input("Prix moyen du repas (€)", 0.0, 50.0, 10.0, 0.5)
            frais_repas = max(0, (prix_repas_moyen - FraisReels.REPAS_VALEUR_FOYER) * nb_repas)
            if nb_repas > 0:
                st.info(f"Frais supplémentaires : **{frais_repas:,.0f} €**\n(prix repas − 5,35 € × {nb_repas} jours)")

        with st.expander("💻 Télétravail"):
            jours_tt = st.number_input("Jours de télétravail en 2024", 0, 230, 0, 5)
            frais_tt = FraisReels.calculer_teletravail(jours_tt) if jours_tt > 0 else 0
            if jours_tt > 0:
                st.info(f"Forfait télétravail : **{frais_tt:,.0f} €** ({jours_tt}j × 2,70 €/j)")

        with st.expander("🏠 Double résidence & autres frais"):
            double_res = st.number_input("Double résidence (loyer, charges, déménagement) €", 0, 50000, 0, 200)
            formation = st.number_input("Formation professionnelle €", 0, 20000, 0, 100)
            materiel  = st.number_input("Matériel professionnel €", 0, 20000, 0, 100)
            autres_fr = st.number_input("Autres frais professionnels justifiés €", 0, 20000, 0, 100)

        montant_fr1 = round(frais_km + frais_repas + frais_tt + double_res + formation + materiel + autres_fr)
        forfait_10 = max(moteur.ABATTEMENT_SALAIRES_MIN,
                         min(sal1 * 0.10, moteur.ABATTEMENT_SALAIRES_MAX))

        if montant_fr1 > 0:
            if montant_fr1 > forfait_10:
                st.success(f"✅ Frais réels ({montant_fr1:,.0f} €) > forfait ({forfait_10:,.0f} €) → **AVANTAGE : +{montant_fr1-forfait_10:,.0f} €**")
            else:
                st.warning(f"⚠️ Frais réels ({montant_fr1:,.0f} €) < forfait ({forfait_10:,.0f} €). Le forfait 10% est plus avantageux.")
                frais_reels_1 = False  # Revenir au forfait

    # Déclarant 2 frais réels
    frais_reels_2, montant_fr2 = False, 0
    if situation == "Marié(e) / Pacsé(e)" and sal2 > 0:
        mode_frais_2 = st.selectbox(
            "Frais professionnels — Déclarant 2",
            ["Forfait 10%", "Frais réels (montant total)"]
        )
        if mode_frais_2 == "Frais réels (montant total)":
            frais_reels_2 = True
            montant_fr2 = st.number_input("Montant frais réels déclarant 2 €", 0, 50000, 0, 100)

    # ─── Déductions & Réductions ──────────────────────────────────
    st.markdown("### 🎯 Déductions & Réductions")
    per = st.number_input(
        "Versements PER (Plan Épargne Retraite) €", 0, 50000, 0, 500,
        help="Déductibles du revenu imposable dans la limite du plafond PASS (10% des revenus)"
    )
    dons_75 = st.number_input(
        "Dons aide aux personnes en difficulté (75%) €", 0, 5000, 0, 50,
        help="Restos du Cœur, Croix-Rouge, Secours populaire… Plafond base : 1 000 €"
    )
    dons_mayo = st.number_input(
        "Dons Mayotte urgence / cyclone Chido (75%) €", 0, 5000, 0, 50,
        help="Dons du 14/12/2024 au 17/05/2025. Plafond base spécial : 2 000 €"
    )
    dons_66 = st.number_input(
        "Dons associations d'utilité publique (66%) €", 0, 50000, 0, 50,
        help="Associations culturelles, sportives, caritatives… Plafond : 20% du RNI"
    )

    nb_enf_moins_6 = st.number_input(
        "Enfants < 6 ans au 01/01/2024 (nés à partir du 01/01/2018)", 0, 5, 0, 1
    )
    frais_garde = st.number_input(
        "Frais de garde (crèche, assistante maternelle…) €", 0, 10000, 0, 100,
        help="Crédit 50%, plafond 3 500 € par enfant"
    ) if nb_enf_moins_6 > 0 else 0

    premiere_annee = st.checkbox(
        "Première année d'emploi d'un salarié à domicile",
        help="Plafond porté à 15 000 € (au lieu de 12 000 €) la 1ère année"
    )
    emploi_domicile = st.number_input(
        "Emploi à domicile (ménage, jardinage, garde, soutien scolaire…) €", 0, 25000, 0, 200,
        help="Crédit 50%, plafond 12 000 € + 1 500 €/enfant (max 15 000 €)"
    )

    # ─── Module Enfant Majeur ─────────────────────────────────────
    st.markdown("### 🎓 Comparaison Enfant Majeur")
    activer_comp = st.checkbox("Activer la comparaison rattachement / pension")
    enfant_data = {}
    if activer_comp:
        enfant_data['niveau_etude'] = st.selectbox(
            "Niveau d'études de l'enfant",
            list(moteur.SCOLARITE.keys())
        )
        enfant_data['pension_versee'] = st.slider(
            "Pension alimentaire envisagée €",
            min_value=0, max_value=6794, value=6794, step=100,
            help=f"Plafond légal 2024 : 6 794 € par enfant majeur"
        )

# ═════════════════════════════════════════════════════════════════════
# CALCUL
# ═════════════════════════════════════════════════════════════════════
profil = {
    'situation':              situation,
    'nb_enfants':             nb_enfants,
    'invalide_declarant':     invalide,
    'parent_isole':           parent_isole,
    'revenu_salaire_declarant': sal1,
    'revenu_pension_declarant': pen1,
    'revenu_salaire_conjoint':  sal2,
    'revenu_pension_conjoint':  pen2,
    'frais_reels':            frais_reels_1,
    'montant_frais_reels_1':  montant_fr1,
    'frais_reels_2':          frais_reels_2,
    'montant_frais_reels_2':  montant_fr2,
    'versement_per':          per,
    'dons_60_75':             dons_75,
    'dons_mayotte':           dons_mayo,
    'dons_60':                dons_66,
    'nb_enfants_moins_6':     nb_enf_moins_6,
    'frais_garde':            frais_garde,
    'premiere_annee_emploi':  premiere_annee,
    'emploi_domicile':        emploi_domicile,
}
res = moteur.calculer(profil)

# ═════════════════════════════════════════════════════════════════════
# AFFICHAGE — Métriques principales
# ═════════════════════════════════════════════════════════════════════
st.markdown("## 📊 Résultats de votre simulation 2025 (Revenus 2024)")

c1, c2, c3, c4 = st.columns(4)
cards = [
    ("Revenu net imposable", f"{res['revenu_imposable']:,.0f} €", "#003189"),
    ("Impôt brut (avant décote)", f"{res['impot_brut']:,.0f} €", "#c62828"),
    ("Décote appliquée", f"−{res['decote']:,.0f} €", "#2e7d32"),
    ("🎯 Impôt net à payer", f"{res['impot_net']:,.0f} €", "#003189"),
]
for col, (label, val, color) in zip([c1,c2,c3,c4], cards):
    with col:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{color}">{val}</div>
            <div class="metric-label">{label}</div></div>""", unsafe_allow_html=True)

st.markdown("---")
ca, cb, cc, cd = st.columns(4)
with ca:
    st.metric("Taux moyen d'imposition", f"{res['taux_moyen']:.2f}%")
with cb:
    st.metric("Taux marginal (TMI)", f"{res['taux_marginal']}%")
with cc:
    st.metric("Nombre de parts fiscales", f"{res['nb_parts']:.1f}")
with cd:
    abatt_type = "Frais réels" if frais_reels_1 else "Forfait 10%"
    st.metric("Abattement appliqué", f"{res['abattement_applique']:,.0f} €",
              delta=abatt_type)

# Source note
st.markdown("""<div class="source-note">
📌 <strong>Barème 2024 officiel</strong> — Source : Brochure Pratique DGFiP 2025 (Tableau 5 p.361) ·
Décote : formule 45,25% (889 € - célibataire / 1 470 € - couple) ·
Plafonnement QF : 1 791 €/demi-part · PASS 2024 : 46 368 €
</div>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════
# DÉTAIL CALCUL
# ═════════════════════════════════════════════════════════════════════
with st.expander("🔍 Détail complet du calcul fiscal", expanded=False):
    c_d1, c_d2 = st.columns(2)
    with c_d1:
        st.markdown("**📐 Revenu net imposable**")
        rows_rni = [
            ["Salaires bruts déclarant 1", f"{sal1:,.0f} €"],
            ["Abattement salaires D1 (10% ou frais réels)", f"−{res['abattement_salaires_1']:,.0f} €"],
            ["Pensions/retraites déclarant 1", f"{pen1:,.0f} €"],
            ["Abattement pensions D1 (10%)", f"−{res['abattement_pensions_1']:,.0f} €"],
        ]
        if situation == "Marié(e) / Pacsé(e)":
            rows_rni += [
                ["Salaires bruts déclarant 2", f"{sal2:,.0f} €"],
                ["Abattement salaires D2", f"−{res['abattement_salaires_2']:,.0f} €"],
                ["Pensions déclarant 2", f"{pen2:,.0f} €"],
                ["Abattement pensions D2", f"−{res['abattement_pensions_2']:,.0f} €"],
            ]
        rows_rni += [
            ["Déduction versements PER", f"−{res['deduction_per']:,.0f} €"],
            ["= Revenu Net Imposable", f"➡ {res['revenu_imposable']:,.0f} €"],
        ]
        st.dataframe(pd.DataFrame(rows_rni, columns=["Étape", "Montant"]),
                     hide_index=True, use_container_width=True)

    with c_d2:
        st.markdown("**🧮 Calcul de l'impôt**")
        rows_imp = [
            [f"Quotient (RNI ÷ {res['nb_parts']:.1f} parts)", f"{res['quotient_familial']:,.0f} €"],
            ["Impôt sur 1 part (barème)", f"{res['impot_une_part']:,.0f} €"],
            [f"× {res['nb_parts']:.1f} parts", f"= {res['impot_avant_plafond']:,.0f} €"],
            ["Plafonnement QF (1 791 €/½-part)", f"−{res['plafonnement_qf']:,.0f} €"],
            ["Impôt brut après plafonnement QF", f"{res['impot_brut']:,.0f} €"],
            [f"Décote (889/1470 − 45,25% × impôt)", f"−{res['decote']:,.0f} €"],
            ["Réductions dons 75%", f"−{res['reduction_dons_75']:,.0f} €"],
            ["Réductions dons 66%", f"−{res['reduction_dons_66']:,.0f} €"],
            ["Crédit frais de garde", f"−{res['credit_garde']:,.0f} €"],
            ["Crédit emploi à domicile", f"−{res['credit_emploi']:,.0f} €"],
            ["= IMPÔT NET À PAYER", f"➡ {res['impot_net']:,.0f} €"],
        ]
        st.dataframe(pd.DataFrame(rows_imp, columns=["Étape", "Montant"]),
                     hide_index=True, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════
# GRAPHIQUES
# ═════════════════════════════════════════════════════════════════════
st.markdown("### 📈 Visualisation de votre impôt")
g1, g2 = st.columns(2)

with g1:
    tranches = [t for t in res['detail_tranches'] if t['impot_tranche'] > 0]
    if tranches:
        couleurs = ['#e8f5e9','#a5d6a7','#4caf50','#2e7d32','#1b5e20']
        fig = go.Figure()
        for i, t in enumerate(tranches):
            fig.add_trace(go.Bar(
                name=t['label'], x=[t['label']], y=[t['impot_tranche']],
                marker_color=couleurs[i % 5],
                text=f"{t['impot_tranche']:,.0f} €", textposition='outside',
                hovertemplate=f"<b>{t['label']}</b><br>Base: {t['base']:,.0f} €<br>Taux: {t['taux']}%<br>Impôt: {t['impot_tranche']:,.0f} €<extra></extra>"
            ))
        fig.update_layout(title="Impôt par tranche (barème 2024)", showlegend=False,
                          height=380, plot_bgcolor='white')
        fig.update_yaxes(gridcolor='#f0f0f0')
        st.plotly_chart(fig, use_container_width=True)

with g2:
    total = res['revenu_total_brut']
    if total > 0:
        fig2 = go.Figure(go.Pie(
            labels=['Impôt net', 'Revenu disponible'],
            values=[res['impot_net'], max(0, total - res['impot_net'])],
            hole=0.55, marker_colors=['#c62828','#1565c0'],
            textinfo='label+percent',
        ))
        fig2.update_layout(
            title="Répartition de votre revenu",
            height=380,
            annotations=[dict(text=f"{res['taux_moyen']:.1f}%<br>taux moyen",
                               x=0.5, y=0.5, font_size=13, showarrow=False)]
        )
        st.plotly_chart(fig2, use_container_width=True)

# Graphique économies
economies = {
    'QF': res.get('economie_qf', 0),
    'Décote': res['decote'],
    'PER': res.get('economie_per', 0),
    'Dons 75%': res['reduction_dons_75'],
    'Dons 66%': res['reduction_dons_66'],
    'Garde': res['credit_garde'],
    'Emploi dom.': res['credit_emploi'],
}
eco_filtr = {k: v for k, v in economies.items() if v > 0}
if eco_filtr:
    fig3 = go.Figure(go.Bar(
        x=list(eco_filtr.keys()), y=list(eco_filtr.values()),
        marker_color='#1565c0',
        text=[f"{v:,.0f} €" for v in eco_filtr.values()],
        textposition='outside'
    ))
    fig3.update_layout(title="Vos économies fiscales par mécanisme", height=320,
                       plot_bgcolor='white')
    fig3.update_yaxes(gridcolor='#f0f0f0')
    st.plotly_chart(fig3, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════
# COMPARAISON ENFANT MAJEUR
# ═════════════════════════════════════════════════════════════════════
comparaison = None
if activer_comp and enfant_data:
    st.markdown("---")
    st.markdown("## 🎓 Comparaison : Rattachement vs Pension alimentaire")
    st.caption(f"Pension alimentaire 2024 — Plafond de déduction : **6 794 €** par enfant (source : Brochure DGFiP 2025, CGI art.156)")

    scenario = ScenarioEnfantMajeur(moteur)
    comparaison = scenario.comparer(profil, enfant_data)

    cs1, cs2 = st.columns(2)
    with cs1:
        sc_a = comparaison['scenario_a']
        st.markdown("""<div style="background:#e3f2fd;border-radius:10px;padding:1rem;border:2px solid #1565c0">
            <h4 style="color:#1565c0;margin:0">📎 Scénario A — Rattachement au foyer</h4></div>""",
            unsafe_allow_html=True)
        st.metric("Parts fiscales", f"{sc_a['nb_parts']:.1f}")
        st.metric("Impôt foyer après réduction scolarité", f"{sc_a['impot_net']:,.0f} €")
        st.metric("Réduction frais de scolarité", f"−{sc_a['reduction_scolarite']:,.0f} €",
                  help=f"Niveau : {enfant_data['niveau_etude']}")
        st.metric("**Coût total pour le foyer**", f"{sc_a['cout_total']:,.0f} €")

    with cs2:
        sc_b = comparaison['scenario_b']
        st.markdown("""<div style="background:#e8f5e9;border-radius:10px;padding:1rem;border:2px solid #2e7d32">
            <h4 style="color:#2e7d32;margin:0">📤 Scénario B — Pension alimentaire</h4></div>""",
            unsafe_allow_html=True)
        st.metric("Parts fiscales (sans cet enfant)", f"{sc_b['nb_parts']:.1f}")
        st.metric("Pension déduite du RNI", f"{sc_b['pension_deduite']:,.0f} €")
        st.metric("Impôt foyer", f"{sc_b['impot_net']:,.0f} €")
        st.metric("**Coût total (impôt + pension versée)**", f"{sc_b['cout_total']:,.0f} €")

    meill = comparaison['meilleur_scenario']
    eco   = comparaison['economie']
    if meill == 'A':
        st.markdown(f"""<div class="verdict-blue">
            <h3>✅ Recommandation : Scénario A — Rattachement</h3>
            <p>Le rattachement de votre enfant est <strong>plus avantageux de {eco:,.0f} €</strong>.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="verdict-green">
            <h3>✅ Recommandation : Scénario B — Pension alimentaire</h3>
            <p>La déduction de pension alimentaire est <strong>plus avantageuse de {eco:,.0f} €</strong>.
            L'enfant devra déclarer la pension comme revenu (mais bénéficiera de son propre abattement 10% et sera souvent non imposable).</p>
        </div>""", unsafe_allow_html=True)

    fig_c = go.Figure([
        go.Bar(name='A (Rattachement)', x=['Coût fiscal'],
               y=[sc_a['cout_total']], marker_color='#1565c0',
               text=f"{sc_a['cout_total']:,.0f} €", textposition='outside'),
        go.Bar(name='B (Pension)', x=['Coût fiscal'],
               y=[sc_b['cout_total']], marker_color='#2e7d32',
               text=f"{sc_b['cout_total']:,.0f} €", textposition='outside'),
    ])
    fig_c.update_layout(barmode='group', title="Comparaison du coût fiscal global",
                        height=320, plot_bgcolor='white')
    st.plotly_chart(fig_c, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════
# CONSEILS D'OPTIMISATION
# ═════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("## 💡 Conseils d'optimisation fiscale personnalisés")
conseils = moteur.generer_conseils(profil, res)
if conseils:
    for i, c in enumerate(conseils):
        detail_clean = c['detail'].replace('<strong>','**').replace('</strong>','**')
        st.markdown(f"""<div class="conseil-box">
            <strong>{c['icone']} {c['titre']}</strong><br>
            {c['detail']}</div>""", unsafe_allow_html=True)
else:
    st.success("✅ Votre situation fiscale est bien optimisée. Aucun gain majeur identifié.")

# ═════════════════════════════════════════════════════════════════════
# GÉNÉRATION PDF
# ═════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("## 📄 Bilan fiscal PDF")
st.caption("Rapport professionnel : détail du calcul, tableau comparatif, conseils personnalisés")

if st.button("🖨️ Générer mon bilan fiscal PDF", type="primary"):
    with st.spinner("Génération en cours…"):
        try:
            gen = GenererRapportPDF()
            pdf_bytes = gen.generer(profil, res, conseils, comparaison)
            b64 = base64.b64encode(pdf_bytes).decode()
            href = (f'<a href="data:application/pdf;base64,{b64}" '
                    f'download="bilan_fiscal_2025_revenus_2024.pdf" '
                    f'style="background:linear-gradient(135deg,#003189,#0052b4);color:white;'
                    f'padding:0.8rem 2rem;border-radius:8px;text-decoration:none;'
                    f'font-weight:600;display:inline-block;margin-top:1rem">'
                    f'⬇️ Télécharger le rapport PDF</a>')
            st.markdown(href, unsafe_allow_html=True)
            st.success("✅ Rapport généré !")
        except Exception as e:
            st.error(f"Erreur : {e}")
            raise

# Footer
st.markdown("---")
st.markdown("""<div style="text-align:center;color:#999;font-size:0.78rem;padding:1rem">
    🇫🇷 <strong>Simulateur basé sur la Brochure Pratique DGFiP 2025 (Revenus 2024)</strong><br>
    Barème : Tableau 5, p.361 · Décote : note 70 · Aide-mémoire pp.52-59 · Pour information uniquement<br>
    Consultez un expert-comptable ou le site <a href="https://www.impots.gouv.fr" target="_blank">impots.gouv.fr</a> pour votre situation personnelle.
</div>""", unsafe_allow_html=True)
