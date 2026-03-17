"""
Generateur PDF - Simulateur IR 2026
Encodage Latin-1 uniquement (Helvetica) - tous caracteres speciaux remplaces
"""
from fpdf import FPDF
from datetime import date


def fr(val, dec=0):
    """Formatage nombre francais pour PDF - espace classique separateur milliers."""
    if val is None:
        return "-"
    if dec == 0:
        s = f"{abs(val):,.0f}".replace(",", " ")
    else:
        s = f"{abs(val):,.{dec}f}"
        parts = s.split(".")
        s = parts[0].replace(",", " ") + "," + parts[1]
    return ("-" if val < 0 else "") + s


def _s(text):
    """Sanitise les caracteres hors Latin-1 pour la police Helvetica."""
    if not isinstance(text, str):
        text = str(text)
    table = {
        '\u2014': '-', '\u2013': '-',
        '\u202f': ' ', '\u00a0': ' ',
        '\u2192': '=>', '\u2190': '<=',
        '\u2264': '<=', '\u2265': '>=',
        '\u2022': '*',
        '\u2019': "'", '\u2018': "'",
        '\u201c': '"', '\u201d': '"',
        '\u20ac': 'EUR',
        '\u2705': '[OK]', '\u274c': '[X]', '\u2714': '[V]',
        '\U0001f4b0': '', '\U0001f4cb': '', '\U0001f4cc': '',
        '\U0001f4ce': '', '\U0001f4c4': '', '\U0001f4ca': '',
        '\U0001f4c9': '', '\U0001f4dd': '', '\U0001f4a1': '',
        '\U0001f3e0': '', '\U0001f393': '', '\U0001f3c6': '',
        '\U0001f91d': '', '\U0001f1eb': '', '\U0001f1f7': '',
        '\u23f0': '',    '\u2764': '',    '\u2665': '',
        '\U0001f4e4': '', '\U0001f514': '', '\U0001f6a7': '',
    }
    for old, new in table.items():
        text = text.replace(old, new)
    return text.encode('latin-1', errors='replace').decode('latin-1')


CASES = {
    '1AJ': 'Traitements, salaires - Declarant 1',
    '1BJ': 'Traitements, salaires - Declarant 2',
    '1AS': 'Pensions, retraites - Declarant 1',
    '1BS': 'Pensions, retraites - Declarant 2',
    '1GH': 'Heures supplementaires exonerees - D1 (plafond 7 500 EUR)',
    '1HH': 'Heures supplementaires exonerees - D2',
    '1AK': 'Frais reels justifies - Declarant 1',
    '1BK': 'Frais reels justifies - Declarant 2',
    '6NS': 'PER individuel deductible (cotisations)',
    '6NT': 'PER individuel deductible (primes)',
    '6GI': 'Pension alimentaire versee a enfant majeur',
    'T'  : 'Case T - Parent isole (monoparentale)',
    'D'  : 'Rattachement enfant majeur (case D)',
    '7UD': 'Dons 75 % - aide aux personnes en difficulte',
    '7UM': 'Dons 75 % - urgence Mayotte',
    '7VC': 'Dons 66 % - associations interet general',
    '7GA': 'Frais garde 1er enfant < 6 ans',
    '7GB': 'Frais garde 2e enfant',
    '7GC': 'Frais garde 3e enfant et plus',
    '7DB': 'Emploi a domicile - depenses',
    '7DQ': 'Emploi a domicile - 1ere annee',
    '7AC': 'Cotisations syndicales',
}


class GenererRapportPDF(FPDF):

    # Palette couleurs raffinee
    BLEU      = (0, 49, 137)       # Bleu France profond
    BLEU_CLAIR= (37, 99, 235)      # Bleu vif pour accents
    ROUGE     = (185, 28, 28)      # Rouge sobre
    VERT      = (21, 128, 61)      # Vert confiance
    VERT_CLAIR= (220, 252, 231)    # Fond vert pale
    ORANGE    = (146, 64, 14)      # Ambre conseil
    GRIS_FONCE= (55, 65, 81)       # Texte secondaire
    GRIS      = (107, 114, 128)    # Texte leger
    GRIS_CLAIR= (243, 244, 246)    # Fond alternance
    BLANC     = (255, 255, 255)
    NOIR      = (17, 24, 39)       # Texte principal
    CLR       = (239, 246, 255)    # Fond bleu tres pale
    CLR_OR    = (255, 251, 235)    # Fond ambre tres pale
    BLEU_PALE = (219, 234, 254)    # Fond badge bleu

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(True, margin=18)
        self.set_margins(16, 18, 16)

    # ─── En-tete raffine ─────────────────────────────────────────────
    def header(self):
        # Bande bleue principale
        self.set_fill_color(*self.BLEU)
        self.rect(0, 0, 210, 11, 'F')
        # Liseré rouge tricolore
        self.set_fill_color(200, 16, 46)
        self.rect(0, 11, 210, 2, 'F')

        self.set_font('Helvetica', 'B', 8.5)
        self.set_text_color(*self.BLANC)
        self.set_xy(0, 1.5)
        self.cell(120, 8,
            _s('  Simulateur IR 2026 - Revenus 2025 - Bareme officiel DGFiP'),
            ln=False)
        self.set_xy(-80, 1.5)
        self.set_font('Helvetica', '', 7.5)
        self.cell(70, 8,
            _s(f'Edition du {date.today().strftime("%d/%m/%Y")}'),
            align='R')
        self.set_text_color(*self.NOIR)
        self.ln(10)

    # ─── Pied de page raffine ─────────────────────────────────────────
    def footer(self):
        self.set_y(-12)
        # Ligne de separation
        self.set_draw_color(*self.BLEU_CLAIR)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(),
                  210 - self.r_margin, self.get_y())
        self.ln(1.5)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(*self.GRIS)
        self.cell(0, 5,
            _s(f'Simulation a titre indicatif - Consultez impots.gouv.fr - Page {self.page_no()}/{{nb}}'),
            align='C')
        self.set_line_width(0.2)
        self.set_draw_color(200, 200, 200)

    # ─── Titre de section ameliore ────────────────────────────────────
    def titre_section(self, txt, bg=None):
        if bg is None:
            bg = self.BLEU
        self.ln(4)
        # Rectangle de fond
        self.set_fill_color(*bg)
        self.set_text_color(*self.BLANC)
        self.set_font('Helvetica', 'B', 9.5)
        self.cell(0, 8, _s(f'  {txt}'), fill=True, ln=True)
        # Trait de soulignement color
        r, g, b = bg
        self.set_fill_color(min(r+40,255), min(g+40,255), min(b+60,255))
        self.rect(self.l_margin, self.get_y(), 178, 1.2, 'F')
        self.set_text_color(*self.NOIR)
        self.ln(3)

    # ─── Ligne label / valeur ─────────────────────────────────────────
    def ligne(self, label, val, bold_val=False, col=None):
        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(*self.GRIS_FONCE)
        self.cell(100, 5.5, _s(label))
        self.set_text_color(*(col if col else self.NOIR))
        self.set_font('Helvetica', 'B' if bold_val else '', 8.5)
        self.cell(0, 5.5, _s(val), ln=True)
        self.set_text_color(*self.NOIR)

    # ─── Separateur ───────────────────────────────────────────────────
    def sep(self):
        self.ln(1)
        self.set_draw_color(*self.BLEU_CLAIR)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y(), 210 - self.r_margin, self.get_y())
        self.set_line_width(0.2)
        self.set_draw_color(200, 200, 200)
        self.ln(3)

    # ─── Badge case fiscale ───────────────────────────────────────────
    def badge(self, code, desc, val):
        y0 = self.get_y()
        # Fond complet de la ligne
        self.set_fill_color(248, 250, 255)
        self.rect(self.l_margin, y0, 178, 6.5, 'F')
        # Badge code (fond bleu)
        self.set_fill_color(*self.BLEU)
        self.set_text_color(*self.BLANC)
        self.set_font('Courier', 'B', 8)
        self.set_xy(self.l_margin, y0)
        self.cell(16, 6.5, _s(f' {code}'), fill=True)
        # Description
        self.set_text_color(*self.GRIS_FONCE)
        self.set_font('Helvetica', '', 8)
        self.cell(112, 6.5, _s(f'  {desc}'))
        # Valeur
        self.set_text_color(*self.BLEU_CLAIR)
        self.set_font('Helvetica', 'B', 8.5)
        self.cell(0, 6.5, _s(val), ln=True)
        self.set_text_color(*self.NOIR)
        self.ln(0.5)

    # ─── Note explicative ─────────────────────────────────────────────
    def note(self, txt):
        self.set_font('Helvetica', 'I', 7.5)
        self.set_text_color(*self.GRIS)
        self.set_fill_color(249, 250, 251)
        self.cell(0, 4.5, _s(f'      => {txt}'), fill=True, ln=True)
        self.set_text_color(*self.NOIR)

    # ─── Rangee de KPIs ameliores ─────────────────────────────────────
    def kpi_row(self, items):
        w = (210 - 32) / len(items)
        y0 = self.get_y()
        for i, (label, val, col) in enumerate(items):
            x0 = self.l_margin + i * w
            # Fond blanc avec bordure coloree en haut
            self.set_fill_color(255, 255, 255)
            self.rect(x0, y0, w - 2, 24, 'FD')
            # Barre coloree en haut de la carte
            self.set_fill_color(*col)
            self.rect(x0, y0, w - 2, 2.5, 'F')
            # Valeur principale
            self.set_xy(x0, y0 + 4)
            self.set_font('Helvetica', 'B', 12)
            self.set_text_color(*col)
            self.cell(w - 2, 8, _s(val), align='C')
            # Label
            self.set_xy(x0, y0 + 13)
            self.set_font('Helvetica', '', 6.5)
            self.set_text_color(*self.GRIS)
            self.cell(w - 2, 5, _s(label.upper()), align='C')
        self.ln(28)
        self.set_text_color(*self.NOIR)

    # ─── Tableau des tranches ameliore ────────────────────────────────
    def tableau_tranches(self, tranches):
        cols = [96, 22, 36, 30]
        hdrs = ['Tranche d\'imposition', 'Taux', 'Base imposable', 'Impot tranche']
        # En-tete avec fond bleu fonce
        self.set_fill_color(*self.BLEU)
        self.set_text_color(*self.BLANC)
        self.set_font('Helvetica', 'B', 8)
        for h, w in zip(hdrs, cols):
            self.cell(w, 6.5, _s(h), fill=True, align='C' if w < 50 else 'L')
        self.ln()
        self.set_text_color(*self.NOIR)
        alt = False
        for t in tranches:
            if t['base'] == 0:
                continue
            # Alternance de couleurs
            if alt:
                self.set_fill_color(239, 246, 255)
            else:
                self.set_fill_color(*self.BLANC)
            self.set_font('Helvetica', '', 8)
            self.set_text_color(*self.GRIS_FONCE)
            self.cell(cols[0], 6, _s(t['label']), fill=True)
            self.set_text_color(*self.BLEU_CLAIR)
            self.set_font('Helvetica', 'B', 8)
            self.cell(cols[1], 6, _s(f"{t['taux']} %"), fill=True, align='C')
            self.set_text_color(*self.NOIR)
            self.set_font('Helvetica', '', 8)
            self.cell(cols[2], 6, _s(f"{fr(t['base'])} EUR"), fill=True, align='R')
            self.set_font('Helvetica', 'B', 8)
            self.set_text_color(*self.ROUGE)
            self.cell(cols[3], 6, _s(f"{fr(t['impot_tranche'])} EUR"), fill=True, align='R')
            self.ln()
            self.set_text_color(*self.NOIR)
            alt = not alt
        # Ligne de cloture du tableau
        self.set_fill_color(*self.BLEU)
        self.rect(self.l_margin, self.get_y(), 178, 0.8, 'F')
        self.ln(3)

    # ─── Pages ───────────────────────────────────────────────────────

    def page_titre(self, profil, res):
        sit_map = {
            'Celibataire / Divorce(e)': 'Celibataire / Divorce(e)',
            'Marie(e) / Pacse(e)': 'Marie(e) / Pacse(e)',
            'Veuf(ve)': 'Veuf(ve)',
        }
        sit = sit_map.get(profil.get('situation', ''), profil.get('situation', ''))

        # Grand titre
        self.ln(2)
        self.set_font('Helvetica', 'B', 22)
        self.set_text_color(*self.BLEU)
        self.cell(0, 12, _s('BILAN FISCAL 2026'), ln=True, align='C')

        self.set_font('Helvetica', '', 10)
        self.set_text_color(*self.GRIS)
        self.cell(0, 6, _s('Declaration revenus 2025 - Bareme DGFiP officiel'),
                  ln=True, align='C')
        self.ln(3)

        # Trait decoratif tricolore
        self.set_fill_color(*self.BLEU)
        self.rect(self.l_margin, self.get_y(), 60, 2, 'F')
        self.set_fill_color(255, 255, 255)
        self.rect(self.l_margin + 60, self.get_y(), 58, 2, 'F')
        self.set_fill_color(200, 16, 46)
        self.rect(self.l_margin + 118, self.get_y(), 60, 2, 'F')
        self.ln(5)

        # Bandeau situation
        self.set_fill_color(*self.CLR)
        self.set_draw_color(*self.BLEU_CLAIR)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*self.BLEU)
        self.cell(0, 8,
            _s(f'  Situation : {sit}   |   Enfants : {profil.get("nb_enfants",0)}'
               f'   |   Parts fiscales : {res["nb_parts"]:.1f}   |   TMI : {res["taux_marginal"]} %'),
            fill=True, border=1, ln=True)
        self.set_draw_color(200, 200, 200)
        self.ln(6)

        # KPIs
        self.kpi_row([
            ('Revenu Net Imposable', f'{fr(res["revenu_imposable"])} EUR', self.BLEU),
            ('Impot brut',           f'{fr(res["impot_brut"])} EUR',       self.ROUGE),
            ('Decote appliquee',     f'-{fr(res["decote"])} EUR',          self.VERT),
            ('IMPOT NET A PAYER',    f'{fr(res["impot_net"])} EUR',        self.BLEU_CLAIR),
        ])

        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(*self.GRIS)
        self.cell(0, 6,
            _s(f'Taux moyen : {res["taux_moyen"]:.2f} %   |   '
               f'TMI : {res["taux_marginal"]} %   |   '
               f'Quotient familial : {fr(res["quotient_familial"])} EUR'),
            ln=True, align='C')
        self.set_text_color(*self.NOIR)

    def page_detail(self, profil, res):
        self.titre_section('DETAIL DU CALCUL FISCAL')

        sal1  = profil.get('revenu_salaire_declarant', 0)
        pen1  = profil.get('revenu_pension_declarant', 0)
        sal2  = profil.get('revenu_salaire_conjoint', 0)
        pen2  = profil.get('revenu_pension_conjoint', 0)
        hs1   = profil.get('heures_sup_declarant', 0)
        hs2   = profil.get('heures_sup_conjoint', 0)
        exo_e = profil.get('exoneration_emploi_etudiant', 0)

        self.set_font('Helvetica', 'B', 8.5)
        self.set_text_color(*self.BLEU_CLAIR)
        self.cell(0, 5.5, _s('Revenus et abattements'), ln=True)
        self.set_text_color(*self.NOIR)

        self.ligne('Salaires bruts D1', f'{fr(sal1)} EUR')
        if hs1 > 0:
            self.ligne('  dont Heures sup exonerees D1',
                       f'-{fr(min(hs1,7500))} EUR')
        if exo_e > 0:
            self.ligne('  dont Exoneration jobs etudiants',
                       f'-{fr(exo_e)} EUR')
        self.ligne('Abattement salaires D1',
                   f'-{fr(res["abattement_salaires_1"])} EUR')
        self.ligne('Pensions / Retraites D1', f'{fr(pen1)} EUR')
        self.ligne('Abattement pensions D1',
                   f'-{fr(res["abattement_pensions_1"])} EUR')

        if profil.get('situation') == 'Marie(e) / Pacse(e)':
            self.ligne('Salaires D2', f'{fr(sal2)} EUR')
            if hs2 > 0:
                self.ligne('  dont Heures sup D2', f'-{fr(min(hs2,7500))} EUR')
            self.ligne('Abattement D2',
                       f'-{fr(res["abattement_salaires_2"])} EUR')
            self.ligne('Pensions D2', f'{fr(pen2)} EUR')
            self.ligne('Abattement pensions D2',
                       f'-{fr(res["abattement_pensions_2"])} EUR')

        self.ligne('Deduction PER', f'-{fr(res["deduction_per"])} EUR')
        if res.get('pension_versee_ded', 0) > 0:
            self.ligne('Pension alimentaire versee',
                       f'-{fr(res["pension_versee_ded"])} EUR')
        self.sep()
        self.ligne('= Revenu Net Imposable',
                   f'{fr(res["revenu_imposable"])} EUR', bold_val=True)
        self.ln(3)

        self.set_font('Helvetica', 'B', 8.5)
        self.set_text_color(*self.BLEU_CLAIR)
        self.cell(0, 5.5,
            _s(f'Bareme progressif ({res["nb_parts"]:.1f} parts)'), ln=True)
        self.set_text_color(*self.NOIR)
        self.tableau_tranches(res['detail_tranches'])

        self.ligne('Impot brut apres QF', f'{fr(res["impot_brut"])} EUR')
        self.ligne('Decote (889 - 45,25 % x impot)',
                   f'-{fr(res["decote"])} EUR')
        if res['reduction_dons_75'] > 0:
            self.ligne('Reduction dons 75 %',
                       f'-{fr(res["reduction_dons_75"])} EUR')
        if res['reduction_dons_66'] > 0:
            self.ligne('Reduction dons 66 %',
                       f'-{fr(res["reduction_dons_66"])} EUR')
        if res['credit_garde'] > 0:
            self.ligne('Credit frais de garde',
                       f'-{fr(res["credit_garde"])} EUR')
        if res['credit_emploi'] > 0:
            self.ligne('Credit emploi domicile',
                       f'-{fr(res["credit_emploi"])} EUR')
        if res['credit_syndicat'] > 0:
            self.ligne('Credit cotisations syndicales',
                       f'-{fr(res["credit_syndicat"])} EUR')
        self.sep()
        self.ligne('= IMPOT NET A PAYER',
                   f'{fr(res["impot_net"])} EUR', bold_val=True)

    def page_cases(self, profil, res):
        self.titre_section('GUIDE DES CASES A RENSEIGNER - Formulaire 2042')

        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(*self.GRIS)
        self.cell(0, 5,
            _s('Cases correspondant a la declaration en ligne sur impots.gouv.fr'), ln=True)
        self.set_text_color(*self.NOIR)
        self.ln(2)

        sal1 = profil.get('revenu_salaire_declarant', 0)
        pen1 = profil.get('revenu_pension_declarant', 0)
        sal2 = profil.get('revenu_salaire_conjoint', 0)
        pen2 = profil.get('revenu_pension_conjoint', 0)
        hs1  = min(profil.get('heures_sup_declarant', 0), 7500)
        hs2  = min(profil.get('heures_sup_conjoint', 0), 7500)
        exo  = profil.get('exoneration_emploi_etudiant', 0)
        fr1  = profil.get('frais_reels', False)
        fr2  = profil.get('frais_reels_2', False)

        self.set_font('Helvetica', 'B', 8.5)
        self.set_text_color(*self.BLEU_CLAIR)
        self.cell(0, 5.5, _s('REVENUS - Formulaire 2042'), ln=True)
        self.set_text_color(*self.NOIR)

        if sal1 > 0:
            self.badge('1AJ', CASES['1AJ'], f'{fr(sal1)} EUR')
        if pen1 > 0:
            self.badge('1AS', CASES['1AS'], f'{fr(pen1)} EUR')
        if hs1 > 0:
            self.badge('1GH', CASES['1GH'], f'{fr(hs1)} EUR')
            self.note('Montant inclus dans 1AJ, a reporter separement')
        if exo > 0:
            self.badge('1AJ', 'Exoneration emploi etudiant (a deduire de 1AJ)',
                       f'-{fr(exo)} EUR')
            self.note(f'Art. 81 bis CGI - 3 x SMIC mensuel 2024 = 5 301 EUR max')
        if fr1:
            self.badge('1AK', CASES['1AK'],
                       f'{fr(res.get("abattement_salaires_1",0))} EUR')

        if profil.get('situation') == 'Marie(e) / Pacse(e)':
            if sal2 > 0:
                self.badge('1BJ', CASES['1BJ'], f'{fr(sal2)} EUR')
            if pen2 > 0:
                self.badge('1BS', CASES['1BS'], f'{fr(pen2)} EUR')
            if hs2 > 0:
                self.badge('1HH', CASES['1HH'], f'{fr(hs2)} EUR')
            if fr2:
                self.badge('1BK', CASES['1BK'],
                           f'{fr(res.get("abattement_salaires_2",0))} EUR')
        self.ln(2)

        # Deductions
        per = profil.get('versement_per', 0)
        if per > 0 or res.get('pension_versee_ded',0) > 0 or profil.get('cotisations_syndicales',0) > 0:
            self.set_font('Helvetica', 'B', 8.5)
            self.set_text_color(*self.BLEU_CLAIR)
            self.cell(0, 5.5, _s('DEDUCTIONS'), ln=True)
            self.set_text_color(*self.NOIR)
            if per > 0:
                self.badge('6NS', CASES['6NS'], f'{fr(per)} EUR')
                self.note('Selon type de PER : 6NS / 6NT / 6NU')
            if res.get('pension_versee_ded',0) > 0:
                self.badge('6GI', CASES['6GI'],
                           f'{fr(res["pension_versee_ded"])} EUR')
            if profil.get('cotisations_syndicales',0) > 0:
                self.badge('7AC', CASES['7AC'],
                           f'{fr(profil["cotisations_syndicales"])} EUR => credit {fr(res.get("credit_syndicat",0))} EUR')
            self.ln(2)

        # Dons
        if res.get('reduction_dons_75',0) > 0 or res.get('reduction_dons_66',0) > 0:
            self.set_font('Helvetica', 'B', 8.5)
            self.set_text_color(*self.BLEU_CLAIR)
            self.cell(0, 5.5, _s('REDUCTIONS - DONS'), ln=True)
            self.set_text_color(*self.NOIR)
            if profil.get('dons_60_75',0) > 0:
                self.badge('7UD', CASES['7UD'],
                           f'{fr(profil["dons_60_75"])} EUR')
            if profil.get('dons_mayotte',0) > 0:
                self.badge('7UM', CASES['7UM'],
                           f'{fr(profil["dons_mayotte"])} EUR')
            if profil.get('dons_60',0) > 0:
                self.badge('7VC', CASES['7VC'],
                           f'{fr(profil["dons_60"])} EUR')
            self.ln(2)

        # Credits
        if res.get('credit_garde',0) > 0 or res.get('credit_emploi',0) > 0:
            self.set_font('Helvetica', 'B', 8.5)
            self.set_text_color(*self.BLEU_CLAIR)
            self.cell(0, 5.5, _s('CREDITS D\'IMPOT'), ln=True)
            self.set_text_color(*self.NOIR)
            nb6   = profil.get('nb_enfants_moins_6', 0)
            garde = profil.get('frais_garde', 0)
            if garde > 0 and nb6 > 0:
                case_g = '7GA' if nb6 == 1 else ('7GB' if nb6 == 2 else '7GC')
                self.badge(case_g, f'Frais garde ({nb6} enfant(s))',
                           f'depenses : {fr(garde)} EUR => credit : {fr(res["credit_garde"])} EUR')
            emp = profil.get('emploi_domicile', 0)
            if emp > 0:
                case_e = '7DQ' if profil.get('premiere_annee_emploi') else '7DB'
                self.badge(case_e, CASES['7DB'],
                           f'depenses : {fr(emp)} EUR => credit : {fr(res["credit_emploi"])} EUR')

    def page_conseils(self, conseils):
        if not conseils:
            return
        self.titre_section('CONSEILS D\'OPTIMISATION PERSONNALISES', bg=self.ORANGE)
        for i, c in enumerate(conseils, 1):
            self.set_fill_color(*self.CLR_OR)
            self.set_draw_color(180, 83, 9)
            self.set_font('Helvetica', 'B', 8.5)
            self.set_text_color(*self.ORANGE)
            ico = {'PER':'[PER]','FR':'[FR]','DONS':'[DONS]',
                   'DOM':'[DOM]','TMI':'[TMI]','SYND':'[SYND]','HS':'[HS]'}
            self.cell(0, 6.5,
                _s(f'  {i}. {ico.get(c["icone"],"")} {c["titre"]}'),
                fill=True, border='L', ln=True)
            self.set_draw_color(200, 200, 200)
            self.set_font('Helvetica', '', 8)
            self.set_text_color(*self.GRIS_FONCE)
            self.multi_cell(0, 5, _s(f'  {c["detail"]}'))
            self.ln(2)
        self.set_text_color(*self.NOIR)

    def page_comparaison(self, comparaison, profil_enfant):
        self.add_page()
        self.titre_section(
            'COMPARAISON ENFANT MAJEUR - RATTACHEMENT vs FOYER INDEPENDANT',
            bg=(21, 101, 192))

        sc_a  = comparaison['scenario_a']
        sc_b  = comparaison['scenario_b']
        meill = comparaison['meilleur_scenario']
        eco   = comparaison['economie']
        etud  = comparaison.get('etudiant', False)
        pb    = sc_b['parents']
        eb    = sc_b['enfant']

        self.set_font('Helvetica', 'B', 8.5)
        self.set_text_color(*self.BLEU_CLAIR)
        self.cell(0, 6,
            _s(f'Enfant : {"Etudiant" if etud else "Actif"}'
               f' | Revenus enfant : {fr(sc_a["revenus_enfant_integres"])} EUR'
               f' | Pension potentielle : {fr(eb.get("pension_recue",0))} EUR'),
            ln=True)
        self.set_text_color(*self.NOIR)
        self.ln(3)

        # ── Scenario A ──────────────────────────────────────────────
        self.set_fill_color(*self.CLR)
        self.set_draw_color(*self.BLEU)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*self.BLEU)
        self.cell(0, 7, _s('  Scenario A - Rattachement au foyer parental'),
                  fill=True, border='L', ln=True)
        self.set_draw_color(200, 200, 200)
        self.set_text_color(*self.NOIR)
        self.ln(1)
        self.ligne('Parts foyer avec enfant rattache (+0,5 part)',
                   f'{sc_a["nb_parts"]:.1f}')
        self.ligne('Revenus enfant integres au foyer',
                   f'{fr(sc_a["revenus_enfant_integres"])} EUR')
        if etud and sc_a['exoneration_etudiant'] > 0:
            self.ligne('  Exoneration jobs etudiants',
                       f'-{fr(sc_a["exoneration_etudiant"])} EUR')
        self.ligne('RNI foyer combine',
                   f'{fr(sc_a["rni"])} EUR')
        self.ligne('Impot brut foyer',
                   f'{fr(sc_a["impot_brut"])} EUR')
        self.ligne('Decote',
                   f'-{fr(sc_a["decote"])} EUR')
        self.ligne('IR foyer avant reduction scolarite',
                   f'{fr(sc_a["impot_net_avant_scol"])} EUR')
        if etud:
            self.ligne(f'Reduction scolarite ({sc_a["niveau_etude"]})',
                       f'-{sc_a["reduction_scolarite"]} EUR')
        self.sep()
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*self.BLEU)
        self.cell(0, 7,
            _s(f'  IMPOT NET TOTAL (Scenario A) : {fr(sc_a["cout_total"])} EUR'),
            ln=True)
        self.set_text_color(*self.NOIR)
        self.ln(4)

        # ── Scenario B ──────────────────────────────────────────────
        self.set_fill_color(*self.VERT_CLAIR)
        self.set_draw_color(*self.VERT)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*self.VERT)
        self.cell(0, 7, _s('  Scenario B - Foyer independant'),
                  fill=True, border='L', ln=True)
        self.set_draw_color(200, 200, 200)
        self.set_text_color(*self.NOIR)
        self.ln(1)

        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*self.GRIS_FONCE)
        self.cell(0, 5, _s('  Parents (sans enfant rattache) :'), ln=True)
        self.set_text_color(*self.NOIR)
        self.ligne('  Parts parents', f'{pb["nb_parts"]:.1f}')
        self.ligne('  Pension versee deductible (case 6GI)',
                   f'{fr(pb.get("pension_versee",0))} EUR')
        self.ligne('  IR parents', f'{fr(pb["impot_net"])} EUR')
        self.ln(1)
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*self.GRIS_FONCE)
        self.cell(0, 5, _s('  Enfant (propre declaration) :'), ln=True)
        self.set_text_color(*self.NOIR)
        self.ligne('  Parts enfant', f'{eb["nb_parts"]:.1f}')
        if etud and eb.get('exoneration_etudiant',0) > 0:
            self.ligne('  Exoneration jobs etudiants',
                       f'-{fr(eb["exoneration_etudiant"])} EUR')
        self.ligne('  Pension recue imposable (case 1AS)',
                   f'{fr(eb.get("pension_recue",0))} EUR')
        self.ligne('  RNI enfant', f'{fr(eb["revenu_imposable"])} EUR')
        self.ligne('  TMI enfant', f'{eb.get("taux_marginal",0)} %')
        self.ligne('  IR enfant', f'{fr(eb["impot_net"])} EUR')
        self.sep()
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*self.VERT)
        self.cell(0, 7,
            _s(f'  IMPOT NET TOTAL (Scenario B) : {fr(sc_b["cout_total"])} EUR'),
            ln=True)
        self.set_text_color(*self.NOIR)
        self.ln(4)

        # ── Verdict ─────────────────────────────────────────────────
        if meill == 'A':
            self.set_fill_color(*self.BLEU_PALE)
            self.set_draw_color(*self.BLEU)
            col_v = self.BLEU
            lab   = 'RATTACHEMENT AU FOYER (Scenario A)'
        else:
            self.set_fill_color(*self.VERT_CLAIR)
            self.set_draw_color(*self.VERT)
            col_v = self.VERT
            lab   = 'FOYER INDEPENDANT (Scenario B)'

        self.set_text_color(*col_v)
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 9,
            _s(f'  [OK] Recommandation : {lab}  |  Economie : {fr(eco)} EUR'),
            fill=True, border='L', ln=True)
        self.set_draw_color(200, 200, 200)
        self.set_text_color(*self.NOIR)
        self.ln(3)

        # ── Cases declaration enfant ─────────────────────────────────
        self.set_font('Helvetica', 'B', 8.5)
        self.set_text_color(*self.BLEU_CLAIR)
        self.cell(0, 5.5,
            _s('Cases declaration de l\'enfant (Scenario B)'), ln=True)
        self.set_text_color(*self.NOIR)
        if profil_enfant:
            s1e  = profil_enfant.get('revenu_salaire_declarant', 0)
            p1e  = profil_enfant.get('revenu_pension_declarant', 0)
            hs1e = min(profil_enfant.get('heures_sup_declarant', 0), 7500)
            pen  = eb.get('pension_recue', 0)
            exoe = eb.get('exoneration_etudiant', 0)
            if s1e > 0:
                self.badge('1AJ', 'Salaires enfant', f'{fr(s1e)} EUR')
            if exoe > 0:
                self.badge('1AJ', 'Exoneration emploi etudiant (a deduire)',
                           f'-{fr(exoe)} EUR')
            if p1e > 0:
                self.badge('1AS', 'Pensions enfant', f'{fr(p1e)} EUR')
            if hs1e > 0:
                self.badge('1GH', 'Heures sup enfant', f'{fr(hs1e)} EUR')
            if pen > 0:
                self.badge('1AS', 'Pension recue des parents',
                           f'{fr(pen)} EUR')
                self.note('Imposable comme pension - a ajouter a la case 1AS')

    def generer(self, profil, res, conseils, comparaison=None,
                profil_enfant=None, res_enfant_seul=None) -> bytes:
        self.alias_nb_pages()
        self.add_page()
        self.page_titre(profil, res)
        self.ln(4)
        self.page_detail(profil, res)
        self.add_page()
        self.page_cases(profil, res)
        self.page_conseils(conseils)
        if comparaison:
            self.page_comparaison(comparaison, profil_enfant)
        return bytes(self.output())


class GenererRapportDirigeantPDF(GenererRapportPDF):
    """Rapport PDF specifique aux revenus de dirigeant."""

    def generer(self, profil_dir: dict, moteur_dir) -> bytes:
        self.alias_nb_pages()
        self.add_page()

        # Titre
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(*self.BLEU)
        self.ln(2)
        self.cell(0, 12, _s('BILAN FISCAL DIRIGEANT 2026'), ln=True, align='C')

        self.set_font('Helvetica', '', 9)
        self.set_text_color(*self.GRIS)
        self.cell(0, 6, _s('Revenus professionnels 2025 - Bareme DGFiP'),
                  ln=True, align='C')
        self.ln(2)

        # Trait tricolore
        self.set_fill_color(*self.BLEU)
        self.rect(self.l_margin, self.get_y(), 60, 2, 'F')
        self.set_fill_color(255, 255, 255)
        self.rect(self.l_margin + 60, self.get_y(), 58, 2, 'F')
        self.set_fill_color(200, 16, 46)
        self.rect(self.l_margin + 118, self.get_y(), 60, 2, 'F')
        self.ln(5)

        statut = profil_dir.get('statut', '')
        rem    = profil_dir.get('remuneration', 0)
        tmi    = profil_dir.get('tmi', 30)
        ben    = profil_dir.get('benefice', 0)
        div_b  = profil_dir.get('dividendes', 0)

        # Bandeau statut
        self.set_fill_color(*self.CLR)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*self.BLEU)
        self.cell(0, 8,
            _s(f'  Statut : {statut}   |   TMI : {tmi} %'
               f'   |   Remuneration : {fr(rem)} EUR'
               f'   |   Benefice : {fr(ben)} EUR'),
            fill=True, border=1, ln=True)
        self.set_draw_color(200, 200, 200)
        self.set_text_color(*self.NOIR)
        self.ln(5)

        # IS
        if ben > 0:
            self.titre_section('IMPOT SUR LES SOCIETES (IS)')
            is_d = moteur_dir.calculer_is(ben)
            self.ligne('IS taux reduit 15 %',
                       f'{fr(is_d["is_reduit"])} EUR (base : {fr(is_d["base_reduit"])} EUR)')
            self.ligne('IS taux normal 25 %',
                       f'{fr(is_d["is_normal"])} EUR (base : {fr(is_d["base_normal"])} EUR)')
            self.sep()
            self.ligne('IS total', f'{fr(is_d["is_total"])} EUR', bold_val=True,
                       col=self.ROUGE)
            self.ligne('Taux effectif IS', f'{is_d["taux_effectif"]:.2f} %')
            self.ligne('Benefice net disponible', f'{fr(is_d["benefice_net"])} EUR',
                       bold_val=True, col=self.VERT)

        # Remuneration
        if rem > 0:
            self.titre_section('REMUNERATION DE GERANCE (cat. TS)')
            r_ger = moteur_dir.calculer_gerance(rem)
            self.ligne('Remuneration brute', f'{fr(rem)} EUR')
            self.ligne(f'Abattement ({r_ger["type_abattement"]})',
                       f'-{fr(r_ger["abattement"])} EUR')
            self.ligne('Imposable IR', f'{fr(r_ger["imposable"])} EUR', bold_val=True)
            self.ligne(f'IR estime (TMI {tmi} %)',
                       f'{fr(int(r_ger["imposable"]*tmi/100))} EUR')
            if statut:
                cot = moteur_dir.calculer_cotisations_tns(rem, statut)
                self.ln(2)
                self.set_font('Helvetica', 'B', 8.5)
                self.set_text_color(*self.BLEU_CLAIR)
                self.cell(0, 5, _s('Cotisations sociales'), ln=True)
                self.set_text_color(*self.NOIR)
                for k, v in cot['detail'].items():
                    self.set_font('Helvetica', '', 8)
                    self.set_text_color(*self.GRIS_FONCE)
                    self.cell(80, 5, _s(k))
                    self.set_text_color(*self.NOIR)
                    self.set_font('Helvetica', 'B', 8)
                    self.cell(0, 5, _s(v), ln=True)
                self.sep()
                self.ligne('Total cotisations',
                           f'{fr(cot["cotisations"])} EUR ({int(cot["taux_global"]*100)} %)',
                           bold_val=True, col=self.ROUGE)
                self.ligne('Net avant IR', f'{fr(cot["net_avant_ir"])} EUR',
                           bold_val=True, col=self.VERT)

        # Dividendes
        if div_b > 0:
            self.titre_section('DIVIDENDES')
            d_data = moteur_dir.calculer_dividendes(div_b, tmi)
            self.ligne('Dividendes bruts', f'{fr(div_b)} EUR')
            pfu = d_data['pfu']
            bar = d_data['bareme']
            self.ligne('PFU 30 % : IR 12,8 %',
                       f'{fr(pfu["ir"])} EUR | PS : {fr(pfu["ps"])} EUR | Total : {fr(pfu["total_imposition"])} EUR')
            self.ligne(f'Option bareme {tmi} % + abatt. 40 %',
                       f'IR : {fr(bar["ir"])} EUR | Total : {fr(bar["total_imposition"])} EUR')
            if d_data['meilleur'] == 'Bareme':
                self.set_fill_color(*self.VERT_CLAIR)
                col_d = self.VERT
            else:
                self.set_fill_color(*self.BLEU_PALE)
                col_d = self.BLEU
            self.set_text_color(*col_d)
            self.set_font('Helvetica', 'B', 9)
            self.cell(0, 7,
                _s(f'  Recommande : {d_data["meilleur"]} - economie : {fr(d_data["economie"])} EUR'),
                fill=True, ln=True)
            self.set_text_color(*self.NOIR)

        # Optimisations
        opts = moteur_dir.optimisation_fiscale({
            'benefice': ben, 'remuneration': rem, 'tmi': tmi,
            'statut_actuel': statut, 'ca': ben * 3, 'type_activite': 'services'
        })
        if opts:
            self.add_page()
            self.titre_section('RECOMMANDATIONS D\'OPTIMISATION FISCALE',
                               bg=self.ORANGE)
            for i, opt in enumerate(opts[:5], 1):
                self.set_fill_color(*self.CLR_OR)
                self.set_draw_color(180, 83, 9)
                self.set_font('Helvetica', 'B', 8.5)
                self.set_text_color(*self.ORANGE)
                self.cell(0, 6.5,
                    _s(f'  {i}. [{opt["impact"]}] {opt["titre"]}' +
                       (f' - Gain estime : {fr(opt["gain_estime"])} EUR'
                        if opt['gain_estime'] else '')),
                    fill=True, border='L', ln=True)
                self.set_draw_color(200, 200, 200)
                self.set_font('Helvetica', '', 8)
                self.set_text_color(*self.GRIS_FONCE)
                self.multi_cell(0, 5, _s(f'  {opt["detail"]}'))
                self.set_text_color(*self.VERT)
                self.set_font('Helvetica', '', 8)
                self.multi_cell(0, 5, _s(f'  Action : {opt["action"]}'))
                self.set_text_color(*self.NOIR)
                self.ln(2)

        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(*self.GRIS)
        self.ln(3)
        self.cell(0, 5,
            _s('Simulation indicative. Consultez un expert-comptable pour votre situation specifique.'),
            align='C', ln=True)

        return bytes(self.output())
