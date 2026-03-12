"""
Générateur de rapport PDF — Simulateur IR 2026
Inclut le guide des cases à renseigner sur la déclaration 2042
"""

from fpdf import FPDF
from datetime import date


def fr(val, dec=0):
    """Formatage nombre français : séparateur milliers = espace insécable"""
    if val is None: return "—"
    if dec == 0:
        s = f"{abs(val):,.0f}".replace(",", "\u202f")
    else:
        s = f"{abs(val):,.{dec}f}"
        parts = s.split(".")
        s = parts[0].replace(",", "\u202f") + "," + parts[1]
    return ("−" if val < 0 else "") + s


# ─── Mapping cases fiscales ────────────────────────────────────────────────
CASES = {
    # Revenus
    '1AJ': 'Traitements, salaires — Déclarant 1',
    '1BJ': 'Traitements, salaires — Déclarant 2',
    '1AS': 'Pensions, retraites — Déclarant 1',
    '1BS': 'Pensions, retraites — Déclarant 2',
    '1GH': 'Heures supplémentaires exonérées — Déclarant 1',
    '1HH': 'Heures supplémentaires exonérées — Déclarant 2',
    '1AK': 'Frais réels — Déclarant 1',
    '1BK': 'Frais réels — Déclarant 2',
    # Charges déductibles
    '6NS': 'Versements PER individuel (cotisations)',
    '6NT': 'Versements PER individuel (primes)',
    '6NU': 'Versements PER collectif',
    '6GI': 'Pension alimentaire versée à un enfant majeur',
    # Quotient familial
    'T'  : 'Case T — Parent isolé (chef de famille monoparentale)',
    'D'  : 'Rattachement enfant majeur (case D)',
    # Réductions dons
    '7UD': 'Dons 75 % — Aide aux personnes en difficulté',
    '7UM': 'Dons 75 % — Urgence Mayotte (cyclone Chido)',
    '7VC': 'Dons 66 % — Associations intérêt général',
    # Crédits garde
    '7GA': 'Frais garde enfant (1er enfant < 6 ans)',
    '7GB': 'Frais garde enfant (2e enfant)',
    '7GC': 'Frais garde enfant (3e enfant)',
    # Emploi domicile
    '7DB': 'Emploi à domicile — dépenses',
    '7DQ': 'Emploi à domicile — 1ère année',
    # Cotisations syndicales
    '7AC': 'Cotisations syndicales',
}


class GenererRapportPDF(FPDF):

    BLEU_FR  = (0, 49, 137)
    ROUGE_FR = (237, 41, 57)
    GRIS     = (100, 100, 100)
    GRIS_CLR = (245, 247, 250)
    NOIR     = (30, 30, 30)

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(18, 18, 18)

    def header(self):
        self.set_fill_color(*self.BLEU_FR)
        self.rect(0, 0, 210, 14, 'F')
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(255, 255, 255)
        self.set_xy(0, 3)
        self.cell(0, 8, '  Simulateur IR 2026 — Revenus 2025 — Barème DGFiP 2025', ln=False)
        self.set_xy(-80, 3)
        self.cell(70, 8, f'Édité le {date.today().strftime("%d/%m/%Y")}', align='R')
        self.set_text_color(*self.NOIR)
        self.ln(10)

    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(*self.GRIS)
        self.cell(0, 5,
            'Document à titre informatif uniquement. Consultez impots.gouv.fr ou un expert-comptable. '
            f'Page {self.page_no()} / {{nb}}',
            align='C')

    # ─── Helpers ───────────────────────────────────────────────────────
    def titre_section(self, txt, couleur=None):
        if couleur is None:
            couleur = self.BLEU_FR
        self.ln(4)
        self.set_fill_color(*couleur)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 7, f'  {txt}', fill=True, ln=True)
        self.set_text_color(*self.NOIR)
        self.ln(2)

    def ligne_kv(self, label, valeur, bold_val=False, indent=0):
        self.set_font('Helvetica', '', 9)
        x0 = self.get_x() + indent
        self.set_x(x0)
        self.set_text_color(*self.GRIS)
        self.cell(100 - indent, 6, label)
        self.set_text_color(*self.NOIR)
        self.set_font('Helvetica', 'B' if bold_val else '', 9)
        self.cell(0, 6, valeur, ln=True)
        self.set_font('Helvetica', '', 9)

    def ligne_separatrice(self):
        self.set_draw_color(220, 220, 220)
        self.line(self.l_margin, self.get_y(), 210 - self.r_margin, self.get_y())
        self.ln(2)

    def badge_case(self, case_code, description, valeur):
        """Affiche une ligne avec le code de case en badge bleu."""
        self.set_fill_color(219, 234, 254)
        self.set_text_color(30, 64, 175)
        self.set_font('Courier', 'B', 8)
        self.cell(14, 6, f' {case_code}', fill=True, border=0)
        self.set_text_color(*self.GRIS)
        self.set_font('Helvetica', '', 8)
        self.cell(120, 6, f'  {description}')
        self.set_text_color(*self.BLEU_FR)
        self.set_font('Helvetica', 'B', 9)
        self.cell(0, 6, valeur, ln=True)
        self.set_text_color(*self.NOIR)

    def bloc_encadre(self, titre, couleur_fond=(240, 249, 255)):
        y = self.get_y()
        self.set_fill_color(*couleur_fond)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*self.BLEU_FR)
        self.cell(0, 7, f'  {titre}', fill=True, border='LTR', ln=True)
        self.set_text_color(*self.NOIR)

    def tableau_tranches(self, tranches):
        cols = [100, 30, 30, 25]
        headers = ['Tranche', 'Taux', 'Base', 'Impôt']
        self.set_fill_color(*self.BLEU_FR)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 8)
        for h, w in zip(headers, cols):
            self.cell(w, 6, h, fill=True, border=0)
        self.ln()
        self.set_text_color(*self.NOIR)
        alt = False
        for t in tranches:
            if t['base'] == 0: continue
            self.set_fill_color(245, 247, 250) if alt else self.set_fill_color(255, 255, 255)
            self.set_font('Helvetica', '', 8)
            self.cell(cols[0], 6, t['label'], fill=True)
            self.cell(cols[1], 6, f"{t['taux']} %", fill=True, align='C')
            self.cell(cols[2], 6, f"{fr(t['base'])} €", fill=True, align='R')
            self.cell(cols[3], 6, f"{fr(t['impot_tranche'])} €", fill=True, align='R')
            self.ln()
            alt = not alt
        self.ln(2)

    # ─── Page de titre ──────────────────────────────────────────────────
    def page_titre(self, profil, res):
        sit_labels = {
            "Célibataire / Divorcé(e)": "Célibataire / Divorcé(e)",
            "Marié(e) / Pacsé(e)": "Marié(e) / Pacsé(e)",
            "Veuf(ve)": "Veuf(ve)",
        }
        sit = sit_labels.get(profil['situation'], profil['situation'])

        # Titre principal
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(*self.BLEU_FR)
        self.ln(4)
        self.cell(0, 10, 'BILAN FISCAL 2026', ln=True, align='C')
        self.set_font('Helvetica', '', 11)
        self.set_text_color(*self.GRIS)
        self.cell(0, 7, 'Déclaration des revenus 2025 — Barème DGFiP officiel', ln=True, align='C')
        self.ln(6)

        # Bandeau récapitulatif
        self.set_fill_color(*self.GRIS_CLR)
        self.set_text_color(*self.NOIR)
        self.set_font('Helvetica', '', 9)
        self.cell(0, 6,
            f'  Situation : {sit}  |  Enfants : {profil.get("nb_enfants",0)}  '
            f'|  Parts : {res["nb_parts"]:.1f}  |  TMI : {res["taux_marginal"]} %',
            fill=True, ln=True)
        self.ln(6)

        # 4 métriques en boîtes
        metrics = [
            ('Revenu Net Imposable',   f"{fr(res['revenu_imposable'])} €",   self.BLEU_FR),
            ('Impôt brut',             f"{fr(res['impot_brut'])} €",          (180, 40, 40)),
            ('Décote appliquée',       f"−{fr(res['decote'])} €",             (21, 128, 61)),
            ('IMPÔT NET À PAYER',      f"{fr(res['impot_net'])} €",           self.BLEU_FR),
        ]
        w = (210 - 36) / 4
        for label, val, color in metrics:
            x0 = self.get_x()
            y0 = self.get_y()
            self.set_fill_color(245, 247, 250)
            self.rect(x0, y0, w - 1, 22, 'F')
            self.set_xy(x0, y0 + 2)
            self.set_font('Helvetica', 'B', 12)
            self.set_text_color(*color)
            self.cell(w - 1, 7, val, align='C')
            self.set_xy(x0, y0 + 10)
            self.set_font('Helvetica', '', 7)
            self.set_text_color(*self.GRIS)
            self.cell(w - 1, 5, label, align='C')
            self.set_xy(x0 + w, y0)
        self.ln(26)

        # Taux
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*self.GRIS)
        self.cell(0, 6,
            f'Taux moyen effectif : {res["taux_moyen"]:.2f} %   |   '
            f'Taux marginal (TMI) : {res["taux_marginal"]} %   |   '
            f'Quotient familial : {fr(res["quotient_familial"])} €',
            ln=True, align='C')

    # ─── Détail fiscal ──────────────────────────────────────────────────
    def section_detail(self, profil, res):
        self.titre_section('DÉTAIL DU CALCUL FISCAL')

        # Revenus
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*self.BLEU_FR)
        self.cell(0, 6, 'Revenus et abattements', ln=True)
        self.set_text_color(*self.NOIR)

        sal1 = profil.get('revenu_salaire_declarant', 0)
        pen1 = profil.get('revenu_pension_declarant', 0)
        sal2 = profil.get('revenu_salaire_conjoint', 0)
        pen2 = profil.get('revenu_pension_conjoint', 0)
        hs1  = profil.get('heures_sup_declarant', 0)
        hs2  = profil.get('heures_sup_conjoint', 0)

        self.ligne_kv('Salaires bruts D1',           f"{fr(sal1)} €")
        if hs1 > 0:
            self.ligne_kv('  dont Heures sup exonérées D1', f"−{fr(min(hs1,7500))} €", indent=4)
        self.ligne_kv('Abattement salaires D1',       f"−{fr(res['abattement_salaires_1'])} €")
        self.ligne_kv('Pensions D1',                  f"{fr(pen1)} €")
        self.ligne_kv('Abattement pensions D1',       f"−{fr(res['abattement_pensions_1'])} €")
        if profil.get('situation') == "Marié(e) / Pacsé(e)":
            self.ligne_kv('Salaires bruts D2',        f"{fr(sal2)} €")
            if hs2 > 0:
                self.ligne_kv('  dont Heures sup D2', f"−{fr(min(hs2,7500))} €", indent=4)
            self.ligne_kv('Abattement D2',            f"−{fr(res['abattement_salaires_2'])} €")
            self.ligne_kv('Pensions D2',              f"{fr(pen2)} €")
            self.ligne_kv('Abattement pensions D2',   f"−{fr(res['abattement_pensions_2'])} €")
        self.ligne_kv('Déduction PER',                f"−{fr(res['deduction_per'])} €")
        if res.get('pension_versee_ded', 0) > 0:
            self.ligne_kv('Pension alimentaire versée', f"−{fr(res['pension_versee_ded'])} €")
        self.ligne_separatrice()
        self.ligne_kv('= Revenu Net Imposable', f"{fr(res['revenu_imposable'])} €", bold_val=True)
        self.ln(3)

        # Barème par tranches
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*self.BLEU_FR)
        self.cell(0, 6, f'Barème progressif ({res["nb_parts"]:.1f} parts)', ln=True)
        self.set_text_color(*self.NOIR)
        self.tableau_tranches(res['detail_tranches'])

        # Réductions et crédits
        self.ligne_kv('Impôt brut après QF',          f"{fr(res['impot_brut'])} €")
        self.ligne_kv('Décote (cst − 45,25 % × impôt)', f"−{fr(res['decote'])} €")
        if res['reduction_dons_75'] > 0:
            self.ligne_kv('Réduction dons 75 %',      f"−{fr(res['reduction_dons_75'])} €")
        if res['reduction_dons_66'] > 0:
            self.ligne_kv('Réduction dons 66 %',      f"−{fr(res['reduction_dons_66'])} €")
        if res['credit_garde'] > 0:
            self.ligne_kv('Crédit frais de garde',    f"−{fr(res['credit_garde'])} €")
        if res['credit_emploi'] > 0:
            self.ligne_kv('Crédit emploi domicile',   f"−{fr(res['credit_emploi'])} €")
        if res['credit_syndicat'] > 0:
            self.ligne_kv('Crédit cotisations syndicales', f"−{fr(res['credit_syndicat'])} €")
        self.ligne_separatrice()
        self.ligne_kv('= IMPÔT NET À PAYER',           f"{fr(res['impot_net'])} €", bold_val=True)

    # ─── Guide des cases ───────────────────────────────────────────────
    def section_cases(self, profil, res):
        self.titre_section('GUIDE DES CASES À RENSEIGNER SUR VOTRE DÉCLARATION')

        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(*self.GRIS)
        self.cell(0, 5,
            'Ces cases correspondent au formulaire 2042 (déclaration en ligne sur impots.gouv.fr)',
            ln=True)
        self.set_text_color(*self.NOIR)
        self.ln(2)

        # Revenus
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*self.BLEU_FR)
        self.cell(0, 6, 'Section REVENUS — Formulaire 2042', ln=True)
        self.set_text_color(*self.NOIR)

        sal1 = profil.get('revenu_salaire_declarant', 0)
        pen1 = profil.get('revenu_pension_declarant', 0)
        sal2 = profil.get('revenu_salaire_conjoint', 0)
        pen2 = profil.get('revenu_pension_conjoint', 0)
        hs1  = min(profil.get('heures_sup_declarant', 0), 7500)
        hs2  = min(profil.get('heures_sup_conjoint', 0), 7500)
        fr1  = profil.get('frais_reels', False)
        fr2  = profil.get('frais_reels_2', False)

        if sal1 > 0:
            self.badge_case('1AJ', CASES['1AJ'], f"{fr(sal1)} €")
        if pen1 > 0:
            self.badge_case('1AS', CASES['1AS'], f"{fr(pen1)} €")
        if hs1 > 0:
            self.badge_case('1GH', CASES['1GH'], f"{fr(hs1)} €")
            self.set_font('Helvetica', 'I', 7.5)
            self.set_text_color(*self.GRIS)
            self.cell(0, 4.5, '    → Inclus dans la case 1AJ ci-dessus, mais à reporter séparément', ln=True)
            self.set_text_color(*self.NOIR)
        if fr1 and res.get('abattement_salaires_1', 0) > 0:
            self.badge_case('1AK', CASES['1AK'], f"{fr(res['abattement_salaires_1'])} €")

        if profil.get('situation') == "Marié(e) / Pacsé(e)":
            if sal2 > 0:
                self.badge_case('1BJ', CASES['1BJ'], f"{fr(sal2)} €")
            if pen2 > 0:
                self.badge_case('1BS', CASES['1BS'], f"{fr(pen2)} €")
            if hs2 > 0:
                self.badge_case('1HH', CASES['1HH'], f"{fr(hs2)} €")
            if fr2 and res.get('abattement_salaires_2', 0) > 0:
                self.badge_case('1BK', CASES['1BK'], f"{fr(res['abattement_salaires_2'])} €")

        self.ln(3)

        # Quotient familial
        if profil.get('parent_isole'):
            self.set_font('Helvetica', 'B', 9)
            self.set_text_color(*self.BLEU_FR)
            self.cell(0, 6, 'Section CHARGES DE FAMILLE', ln=True)
            self.set_text_color(*self.NOIR)
            self.badge_case('T', CASES['T'], '✓ À cocher')
            self.ln(2)

        # Déductions
        has_ded = (res.get('deduction_per', 0) > 0 or
                   res.get('pension_versee_ded', 0) > 0 or
                   profil.get('cotisations_syndicales', 0) > 0)
        if has_ded:
            self.set_font('Helvetica', 'B', 9)
            self.set_text_color(*self.BLEU_FR)
            self.cell(0, 6, 'Section CHARGES DÉDUCTIBLES', ln=True)
            self.set_text_color(*self.NOIR)
            if res.get('deduction_per', 0) > 0:
                self.badge_case('6NS', CASES['6NS'], f"{fr(res['deduction_per'])} €")
                self.set_font('Helvetica', 'I', 7.5)
                self.set_text_color(*self.GRIS)
                self.cell(0, 4.5,
                    '    → Selon type de PER : 6NS (individuel-déductible) / 6NT (autre) / 6NU (collectif)', ln=True)
                self.set_text_color(*self.NOIR)
            if res.get('pension_versee_ded', 0) > 0:
                self.badge_case('6GI', CASES['6GI'], f"{fr(res['pension_versee_ded'])} €")
            if profil.get('cotisations_syndicales', 0) > 0:
                self.badge_case('7AC', CASES['7AC'],
                    f"{fr(profil['cotisations_syndicales'])} € → crédit {fr(res.get('credit_syndicat',0))} €")
            self.ln(2)

        # Réductions
        has_red = (res.get('reduction_dons_75', 0) > 0 or
                   res.get('reduction_dons_66', 0) > 0)
        if has_red:
            self.set_font('Helvetica', 'B', 9)
            self.set_text_color(*self.BLEU_FR)
            self.cell(0, 6, 'Section RÉDUCTIONS D\'IMPÔT — DONS', ln=True)
            self.set_text_color(*self.NOIR)
            if profil.get('dons_60_75', 0) > 0:
                self.badge_case('7UD', CASES['7UD'], f"{fr(profil['dons_60_75'])} €")
            if profil.get('dons_mayotte', 0) > 0:
                self.badge_case('7UM', CASES['7UM'], f"{fr(profil['dons_mayotte'])} €")
            if profil.get('dons_60', 0) > 0:
                self.badge_case('7VC', CASES['7VC'], f"{fr(profil['dons_60'])} €")
            self.ln(2)

        # Crédits
        has_cred = (res.get('credit_garde', 0) > 0 or
                    res.get('credit_emploi', 0) > 0)
        if has_cred:
            self.set_font('Helvetica', 'B', 9)
            self.set_text_color(*self.BLEU_FR)
            self.cell(0, 6, 'Section CRÉDITS D\'IMPÔT', ln=True)
            self.set_text_color(*self.NOIR)
            nb6 = profil.get('nb_enfants_moins_6', 0)
            garde = profil.get('frais_garde', 0)
            if garde > 0 and nb6 > 0:
                case_garde = '7GA' if nb6 == 1 else ('7GB' if nb6 == 2 else '7GC')
                self.badge_case(case_garde, f'Frais garde ({nb6} enfant(s))',
                    f"dépenses : {fr(garde)} € → crédit : {fr(res['credit_garde'])} €")
            if profil.get('emploi_domicile', 0) > 0:
                self.badge_case('7DB' if not profil.get('premiere_annee_emploi') else '7DQ',
                    CASES['7DB'],
                    f"dépenses : {fr(profil['emploi_domicile'])} € → crédit : {fr(res['credit_emploi'])} €")
            self.ln(2)

    # ─── Conseils ──────────────────────────────────────────────────────
    def section_conseils(self, conseils):
        if not conseils: return
        self.titre_section('CONSEILS D\'OPTIMISATION PERSONNALISÉS')
        for c in conseils:
            self.set_fill_color(255, 251, 235)
            self.set_font('Helvetica', 'B', 9)
            self.set_text_color(146, 64, 14)
            self.cell(0, 6, f"  {c['icone']} {c['titre']}", fill=True, ln=True)
            self.set_font('Helvetica', '', 8.5)
            self.set_text_color(*self.GRIS)
            self.multi_cell(0, 5, f"  {c['detail']}")
            self.ln(2)

    # ─── Comparaison enfant majeur ─────────────────────────────────────
    def section_comparaison(self, comparaison, profil_enfant, res_enfant_seul):
        if not comparaison: return
        self.add_page()
        self.titre_section('COMPARAISON ENFANT MAJEUR — RATTACHEMENT VS FOYER INDÉPENDANT',
                           couleur=(21, 101, 192))

        sc_a = comparaison['scenario_a']
        sc_b = comparaison['scenario_b']
        meill = comparaison['meilleur_scenario']
        eco   = comparaison['economie']
        pb    = sc_b['parents']
        eb    = sc_b['enfant']

        # Scénario A
        self.bloc_encadre('Scénario A — Rattachement au foyer parental')
        self.ligne_kv('Parts du foyer avec enfant rattaché', f"{sc_a['nb_parts']:.1f}")
        self.ligne_kv('RNI foyer (après abattement rattachement 6 794 €)',
                      f"{fr(sc_a['rni'])} €")
        self.ligne_kv('Impôt brut foyer',                   f"{fr(sc_a['impot_brut'])} €")
        self.ligne_kv('Décote',                             f"−{fr(sc_a['decote'])} €")
        self.ligne_kv(f'Réduction scolarité ({sc_a["niveau_etude"]})',
                      f"−{sc_a['reduction_scolarite']} €")
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*self.BLEU_FR)
        self.cell(0, 7,
            f'  Impôt net TOTAL (Scénario A) : {fr(sc_a["cout_total"])} €',
            ln=True)
        self.set_text_color(*self.NOIR)
        self.ln(3)

        # Scénario B
        self.bloc_encadre('Scénario B — Foyer fiscal indépendant', couleur_fond=(240, 253, 244))
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*self.GRIS)
        self.cell(0, 5, '  Parents (sans enfant) :', ln=True)
        self.set_text_color(*self.NOIR)
        self.ligne_kv('  Pension alimentaire versée (déduite, case 6GI)',
                      f"{fr(pb.get('pension_versee', 0))} €", indent=4)
        self.ligne_kv('  IR parents',                       f"{fr(pb['impot_net'])} €", indent=4)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*self.GRIS)
        self.cell(0, 5, '  Enfant (foyer propre) :', ln=True)
        self.set_text_color(*self.NOIR)
        self.ligne_kv('  Parts fiscales',                   f"{eb['nb_parts']:.1f}", indent=4)
        self.ligne_kv('  RNI enfant (incl. pension reçue)', f"{fr(eb['revenu_imposable'])} €", indent=4)
        self.ligne_kv('  TMI enfant',                       f"{eb.get('taux_marginal', 0)} %", indent=4)
        self.ligne_kv('  IR enfant',                        f"{fr(eb['impot_net'])} €", indent=4)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(21, 128, 61)
        self.cell(0, 7,
            f'  Impôt net TOTAL (Scénario B) : {fr(sc_b["cout_total"])} €',
            ln=True)
        self.set_text_color(*self.NOIR)
        self.ln(3)

        # Verdict
        best_lbl = 'RATTACHEMENT' if meill == 'A' else 'FOYER INDÉPENDANT'
        col = self.BLEU_FR if meill == 'A' else (21, 128, 61)
        self.set_fill_color(219, 234, 254) if meill == 'A' else self.set_fill_color(220, 252, 231)
        self.set_text_color(*col)
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 8,
            f'  ✅ Recommandation : Scénario {meill} — {best_lbl}  |  Économie : {fr(eco)} €',
            fill=True, ln=True)
        self.set_text_color(*self.NOIR)
        self.ln(4)

        # Cases déclaration enfant (scénario B)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*self.BLEU_FR)
        self.cell(0, 6, 'Cases déclaration de l\'enfant (Scénario B — foyer indépendant)', ln=True)
        self.set_text_color(*self.NOIR)
        if profil_enfant:
            s1e = profil_enfant.get('revenu_salaire_declarant', 0)
            p1e = profil_enfant.get('revenu_pension_declarant', 0)
            hs1e = min(profil_enfant.get('heures_sup_declarant', 0), 7500)
            pens = profil_enfant.get('pension_recue', 0)
            if s1e > 0:
                self.badge_case('1AJ', 'Salaires enfant', f"{fr(s1e)} €")
            if p1e > 0:
                self.badge_case('1AS', 'Pensions enfant', f"{fr(p1e)} €")
            if hs1e > 0:
                self.badge_case('1GH', 'Heures sup enfant (exonérées)', f"{fr(hs1e)} €")
            if pens > 0:
                self.badge_case('1AS', 'Pension alimentaire reçue des parents',
                    f"{fr(min(pens, 6794))} €")
                self.set_font('Helvetica', 'I', 7.5)
                self.set_text_color(*self.GRIS)
                self.cell(0, 4.5,
                    '    → À déclarer dans la rubrique Pensions / Rentes (case 1AS)', ln=True)
                self.set_text_color(*self.NOIR)

    # ─── Point d'entrée principal ──────────────────────────────────────
    def generer(self, profil, res, conseils, comparaison=None,
                profil_enfant=None, res_enfant_seul=None) -> bytes:
        self.alias_nb_pages()
        self.add_page()
        self.page_titre(profil, res)
        self.ln(4)
        self.section_detail(profil, res)
        self.add_page()
        self.section_cases(profil, res)
        self.section_conseils(conseils)
        if comparaison:
            self.section_comparaison(comparaison, profil_enfant, res_enfant_seul)
        return bytes(self.output())
