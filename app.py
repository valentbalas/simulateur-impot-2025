"""
Simulateur IR 2026 — Interface questionnaire pas-a-pas
Navigation par etapes, frais reels auto-calcules
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
from calcul_impot import MoteurImpot, ScenarioEnfantMajeur, FraisReels
from rapport_pdf import GenererRapportPDF
from dirigeant import MoteurDirigeant
from autres_revenus import AutresRevenus
from frais_reels_auto import calculer_frais_reels_complets, calculer_frais_repas
try:
    from streamlit_option_menu import option_menu
    HAS_OPTION_MENU = True
except ImportError:
    HAS_OPTION_MENU = False

st.set_page_config(
    page_title="Simulateur IR 2026",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS : dark + wizard ───────────────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }

/* ── Fond global ── */
.stApp{background:#0f172a !important;color:#e2e8f0}
[data-testid="stHeader"]{background:#0f172a !important}
[data-testid="stSidebar"]{background:#1e293b !important}
.block-container{padding:1.2rem 2rem 2rem !important;max-width:1100px}

/* ── Boutons ── */
.stButton>button{
  background:linear-gradient(135deg,#1d4ed8,#2563eb);
  color:#fff;border:none;border-radius:10px;
  padding:.55rem 1.2rem;font-weight:600;font-size:.88rem;
  transition:all .2s ease;box-shadow:0 2px 8px rgba(29,78,216,0.35)}
.stButton>button:hover{
  background:linear-gradient(135deg,#1e40af,#1d4ed8);
  transform:translateY(-1px);box-shadow:0 4px 16px rgba(29,78,216,0.5)}
.stButton>button:active{transform:translateY(0)}

/* ── Inputs ── */
.stTextInput>div>div>input,
.stNumberInput>div>div>input,
.stSelectbox>div>div,
.stMultiSelect>div>div{
  background:#1e293b !important;color:#e2e8f0 !important;
  border:1px solid #334155 !important;border-radius:8px !important}
.stTextInput>div>div>input:focus,
.stNumberInput>div>div>input:focus{
  border-color:#3b82f6 !important;
  box-shadow:0 0 0 2px rgba(59,130,246,0.2) !important}
.stSlider>div{color:#e2e8f0}
.stRadio>div{color:#e2e8f0 !important}
.stCheckbox>label{color:#e2e8f0 !important}
label{color:#94a3b8 !important;font-size:.85rem !important;font-weight:500}

/* ── Cards ── */
.card{
  background:linear-gradient(135deg,#1e293b,#1a2540);
  border:1px solid #334155;border-radius:14px;
  padding:1.3rem;margin-bottom:.8rem;
  box-shadow:0 4px 16px rgba(0,0,0,0.3);
  transition:border-color .2s,box-shadow .2s}
.card:hover{border-color:#3b82f6;box-shadow:0 6px 24px rgba(59,130,246,0.15)}

/* ── KPI box ── */
.kpi{
  background:linear-gradient(135deg,#1e293b,#162032);
  border:1px solid #334155;border-radius:12px;
  padding:1rem;text-align:center;
  box-shadow:0 2px 12px rgba(0,0,0,0.3)}
.kpi-val{font-size:1.6rem;font-weight:800;color:#93c5fd;line-height:1.1}
.kpi-lbl{font-size:.75rem;color:#64748b;margin-top:.25rem;font-weight:500}

/* ── Source note ── */
.src{font-size:.72rem;color:#475569;margin:.3rem 0;text-align:center}

/* ── Alerts Streamlit ── */
.stAlert{background:#1e293b !important;border-radius:10px !important;
  border-left:3px solid #3b82f6 !important;color:#e2e8f0 !important}

/* ── Info box ── */
.stInfo{background:#172133 !important;border-color:#1d4ed8 !important}
.stSuccess{background:#0f2218 !important;border-color:#16a34a !important}
.stWarning{background:#1c1207 !important;border-color:#d97706 !important}
.stError{background:#1c0a0a !important;border-color:#dc2626 !important}

/* ── Progress bar wizard ── */
.progress-wrap{background:#1e293b;border-radius:12px;padding:.8rem 1rem;
  margin-bottom:1rem;border:1px solid #334155}
.step-row{display:flex;align-items:center;gap:.4rem;flex-wrap:wrap}
.step-done{display:inline-flex;align-items:center;gap:.3rem;
  background:#166534;color:#86efac;border-radius:20px;
  padding:.18rem .7rem;font-size:.75rem;font-weight:600}
.step-active{display:inline-flex;align-items:center;gap:.3rem;
  background:linear-gradient(135deg,#1d4ed8,#3b82f6);color:#fff;
  border-radius:20px;padding:.18rem .9rem;font-size:.75rem;font-weight:700;
  box-shadow:0 2px 8px rgba(59,130,246,0.4)}
.step-todo{display:inline-flex;align-items:center;gap:.3rem;
  background:#1e293b;color:#475569;border:1px solid #334155;
  border-radius:20px;padding:.18rem .7rem;font-size:.75rem}
.sep{color:#334155;font-size:.8rem}

/* ── Tabs ── */
.stTabs [data-baseweb="tab"]{
  background:#1e293b;color:#94a3b8;border-radius:8px 8px 0 0;
  border:1px solid #334155;padding:.4rem 1rem;font-weight:500}
.stTabs [aria-selected="true"]{
  background:linear-gradient(135deg,#1d4ed8,#2563eb) !important;
  color:#fff !important;border-color:#1d4ed8 !important}

/* ── Expander ── */
.streamlit-expanderHeader{
  background:#1e293b !important;color:#93c5fd !important;
  border-radius:8px !important;font-weight:600}

/* ── Dataframe ── */
.stDataFrame{background:#1e293b !important;border-radius:10px;overflow:hidden}

/* ── Bouton home dans header ── */
button[kind="secondary"]{font-size:.8rem !important;padding:.3rem .8rem !important}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:#0f172a}
::-webkit-scrollbar-thumb{background:#334155;border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:#475569}

/* ── Hide default streamlit UI ── */
#MainMenu{visibility:hidden !important}
footer{visibility:hidden !important}
.stDecoration{display:none !important}
</style>""", unsafe_allow_html=True)

moteur      = MoteurImpot()
dm          = MoteurDirigeant()
ar_engine   = AutresRevenus()


def fr(val, dec=0):
    if val is None: return "-"
    if dec == 0:
        s = f"{abs(val):,.0f}".replace(",", "\u202f")
    else:
        s = f"{abs(val):,.{dec}f}"
        p = s.split("."); s = p[0].replace(",", "\u202f") + "," + p[1]
    return ("-\u202f" if val < 0 else "") + s


def kpi_html(label, val, color="#93c5fd"):
    return (f'<div class="kpi"><div class="kpi-val" style="color:{color}">{val}</div>'
            f'<div class="kpi-lbl">{label}</div></div>')


# ─── State init ───────────────────────────────────────────────────
def home_button():
    """Bouton retour accueil avec confirmation si données présentes."""
    if SS.get('step', 0) == 0:
        return
    col_h, _ = st.columns([1, 7])
    with col_h:
        if st.button("⬅ Accueil", key=f"home_btn_{SS.get('step',0)}_{SS.get('mode','x')}"):
            has_data = bool(SS.get('data') and any(
                v for v in SS['data'].values() if v not in (0, False, None, [], {})))
            if has_data:
                SS['confirm_home'] = True
                st.rerun()
            else:
                for k in list(SS.keys()): del SS[k]
                st.rerun()
    if SS.get('confirm_home'):
        st.markdown("""<div style="background:#1e293b;border:1px solid #f87171;
          border-radius:10px;padding:.8rem 1rem;margin:.3rem 0">
          <span style="color:#fca5a5;font-weight:700">⚠️ Retourner à l'accueil ?</span>
          <span style="color:#94a3b8;font-size:.85rem;margin-left:.5rem">
          Toutes vos données saisies seront perdues.</span>
        </div>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1.4, 1.2, 5])
        with c1:
            if st.button("✅ Oui, retour", key="confirm_yes_h"):
                for k in list(SS.keys()): del SS[k]
                st.rerun()
        with c2:
            if st.button("❌ Annuler", key="confirm_no_h"):
                SS['confirm_home'] = False
                st.rerun()


SS = st.session_state
if 'step' not in SS: SS.step = 0
if 'data' not in SS: SS.data = {}
if 'mode' not in SS: SS.mode = None
if 'resultats' not in SS: SS.resultats = None


def next_step(n=1): SS.step += n; st.rerun()
def prev_step(n=1): SS.step = max(0, SS.step - n); st.rerun()
def go_step(n): SS.step = n; st.rerun()
def save(key, val): SS.data[key] = val


# ─── Étapes définition ────────────────────────────────────────────
STEPS_FOYER = [
    "Accueil", "Situation", "Revenus D1", "Revenus D2",
    "Frais pro", "Deductions", "Credits", "Autres revenus",
    "Resultats", "Export PDF"
]
STEPS_COMP = [
    "Accueil", "Situation", "Revenus D1", "Revenus D2",
    "Frais pro", "Deductions", "Credits",
    "Enfant majeur", "Resultats", "Export PDF"
]
STEPS_DIR = [
    "Accueil", "Parametres", "Remuneration", "IS & Dividendes",
    "Activite", "Immobilier", "Optimisation", "Rapport PDF"
]


def render_progress(steps, current):
    html = '<div class="step-bar">'
    for i, label in enumerate(steps):
        if i < current:
            cls = "done"; sym = "&#10003;"
        elif i == current:
            cls = "current"; sym = str(i + 1)
        else:
            cls = "todo"; sym = str(i + 1)
        lbl_cls = "current" if i == current else ""
        html += f'<div class="step-item"><div class="step-dot {cls}">{sym}</div><span class="step-label {lbl_cls}">{label}</span></div>'
        if i < len(steps) - 1:
            html += '<div class="step-sep"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def nav_buttons(can_next=True, label_next="Suivant →", label_prev="← Precedent",
                show_prev=True, final=False):
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        if show_prev and SS.step > 0:
            if st.button(label_prev, key=f"prev_{SS.step}"):
                prev_step()
    with c3:
        if final:
            pass
        elif can_next:
            if st.button(label_next, key=f"next_{SS.step}"):
                next_step()


# ═══════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════
# Titre cliquable → retour accueil (toutes pages sauf accueil)
if SS.get('step', 0) > 0:
    if st.button(
        "🧮  Simulateur IR 2026  ·  ← Retour à l'accueil",
        key="title_home_btn",
        help="Cliquez pour revenir à la page d'accueil",
    ):
        has_data = bool(SS.get('data') and any(
            v for v in SS['data'].values() if v not in (0, False, None, [], {})))
        if has_data:
            SS['confirm_home'] = True
        else:
            for k in list(SS.keys()): del SS[k]
        st.rerun()

st.markdown("""
<div style="
  background:linear-gradient(135deg,#003189 0%,#1d4ed8 50%,#ed2939 100%);
  padding:1.6rem 2.5rem;border-radius:20px;color:white;text-align:center;
  margin-bottom:1.6rem;box-shadow:0 8px 32px rgba(29,78,216,0.35);
  position:relative;overflow:hidden">
  <div style="position:absolute;top:-40px;right:-40px;width:160px;height:160px;
    background:rgba(255,255,255,0.04);border-radius:50%"></div>
  <div style="position:absolute;bottom:-30px;left:-30px;width:120px;height:120px;
    background:rgba(255,255,255,0.04);border-radius:50%"></div>
  <div style="position:relative">
    <div style="font-size:2rem;margin-bottom:.3rem">🧮</div>
    <h1 style="margin:0;font-size:1.9rem;font-weight:700;letter-spacing:-.5px;
      text-shadow:0 2px 8px rgba(0,0,0,0.3)">
      Simulateur Impot sur le Revenu 2026
    </h1>
    <p style="margin:.4rem 0 0;opacity:.85;font-size:.9rem;font-weight:500;letter-spacing:.3px">
      Declaration 2026 &bull; Revenus 2025 &bull; Bareme officiel DGFiP
    </p>
  </div>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# ÉTAPE 0 — ACCUEIL / CHOIX DU MODE
# ═══════════════════════════════════════════════════════════════════
if SS.step == 0:
    # ── Hero ──────────────────────────────────────────────────────
    st.markdown("""
<div style="text-align:center;padding:2.5rem 1rem 1.5rem">
  <div style="display:inline-flex;align-items:center;justify-content:center;
    background:linear-gradient(135deg,#1d4ed8,#3b82f6);
    border-radius:24px;padding:1rem 1.6rem;margin-bottom:1.2rem;
    box-shadow:0 8px 32px rgba(59,130,246,0.45)">
    <span style="font-size:2.8rem">🧮</span>
  </div>
  <h1 style="font-size:2.6rem;font-weight:800;color:#f1f5f9;margin:.5rem 0;
    letter-spacing:-1.5px;line-height:1.15">
    Simulateur Impôt sur le Revenu
    <span style="background:linear-gradient(90deg,#60a5fa,#93c5fd);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent"> 2026</span>
  </h1>
  <p style="font-size:1.05rem;color:#94a3b8;margin:.6rem auto 0;max-width:580px;
    line-height:1.75;font-weight:400">
    Calculez votre impôt, optimisez votre situation fiscale et comparez vos scénarios
    — en quelques minutes, <strong style="color:#cbd5e1">gratuitement</strong>,
    selon le barème officiel DGFiP.
  </p>
</div>
""", unsafe_allow_html=True)

    # ── 4 Badges de confiance ─────────────────────────────────────
    b1, b2, b3, b4 = st.columns(4)
    for col, ico, titre, sous, accent in zip(
        [b1, b2, b3, b4],
        ["✅", "🔒", "⚡", "📄"],
        ["Barème officiel DGFiP", "100 % confidentiel", "Résultat immédiat", "Export PDF"],
        ["Données 2026 / Revenus 2025", "Aucune donnée transmise",
         "Calcul en temps réel", "Bilan complet téléchargeable"],
        ["rgba(34,197,94,0.15)", "rgba(168,85,247,0.15)",
         "rgba(234,179,8,0.15)", "rgba(59,130,246,0.15)"],
    ):
        with col:
            st.markdown(f"""<div style="background:linear-gradient(135deg,#1e293b,#162032);
              border:1px solid rgba(255,255,255,0.06);border-radius:14px;
              padding:1rem .8rem;text-align:center;
              box-shadow:0 4px 16px rgba(0,0,0,0.4);
              transition:transform .2s">
              <div style="width:40px;height:40px;border-radius:12px;
                background:{accent};margin:0 auto .5rem;
                display:flex;align-items:center;justify-content:center;
                font-size:1.3rem">{ico}</div>
              <div style="color:#e2e8f0;font-weight:700;font-size:.82rem;
                margin-bottom:.2rem">{titre}</div>
              <div style="color:#64748b;font-size:.72rem;line-height:1.4">{sous}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

    # ── Titre section ─────────────────────────────────────────────
    st.markdown("""<div style="text-align:center;margin-bottom:1.2rem">
      <span style="background:rgba(59,130,246,0.12);color:#93c5fd;
        border:1px solid rgba(59,130,246,0.25);border-radius:20px;
        padding:.3rem 1rem;font-size:.8rem;font-weight:700;
        text-transform:uppercase;letter-spacing:1px">
        Choisissez votre simulation
      </span>
    </div>""", unsafe_allow_html=True)

    # ── 3 Cartes de choix ─────────────────────────────────────────
    c1, c2, c3 = st.columns(3)

    cards = [
        (c1, "btn_foyer", "foyer",
         "🏠", "Mon foyer fiscal",
         "Calculez l'impôt de votre foyer avec toutes les déductions, crédits et optimisations personnalisées.",
         "#1e3a5f", "rgba(59,130,246,0.3)", "#93c5fd",
         ["Salaires", "Pensions", "PER", "Frais réels", "Heures sup"],
         "rgba(29,78,216,0.2)", "rgba(29,78,216,0.5)",
         "🏠  Simuler mon foyer  →"),
        (c2, "btn_comp", "comparaison",
         "🎓", "Enfant majeur : rattacher ?",
         "Comparez les deux scénarios et choisissez la meilleure option fiscale pour votre famille.",
         "#1a2e1a", "rgba(34,197,94,0.3)", "#86efac",
         ["Rattachement", "Foyer indép.", "Pension alim.", "Verdict auto"],
         "rgba(22,83,45,0.2)", "rgba(22,83,45,0.5)",
         "🎓  Comparer les scénarios  →"),
        (c3, "btn_dir", "dirigeant",
         "💼", "Revenus de dirigeant",
         "IS, dividendes, TNS, LMNP, SCI... Optimisez votre rémunération selon votre statut juridique.",
         "#2d1a0e", "rgba(251,146,60,0.3)", "#fdba74",
         ["IS / SARL", "BIC / BNC", "LMNP / SCI", "TNS", "Dividendes"],
         "rgba(124,45,13,0.2)", "rgba(124,45,13,0.5)",
         "💼  Simuler mes revenus pro  →"),
    ]

    for (col, btn_key, mode_val,
         ico, titre, desc,
         bg2, border_col, title_col,
         tags, tag_bg, tag_border,
         btn_label) in cards:
        with col:
            tag_html = "".join([
                f'<span style="background:{tag_bg};color:{title_col};'
                f'border:1px solid {tag_border};border-radius:20px;'
                f'padding:.12rem .55rem;font-size:.7rem;font-weight:600">{t}</span> '
                for t in tags
            ])
            st.markdown(f"""<div style="
              background:linear-gradient(160deg,#1e293b 55%,{bg2});
              border:1.5px solid {border_col};border-radius:18px;
              padding:1.6rem 1.4rem 1.2rem;min-height:240px;
              box-shadow:0 8px 28px rgba(0,0,0,0.4);
              transition:transform .2s,box-shadow .2s">
              <div style="font-size:2.2rem;margin-bottom:.5rem">{ico}</div>
              <h3 style="color:{title_col};font-size:1.05rem;font-weight:700;
                margin:0 0 .5rem;letter-spacing:-.3px">{titre}</h3>
              <p style="color:#94a3b8;font-size:.83rem;line-height:1.65;
                margin:0 0 1rem">{desc}</p>
              <div style="display:flex;flex-wrap:wrap;gap:.3rem">{tag_html}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(btn_label, key=btn_key, use_container_width=True):
                SS.mode = mode_val; SS.data = {}; next_step()

    # ── Section "Ce que vous obtenez" ─────────────────────────────
    st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)
    feats = [
        ("🎯", "Calcul officiel DGFiP",       "Barème 2026, décote, quotient familial, plafonnement QF"),
        ("📐", "Frais réels automatiques",      "Barème km, repas, télétravail — comparaison instantanée"),
        ("💡", "Optimisations personnalisées",  "PER, dons, emploi domicile, heures sup, syndicat"),
        ("🎓", "Comparaison enfant majeur",     "Rattachement vs indép. avec verdict fiscal automatique"),
        ("📋", "Guide des cases 2042",          "Chaque case expliquée avec montant à reporter"),
        ("📄", "Rapport PDF professionnel",     "Bilan complet avec conseils d'optimisation"),
    ]
    st.markdown("""<div style="background:linear-gradient(135deg,#1e293b,#162032);
      border:1px solid rgba(255,255,255,0.06);border-radius:16px;
      padding:1.4rem 1.8rem;box-shadow:0 4px 20px rgba(0,0,0,0.3)">
      <div style="text-align:center;margin-bottom:1.1rem">
        <span style="color:#93c5fd;font-size:.85rem;font-weight:700;
          text-transform:uppercase;letter-spacing:.8px">Ce que vous obtenez</span>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:.9rem">""" +
      "".join([
          f'<div style="display:flex;gap:.6rem;align-items:flex-start">'
          f'<span style="font-size:1.1rem;flex-shrink:0">{ico}</span>'
          f'<div><div style="color:#e2e8f0;font-weight:600;font-size:.82rem">{titre}</div>'
          f'<div style="color:#64748b;font-size:.74rem;margin-top:.15rem">{desc}</div></div></div>'
          for ico, titre, desc in feats
      ]) +
      "</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
    st.markdown("""<div class="src">
      Simulation à titre informatif — Brochure DGFiP 2025 (revenus 2024) —
      Consultez impots.gouv.fr ou un expert-comptable pour votre situation personnelle.
    </div>""", unsafe_allow_html=True)


elif SS.mode in ("foyer", "comparaison"):
    d = SS.data
    steps = STEPS_COMP if SS.mode == "comparaison" else STEPS_FOYER
    render_progress(steps, SS.step)
    home_button()

    # ── Étape 1 : Situation familiale ──────────────────────────────
    if SS.step == 1:
        st.markdown("## Quelle est votre situation familiale ?")
        st.caption("Ces informations determinent votre nombre de parts fiscales.")

        sit = st.radio("Vous etes :", [
            "Celibataire / Divorce(e)",
            "Marie(e) ou Pacse(e)",
            "Veuf(ve)",
        ], key="sit_radio", index=["Celibataire / Divorce(e)", "Marie(e) ou Pacse(e)", "Veuf(ve)"].index(
            d.get('situation', "Celibataire / Divorce(e)")))

        st.markdown("---")
        nb_enf = st.slider("Combien d'enfants mineurs avez-vous a charge ?", 0, 10,
                           int(d.get('nb_enfants', 0)), key="nb_enf_s")

        parent_isole = False
        if sit in ("Celibataire / Divorce(e)", "Veuf(ve)") and nb_enf > 0:
            parent_isole = st.checkbox(
                "Je suis parent isole (case T sur la declaration)",
                value=d.get('parent_isole', False),
                help="+1 part entiere pour le 1er enfant a charge")

        invalide = st.checkbox(
            "Je beneficie d'une carte d'invalidite >= 80 % (+0,5 part)",
            value=d.get('invalide', False))

        if sit == "Marie(e) ou Pacse(e)":
            st.info("Votre conjoint(e) sera renseigne a l'etape suivante.")

        # Enfants majeurs rattaches
        st.markdown("---")
        st.markdown("**Avez-vous des enfants majeurs rattaches a votre foyer ?**")
        nb_rat = st.number_input(
            "Nombre d'enfants majeurs rattaches (leurs revenus s'ajoutent au foyer, +0,5 part chacun)",
            0, 3, int(d.get('nb_rat', 0)), key="nb_rat_s")

        enfants_rattaches = d.get('enfants_rattaches', [])
        enfants_rattaches_new = []
        for i in range(int(nb_rat)):
            st.markdown(f"**Enfant majeur rattache n°{i+1}**")
            er = enfants_rattaches[i] if i < len(enfants_rattaches) else {}
            c1, c2 = st.columns(2)
            with c1:
                sal_r = st.number_input(f"Ses salaires EUR", 0, 200000, int(er.get('salaire',0)), 500, key=f"sal_r_{i}")
                pen_r = st.number_input(f"Ses pensions EUR", 0, 100000, int(er.get('pension',0)), 200, key=f"pen_r_{i}")
            with c2:
                hs_r = st.number_input(f"Heures sup EUR (case 1GH)", 0, 7500, int(er.get('heures_sup',0)), 100, key=f"hs_r_{i}")
                etud_r = st.checkbox(f"Etudiant (exo. 5 301 EUR)", er.get('etudiant', False), key=f"etud_r_{i}")
                exo_r = min(sal_r, 5301) if etud_r else 0
                if etud_r and exo_r:
                    st.caption(f"Exoneration : {fr(exo_r)} EUR")
            enfants_rattaches_new.append({'salaire': sal_r, 'pension': pen_r, 'heures_sup': hs_r,
                                          'exoneration_etudiant': exo_r, 'etudiant': etud_r,
                                          'frais_reels': False, 'montant_fr': 0})

        # Mapping vers le nom interne
        sit_map = {"Celibataire / Divorce(e)":"Celibataire / Divorce(e)",
                   "Marie(e) ou Pacse(e)":"Marie(e) / Pacse(e)",
                   "Veuf(ve)":"Veuf(ve)"}
        d.update({'situation': sit_map[sit], 'nb_enfants': nb_enf,
                  'parent_isole': parent_isole, 'invalide': invalide,
                  'nb_rat': nb_rat, 'enfants_rattaches': enfants_rattaches_new})
        nav_buttons()

    # ── Étape 2 : Revenus Déclarant 1 ─────────────────────────────
    elif SS.step == 2:
        st.markdown("## Vos revenus 2024 — Declarant 1")
        st.caption("Indiquez les montants bruts avant tout abattement. Vous les trouvez sur vos bulletins de salaire ou votre avis d'imposition.")

        st.info(
            "**Arrêt maladie en 2024 ?** "
            "Les indemnités journalières CPAM sont **imposables** et pré-remplies dans votre case 1AJ. "
            "**Exception : IJ pour ALD (maladie longue durée) → exonérées, ne pas inclure.**"
        )
        c1, c2 = st.columns(2)
        with c1:
            sal1 = st.number_input("Salaires / Traitements EUR (case 1AJ — inclut IJ CPAM maladie ordinaire)",
                                   0, 500000, int(d.get('sal1', 45000)), 500, key="sal1_w",
                                   help="Inclut salaires + IJ maladie ordinaire/maternité/paternité. Excluez IJ ALD.")
            pen1 = st.number_input("Pensions / Retraites EUR (case 1AS)",
                                   0, 200000, int(d.get('pen1', 0)), 200, key="pen1_w")
        with c2:
            hsup1 = st.number_input(
                "dont Heures supplementaires exonerees EUR (case 1GH)",
                0, 7500, int(d.get('hsup1', 0)), 100, key="hsup1_w",
                help="Inclus dans les salaires ci-dessus. Exoneration d'IR plafonnee a 7 500 EUR/an.")
            if hsup1:
                st.success(f"Exoneration IR : {fr(min(hsup1, 7500))} EUR")

        # Autres revenus
        st.markdown("---")
        autres_rev_on = st.checkbox(
            "J'ai d'autres types de revenus (placements, assurance vie, PEA, CTO...)",
            value=d.get('autres_rev_on', False), key="autres_rev_on_w")
        ar_data = {}
        if autres_rev_on:
            st.markdown("#### Revenus de placements — informations simplifiees")
            ar1, ar2, ar3 = st.columns(3)
            with ar1:
                av_gain  = st.number_input("Gains assurance vie EUR", 0, 500000, int(d.get('av_gain',0)), 500, key="av_gain_w")
                av_duree = st.number_input("Duree du contrat (ans)", 0, 50, int(d.get('av_duree',9)), 1, key="av_duree_w")
                av_vers  = st.number_input("Versements totaux EUR", 0, 1000000, int(d.get('av_vers',50000)), 5000, key="av_vers_w")
            with ar2:
                pea_gain = st.number_input("Gains PEA EUR", 0, 500000, int(d.get('pea_gain',0)), 500, key="pea_gain_w")
                pea_age  = st.number_input("Age du PEA (ans)", 0, 40, int(d.get('pea_age',6)), 1, key="pea_age_w")
            with ar3:
                cto_pv   = st.number_input("Plus-values CTO EUR", 0, 500000, int(d.get('cto_pv',0)), 500, key="cto_pv_w")
                cto_div  = st.number_input("Dividendes CTO EUR", 0, 200000, int(d.get('cto_div',0)), 200, key="cto_div_w")
            ar_data = {'av_gain': av_gain, 'av_duree': av_duree, 'av_vers': av_vers,
                       'pea_gain': pea_gain, 'pea_age': pea_age, 'pea_clot': False,
                       'cto_pv': cto_pv, 'cto_div': cto_div}

        d.update({'sal1': sal1, 'pen1': pen1, 'hsup1': hsup1,
                  'autres_rev_on': autres_rev_on, 'ar_data': ar_data})
        nav_buttons()

    # ── Étape 3 : Revenus D2 (si couple) ou Frais Pro (si seul) ────
    elif SS.step == 3:
        if d.get('situation') == "Marie(e) / Pacse(e)":
            st.markdown("## Revenus 2024 — Declarant 2 (conjoint / partenaire)")
            c1, c2 = st.columns(2)
            with c1:
                sal2 = st.number_input("Salaires / Traitements EUR (case 1BJ)",
                                       0, 500000, int(d.get('sal2',0)), 500, key="sal2_w")
                pen2 = st.number_input("Pensions / Retraites EUR (case 1BS)",
                                       0, 200000, int(d.get('pen2',0)), 200, key="pen2_w")
            with c2:
                hsup2 = st.number_input("dont Heures sup EUR (case 1HH)",
                                        0, 7500, int(d.get('hsup2',0)), 100, key="hsup2_w")
                if hsup2: st.success(f"Exoneration IR : {fr(min(hsup2, 7500))} EUR")
            d.update({'sal2': sal2, 'pen2': pen2, 'hsup2': hsup2})
        else:
            d.setdefault('sal2', 0); d.setdefault('pen2', 0); d.setdefault('hsup2', 0)
            st.markdown("## Cette etape ne vous concerne pas")
            st.info("Vous n'avez pas de co-declarant. Cliquez sur Suivant.")
        nav_buttons()

    # ── Étape 4 : Frais professionnels ────────────────────────────
    elif SS.step == 4:
        st.markdown("## Frais professionnels")
        st.markdown("""
        Le calculateur va **estimer automatiquement** vos frais deductibles et les comparer avec
        l'abattement forfaitaire de 10 % (applique automatiquement si vous ne renseignez rien).
        """)

        sal_ref = d.get('sal1', 0)
        forfait = max(moteur.ABATTEMENT_SALAIRES_MIN,
                      min(sal_ref * 0.10, moteur.ABATTEMENT_SALAIRES_MAX))
        st.markdown(f'<div class="highlight">Votre abattement forfaitaire actuel : <b>{fr(forfait)} EUR</b> — les frais reels ne sont utiles que s\'ils depassent ce montant.</div>',
                    unsafe_allow_html=True)

        tabs_fr = st.tabs(["🚗 Deplacement", "🍽️ Repas", "💻 Teletravail", "📚 Autres"])

        with tabs_fr[0]:
            st.markdown("#### Frais de deplacement — bareme kilometrique 2024")
            st.caption("Renseignez les informations de votre vehicule pour calculer vos indemnites kilomestriques.")
            fa, fb = st.columns(2)
            with fa:
                tveh = st.selectbox("Type de vehicule",
                    ["thermique","electrique","moto","cyclo"],
                    format_func={"thermique":"Voiture thermique/hybride",
                        "electrique":"Voiture electrique (+20 %)",
                        "moto":"Moto","cyclo":"Cyclomoteur"}.get,
                    index=["thermique","electrique","moto","cyclo"].index(d.get('fr_tveh','thermique')),
                    key="tveh_w")
                cv = 5
                if tveh in ("thermique","electrique"):
                    cv = st.select_slider("Puissance fiscale du vehicule (CV)",
                        [3,4,5,6,7], d.get('fr_cv', 5), key="cv_w")
                km = st.number_input("Kilometres professionnels en 2024",
                    0, 100000, int(d.get('fr_km', 0)), 500, key="km_w",
                    help="Domicile-travail (si domicile eloigne du lieu de travail) + deplacements pro")
            with fb:
                if km > 0:
                    fkm = round(FraisReels.calculer_bareme_km(km, cv, tveh), 2)
                    st.markdown(f"""<div class="card">
                    <h4>Indemnites kilomestriques 2024</h4>
                    {km:,} km &times; bareme {tveh} {cv} CV<br>
                    <span style="font-size:1.4rem;font-weight:700;color:#4ade80">{fr(fkm)} EUR</span><br>
                    <span style="color:#94a3b8;font-size:.82rem">vs forfait actuel : {fr(forfait)} EUR</span>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown("""<div class="card">
                    <h4>Aucun km renseigne</h4>
                    <p style="color:#94a3b8;font-size:.88rem">Renseignez vos km professionnels pour estimer vos indemnites.</p>
                    </div>""", unsafe_allow_html=True)
            d.update({'fr_tveh': tveh, 'fr_cv': cv, 'fr_km': km})

        with tabs_fr[1]:
            st.markdown("#### Frais de repas professionnels")
            st.info("Vous pouvez deduire la difference entre le cout d'un repas pris a l'exterieur et la valeur d'un repas au domicile (5,35 EUR en 2024).")

            nb_rep = st.number_input("Nombre de repas pris a l'exterieur pour raisons professionnelles en 2024",
                0, 300, int(d.get('fr_nb_rep', 0)), 5, key="nb_rep_w")

            if nb_rep > 0:
                st.markdown("---")
                rep_type = st.radio("Avez-vous des justificatifs (tickets, factures) ?",
                    ["Aucun justificatif", "Justificatifs partiels", "Tous les justificatifs"],
                    index=int(d.get('fr_rep_type_idx', 0)), key="rep_type_w")

                nb_avec = 0; montant_avec = 0
                if rep_type != "Aucun justificatif":
                    nb_avec = st.number_input("Nombre de repas avec justificatifs",
                        0, nb_rep, int(min(d.get('fr_nb_avec',0), nb_rep)), key="nb_avec_w")
                    if nb_avec > 0:
                        montant_avec = st.number_input(
                            f"Montant total des {nb_avec} repas avec justificatifs EUR",
                            0.0, 10000.0, float(d.get('fr_montant_avec', nb_avec * 15.0)),
                            0.5, key="montant_avec_w",
                            help="Indiquez le montant total que vous avez paye")

                # Tickets restaurant
                st.markdown("---")
                tickets_on = st.checkbox("Mon employeur verse des tickets restaurant",
                    value=d.get('fr_tickets_on', False), key="tickets_on_w")
                tr_val = tr_pat = 0
                if tickets_on:
                    tc1, tc2 = st.columns(2)
                    with tc1:
                        tr_val = st.number_input("Valeur faciale des tickets (EUR/ticket)",
                            0.0, 25.0, float(d.get('fr_tr_val', 10.0)), 0.5, key="tr_val_w")
                    with tc2:
                        tr_pat_pct = st.slider("Part patronale (%)",
                            50, 70, int(d.get('fr_tr_pat_pct', 60)), key="tr_pat_w")
                        nb_tickets = min(nb_rep, 220)
                        tr_pat = round(tr_val * tr_pat_pct / 100 * nb_tickets, 2)
                        st.caption(f"Part patronale annuelle estimee : {fr(tr_pat)} EUR")
                    d.update({'fr_tr_val': tr_val, 'fr_tr_pat_pct': tr_pat_pct})

                # Calcul automatique
                rep_calc = calculer_frais_repas(
                    nb_repas_pro_an=nb_rep,
                    repas_avec_justif=nb_avec,
                    montant_total_avec_justif=montant_avec,
                    tickets_resto_part_patronale=tr_pat,
                )
                rep_idx = ["Aucun justificatif","Justificatifs partiels","Tous les justificatifs"].index(rep_type)
                d.update({'fr_nb_rep': nb_rep, 'fr_rep_type_idx': rep_idx,
                          'fr_nb_avec': nb_avec, 'fr_montant_avec': montant_avec,
                          'fr_tickets_on': tickets_on, 'fr_tr_pat': tr_pat})

                st.markdown(f"""<div class="compare-bar">
                <b style="color:#93c5fd">Calcul automatique frais de repas</b><br>
                <div class="fr-row">
                <div class="fr-item"><div class="lbl">Repas sans justif ({rep_calc['nb_repas_sans_justif']})</div>
                <div class="val">{fr(rep_calc['deductible_sans_justif'])} EUR</div></div>
                <div class="fr-item"><div class="lbl">Repas avec justif ({rep_calc['nb_repas_avec_justif']})</div>
                <div class="val">{fr(rep_calc['deductible_avec_justif'])} EUR</div></div>
                </div>
                {"<div class='fr-item'><div class='lbl'>Deduction tickets resto</div><div class='val'>-"+fr(rep_calc['avantage_ticket_resto'])+" EUR</div></div>" if tr_pat > 0 else ""}
                <b style="color:#4ade80">Total repas deductibles : {fr(rep_calc['total_deductible_repas'])} EUR</b>
                </div>""", unsafe_allow_html=True)
                d['fr_repas_deductibles'] = rep_calc['total_deductible_repas']

        with tabs_fr[2]:
            st.markdown("#### Teletravail")
            jours_tt = st.number_input("Jours de teletravail en 2024",
                0, 230, int(d.get('fr_jours_tt', 0)), 5, key="jours_tt_w",
                help="Allocation forfaitaire : 2,70 EUR/jour, plafond 59,40 EUR/mois")
            if jours_tt > 0:
                ftt = min(jours_tt * 2.70, 59.40 * 12)
                st.success(f"Frais teletravail : {fr(ftt)} EUR")
            d['fr_jours_tt'] = jours_tt

        with tabs_fr[3]:
            st.markdown("#### Autres frais justifies")
            fa2, fb2 = st.columns(2)
            with fa2:
                double_res = st.number_input("Double residence EUR", 0, 30000, int(d.get('fr_double_res',0)), 200, key="dres_w")
                formation  = st.number_input("Formation professionnelle EUR", 0, 20000, int(d.get('fr_formation',0)), 100, key="form_w")
            with fb2:
                materiel   = st.number_input("Materiel et outillage EUR", 0, 20000, int(d.get('fr_materiel',0)), 100, key="mat_w")
                autres_fr  = st.number_input("Autres frais justifies EUR", 0, 20000, int(d.get('fr_autres',0)), 100, key="autr_w")
            d.update({'fr_double_res': double_res, 'fr_formation': formation,
                      'fr_materiel': materiel, 'fr_autres': autres_fr})

        # ── Calcul global frais réels ──
        fr_data = {
            'km': d.get('fr_km', 0), 'cv': d.get('fr_cv', 5),
            'type_vehicule': d.get('fr_tveh', 'thermique'),
            'nb_repas': d.get('fr_nb_rep', 0),
            'nb_repas_avec_justif': d.get('fr_nb_avec', 0),
            'montant_repas_justif': d.get('fr_montant_avec', 0),
            'tickets_part_patronale': d.get('fr_tr_pat', 0),
            'jours_teletravail': d.get('fr_jours_tt', 0),
            'double_residence': d.get('fr_double_res', 0),
            'formation': d.get('fr_formation', 0),
            'materiel': d.get('fr_materiel', 0),
            'autres': d.get('fr_autres', 0),
        }
        calcul_fr = calculer_frais_reels_complets(fr_data, sal_ref)
        d['calcul_fr_d1'] = calcul_fr

        st.markdown("---")
        col_r1, col_r2 = st.columns(2)
        total_fr = calcul_fr['total_frais_reels']
        ff = calcul_fr['forfait_10pct']
        gain = calcul_fr['gain_vs_forfait']

        with col_r1:
            c_gain = "#4ade80" if gain > 0 else "#f87171"
            st.markdown(f"""<div class="compare-bar">
            <b style="color:#93c5fd">Comparaison frais reels vs forfait</b><br><br>
            Forfait 10 % automatique : <b>{fr(ff)} EUR</b><br>
            Vos frais reels calcules : <b>{fr(total_fr)} EUR</b><br>
            Difference : <b style="color:{c_gain}">{"+" if gain > 0 else ""}{fr(gain)} EUR</b><br><br>
            <b style="color:{c_gain}">{calcul_fr['recommandation']}</b>
            </div>""", unsafe_allow_html=True)

        with col_r2:
            if total_fr > 0:
                detail_items = [
                    ("Frais km", calcul_fr['frais_km']),
                    ("Frais repas", calcul_fr['frais_repas']),
                    ("Teletravail", calcul_fr['frais_teletravail']),
                    ("Double residence", calcul_fr['double_residence']),
                    ("Formation", calcul_fr['formation']),
                    ("Materiel", calcul_fr['materiel']),
                    ("Autres", calcul_fr['autres']),
                ]
                detail_html = "".join(
                    f"<div style='display:flex;justify-content:space-between;padding:.2rem 0'>"
                    f"<span style='color:#94a3b8;font-size:.85rem'>{label}</span>"
                    f"<b style='font-size:.85rem'>{fr(val)} EUR</b></div>"
                    for label, val in detail_items if val > 0)
                st.markdown(f"""<div class="card">
                <h4>Detail des frais reels</h4>
                {detail_html}
                <div style="border-top:1px solid #334155;margin:.5rem 0;padding-top:.4rem;
                  display:flex;justify-content:space-between">
                <b>Total</b><b style="color:#4ade80">{fr(total_fr)} EUR</b></div>
                </div>""", unsafe_allow_html=True)

        # Frais D2 si couple
        if d.get('situation') == "Marie(e) / Pacse(e)" and d.get('sal2', 0) > 0:
            st.markdown("---")
            st.markdown("#### Frais professionnels — Declarant 2")
            d2_km = st.number_input("Km pro D2", 0, 100000, int(d.get('fr_km_d2',0)), 500, key="km_d2_w")
            d2_rep = st.number_input("Repas pro D2", 0, 300, int(d.get('fr_rep_d2',0)), 5, key="rep_d2_w")
            fr_d2 = calculer_frais_reels_complets(
                {'km': d2_km, 'nb_repas': d2_rep, 'cv': 5, 'type_vehicule': 'thermique'},
                d.get('sal2', 0))
            d.update({'fr_km_d2': d2_km, 'fr_rep_d2': d2_rep, 'calcul_fr_d2': fr_d2})
            if fr_d2['total_frais_reels'] > 0:
                c_g2 = "#4ade80" if fr_d2['gain_vs_forfait'] > 0 else "#f87171"
                st.markdown(f"Frais reels D2 : **{fr(fr_d2['total_frais_reels'])} EUR** vs forfait **{fr(fr_d2['forfait_10pct'])} EUR** — "
                            f"<span style='color:{c_g2}'>{fr_d2['recommandation']}</span>", unsafe_allow_html=True)

        nav_buttons()

    # ── Étape 5 : Déductions ───────────────────────────────────────
    elif SS.step == 5:
        st.markdown("## Deductions du revenu global")
        st.caption("Ces elements reduisent directement votre revenu imposable avant calcul de l'impot.")

        st.markdown("#### Plan Epargne Retraite (PER)")
        per = st.number_input(
            "Versements PER en 2024 EUR (cases 6NS / 6NT / 6NU)",
            0, 80000, int(d.get('per', 0)), 500, key="per_w",
            help="Deductible dans la limite de 10 % de vos revenus (minimum 4 637 EUR, maximum 37 094 EUR)")

        sal_total = d.get('sal1',0) + d.get('sal2',0)
        plaf_per = max(4637, min(sal_total * 0.10, 37094))
        if per > 0:
            eco_per_est = min(per, plaf_per) * 0.30
            st.success(f"Plafond annuel disponible : {fr(plaf_per)} EUR — Economie fiscale estimee (TMI 30 %) : {fr(eco_per_est)} EUR")
            if per > plaf_per:
                st.warning(f"Votre versement depasse le plafond ({fr(plaf_per)} EUR). Seule la partie dans le plafond sera deductible.")

        st.markdown("---")
        st.markdown("#### Pension alimentaire")
        pen_versee = st.number_input(
            "Pension alimentaire versee a un enfant majeur EUR (case 6GI)",
            0, 20000, int(d.get('pen_versee', 0)), 200, key="pen_v_w",
            help="Plafond legal 2024 : 6 794 EUR par enfant majeur hors foyer")
        if pen_versee > 6794:
            st.warning("Plafond de deductibilite : 6 794 EUR. L'excedent ne sera pas deductible.")

        st.markdown("---")
        cot_synd = st.number_input(
            "Cotisations syndicales EUR (case 7AC)",
            0, 2000, int(d.get('cot_synd', 0)), 50, key="synd_w",
            help="Credit d'impot 66 % dans la limite de 1 % des salaires")

        d.update({'per': per, 'pen_versee': pen_versee, 'cot_synd': cot_synd})
        nav_buttons()

    # ── Étape 6 : Credits & Réductions ────────────────────────────
    elif SS.step == 6:
        st.markdown("## Credits et reductions d'impot")

        st.markdown("#### Dons et liberalites")
        c_d1, c_d2, c_d3 = st.columns(3)
        with c_d1:
            dons_75 = st.number_input("Dons 75 % (aide personnes) EUR", 0, 5000, int(d.get('dons_75',0)), 50, key="d75_w", help="Case 7UD — plafond 1 000 EUR — Croix-Rouge, Resto du Coeur...")
        with c_d2:
            dons_mayo = st.number_input("Dons Mayotte urgence 75 % EUR", 0, 5000, int(d.get('dons_mayo',0)), 50, key="dmayo_w", help="Case 7UM — cyclone Chido 14/12/2024 au 17/05/2025")
        with c_d3:
            dons_66 = st.number_input("Dons 66 % (associations) EUR", 0, 50000, int(d.get('dons_66',0)), 50, key="d66_w", help="Case 7VC — plafond 20 % du RNI")

        st.markdown("---")
        st.markdown("#### Garde d'enfants de moins de 6 ans")
        nb_enf6 = st.number_input("Nombre d'enfants de moins de 6 ans au 01/01/2024",
            0, 5, int(d.get('nb_enf6',0)), key="nb_enf6_w")
        res_alt = False; frais_garde = 0
        if nb_enf6 > 0:
            res_alt = st.checkbox("Residence alternee (plafond divise par 2)", d.get('res_alt', False), key="res_alt_w")
            frais_garde = st.number_input("Frais de garde EUR (creche, assistante maternelle)",
                0, 15000, int(d.get('frais_garde',0)), 100, key="garde_w",
                help="Cases 7GA-7GC — credit d'impot 50 %, plafond 3 500 EUR/enfant")
            plaf_g = (3500 / (2 if res_alt else 1)) * nb_enf6
            if frais_garde > 0:
                st.success(f"Credit estime : {fr(min(frais_garde, plaf_g) * 0.5)} EUR (plafond depenses : {fr(plaf_g)} EUR)")

        st.markdown("---")
        st.markdown("#### Emploi a domicile")
        prem_annee = st.checkbox("Premiere annee d'emploi d'un salarie a domicile (+3 000 EUR de plafond)", d.get('prem_annee', False), key="prem_annee_w")
        emploi_dom = st.number_input("Depenses d'emploi a domicile EUR",
            0, 25000, int(d.get('emploi_dom',0)), 200, key="emp_dom_w",
            help="Cases 7DB/7DQ — credit 50 %, plafond 12 000 EUR + 1 500 EUR/enfant a charge")
        if emploi_dom > 0:
            plaf_e = (15000 if prem_annee else 12000) + d.get('nb_enfants',0) * 1500
            st.success(f"Credit estime : {fr(min(emploi_dom, min(plaf_e, 18000 if prem_annee else 15000)) * 0.5)} EUR")

        d.update({'dons_75': dons_75, 'dons_mayo': dons_mayo, 'dons_66': dons_66,
                  'nb_enf6': nb_enf6, 'res_alt': res_alt, 'frais_garde': frais_garde,
                  'prem_annee': prem_annee, 'emploi_dom': emploi_dom})
        nav_buttons()

    # ── Étape 7 : Enfant majeur (mode comparaison uniquement) ──────
    elif SS.step == 7 and SS.mode == "comparaison":
        st.markdown("## Profil fiscal de votre enfant majeur")
        st.markdown("""
        Renseignez la situation **comme si votre enfant declarait seul**.
        Le simulateur comparera ensuite :
        - **Scenario A** — Rattachement : ses revenus integres dans votre foyer
        - **Scenario B** — Foyer independant : sa propre declaration + pension eventuelle
        """)

        et1, et2, et3 = st.tabs(["Situation & Revenus","Deductions","Statut & Pension"])
        with et1:
            ea, eb_c = st.columns(2)
            ed = d.get('enf_data', {})
            with ea:
                sit_enf = st.selectbox("Statut matrimonial",
                    ["Celibataire / Divorce(e)","Marie(e) / Pacse(e)","Veuf(ve)"],
                    index=["Celibataire / Divorce(e)","Marie(e) / Pacse(e)","Veuf(ve)"].index(ed.get('situation',"Celibataire / Divorce(e)")),
                    key="sit_enf_w")
                nb_enf_enf = st.number_input("Ses propres enfants a charge",0,10,int(ed.get('nb_enfants',0)),key="enf_enf_w")
                inv_enf = st.checkbox("Invalide >= 80 %",ed.get('invalide',False),key="inv_enf_w")
            with eb_c:
                sal1_enf = st.number_input("Salaires EUR (case 1AJ)",0,200000,int(ed.get('sal1',18000)),500,key="sal1_enf_w",help="Emploi etudiant, alternance, CDI...")
                pen1_enf = st.number_input("Pensions EUR (case 1AS)",0,100000,int(ed.get('pen1',0)),200,key="pen1_enf_w")
                hsup1_enf = st.number_input("Heures sup EUR (case 1GH)",0,7500,int(ed.get('hsup1',0)),100,key="hsup1_enf_w")
                sal2_enf = pen2_enf = 0
                if sit_enf == "Marie(e) / Pacse(e)":
                    sal2_enf = st.number_input("Salaires conjoint(e) EUR",0,200000,int(ed.get('sal2',0)),500,key="sal2_enf_w")

        with et2:
            ec1, ec2 = st.columns(2)
            with ec1:
                per_enf = st.number_input("PER EUR",0,20000,int(ed.get('per',0)),200,key="per_enf_w")
                dons_75_enf = st.number_input("Dons 75 % EUR",0,2000,int(ed.get('d75',0)),50,key="d75e_w")
                dons_66_enf = st.number_input("Dons 66 % EUR",0,10000,int(ed.get('d66',0)),50,key="d66e_w")
            with ec2:
                emploi_enf = st.number_input("Emploi domicile EUR",0,15000,int(ed.get('emploi',0)),200,key="emp_enf_w")

        with et3:
            eg1, eg2 = st.columns(2)
            with eg1:
                etudiant_enf = st.checkbox("Enfant etudiant (< 26 ans)",ed.get('etudiant',False),key="etudiant_enf_w",
                    help="Exoneration emploi etudiant : 5 301 EUR max (art. 81 bis CGI)")
                if etudiant_enf:
                    niveau_enf = st.selectbox("Niveau d'etudes",list(moteur.SCOLARITE.keys()),key="niv_enf_w")
                    red_scol_est = moteur.SCOLARITE.get(niveau_enf,183)
                    st.success(f"Exoneration : {fr(min(sal1_enf,5301))} EUR | Reduction scolarite (Scenario A) : {red_scol_est} EUR")
                else:
                    niveau_enf = list(moteur.SCOLARITE.keys())[-1]
            with eg2:
                pension_enf = st.slider("Pension que vous pourriez verser EUR",0,6794,int(ed.get('pension',6794)),100,key="pension_enf_w",
                    help="Deductible chez vous (case 6GI) — Imposable chez l'enfant (case 1AS) — Plafond 6 794 EUR")
                st.caption("Chez vous : deductible **case 6GI**")
                st.caption("Chez l'enfant : imposable **case 1AS**")

        exo_etud_enf = min(sal1_enf, 5301) if etudiant_enf else 0
        d['enf_data'] = {
            'situation': sit_enf, 'nb_enfants': nb_enf_enf,
            'invalide': inv_enf, 'parent_isole': False,
            'sal1': sal1_enf, 'pen1': pen1_enf, 'hsup1': hsup1_enf,
            'sal2': sal2_enf, 'pen2': 0,
            'per': per_enf, 'd75': dons_75_enf, 'd66': dons_66_enf,
            'emploi': emploi_enf, 'etudiant': etudiant_enf,
            'exo_etudiant': exo_etud_enf, 'niveau': niveau_enf,
            'pension': pension_enf,
        }
        nav_buttons()

    # ── Étape 7 (foyer) ou 8 (comp) : Résultats ───────────────────
    elif SS.step in (7, 8):
        # Normalisation des numéros d'étape selon le mode
        step_res = 7 if SS.mode == "foyer" else 8

        if SS.step != step_res:
            next_step()
            st.stop()

        st.markdown("## Vos resultats fiscaux 2026")

        # Construire frais réels finaux
        calcul_fr_d1 = d.get('calcul_fr_d1', {})
        use_fr1 = calcul_fr_d1.get('utiliser_frais_reels', False)
        mfr1 = calcul_fr_d1.get('total_frais_reels', 0) if use_fr1 else 0

        calcul_fr_d2 = d.get('calcul_fr_d2', {})
        use_fr2 = calcul_fr_d2.get('utiliser_frais_reels', False)
        mfr2 = calcul_fr_d2.get('total_frais_reels', 0) if use_fr2 else 0

        profil = {
            'situation': d.get('situation','Celibataire / Divorce(e)'),
            'nb_enfants': d.get('nb_enfants', 0),
            'invalide_declarant': d.get('invalide', False),
            'parent_isole': d.get('parent_isole', False),
            'revenu_salaire_declarant': d.get('sal1', 0),
            'revenu_pension_declarant': d.get('pen1', 0),
            'revenu_salaire_conjoint':  d.get('sal2', 0),
            'revenu_pension_conjoint':  d.get('pen2', 0),
            'heures_sup_declarant':     d.get('hsup1', 0),
            'heures_sup_conjoint':      d.get('hsup2', 0),
            'frais_reels': use_fr1, 'montant_frais_reels_1': mfr1,
            'frais_reels_2': use_fr2, 'montant_frais_reels_2': mfr2,
            'versement_per': d.get('per', 0),
            'cotisations_syndicales': d.get('cot_synd', 0),
            'pension_alimentaire_versee': min(d.get('pen_versee',0), 6794),
            'dons_60_75': d.get('dons_75', 0),
            'dons_mayotte': d.get('dons_mayo', 0),
            'dons_60': d.get('dons_66', 0),
            'nb_enfants_moins_6': d.get('nb_enf6', 0),
            'residence_alternee': d.get('res_alt', False),
            'frais_garde': d.get('frais_garde', 0),
            'premiere_annee_emploi': d.get('prem_annee', False),
            'emploi_domicile': d.get('emploi_dom', 0),
            'enfants_rattaches': d.get('enfants_rattaches', []),
        }
        res = moteur.calculer(profil)
        conseils = moteur.generer_conseils(profil, res)
        SS.profil = profil
        SS.res = res
        SS.conseils = conseils

        # ── KPIs ──
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(kpi_html("Revenu Net Imposable",f"{fr(res['revenu_imposable'])} EUR","#93c5fd"),unsafe_allow_html=True)
        with k2: st.markdown(kpi_html("Impot brut",f"{fr(res['impot_brut'])} EUR","#f87171"),unsafe_allow_html=True)
        with k3: st.markdown(kpi_html("Decote",f"-{fr(res['decote'])} EUR","#4ade80"),unsafe_allow_html=True)
        with k4: st.markdown(kpi_html("IMPOT NET A PAYER",f"{fr(res['impot_net'])} EUR","#60a5fa"),unsafe_allow_html=True)
        st.markdown("")
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Taux moyen", f"{res['taux_moyen']:.2f} %")
        with m2: st.metric("TMI", f"{res['taux_marginal']} %")
        with m3: st.metric("Parts fiscales", f"{res['nb_parts']:.1f}")
        with m4:
            if use_fr1: st.metric("Frais reels D1", f"{fr(mfr1)} EUR", delta=f"+{fr(calcul_fr_d1.get('gain_vs_forfait',0))} EUR vs forfait")
            else: st.metric("Abattement", f"{fr(res['abattement_applique'])} EUR")

        st.markdown('<div class="src">Bareme 2024 — DGFiP 2025 — Decote : 889 - 45,25 % x impot — QF plafonne 1 791 EUR/demi-part</div>',unsafe_allow_html=True)

        # Graphique tranches
        tr = [t for t in res['detail_tranches'] if t['impot_tranche'] > 0]
        if tr:
            fig = go.Figure([go.Bar(
                x=[t['label'] for t in tr], y=[t['impot_tranche'] for t in tr],
                marker_color=['#1e3a5f','#1d4ed8','#3b82f6','#60a5fa','#93c5fd'][:len(tr)],
                text=[f"{fr(t['impot_tranche'])} EUR" for t in tr],
                textposition='outside', textfont=dict(color='#e2e8f0'))])
            fig.update_layout(
                height=290,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(30,41,59,0.85)',
                font=dict(color='#e2e8f0', family='Inter, sans-serif'),
                showlegend=False,
                margin=dict(t=24,b=24,l=12,r=12),
                hoverlabel=dict(bgcolor='#1e293b', font_color='#e2e8f0',
                                bordercolor='#334155'),
            )
            fig.update_yaxes(gridcolor='#334155', gridwidth=0.5,
                             zeroline=False, showline=False)
            fig.update_xaxes(tickfont=dict(size=8), showline=False)
            st.plotly_chart(fig, use_container_width=True)

        # Comparaison enfant majeur
        if SS.mode == "comparaison" and d.get('enf_data'):
            st.markdown("---")
            st.markdown("### Comparaison enfant majeur")
            ed = d['enf_data']
            profil_enf = {
                'situation': ed['situation'], 'nb_enfants': ed['nb_enfants'],
                'invalide_declarant': ed.get('invalide',False), 'parent_isole': False,
                'revenu_salaire_declarant': ed['sal1'], 'revenu_pension_declarant': ed['pen1'],
                'revenu_salaire_conjoint': ed.get('sal2',0), 'revenu_pension_conjoint': 0,
                'heures_sup_declarant': ed.get('hsup1',0), 'heures_sup_conjoint': 0,
                'frais_reels': False, 'montant_frais_reels_1': 0,
                'frais_reels_2': False, 'montant_frais_reels_2': 0,
                'versement_per': ed.get('per',0), 'cotisations_syndicales': 0,
                'dons_60_75': ed.get('d75',0), 'dons_mayotte': 0, 'dons_60': ed.get('d66',0),
                'nb_enfants_moins_6': 0, 'residence_alternee': False,
                'frais_garde': 0, 'premiere_annee_emploi': False,
                'emploi_domicile': ed.get('emploi',0),
                'etudiant': ed.get('etudiant',False),
                'exoneration_emploi_etudiant': ed.get('exo_etudiant',0),
                'niveau_etude': ed.get('niveau', list(moteur.SCOLARITE.keys())[-1]),
                'pension_recue': ed.get('pension',6794),
            }
            sc_obj = ScenarioEnfantMajeur(moteur)
            comp = sc_obj.comparer(profil, profil_enf)
            SS.comparaison = comp
            SS.profil_enfant = profil_enf

            sc_a = comp['scenario_a']; sc_b = comp['scenario_b']
            meill = comp['meilleur_scenario']
            pb = sc_b['parents']; eb = sc_b['enfant']
            etud = comp.get('etudiant', False)

            ca_c, cb_c = st.columns(2)
            with ca_c:
                bc = "#1d4ed8" if meill == "A" else "#334155"
                lines_a = [
                    f"Parts avec enfant : {sc_a['nb_parts']:.1f}",
                    f"Revenus enfant integres : {fr(sc_a['revenus_enfant_integres'])} EUR",
                ]
                if etud and sc_a.get('exoneration_etudiant',0):
                    lines_a.append(f"Exoneration etudiant : -{fr(sc_a['exoneration_etudiant'])} EUR")
                lines_a += [
                    f"RNI foyer : {fr(sc_a['rni'])} EUR",
                    f"IR avant red. scol. : {fr(sc_a['impot_net_avant_scol'])} EUR",
                ]
                if etud and sc_a.get('reduction_scolarite',0):
                    lines_a.append(f"Red. scolarite : -{sc_a['reduction_scolarite']} EUR")

                body_a = "".join(f"<div style='padding:.2rem 0;color:#cbd5e1;font-size:.88rem'>{l}</div>" for l in lines_a)
                st.markdown(f"""<div class="card" style="border-color:{bc}">
                <h4>{'🏆 ' if meill=='A' else ''}Scenario A — Rattachement</h4>
                {body_a}
                <div style="margin-top:.8rem;font-size:1.3rem;font-weight:700;color:#60a5fa">
                Impot net total : {fr(sc_a['cout_total'])} EUR</div>
                </div>""", unsafe_allow_html=True)

            with cb_c:
                bc = "#16a34a" if meill == "B" else "#334155"
                lines_b_p = [
                    f"Parts parents : {pb['nb_parts']:.1f}",
                    f"Pension versee (6GI) : -{fr(pb.get('pension_versee',0))} EUR",
                    f"IR parents : {fr(pb['impot_net'])} EUR",
                ]
                lines_b_e = [f"Parts enfant : {eb['nb_parts']:.1f}"]
                if etud and eb.get('exoneration_etudiant',0):
                    lines_b_e.append(f"Exoneration etudiant : -{fr(eb['exoneration_etudiant'])} EUR")
                lines_b_e += [
                    f"Pension recue (1AS) : {fr(eb.get('pension_recue',0))} EUR",
                    f"RNI enfant : {fr(eb['revenu_imposable'])} EUR",
                    f"TMI enfant : {eb.get('taux_marginal',0)} %",
                    f"IR enfant : {fr(eb['impot_net'])} EUR",
                ]
                body_p = "".join(f"<div style='padding:.15rem 0;color:#cbd5e1;font-size:.85rem'>{l}</div>" for l in lines_b_p)
                body_e = "".join(f"<div style='padding:.15rem 0;color:#cbd5e1;font-size:.85rem'>{l}</div>" for l in lines_b_e)
                st.markdown(f"""<div class="card" style="border-color:{bc}">
                <h4>{'🏆 ' if meill=='B' else ''}Scenario B — Foyer independant</h4>
                <div style="color:#94a3b8;font-size:.8rem;margin-bottom:.3rem">PARENTS</div>{body_p}
                <div style="color:#94a3b8;font-size:.8rem;margin:.5rem 0 .3rem">ENFANT</div>{body_e}
                <div style="margin-top:.8rem;font-size:1.3rem;font-weight:700;color:#4ade80">
                Total : {fr(sc_b['cout_total'])} EUR</div>
                </div>""", unsafe_allow_html=True)

            cls = "verdict-good" if meill == "A" else "verdict-good"
            col = "#60a5fa" if meill == "A" else "#4ade80"
            lab = "Rattachement (A)" if meill == "A" else "Foyer independant (B)"
            st.markdown(f"""<div style="background:#1e3a5f;border-left:4px solid {col};
              border-radius:0 8px 8px 0;padding:1rem;margin:.7rem 0">
            <h3 style="color:{col};margin:0">Recommandation : {lab}</h3>
            <p style="margin:.4rem 0 0">Economie : {fr(comp['economie'])} EUR par rapport a l'autre scenario.</p>
            </div>""", unsafe_allow_html=True)

        # Conseils
        if conseils:
            st.markdown("---")
            st.markdown("### Conseils personnalises")
            icones = {'PER':'💰','FR':'📋','DONS':'❤️','DOM':'🏠','TMI':'📉','SYND':'🤝','HS':'⏰'}
            for c in conseils:
                ic = icones.get(c['icone'], '💡')
                st.markdown(f"""<div class="conseil">
                <b>{ic} {c['titre']}</b><br>
                <span style="color:#fbbf24;font-size:.85rem">{c['detail']}</span></div>""",
                    unsafe_allow_html=True)

        nav_buttons(label_next="Exporter le rapport PDF →")

    # ── Étape 8 (foyer) ou 9 (comp) : Export PDF ──────────────────
    elif SS.step in (8, 9):
        step_pdf = 8 if SS.mode == "foyer" else 9
        if SS.step != step_pdf:
            next_step(); st.stop()

        st.markdown("## Votre bilan fiscal PDF")
        st.markdown("Votre rapport personalise est pret a etre genere.")

        if not hasattr(SS, 'res') or SS.res is None:
            st.warning("Veuillez d'abord completer les etapes precedentes.")
            nav_buttons(can_next=False)
        else:
            profil = SS.profil
            res    = SS.res
            conseils = SS.conseils
            comp   = getattr(SS, 'comparaison', None)
            p_enf  = getattr(SS, 'profil_enfant', None)

            st.markdown(f"""<div class="card">
            <h4>Contenu du rapport</h4>
            Resume de simulation : RNI <b>{fr(res['revenu_imposable'])} EUR</b> — Impot net <b>{fr(res['impot_net'])} EUR</b><br>
            Detail par tranche &bull; Guide des cases a renseigner (impots.gouv.fr)<br>
            {str(len(conseils))} conseil(s) d'optimisation personnalise(s)
            {"<br>Comparaison enfant majeur incluse" if comp else ""}
            </div>""", unsafe_allow_html=True)

            if st.button("Generer et telecharger le PDF", type="primary"):
                with st.spinner("Generation du rapport..."):
                    try:
                        gen = GenererRapportPDF()
                        pdf_bytes = gen.generer(profil, res, conseils, comp,
                            profil_enfant=p_enf, res_enfant_seul=None)
                        b64 = base64.b64encode(pdf_bytes).decode()
                        href = (f'<a href="data:application/pdf;base64,{b64}" '
                                f'download="bilan_fiscal_2026.pdf" '
                                f'style="display:inline-block;background:#1d4ed8;color:white;'
                                f'padding:.8rem 2rem;border-radius:8px;text-decoration:none;'
                                f'font-weight:700;font-size:1rem">Telecharger mon bilan fiscal PDF</a>')
                        st.markdown(href, unsafe_allow_html=True)
                        st.success("Rapport genere !")
                    except Exception as e:
                        st.error(f"Erreur : {e}")
                        raise

            st.markdown("---")
            if st.button("Recommencer une nouvelle simulation"):
                SS.step = 0; SS.data = {}; SS.mode = None
                SS.resultats = None
                if hasattr(SS, 'res'): del SS.res
                if hasattr(SS, 'profil'): del SS.profil
                if hasattr(SS, 'comparaison'): del SS.comparaison
                st.rerun()

        nav_buttons(can_next=False)

# ═══════════════════════════════════════════════════════════════════
# WIZARD DIRIGEANT
# ═══════════════════════════════════════════════════════════════════
elif SS.mode == "dirigeant":
    d = SS.data
    render_progress(STEPS_DIR, SS.step)
    home_button()

    if SS.step == 1:
        st.markdown("## Vos parametres generaux")
        tmi_dir = st.select_slider("Votre taux marginal d'imposition (TMI)",
            [0,11,30,41,45], int(d.get('tmi_dir',30)), key="tmi_dir_w")
        statut_dir = st.selectbox("Votre statut social actuel",
            list(dm.TNS_COTISATIONS.keys()),
            format_func=lambda x: dm.TNS_COTISATIONS[x]['label'],
            index=list(dm.TNS_COTISATIONS.keys()).index(d.get('statut_dir','gerant_majoritaire_sarl')),
            key="statut_dir_w")
        cot = dm.TNS_COTISATIONS[statut_dir]
        avt = "".join(f"<li style='color:#4ade80;font-size:.83rem'>{a}</li>" for a in cot['avantages'])
        inc = "".join(f"<li style='color:#f87171;font-size:.83rem'>{i}</li>" for i in cot['inconvenients'])
        st.markdown(f"""<div class="card">
        <h4>{cot['label']}</h4>
        Taux de charges global : <b>{int(cot['taux_global']*100)} %</b><br>
        <div style="display:flex;gap:2rem;margin-top:.5rem">
        <div><b style="color:#4ade80">Avantages</b><ul style="margin:.3rem 0 0 1rem">{avt}</ul></div>
        <div><b style="color:#f87171">Points de vigilance</b><ul style="margin:.3rem 0 0 1rem">{inc}</ul></div>
        </div></div>""", unsafe_allow_html=True)
        d.update({'tmi_dir': tmi_dir, 'statut_dir': statut_dir})
        nav_buttons()

    elif SS.step == 2:
        st.markdown("## Votre remuneration")
        rem_ts = st.number_input("Remuneration annuelle brute EUR",0,500000,int(d.get('rem_ts',60000)),1000,key="rem_ts_w")
        if rem_ts > 0:
            tmi = d.get('tmi_dir',30)
            statut = d.get('statut_dir','gerant_majoritaire_sarl')
            ab_ts = max(504, min(rem_ts*0.10, 14426))
            imp_ts = max(0, rem_ts - ab_ts)
            ir_ts = int(imp_ts * tmi / 100)
            cot = dm.calculer_cotisations_tns(rem_ts, statut)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""<div class="card">
                <h4>Traitement et salaires (case 1AJ)</h4>
                Brute : {fr(rem_ts)} EUR<br>
                Abattement 10 % : -{fr(ab_ts)} EUR<br>
                Imposable : {fr(imp_ts)} EUR<br>
                IR estime (TMI {tmi} %) : <b>{fr(ir_ts)} EUR</b>
                </div>""", unsafe_allow_html=True)
            with c2:
                det = "".join(f"<div style='display:flex;justify-content:space-between;padding:.2rem 0'>"
                    f"<span style='color:#94a3b8;font-size:.83rem'>{k}</span>"
                    f"<b style='font-size:.83rem'>{v}</b></div>"
                    for k,v in cot['detail'].items())
                st.markdown(f"""<div class="card">
                <h4>Cotisations sociales ({int(cot['taux_global']*100)} %)</h4>
                {det}
                <div style="border-top:1px solid #334155;margin-top:.4rem;padding-top:.4rem">
                <div style="display:flex;justify-content:space-between">
                <b>Total cotisations</b><b style="color:#f87171">{fr(cot['cotisations'])} EUR</b></div>
                <div style="display:flex;justify-content:space-between">
                <b>Net avant IR</b><b style="color:#4ade80">{fr(cot['net_avant_ir'])} EUR</b></div>
                </div></div>""", unsafe_allow_html=True)
            # Comparaison statuts
            st.markdown("---")
            st.markdown("**Comparaison entre tous les statuts**")
            cmpg = dm.comparer_statuts(rem_ts, tmi)
            df_c = pd.DataFrame([{"Statut": r['label'].split('(')[0].strip(),
                "Charges": f"{r['taux_charges']} %", "Cotisations": f"{fr(r['cotisations'])} EUR",
                "IR estime": f"{fr(r['ir_estime'])} EUR", "Net final": f"{fr(r['net_final'])} EUR",
            } for r in cmpg])
            st.dataframe(df_c, hide_index=True, use_container_width=True)
        d['rem_ts'] = rem_ts
        nav_buttons()

    elif SS.step == 3:
        st.markdown("## IS et Dividendes")
        tmi = d.get('tmi_dir',30)
        c1, c2 = st.columns(2)
        with c1:
            res_fisc = st.number_input("Resultat fiscal de la societe EUR",
                -200000,5000000,int(d.get('res_fisc',80000)),1000,key="resfisc_w")
            if res_fisc > 0:
                is_d = dm.calculer_is(res_fisc)
                st.markdown(f"""<div class="card"><h4>Calcul IS 2024</h4>
                Base 15 % : {fr(is_d['base_reduit'])} EUR => IS : {fr(is_d['is_reduit'])} EUR<br>
                Base 25 % : {fr(is_d['base_normal'])} EUR => IS : {fr(is_d['is_normal'])} EUR<br>
                <b style="color:#f87171">IS total : {fr(is_d['is_total'])} EUR</b> ({is_d['taux_effectif']:.2f} %)<br>
                <b style="color:#4ade80">Benefice net : {fr(is_d['benefice_net'])} EUR</b></div>""",
                unsafe_allow_html=True)
        with c2:
            div_b = st.number_input("Dividendes bruts a distribuer EUR",
                0,2000000,int(d.get('div_b',0)),1000,key="div_b_w")
            if div_b > 0:
                dd = dm.calculer_dividendes(div_b, tmi)
                pfu = dd['pfu']; bar = dd['bareme']
                meill_d = dd['meilleur']
                for lbl, opt, color in [
                    ("PFU 30 %", pfu, "#60a5fa" if meill_d=="PFU" else "#475569"),
                    (f"Bareme {tmi} % + abatt. 40 %", bar, "#4ade80" if meill_d=="Bareme" else "#475569")
                ]:
                    best = "Recommande" if (meill_d=="PFU" and "PFU" in lbl) or (meill_d=="Bareme" and "bareme" in lbl.lower()) else ""
                    st.markdown(f"""<div class="card" style="border-color:{color}">
                    <h4 style="color:{color}">{'Recommande : ' if best else ''}{lbl}</h4>
                    IR : {fr(opt.get('ir',0))} EUR | PS : {fr(opt.get('ps',0))} EUR<br>
                    <b>Total : {fr(opt['total_imposition'])} EUR | Net : {fr(opt['net_percu'])} EUR</b>
                    </div>""", unsafe_allow_html=True)
        d.update({'res_fisc': res_fisc, 'div_b': div_b})
        nav_buttons()

    elif SS.step == 4:
        st.markdown("## BIC / BNC")
        tmi = d.get('tmi_dir', 30)
        regime = st.selectbox("Regime fiscal de votre activite", [
            "BIC micro - ventes/commerce","BIC micro - prestations de services",
            "BIC reel (declaration 2031)","BNC micro (liberale)",
            "BNC reel - declaration controlee (2035)"],
            index=int(d.get('regime_idx',0)), key="regime_w")
        ca_b = st.number_input("CA annuel / Recettes EUR",0,5000000,int(d.get('ca_b',60000)),1000,key="ca_b_w")
        ch_b = am_b = 0
        if "reel" in regime.lower():
            c1, c2 = st.columns(2)
            with c1: ch_b = st.number_input("Charges deductibles EUR",0,5000000,int(d.get('ch_b',40000)),1000,key="ch_b_w")
            with c2: am_b = st.number_input("Amortissements EUR",0,500000,int(d.get('am_b',0)),1000,key="am_b_w") if "BIC" in regime else 0

        if ca_b:
            if "ventes" in regime: r_b = dm.calculer_bic_micro(ca_b,'vente')
            elif "services" in regime and "BIC" in regime: r_b = dm.calculer_bic_micro(ca_b,'services')
            elif "BIC reel" in regime: r_b = dm.calculer_bic_reel(ca_b,ch_b,am_b)
            elif "BNC micro" in regime: r_b = dm.calculer_bnc_micro(ca_b)
            else: r_b = dm.calculer_bnc_reel(ca_b,ch_b)
            imposable = r_b.get('benefice_imposable',r_b.get('imposable',0))
            ir_est = int(imposable * tmi / 100)
            abatt_info = (f"Abattement {r_b['abattement_pct']} % : -{fr(r_b.get('abattement_montant',0))} EUR<br>"
                          if 'abattement_pct' in r_b else f"Charges : -{fr(r_b.get('charges',0))} EUR<br>")
            col_v = "#4ade80" if imposable >= 0 else "#f87171"
            elig_info = (f"Seuil : {fr(r_b.get('seuil_regime',r_b.get('seuil',0)))} EUR — {'OK' if r_b.get('eligible',True) else 'Depasse'}<br>"
                         if 'eligible' in r_b else "")
            st.markdown(f"""<div class="card"><h4>{r_b.get('type',regime)}</h4>
            CA : {fr(ca_b)} EUR<br>{abatt_info}
            <b style="color:{col_v}">Benefice imposable : {fr(imposable)} EUR</b><br>
            {elig_info}IR estime (TMI {tmi} %) : <b>{fr(ir_est)} EUR</b></div>""",unsafe_allow_html=True)

        d.update({'regime_idx': ["BIC micro - ventes/commerce","BIC micro - prestations de services",
            "BIC reel (declaration 2031)","BNC micro (liberale)","BNC reel - declaration controlee (2035)"].index(regime),
            'ca_b': ca_b, 'ch_b': ch_b, 'am_b': am_b})
        nav_buttons()

    elif SS.step == 5:
        st.markdown("## Revenus immobiliers")
        tmi = d.get('tmi_dir',30)
        itype = st.selectbox("Type de bien/regime", [
            "Micro-foncier","Foncier reel (2044)","LMNP Micro-BIC",
            "LMNP Reel","LMP","SCI a l'IR","SCI a l'IS"],
            index=int(d.get('itype_idx',0)), key="itype_w")
        rfb = st.number_input("Revenus/Recettes/Resultat EUR",-200000,5000000,int(d.get('rfb',15000)),500,key="rfb_w")
        int_e=ch_f=trav=tf_f=fg_f=ch_lmnp=am_lmnp=ch_lmp=am_lmp=aut_rev=sci_qp=lmnp_cl=0
        if "Foncier reel" in itype:
            c1,c2=st.columns(2)
            with c1:
                int_e=st.number_input("Interets emprunt EUR",0,200000,int(d.get('int_e',5000)),200,key="int_e_w")
                ch_f=st.number_input("Charges EUR",0,100000,int(d.get('ch_f',2000)),100,key="ch_f_w")
                trav=st.number_input("Travaux EUR",0,500000,int(d.get('trav',0)),500,key="trav_w")
            with c2:
                tf_f=st.number_input("Taxe fonciere EUR",0,20000,int(d.get('tf_f',1000)),100,key="tf_f_w")
                fg_f=st.number_input("Frais gestion EUR",0,20000,int(d.get('fg_f',500)),100,key="fg_f_w")
        elif "LMNP Reel" in itype:
            ch_lmnp=st.number_input("Charges EUR",0,200000,int(d.get('ch_lmnp',5000)),500,key="ch_lmnp_w")
            am_lmnp=st.number_input("Amortissements EUR",0,200000,int(d.get('am_lmnp',4000)),500,key="am_lmnp_w")
        elif "LMNP Micro" in itype:
            lmnp_cl = st.checkbox("Bien classe",d.get('lmnp_cl',False),key="lmnp_cl_w")
        elif "LMP" in itype:
            ch_lmp=st.number_input("Charges EUR",0,500000,int(d.get('ch_lmp',8000)),500,key="ch_lmp_w")
            am_lmp=st.number_input("Amortissements EUR",0,300000,int(d.get('am_lmp',6000)),500,key="am_lmp_w")
            aut_rev=st.number_input("Autres revenus pro foyer EUR",0,500000,int(d.get('aut_rev',45000)),1000,key="aut_rev_w")
        elif "SCI IS" in itype:
            sci_qp = st.slider("Quote-part (%)",1,100,int(d.get('sci_qp',100)),1,key="sci_qp_w") / 100

        if "Micro-foncier" in itype: r_im=dm.calculer_foncier_micro(rfb)
        elif "Foncier reel" in itype: r_im=dm.calculer_foncier_reel(rfb,int_e,ch_f,trav,tf_f,fg_f)
        elif "LMNP Micro" in itype: r_im=dm.calculer_lmnp(rfb,lmnp_cl,'micro')
        elif "LMNP Reel" in itype: r_im=dm.calculer_lmnp(rfb,False,'reel',ch_lmnp,am_lmnp)
        elif "LMP" in itype: r_im=dm.calculer_lmp(rfb,ch_lmp,am_lmp,aut_rev)
        elif "SCI a l'IR" in itype: r_im=dm.calculer_sci_ir(rfb)
        else: r_im=dm.calculer_sci_is(rfb,sci_qp)

        imposable = r_im.get('imposable',r_im.get('benefice_imposable',0))
        col_r="#4ade80" if imposable>=0 else "#f87171"
        st.markdown(f"""<div class="card"><h4>Resultat {itype}</h4>
        <b style="color:{col_r}">Imposable/Resultat : {fr(imposable)} EUR</b><br>
        IR estime (TMI {tmi} %) : {fr(int(imposable*tmi/100))} EUR<br>
        {"PS 17,2 % : "+fr(r_im.get('ps',0))+" EUR<br>" if 'ps' in r_im else ""}
        {"Note : "+str(r_im.get('note','')) if r_im.get('note') else ""}
        </div>""", unsafe_allow_html=True)
        d.update({'itype_idx': ["Micro-foncier","Foncier reel (2044)","LMNP Micro-BIC","LMNP Reel",
            "LMP","SCI a l'IR","SCI a l'IS"].index(itype), 'rfb': rfb})
        nav_buttons()

    elif SS.step == 6:
        st.markdown("## Recommandations d'optimisation fiscale")
        ben_opt = st.number_input("Benefice annuel de la societe EUR",0,5000000,int(d.get('res_fisc',150000)),5000,key="ben_opt_w")
        rem_opt = st.number_input("Remuneration actuelle EUR",0,500000,int(d.get('rem_ts',70000)),5000,key="rem_opt_w")
        tmi_opt = d.get('tmi_dir',30)
        stat_opt = d.get('statut_dir','gerant_majoritaire_sarl')

        if ben_opt > 0:
            opts = dm.optimisation_fiscale({'benefice': ben_opt, 'remuneration': rem_opt,
                'tmi': tmi_opt, 'statut_actuel': stat_opt, 'ca': ben_opt*3, 'type_activite': 'services'})
            impact_colors = {"Tres eleve":"#f59e0b","Eleve":"#3b82f6","A evaluer":"#8b5cf6","Moyen":"#6b7280"}
            for i, opt in enumerate(opts, 1):
                ic = impact_colors.get(opt['impact'],"#6b7280")
                gain_str = f" — Gain : {fr(opt['gain_estime'])} EUR" if opt['gain_estime'] else ""
                pour_html = "".join(f"<div style='color:#4ade80;font-size:.82rem'>+ {p}</div>" for p in opt['pour'])
                contre_html = "".join(f"<div style='color:#f87171;font-size:.82rem'>- {c}</div>" for c in opt['contre'])
                st.markdown(f"""<div style="background:#1e293b;border-left:4px solid {ic};
                  border-radius:0 8px 8px 0;padding:1rem;margin:.5rem 0">
                <div style="color:{ic};font-weight:600">{i}. {opt['titre']}
                <span style="background:{ic}22;color:{ic};font-size:.73rem;
                  padding:.15rem .5rem;border-radius:12px;margin-left:.4rem">{opt['impact']}</span>{gain_str}</div>
                <div style="color:#94a3b8;font-size:.85rem;margin:.4rem 0">{opt['detail']}</div>
                <div style="color:#60a5fa;font-size:.83rem">Action : {opt['action']}</div>
                <div style="display:flex;gap:2rem;margin-top:.5rem">{pour_html}{contre_html}</div>
                </div>""", unsafe_allow_html=True)
        d.update({'ben_opt': ben_opt, 'rem_opt': rem_opt})
        nav_buttons(label_next="Generer le rapport PDF →")

    elif SS.step == 7:
        st.markdown("## Rapport PDF — Revenus de dirigeant")
        if st.button("Generer le rapport dirigeant PDF", type="primary"):
            with st.spinner("Generation..."):
                try:
                    from rapport_pdf import GenererRapportDirigeantPDF
                    profil_dir = {
                        'statut': d.get('statut_dir','gerant_majoritaire_sarl'),
                        'remuneration': d.get('rem_ts',0),
                        'tmi': d.get('tmi_dir',30),
                        'benefice': d.get('res_fisc',0),
                        'dividendes': d.get('div_b',0),
                    }
                    gen_d = GenererRapportDirigeantPDF()
                    pdf_bytes = gen_d.generer(profil_dir, dm)
                    b64 = base64.b64encode(pdf_bytes).decode()
                    href = (f'<a href="data:application/pdf;base64,{b64}" '
                            f'download="rapport_dirigeant_2026.pdf" '
                            f'style="display:inline-block;background:#1d4ed8;color:white;'
                            f'padding:.8rem 2rem;border-radius:8px;text-decoration:none;font-weight:700">'
                            f'Telecharger le rapport dirigeant PDF</a>')
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("Rapport genere !")
                except Exception as e:
                    st.error(f"Erreur : {e}"); raise

        st.markdown("---")
        if st.button("Recommencer"):
            for k in list(SS.keys()): del SS[k]
            st.rerun()
        nav_buttons(can_next=False)

# ═══════════════════════════════════════════════════════════════════
# FALLBACK
# ═══════════════════════════════════════════════════════════════════
else:
    st.error("Navigation incorrecte.")
    if st.button("Retour a l'accueil"):
        SS.step = 0; SS.mode = None; st.rerun()
