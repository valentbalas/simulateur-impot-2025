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

.stApp{background:#0f172a !important;color:#e2e8f0}
[data-testid="stHeader"]{background:#0f172a !important}
[data-testid="stSidebar"]{background:#1e293b !important}
.block-container{padding:1.2rem 2rem 2rem !important;max-width:1100px}

.stButton>button{background:linear-gradient(135deg,#1d4ed8,#2563eb);
  color:#fff;border:none;border-radius:10px;padding:.55rem 1.2rem;
  font-weight:600;font-size:.88rem;transition:all .2s;
  box-shadow:0 2px 8px rgba(29,78,216,0.35)}
.stButton>button:hover{background:linear-gradient(135deg,#1e40af,#1d4ed8);
  transform:translateY(-1px);box-shadow:0 4px 16px rgba(29,78,216,0.5)}

.stTextInput>div>div>input,.stNumberInput>div>div>input,
.stSelectbox>div>div,.stMultiSelect>div>div{
  background:#1e293b !important;color:#e2e8f0 !important;
  border:1px solid #334155 !important;border-radius:8px !important}
.stTextInput>div>div>input:focus,.stNumberInput>div>div>input:focus{
  border-color:#3b82f6 !important;box-shadow:0 0 0 2px rgba(59,130,246,0.2) !important}
.stSlider>div{color:#e2e8f0}
.stRadio>div,.stCheckbox>label{color:#e2e8f0 !important}
label{color:#94a3b8 !important;font-size:.85rem !important;font-weight:500}

.card{background:linear-gradient(135deg,#1e293b,#1a2540);
  border:1px solid #334155;border-radius:14px;padding:1.3rem;
  margin-bottom:.8rem;box-shadow:0 4px 16px rgba(0,0,0,0.3);
  transition:border-color .2s,box-shadow .2s}
.card:hover{border-color:#3b82f6;box-shadow:0 6px 24px rgba(59,130,246,0.15)}

.kpi{background:linear-gradient(135deg,#1e293b,#162032);
  border:1px solid #334155;border-radius:12px;padding:1rem;
  text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.3)}
.kpi-val{font-size:1.6rem;font-weight:800;color:#93c5fd;line-height:1.1}
.kpi-lbl{font-size:.75rem;color:#64748b;margin-top:.25rem;font-weight:500}

.src{font-size:.72rem;color:#475569;margin:.3rem 0;text-align:center}

.stAlert{background:#1e293b !important;border-radius:10px !important;
  border-left:3px solid #3b82f6 !important;color:#e2e8f0 !important}
.stInfo{background:#172133 !important;border-color:#1d4ed8 !important}
.stSuccess{background:#0f2218 !important;border-color:#16a34a !important}
.stWarning{background:#1c1207 !important;border-color:#d97706 !important}

/* ═══ WIZARD PROGRESS ═══════════════════════════════════════════ */
.wizard-wrap{background:linear-gradient(135deg,#1e293b,#162032);
  border:1px solid rgba(59,130,246,0.18);border-radius:16px;
  padding:1.1rem 1.4rem 1rem;margin-bottom:1.4rem;
  box-shadow:0 4px 20px rgba(0,0,0,0.3)}
.wiz-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:.75rem}
.wiz-title{font-size:.82rem;font-weight:700;color:#93c5fd;
  text-transform:uppercase;letter-spacing:.5px}
.wiz-pct{font-size:.82rem;font-weight:700;color:#60a5fa;
  background:rgba(59,130,246,0.12);border-radius:20px;
  padding:.15rem .65rem;border:1px solid rgba(59,130,246,0.2)}
.wiz-track{width:100%;height:8px;background:#0f172a;border-radius:999px;
  overflow:hidden;margin-bottom:.9rem}
.wiz-fill{height:100%;border-radius:999px;
  background:linear-gradient(90deg,#1d4ed8,#3b82f6,#60a5fa);
  transition:width .5s cubic-bezier(.4,0,.2,1);
  box-shadow:0 0 10px rgba(59,130,246,0.5)}
.wiz-steps{display:flex;align-items:flex-start;justify-content:space-between}
.wiz-step{display:flex;flex-direction:column;align-items:center;
  flex:1;position:relative;min-width:0}
.wiz-step:not(:last-child)::after{content:'';position:absolute;
  top:13px;left:calc(50% + 14px);right:calc(-50% + 14px);
  height:2px;background:#1e3a5f;z-index:0}
.wiz-step.s-done:not(:last-child)::after{
  background:linear-gradient(90deg,#1d4ed8,#334155)}
.wiz-dot{width:26px;height:26px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:11px;font-weight:700;flex-shrink:0;
  z-index:1;position:relative;transition:all .3s}
.s-done .wiz-dot{background:linear-gradient(135deg,#1d4ed8,#2563eb);
  color:#fff;box-shadow:0 2px 8px rgba(29,78,216,0.5)}
.s-active .wiz-dot{background:linear-gradient(135deg,#3b82f6,#60a5fa);
  color:#fff;
  box-shadow:0 0 0 4px rgba(59,130,246,0.25),0 2px 12px rgba(59,130,246,0.5)}
.s-todo .wiz-dot{background:#0f172a;color:#475569;
  border:1.5px solid #334155}
.wiz-lbl{font-size:9.5px;margin-top:.35rem;text-align:center;
  max-width:58px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.s-done .wiz-lbl{color:#93c5fd}
.s-active .wiz-lbl{color:#e2e8f0;font-weight:700}
.s-todo .wiz-lbl{color:#475569}

.stTabs [data-baseweb="tab"]{background:#1e293b;color:#94a3b8;
  border-radius:8px 8px 0 0;border:1px solid #334155;
  padding:.4rem 1rem;font-weight:500}
.stTabs [aria-selected="true"]{
  background:linear-gradient(135deg,#1d4ed8,#2563eb) !important;
  color:#fff !important;border-color:#1d4ed8 !important}
.streamlit-expanderHeader{background:#1e293b !important;
  color:#93c5fd !important;border-radius:8px !important;font-weight:600}
.stDataFrame{background:#1e293b !important;border-radius:10px;overflow:hidden}

::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:#0f172a}
::-webkit-scrollbar-thumb{background:#334155;border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:#475569}
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
          <span style="color:#fca5a5;font-weight:700">⚠️ Retourner à l\'accueil ?</span>
          <span style="color:#94a3b8;font-size:.85rem;margin-left:.5rem">
          Toutes vos données saisies seront perdues.</span>
        </div>""", unsafe_allow_html=True)
        c1, c2, _ = st.columns([1.4, 1.2, 5])
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
    "Accueil", "Statut", "Revenus", "Société & IS",
    "Immobilier", "Optimisation", "Rapport PDF"
]


def render_progress(steps, current):
    """Barre de progression avec % + dots connectés."""
    n = len(steps)
    active = n - 1
    pct = int((current / active) * 100) if active > 0 and current > 0 else 0
    pct = min(100, max(0, pct))
    step_label = steps[current] if current < n else steps[-1]

    dots_html = ''
    for i, label in enumerate(steps):
        if i < current:
            cls = "s-done"; sym = "&#10003;"
        elif i == current:
            cls = "s-active"; sym = str(i)
        else:
            cls = "s-todo"; sym = str(i)
        dots_html += (
            f'<div class="wiz-step {cls}">'
            f'<div class="wiz-dot">{sym}</div>'
            f'<span class="wiz-lbl">{label}</span>'
            f'</div>'
        )

    html = f"""<div class="wizard-wrap">
  <div class="wiz-top">
    <span class="wiz-title">&#128203;&nbsp; {step_label}</span>
    <span class="wiz-pct">{pct}%</span>
  </div>
  <div class="wiz-track">
    <div class="wiz-fill" style="width:{pct}%"></div>
  </div>
  <div class="wiz-steps">{dots_html}</div>
</div>"""
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
if SS.get('step', 0) > 0:
    if st.button("🧮  Simulateur IR 2026  ·  ← Retour à l\'accueil",
                 key="title_home_btn",
                 help="Cliquez pour revenir à la page d\'accueil"):
        has_data = bool(SS.get('data') and any(
            v for v in SS['data'].values() if v not in (0, False, None, [], {})))
        if has_data:
            SS['confirm_home'] = True
        else:
            for k in list(SS.keys()): del SS[k]
        st.rerun()
st.markdown("""
<div style="background:linear-gradient(135deg,#003189 0%,#1d4ed8 55%,#ed2939 100%);
  padding:1.2rem 2rem;border-radius:14px;color:white;text-align:center;margin-bottom:1.2rem">
  <h1 style="margin:0;font-size:1.7rem;font-weight:700">Simulateur Impot sur le Revenu 2026</h1>
  <p style="margin:.3rem 0 0;opacity:.9;font-size:.88rem">
    Declaration 2026 &bull; Revenus 2025 &bull; Bareme officiel DGFiP</p>
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
    line-height:1.75">
    Calculez votre impôt, optimisez votre situation fiscale et comparez vos scénarios
    — en quelques minutes, <strong style="color:#cbd5e1">gratuitement</strong>,
    selon le barème officiel DGFiP.
  </p>
</div>""", unsafe_allow_html=True)

    # ── 4 Badges ─────────────────────────────────────────────────
    b1, b2, b3, b4 = st.columns(4)
    for col, ico, titre, sous, acc in zip(
        [b1, b2, b3, b4],
        ["✅", "🔒", "⚡", "📄"],
        ["Barème officiel DGFiP", "100 % confidentiel", "Résultat immédiat", "Export PDF"],
        ["Données 2026 / Revenus 2025", "Aucune donnée transmise",
         "Calcul en temps réel", "Bilan complet téléchargeable"],
        ["rgba(34,197,94,0.12)", "rgba(168,85,247,0.12)",
         "rgba(234,179,8,0.12)", "rgba(59,130,246,0.12)"],
    ):
        with col:
            st.markdown(f"""<div style="background:linear-gradient(135deg,#1e293b,#162032);
              border:1px solid rgba(255,255,255,0.06);border-radius:14px;
              padding:1rem .8rem;text-align:center;
              box-shadow:0 4px 16px rgba(0,0,0,0.4)">
              <div style="width:40px;height:40px;border-radius:12px;background:{acc};
                margin:0 auto .5rem;display:flex;align-items:center;
                justify-content:center;font-size:1.3rem">{ico}</div>
              <div style="color:#e2e8f0;font-weight:700;font-size:.82rem;
                margin-bottom:.2rem">{titre}</div>
              <div style="color:#64748b;font-size:.72rem;line-height:1.4">{sous}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="text-align:center;margin-bottom:1.2rem">
      <span style="background:rgba(59,130,246,0.1);color:#93c5fd;
        border:1px solid rgba(59,130,246,0.25);border-radius:20px;
        padding:.3rem 1rem;font-size:.8rem;font-weight:700;
        text-transform:uppercase;letter-spacing:1px">
        Choisissez votre simulation
      </span>
    </div>""", unsafe_allow_html=True)

    # ── 3 Cartes ─────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    cards = [
        (c1,"btn_foyer","foyer","🏠","Mon foyer fiscal",
         "Calculez l'impôt de votre foyer avec toutes les déductions, crédits et optimisations personnalisées.",
         "#1e3a5f","rgba(59,130,246,0.3)","#93c5fd",
         ["Salaires","Pensions","PER","Frais réels","Heures sup"],
         "rgba(29,78,216,0.18)","rgba(29,78,216,0.45)","🏠  Simuler mon foyer  →"),
        (c2,"btn_comp","comparaison","🎓","Enfant majeur : rattacher ?",
         "Comparez les deux scénarios et choisissez la meilleure option fiscale pour votre famille.",
         "#1a2e1a","rgba(34,197,94,0.3)","#86efac",
         ["Rattachement","Foyer indép.","Pension alim.","Verdict auto"],
         "rgba(22,83,45,0.18)","rgba(22,83,45,0.45)","🎓  Comparer les scénarios  →"),
        (c3,"btn_dir","dirigeant","💼","Revenus de dirigeant",
         "IS, dividendes, TNS, LMNP, SCI... Optimisez votre rémunération selon votre statut.",
         "#2d1a0e","rgba(251,146,60,0.3)","#fdba74",
         ["IS / SARL","BIC / BNC","LMNP / SCI","TNS","Dividendes"],
         "rgba(124,45,13,0.18)","rgba(124,45,13,0.45)","💼  Simuler mes revenus pro  →"),
    ]
    for (col,bk,mode,ico,titre,desc,bg2,bc,tc,tags,tag_bg,tag_bd,btn) in cards:
        with col:
            tags_html = "".join([
                f'<span style="background:{tag_bg};color:{tc};border:1px solid {tag_bd};'
                f'border-radius:20px;padding:.1rem .55rem;font-size:.7rem;font-weight:600">{t}</span> '
                for t in tags])
            st.markdown(f"""<div style="background:linear-gradient(160deg,#1e293b 55%,{bg2});
              border:1.5px solid {bc};border-radius:18px;
              padding:1.6rem 1.4rem 1.2rem;min-height:240px;
              box-shadow:0 8px 28px rgba(0,0,0,0.4)">
              <div style="font-size:2.2rem;margin-bottom:.5rem">{ico}</div>
              <h3 style="color:{tc};font-size:1.05rem;font-weight:700;
                margin:0 0 .5rem">{titre}</h3>
              <p style="color:#94a3b8;font-size:.83rem;line-height:1.65;
                margin:0 0 1rem">{desc}</p>
              <div style="display:flex;flex-wrap:wrap;gap:.3rem">{tags_html}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(btn, key=bk, use_container_width=True):
                SS.mode = mode; SS.data = {}; next_step()

    # ── Section fonctionnalités ───────────────────────────────────
    st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)
    feats = [
        ("🎯","Calcul officiel DGFiP","Barème 2026, décote, quotient familial"),
        ("📐","Frais réels automatiques","Barème km, repas, télétravail"),
        ("💡","Optimisations","PER, dons, emploi domicile, heures sup"),
        ("🎓","Enfant majeur","Rattachement vs indép. avec verdict"),
        ("📋","Guide cases 2042","Chaque case expliquée + montant"),
        ("📄","Rapport PDF","Bilan complet téléchargeable"),
    ]
    feats_html = "".join([
        f'<div style="display:flex;gap:.6rem;align-items:flex-start">' +
        f'<span style="font-size:1.1rem;flex-shrink:0">{i}</span>' +
        f'<div><div style="color:#e2e8f0;font-weight:600;font-size:.82rem">{t}</div>' +
        f'<div style="color:#64748b;font-size:.73rem;margin-top:.1rem">{d}</div></div></div>'
        for i,t,d in feats])
    st.markdown(f"""<div style="background:linear-gradient(135deg,#1e293b,#162032);
      border:1px solid rgba(255,255,255,0.05);border-radius:16px;
      padding:1.4rem 1.8rem;box-shadow:0 4px 20px rgba(0,0,0,0.3)">
      <div style="text-align:center;margin-bottom:1rem">
        <span style="color:#93c5fd;font-size:.85rem;font-weight:700;
          text-transform:uppercase;letter-spacing:.8px">Ce que vous obtenez</span>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:.9rem">
        {feats_html}
      </div></div>""", unsafe_allow_html=True)
    st.markdown('<div class="src" style="margin-top:.8rem">Simulation à titre informatif — Brochure DGFiP 2025 — Consultez impots.gouv.fr ou un expert-comptable.</div>', unsafe_allow_html=True)


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
            "**Arrêt maladie en 2024 ?** Les IJ CPAM sont **imposables** et pré-remplies en case 1AJ. "
            "**Exception : IJ pour ALD (maladie longue durée) → exonérées, à exclure.**"
        )
        c1, c2 = st.columns(2)
        with c1:
            sal1 = st.number_input("Salaires / Traitements EUR (case 1AJ — inclut IJ CPAM maladie ordinaire)",
                                   0, 500000, int(d.get('sal1', 45000)), 500, key="sal1_w",
                                   help="Inclut salaires + IJ maladie/maternité/paternité. Excluez IJ ALD.")
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
            fig.update_layout(height=270,plot_bgcolor='#1e293b',paper_bgcolor='#1e293b',
                font=dict(color='#e2e8f0'),showlegend=False,margin=dict(t=20,b=20))
            fig.update_yaxes(gridcolor='#334155')
            fig.update_xaxes(tickfont=dict(size=8))
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
    from dirigeant import STATUTS
    d = SS.data
    s_key  = d.get("statut_key", "ae_bnc")
    s_info = STATUTS.get(s_key, STATUTS["ae_bnc"])
    tmi    = d.get("tmi_dir", 30)

    render_progress(STEPS_DIR, SS.step)
    home_button()

    # ── ÉTAPE 1 : SÉLECTION DU STATUT ────────────────────────────────────────
    if SS.step == 1:
        st.markdown("## 🏢 Quel est votre statut ?")
        st.caption("Sélectionnez votre situation pour que le simulateur ne vous pose que les questions pertinentes.")

        cat_cfg = {
            "Indépendant TNS":    ("#0f2040", "#3b82f6", "#93c5fd", "🔵 Indépendants & TNS"),
            "Dirigeant société IS": ("#2d1a0e", "#f97316", "#fdba74", "🟣 Dirigeants société IS"),
        }

        for cat, (bg_cat, bc_cat, tc_cat, titre_cat) in cat_cfg.items():
            items = [(k, v) for k, v in STATUTS.items() if v["categorie"] == cat]
            st.markdown(
                f'''<div style="background:rgba(255,255,255,0.03);border:1px solid #1e293b;
                border-radius:10px;padding:.5rem 1rem .3rem;margin:.8rem 0 .4rem">
                <span style="color:{tc_cat};font-size:.78rem;font-weight:700;
                text-transform:uppercase;letter-spacing:.8px">{titre_cat}</span></div>''',
                unsafe_allow_html=True)
            nb   = len(items)
            cols = st.columns(nb)
            for col, (key, sv) in zip(cols, items):
                selected  = (s_key == key)
                border_c  = bc_cat if selected else "#334155"
                bg_c      = bg_cat if selected else "#1e293b"
                check     = "✓ " if selected else ""
                with col:
                    st.markdown(
                        f'''<div style="background:{bg_c};border:2px solid {border_c};
                        border-radius:12px;padding:.8rem .7rem;min-height:110px">
                        <div style="font-size:1.2rem;margin-bottom:.3rem">{sv["icone"]}</div>
                        <div style="color:{"#e2e8f0"};font-weight:700;font-size:.78rem;
                        line-height:1.3;margin-bottom:.3rem">{sv["label"]}</div>
                        <div style="color:#64748b;font-size:.7rem;line-height:1.35">
                        {sv["description"][:75]}…</div></div>''',
                        unsafe_allow_html=True)
                    if st.button(f"{check}Sélectionner", key=f"sel_{key}", use_container_width=True):
                        save("statut_key", key)
                        st.rerun()

        sv      = STATUTS[s_key]
        pts_html = "".join(
            f'<li style="color:#e2e8f0;font-size:.82rem;margin:.25rem 0">{p}</li>'
            for p in sv["points_cles"])
        st.markdown(
            f'''<div class="card" style="margin-top:.9rem;border-color:#3b82f6">
            <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:.6rem">
              <span style="font-size:1.5rem">{sv["icone"]}</span>
              <div>
                <div style="color:#93c5fd;font-weight:700;font-size:.9rem">{sv["label"]}</div>
                <div style="color:#64748b;font-size:.72rem">{sv["categorie"]}</div>
              </div>
              <span style="margin-left:auto;background:#1e3a5f;color:#60a5fa;font-size:.72rem;
              padding:.15rem .55rem;border-radius:20px;border:1px solid #1d4ed8">{sv["fiscal"]}</span>
            </div>
            <div style="color:#94a3b8;font-size:.82rem;margin-bottom:.7rem">{sv["description"]}</div>
            <div style="color:#475569;font-size:.73rem;font-weight:700;text-transform:uppercase;
            letter-spacing:.5px;margin-bottom:.3rem">Points clés</div>
            <ul style="margin:.2rem 0 .6rem 1.1rem;padding:0">{pts_html}</ul>
            <div style="color:#475569;font-size:.74rem">📋 Cases 2042 :
            <strong style="color:#94a3b8">{sv["cases_2042"]}</strong></div>
            </div>''',
            unsafe_allow_html=True)

        st.markdown("---")
        tmi_val = st.select_slider(
            "Votre taux marginal d'imposition (TMI) estimé",
            options=[0, 11, 30, 41, 45],
            value=int(d.get("tmi_dir", 30)),
            key="tmidir_w",
            help="Utilisé pour les estimations d'économies fiscales dans les recommandations.")
        save("tmi_dir", tmi_val)
        nav_buttons()

    # ── ÉTAPE 2 : REVENUS (adapté au statut) ─────────────────────────────────
    elif SS.step == 2:
        sv     = STATUTS[s_key]
        tmi    = d.get("tmi_dir", 30)
        st.markdown(f"## {sv['icone']} Vos revenus — {sv['label']}")

        if not sv["societe_is"]:
            # TNS sans IS
            regime      = sv["regime_fiscal"]
            is_micro    = "micro" in regime
            is_reel_bnc = regime in ("bnc_reel", "sel_bnc")

            st.info(f"✅ En tant que **{sv['label']}**, votre revenu imposable est votre **bénéfice / CA directement**. "
                    "Pas de rémunération séparée, pas d'IS société.")

            if is_micro:
                recettes = st.number_input(
                    f"Recettes / CA annuel brut 2024 (€)",
                    0, 5_000_000, int(d.get("recettes_dir", 50_000)), 500, key="rec_dir_w",
                    help="Montant brut AVANT abattement — c'est le chiffre que vous déclarez.")
                save("recettes_dir", recettes); save("charges_dir", 0); save("amort_dir", 0)

                if recettes > 0:
                    rb    = dm.calculer_revenu_tns_sans_is(s_key, recettes)
                    seuil = rb.get("seuil", 77_700)
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: st.markdown(kpi_html("Recettes brutes", f"{fr(recettes)} €"), unsafe_allow_html=True)
                    with c2: st.markdown(kpi_html(f"Abattement {rb['abattement_pct']} %", f"-{fr(rb['abattement_montant'])} €", "#4ade80"), unsafe_allow_html=True)
                    with c3: st.markdown(kpi_html("Bénéfice imposable", f"{fr(rb['benefice_imposable'])} €", "#60a5fa"), unsafe_allow_html=True)
                    with c4: st.markdown(kpi_html("Cotisations sociales", f"{fr(rb['cotisations'])} €", "#f87171"), unsafe_allow_html=True)

                    if not rb.get("eligible_micro", True):
                        st.warning(f"⚠️ Votre CA ({fr(recettes)} €) **dépasse le seuil micro** ({fr(seuil)} €). Vous devez basculer au régime réel.")
                    else:
                        st.success(f"✅ Sous le seuil micro ({fr(seuil)} €) — régime applicable. Net avant IR estimé : **{fr(rb['net_avant_ir'])} €**")

                    ir_est = round(rb["benefice_imposable"] * tmi / 100)
                    st.markdown(
                        f'''<div class="card" style="margin-top:.6rem">
                        <b style="color:#93c5fd">Récapitulatif fiscal — {sv["type"]}</b><br>
                        <span style="color:#94a3b8;font-size:.83rem">
                        Recettes : <b>{fr(recettes)} €</b> &nbsp;→&nbsp;
                        Abattement : <b style="color:#4ade80">−{fr(rb["abattement_montant"])} €</b> &nbsp;→&nbsp;
                        Imposable : <b style="color:#60a5fa">{fr(rb["benefice_imposable"])} €</b><br>
                        IR estimé TMI {tmi} % : <b style="color:#f87171">{fr(ir_est)} €</b> &nbsp;|&nbsp;
                        Cotisations : <b style="color:#f87171">{fr(rb["cotisations"])} €</b> &nbsp;|&nbsp;
                        Net estimé : <b style="color:#4ade80">{fr(rb["net_avant_ir"] - ir_est)} €</b><br>
                        <span style="color:#475569;font-size:.75rem">📋 Case à remplir : {sv["cases_2042"]}</span>
                        </span></div>''',
                        unsafe_allow_html=True)
                    save("benefice_dir", rb["benefice_imposable"])
                    save("cotisations_dir", rb["cotisations"])

            elif is_reel_bnc:
                c1, c2 = st.columns(2)
                with c1:
                    recettes = st.number_input("Recettes encaissées 2024 (€)",
                        0, 5_000_000, int(d.get("recettes_dir", 80_000)), 1_000, key="rec_dir_w")
                with c2:
                    charges = st.number_input("Charges professionnelles déductibles (€)",
                        0, 5_000_000, int(d.get("charges_dir", 30_000)), 1_000, key="ch_dir_w",
                        help="Loyer cabinet, cotisations Urssaf, frais déplacement, fournitures, etc.")
                save("recettes_dir", recettes); save("charges_dir", charges); save("amort_dir", 0)

                if recettes > 0:
                    rb    = dm.calculer_revenu_tns_sans_is(s_key, recettes, charges)
                    c1b, c2b, c3b = st.columns(3)
                    col_b = "#4ade80" if rb["benefice_imposable"] >= 0 else "#f87171"
                    with c1b: st.markdown(kpi_html("Recettes", f"{fr(recettes)} €"), unsafe_allow_html=True)
                    with c2b: st.markdown(kpi_html("Bénéfice imposable", f"{fr(rb['benefice_imposable'])} €", col_b), unsafe_allow_html=True)
                    with c3b: st.markdown(kpi_html("Cotisations TNS", f"{fr(rb['cotisations'])} €", "#f87171"), unsafe_allow_html=True)
                    if rb.get("deficit", 0) > 0:
                        st.info(f"📉 Déficit : **{fr(rb['deficit'])} €** — reportable sur revenus globaux.")
                    ir_est = round(rb["benefice_imposable"] * tmi / 100)
                    st.markdown(
                        f'''<div class="card">
                        <b style="color:#93c5fd">BNC réel — Déclaration 2035</b><br>
                        <span style="color:#94a3b8;font-size:.83rem">
                        Recettes {fr(recettes)} € − Charges {fr(charges)} € =
                        Bénéfice <b style="color:#60a5fa">{fr(rb["benefice_imposable"])} €</b><br>
                        IR estimé TMI {tmi} % : <b style="color:#f87171">{fr(ir_est)} €</b> &nbsp;|&nbsp;
                        Cotisations TNS : <b style="color:#f87171">{fr(rb["cotisations"])} €</b><br>
                        Net estimé : <b style="color:#4ade80">{fr(max(0, rb["net_avant_ir"] - ir_est))} €</b><br>
                        <span style="color:#475569;font-size:.75rem">📋 {sv["cases_2042"]}</span>
                        </span></div>''',
                        unsafe_allow_html=True)
                    save("benefice_dir", rb["benefice_imposable"])
                    save("cotisations_dir", rb["cotisations"])
                    if s_key == "sel_bnc" and recettes <= 77_700:
                        st.info("💡 **Astuce SEL** : Recettes sous 77 700 €. Option micro-BNC possible (abatt. 34 %). Comparez avec votre expert-comptable.")

            else:
                # BIC réel (EI, EURL IR)
                c1, c2, c3 = st.columns(3)
                with c1: recettes = st.number_input("CA annuel 2024 (€)", 0, 5_000_000, int(d.get("recettes_dir", 100_000)), 1_000, key="rec_dir_w")
                with c2: charges  = st.number_input("Charges déductibles (€)", 0, 5_000_000, int(d.get("charges_dir", 60_000)), 1_000, key="ch_dir_w")
                with c3: amort    = st.number_input("Amortissements (€)", 0, 500_000, int(d.get("amort_dir", 0)), 1_000, key="am_dir_w")
                save("recettes_dir", recettes); save("charges_dir", charges); save("amort_dir", amort)

                if recettes > 0:
                    rb = dm.calculer_revenu_tns_sans_is(s_key, recettes, charges, amort)
                    c1b, c2b, c3b, c4b = st.columns(4)
                    col_b = "#4ade80" if rb["benefice_imposable"] >= 0 else "#f87171"
                    with c1b: st.markdown(kpi_html("CA", f"{fr(recettes)} €"), unsafe_allow_html=True)
                    with c2b: st.markdown(kpi_html("Charges totales", f"-{fr(charges + amort)} €", "#94a3b8"), unsafe_allow_html=True)
                    with c3b: st.markdown(kpi_html("Bénéfice imposable", f"{fr(rb['benefice_imposable'])} €", col_b), unsafe_allow_html=True)
                    with c4b: st.markdown(kpi_html("Cotisations TNS", f"{fr(rb['cotisations'])} €", "#f87171"), unsafe_allow_html=True)
                    save("benefice_dir", rb["benefice_imposable"])
                    save("cotisations_dir", rb["cotisations"])

        else:
            # Dirigeant société IS : rémunération
            st.info(f"✅ En tant que **{sv['label']}**, votre revenu personnel = votre **rémunération**. "
                    "Le bénéfice société sera traité à l'étape suivante (IS + dividendes).")
            remts = st.number_input("Rémunération annuelle brute 2024 (€)",
                0, 1_000_000, int(d.get("rem_ts", 60_000)), 1_000, key="remts_w",
                help="Montant total perçu AVANT cotisations sociales et AVANT IR.")
            fr_on = st.checkbox("Opter pour les frais réels (à la place de l'abattement 10 %)",
                value=d.get("fr_on_dir", False), key="fr_on_dir_w")
            montant_fr = 0
            if fr_on:
                montant_fr = st.number_input("Montant des frais réels justifiés (€)",
                    0, 100_000, int(d.get("montant_fr_dir", 0)), 500, key="montant_fr_dir_w")
            save("rem_ts", remts); save("fr_on_dir", fr_on); save("montant_fr_dir", montant_fr)

            if remts > 0:
                rr = dm.calculer_remuneration_dirigeant_is(s_key, remts, fr_on, montant_fr)
                c1, c2, c3 = st.columns(3)
                with c1: st.markdown(kpi_html("Rémunération brute", f"{fr(remts)} €"), unsafe_allow_html=True)
                with c2: st.markdown(kpi_html(f"Abattement ({rr['type_abattement']})", f"-{fr(rr['abattement'])} €", "#4ade80"), unsafe_allow_html=True)
                with c3: st.markdown(kpi_html("Imposable IR", f"{fr(rr['imposable'])} €", "#60a5fa"), unsafe_allow_html=True)

                ir_est  = round(rr["imposable"] * tmi / 100)
                det_html = "".join(
                    f'<div style="display:flex;justify-content:space-between;padding:.15rem 0">'
                    f'<span style="color:#94a3b8;font-size:.82rem">{k}</span>'
                    f'<b style="font-size:.82rem">{v}</b></div>'
                    for k, v in rr["detail_cotisations"].items())
                ca, cb = st.columns(2)
                with ca:
                    st.markdown(
                        f'''<div class="card">
                        <b style="color:#93c5fd">{sv["fiscal"]}</b><br>
                        <span style="color:#94a3b8;font-size:.82rem">
                        Brute : {fr(remts)} €<br>
                        Abattement ({rr["type_abattement"]}) : <b style="color:#4ade80">−{fr(rr["abattement"])} €</b><br>
                        <b>Imposable IR : {fr(rr["imposable"])} €</b><br>
                        IR estimé TMI {tmi} % : <b style="color:#f87171">{fr(ir_est)} €</b><br>
                        <span style="color:#475569;font-size:.74rem">📋 {sv["cases_2042"]}</span>
                        </span></div>''',
                        unsafe_allow_html=True)
                with cb:
                    st.markdown(
                        f'''<div class="card">
                        <b style="color:#93c5fd">{rr["label_cotisations"]}</b><br>
                        {det_html}
                        <div style="border-top:1px solid #334155;margin-top:.4rem;padding-top:.4rem;
                        display:flex;justify-content:space-between">
                        <b>Total cotisations</b><b style="color:#f87171">{fr(rr["cotisations"])} €</b></div>
                        <div style="display:flex;justify-content:space-between">
                        <span style="color:#94a3b8;font-size:.82rem">Net avant IR</span>
                        <b style="color:#4ade80">{fr(rr["net_avant_ir"])} €</b></div>
                        </div>''',
                        unsafe_allow_html=True)
                save("benefice_dir", rr["imposable"])
                save("cotisations_dir", rr["cotisations"])
        nav_buttons()

    # ── ÉTAPE 3 : SOCIÉTÉ & IS — DIVIDENDES (auto-skip si pas IS) ────────────
    elif SS.step == 3:
        sv  = STATUTS[s_key]
        tmi = d.get("tmi_dir", 30)
        if not sv["societe_is"]:
            next_step()
            st.stop()

        st.markdown("## 🏦 Société & IS — Dividendes")
        col_is, col_div = st.columns(2)

        with col_is:
            st.markdown("### Impôt sur les Sociétés")
            res_fisc = st.number_input(
                "Résultat fiscal société AVANT rémunération (€)",
                -200_000, 5_000_000, int(d.get("res_fisc", 120_000)), 1_000,
                key="resfisc_w",
                help="CA − toutes charges professionnelles, AVANT déduction de votre rémunération de gérant.")
            save("res_fisc", res_fisc)
            if res_fisc > 0:
                remts        = d.get("rem_ts", 0)
                res_apres    = max(0, res_fisc - remts)
                isd          = dm.calculer_is(res_apres)
                st.markdown(
                    f'''<div class="card">
                    <b style="color:#93c5fd">Calcul IS 2024</b><br>
                    <span style="color:#94a3b8;font-size:.83rem">
                    Résultat avant rém. : {fr(res_fisc)} €<br>
                    − Rémunération gérant : <b style="color:#4ade80">−{fr(remts)} €</b><br>
                    = Base IS : <b>{fr(res_apres)} €</b><br><br>
                    Base taux 15 % : {fr(isd["base_reduit"])} € → IS {fr(isd["is_reduit"])} €<br>
                    Base taux 25 % : {fr(isd["base_normal"])} € → IS {fr(isd["is_normal"])} €<br>
                    <b style="color:#f87171">IS total : {fr(isd["is_total"])} €</b>
                    &nbsp;(taux effectif {isd["taux_effectif"]:.1f} %)<br>
                    <b style="color:#4ade80">Bénéfice net : {fr(isd["benefice_net"])} €</b>
                    </span></div>''',
                    unsafe_allow_html=True)
                save("is_total", isd["is_total"])
                save("benefice_net_is", isd["benefice_net"])

        with col_div:
            st.markdown("### Dividendes")
            div_b = st.number_input(
                "Dividendes bruts à distribuer (€)",
                0, 2_000_000, int(d.get("div_b", 0)), 1_000, key="divb_w",
                help="Montant distribué depuis le bénéfice net après IS.")
            save("div_b", div_b)
            if div_b > 0:
                dd    = dm.calculer_dividendes(div_b, tmi)
                meill = dd["meilleur"]
                for lbl, opt, color in [
                    ("PFU (Flat Tax 30 %)", dd["pfu"],
                     "#60a5fa" if meill == "PFU" else "#475569"),
                    (f"Barème IR ({tmi} %) + abatt. 40 %", dd["bareme"],
                     "#4ade80" if meill == "Barème" else "#475569"),
                ]:
                    tag  = "⭐ Recommandé — " if (meill == "PFU" and "PFU" in lbl) or (meill == "Barème" and "arème" in lbl) else ""
                    st.markdown(
                        f'''<div class="card" style="border-color:{color}">
                        <b style="color:{color}">{tag}{lbl}</b><br>
                        <span style="color:#94a3b8;font-size:.83rem">
                        IR : {fr(opt["ir"])} € &nbsp;|&nbsp; PS : {fr(opt["ps"])} €<br>
                        <b>Total prélèvements : {fr(opt["total_imposition"])} €</b><br>
                        <b style="color:#4ade80">Net perçu : {fr(opt["net_percu"])} €</b>
                        </span></div>''',
                        unsafe_allow_html=True)
                if dd["economie"] > 0:
                    st.success(f"💡 Économie en choisissant le meilleur régime : **{fr(dd['economie'])} €**")

        remts    = d.get("rem_ts", 0)
        res_fisc = d.get("res_fisc", 0)
        if remts > 0 and res_fisc > 0:
            st.markdown("---")
            st.markdown("### ⚖️ Stratégie : Rémunération vs Dividendes")
            sim = dm.simuler_remuneration_vs_dividendes(res_fisc, remts, tmi, s_key)
            ca2, cb2 = st.columns(2)
            for col_s, sk, strat_data in [(ca2, "A", sim["strategie_a"]), (cb2, "B", sim["strategie_b"])]:
                best  = sim["meilleure"] == sk
                bc_s  = "#3b82f6" if best else "#334155"
                tag_s = "⭐ Recommandé" if best else ""
                with col_s:
                    lines_html = f"<b style='color:#93c5fd'>{strat_data['label']}</b> <span style='color:#60a5fa;font-size:.78rem'>{tag_s}</span><br>"
                    if "cotisations" in strat_data:
                        lines_html += f"<span style='color:#94a3b8;font-size:.82rem'>Cotisations : {fr(strat_data['cotisations'])} €</span><br>"
                    if "is_societe" in strat_data:
                        lines_html += f"<span style='color:#94a3b8;font-size:.82rem'>IS société : {fr(strat_data['is_societe'])} €</span><br>"
                    if "ir_personnel" in strat_data:
                        lines_html += f"<span style='color:#94a3b8;font-size:.82rem'>IR personnel : {fr(strat_data['ir_personnel'])} €</span><br>"
                    if "pfu" in strat_data:
                        lines_html += f"<span style='color:#94a3b8;font-size:.82rem'>PFU dividendes : {fr(strat_data['pfu'])} €</span><br>"
                    st.markdown(
                        f'''<div class="card" style="border-color:{bc_s}">
                        {lines_html}
                        <div style="border-top:1px solid #334155;margin-top:.4rem;padding-top:.3rem">
                        <span style="color:#94a3b8;font-size:.82rem">Coût total</span><br>
                        <b style="color:#f87171;font-size:1.1rem">{fr(strat_data["cout_total"])} €</b><br>
                        <span style="color:#94a3b8;font-size:.82rem">Net perçu</span><br>
                        <b style="color:#4ade80;font-size:1.1rem">{fr(strat_data["net_percu"])} €</b>
                        </div></div>''',
                        unsafe_allow_html=True)
            if sim["economie"] > 0:
                st.success(f"💰 Économie en choisissant la meilleure stratégie : **{fr(sim['economie'])} €**")
        nav_buttons()

    # ── ÉTAPE 4 : IMMOBILIER ──────────────────────────────────────────────────
    elif SS.step == 4:
        st.markdown("## 🏠 Revenus immobiliers")
        tmi   = d.get("tmi_dir", 30)
        itype = st.selectbox("Type de bien / régime",
            ["Micro-foncier", "Foncier réel (2044)", "LMNP Micro-BIC",
             "LMNP Réel", "LMP", "SCI à l'IR", "SCI à l'IS"],
            index=int(d.get("itype_idx", 0)), key="itype_w")
        rfb   = st.number_input("Revenus / Recettes / Résultat (€)",
            -200_000, 5_000_000, int(d.get("rfb", 12_000)), 500, key="rfb_w")
        inte = chf = trav = tff = fgf = chlmnp = amlmnp = chlmp = amlmp = autrev = sciqp = lmnpcl = 0

        if "Foncier réel" in itype:
            c1, c2 = st.columns(2)
            with c1:
                inte = st.number_input("Intérêts emprunt (€)", 0, 200_000, int(d.get("inte", 0)),    200, key="inte_w")
                chf  = st.number_input("Charges (€)",          0, 100_000, int(d.get("chf",  2_000)), 100, key="chf_w")
                trav = st.number_input("Travaux (€)",           0, 500_000, int(d.get("trav", 0)),    500, key="trav_w")
            with c2:
                tff  = st.number_input("Taxe foncière (€)", 0, 20_000, int(d.get("tff", 800)), 100, key="tff_w")
                fgf  = st.number_input("Frais gestion (€)", 0, 20_000, int(d.get("fgf", 400)), 100, key="fgf_w")
        elif "LMNP Réel" in itype:
            chlmnp = st.number_input("Charges (€)",         0, 200_000, int(d.get("chlmnp", 4_000)), 500, key="chlmnp_w")
            amlmnp = st.number_input("Amortissements (€)",  0, 200_000, int(d.get("amlmnp", 3_000)), 500, key="amlmnp_w")
        elif "LMNP Micro" in itype:
            lmnpcl = st.checkbox("Bien classé (meublé de tourisme classé)", d.get("lmnpcl", False), key="lmnpcl_w")
        elif "LMP" in itype:
            chlmp  = st.number_input("Charges (€)",         0, 500_000, int(d.get("chlmp",  6_000)), 500, key="chlmp_w")
            amlmp  = st.number_input("Amortissements (€)",  0, 300_000, int(d.get("amlmp",  5_000)), 500, key="amlmp_w")
            autrev = st.number_input("Autres revenus pro foyer (€)", 0, 500_000, int(d.get("autrev", 40_000)), 1_000, key="autrev_w")
        elif "SCI" in itype:
            sciqp  = st.slider("Quote-part de détention (%)", 1, 100, int(d.get("sciqp", 100)), 1, key="sciqp_w") / 100

        if   "Micro-foncier" in itype: rim = dm.calculer_foncier_micro(rfb)
        elif "Foncier réel"   in itype: rim = dm.calculer_foncier_reel(rfb, inte, chf, trav, tff, fgf)
        elif "LMNP Micro"     in itype: rim = dm.calculer_lmnp(rfb, lmnpcl, "micro")
        elif "LMNP Réel"      in itype: rim = dm.calculer_lmnp(rfb, False, "reel", chlmnp, amlmnp)
        elif "LMP"            in itype: rim = dm.calculer_lmp(rfb, chlmp, amlmp, autrev)
        elif "SCI à l'IR"    in itype: rim = dm.calculer_sci_ir(rfb)
        else:                           rim = dm.calculer_sci_is(rfb, sciqp)

        imposable = rim.get("imposable", rim.get("benefice_imposable", 0))
        col_r     = "#4ade80" if imposable >= 0 else "#f87171"
        ir_immo   = round(abs(imposable) * tmi / 100)
        st.markdown(
            f'''<div class="card" style="margin-top:.6rem">
            <b style="color:#93c5fd">Résultat — {itype}</b><br>
            <span style="color:#94a3b8;font-size:.83rem">
            Imposable / Résultat : <b style="color:{col_r}">{fr(imposable)} €</b><br>
            IR estimé TMI {tmi} % : <b style="color:#f87171">{fr(ir_immo)} €</b><br>
            PS 17,2 % : <b>{fr(rim.get("ps", 0))} €</b>
            {"<br>💡 " + str(rim.get("note","")) if rim.get("note") else ""}
            </span></div>''',
            unsafe_allow_html=True)
        itype_list = ["Micro-foncier", "Foncier réel (2044)", "LMNP Micro-BIC",
                      "LMNP Réel", "LMP", "SCI à l'IR", "SCI à l'IS"]
        save("itype_idx", itype_list.index(itype))
        save("rfb", rfb)
        save("sciqp", sciqp)
        nav_buttons()

    # ── ÉTAPE 5 : OPTIMISATION ────────────────────────────────────────────────
    elif SS.step == 5:
        sv  = STATUTS[s_key]
        tmi = d.get("tmi_dir", 30)
        st.markdown("## 🎯 Recommandations d'optimisation fiscale")
        st.caption("Basées sur votre statut, vos revenus et votre TMI.")

        ben_opt = d.get("benefice_dir", d.get("res_fisc", 0))
        rem_opt = d.get("rem_ts", 0)
        rec_opt = d.get("recettes_dir", 0)

        opts = dm.optimisation_fiscale({
            "statut_key":   s_key,
            "benefice":     ben_opt,
            "remuneration": rem_opt,
            "recettes":     rec_opt,
            "tmi":          tmi,
        })

        impact_colors = {
            "Très élevé": "#f59e0b",
            "Très élevé (restructuration)": "#f59e0b",
            "Très élevé (long terme)": "#f59e0b",
            "Élevé": "#3b82f6",
            "À évaluer": "#8b5cf6",
            "Moyen": "#6b7280",
        }

        if not opts:
            st.info("✅ Aucune recommandation spécifique. Consultez un expert-comptable pour un audit personnalisé.")
        else:
            for i, opt in enumerate(opts, 1):
                ic        = impact_colors.get(opt["impact"], "#6b7280")
                gain_str  = f" &nbsp;— Gain estimé : <b>{fr(opt['gain_estime'])} €</b>" if opt.get("gain_estime", 0) > 0 else ""
                pour_html = "".join(f"<div style='color:#4ade80;font-size:.81rem'>✓ {p}</div>" for p in opt["pour"])
                ctr_html  = "".join(f"<div style='color:#f87171;font-size:.81rem'>✗ {c}</div>" for c in opt["contre"])
                st.markdown(
                    f'''<div style="background:#1e293b;border-left:4px solid {ic};
                      border-radius:0 10px 10px 0;padding:1rem;margin:.5rem 0">
                    <div style="color:{ic};font-weight:700">{opt.get("icone","")} {i}. {opt["titre"]}
                    <span style="background:{ic}22;color:{ic};font-size:.72rem;padding:.15rem .5rem;
                    border-radius:12px;margin-left:.4rem">{opt["impact"]}</span>{gain_str}</div>
                    <div style="color:#94a3b8;font-size:.84rem;margin:.4rem 0">{opt["detail"]}</div>
                    <div style="color:#60a5fa;font-size:.82rem">→ {opt["action"]}</div>
                    <div style="display:flex;gap:2rem;margin-top:.5rem">{pour_html}{ctr_html}</div>
                    </div>''',
                    unsafe_allow_html=True)

        save("ben_opt", ben_opt)
        save("rem_opt", rem_opt)
        nav_buttons(label_next="Générer le rapport PDF →")

    # ── ÉTAPE 6 : RAPPORT PDF ─────────────────────────────────────────────────
    elif SS.step == 6:
        sv  = STATUTS[s_key]
        tmi = d.get("tmi_dir", 30)
        st.markdown("## 📄 Rapport PDF — Revenus de dirigeant")
        st.success("✅ Simulation terminée ! Téléchargez votre rapport complet.")

        if st.button("Générer le rapport dirigeant PDF", type="primary"):
            with st.spinner("Génération..."):
                try:
                    from rapport_pdf import GenererRapportDirigeantPDF
                    profil_dir = {
                        "statut":      s_key,
                        "label":       sv["label"],
                        "remuneration": d.get("rem_ts", 0),
                        "tmi":         tmi,
                        "benefice":    d.get("res_fisc", d.get("benefice_dir", 0)),
                        "dividendes":  d.get("div_b", 0),
                        "is_total":    d.get("is_total", 0),
                        "cases_2042":  sv["cases_2042"],
                    }
                    gen_d     = GenererRapportDirigeantPDF()
                    pdf_bytes = gen_d.generer(profil_dir, dm)
                    b64  = base64.b64encode(pdf_bytes).decode()
                    href = (f'<a href="data:application/pdf;base64,{b64}" '
                            f'download="rapport_dirigeant_2026.pdf" '
                            f'style="display:inline-block;background:#1d4ed8;color:white;'
                            f'padding:.8rem 2rem;border-radius:8px;text-decoration:none;font-weight:700">'
                            f'⬇️ Télécharger le rapport dirigeant PDF</a>')
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("Rapport généré !")
                except Exception as e:
                    st.error(f"Erreur : {e}")

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(kpi_html("Bénéfice imposable", f"{fr(d.get('benefice_dir', 0))} €", "#60a5fa"), unsafe_allow_html=True)
        with c2: st.markdown(kpi_html("Cotisations sociales", f"{fr(d.get('cotisations_dir', 0))} €", "#f87171"), unsafe_allow_html=True)
        with c3:
            ir_fin = round(d.get("benefice_dir", 0) * tmi / 100)
            st.markdown(kpi_html("IR estimé", f"{fr(ir_fin)} €", "#fbbf24"), unsafe_allow_html=True)

        st.markdown('<div class="src">Simulation à titre informatif — Brochure DGFiP 2025. Consultez impots.gouv.fr ou un expert-comptable.</div>', unsafe_allow_html=True)
        st.markdown("---")
        if st.button("Recommencer une simulation"):
            for k in list(SS.keys()): del SS[k]
            st.rerun()
        nav_buttons(can_next=False)


# ═══════════════════════════════════════════════════════════════════
else:
    st.error("Navigation incorrecte.")
    if st.button("Retour a l'accueil"):
        SS.step = 0; SS.mode = None; st.rerun()
