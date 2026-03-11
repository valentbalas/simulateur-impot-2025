"""
Générateur de rapport PDF fiscal professionnel — Revenus 2024
Brochure Pratique DGFiP 2025 · fpdf2
"""
from fpdf import FPDF
from datetime import datetime


class PDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(150, 150, 150)
            self.set_xy(10, 5)
            self.cell(150, 5, "Bilan Fiscal 2025 — Revenus 2024 · Barème officiel DGFiP")
            self.cell(40, 5, f"Page {self.page_no()}", align='R', ln=1)
            self.set_draw_color(200, 200, 200)
            self.set_line_width(0.2)
            self.line(10, 12, 200, 12)
            self.set_y(16)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-12)
            self.set_font('Helvetica', 'I', 7)
            self.set_text_color(180, 180, 180)
            self.cell(190, 5, "Pour information uniquement — Consultez impots.gouv.fr ou un expert-comptable",
                      align='C')


class GenererRapportPDF:
    BLEU   = (0, 49, 137)
    BLEU_M = (0, 82, 180)
    ROUGE  = (237, 41, 57)
    GRIS   = (245, 246, 250)
    NOIR   = (40, 40, 40)
    BLANC  = (255, 255, 255)
    VERT   = (46, 125, 50)
    ORANGE = (230, 119, 0)

    def generer(self, profil, resultat, conseils, comparaison=None) -> bytes:
        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()

        self._header(pdf, profil, resultat)
        self._section_synthese(pdf, resultat)
        self._section_calcul(pdf, resultat, profil)

        pdf.add_page()
        self._section_reductions(pdf, resultat)
        if comparaison:
            self._section_comparaison(pdf, comparaison, profil)
        if conseils:
            if not comparaison:
                pdf.add_page()
            else:
                pdf.ln(5)
                if pdf.get_y() > 200:
                    pdf.add_page()
            self._section_conseils(pdf, conseils)

        self._footer_legal(pdf)
        return bytes(pdf.output())

    def _header(self, pdf, profil, res):
        # Tricolore
        pdf.set_fill_color(*self.BLEU)
        pdf.rect(10, 10, 63, 22, 'F')
        pdf.set_fill_color(*self.BLANC)
        pdf.rect(73, 10, 63, 22, 'F')
        pdf.set_fill_color(*self.ROUGE)
        pdf.rect(136, 10, 64, 22, 'F')

        pdf.set_font('Helvetica', 'B', 15)
        pdf.set_text_color(*self.BLANC)
        pdf.set_xy(10, 13)
        pdf.cell(190, 8, "BILAN FISCAL 2025 — REVENUS 2024", align='C')
        pdf.set_font('Helvetica', '', 9)
        pdf.set_xy(10, 22)
        pdf.cell(190, 6, "Barème officiel DGFiP · Brochure Pratique 2025", align='C')

        pdf.set_y(37)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(*self.NOIR)
        pdf.cell(130, 5, f"Situation : {profil['situation']} · {profil['nb_enfants']} enfant(s) · {res['nb_parts']:.1f} parts")
        pdf.cell(60, 5, f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}", align='R', ln=1)
        pdf.set_draw_color(*self.BLEU_M)
        pdf.set_line_width(0.5)
        pdf.line(10, pdf.get_y() + 1, 200, pdf.get_y() + 1)
        pdf.ln(5)

    def _section_synthese(self, pdf, res):
        self._titre(pdf, "1. SYNTHÈSE FISCALE")
        metrics = [
            ("Revenu brut total", f"{res['revenu_total_brut']:,.0f} €", self.BLEU_M),
            ("Revenu net imposable", f"{res['revenu_imposable']:,.0f} €", self.BLEU),
            ("Impôt net à payer", f"{res['impot_net']:,.0f} €", self.ROUGE),
            ("Taux marginal (TMI)", f"{res['taux_marginal']}%", self.ORANGE),
        ]
        y = pdf.get_y()
        for i, (lab, val, col) in enumerate(metrics):
            x = 10 + i * 47
            pdf.set_fill_color(245, 247, 255)
            pdf.rect(x, y, 45, 20, 'F')
            pdf.set_draw_color(*col)
            pdf.set_line_width(0.8)
            pdf.line(x, y, x, y + 20)
            pdf.set_line_width(0.2)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(*col)
            pdf.set_xy(x + 1, y + 3)
            pdf.cell(43, 7, val, align='C')
            pdf.set_font('Helvetica', '', 7)
            pdf.set_text_color(100, 100, 100)
            pdf.set_xy(x + 1, y + 11)
            pdf.cell(43, 5, lab, align='C')
        pdf.set_y(y + 25)
        pdf.set_font('Helvetica', 'I', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(190, 5,
            f"Taux moyen : {res['taux_moyen']:.2f}%  ·  "
            f"Abattement appliqué : {res['abattement_applique']:,.0f} €  ·  "
            f"Décote : {res['decote']:,.0f} €  ·  Déduction PER : {res['deduction_per']:,.0f} €", ln=1)
        pdf.ln(3)

    def _section_calcul(self, pdf, res, profil):
        self._titre(pdf, "2. DÉTAIL DU CALCUL PAS À PAS")

        rows_rni = [
            ("Revenus bruts totaux", f"{res['revenu_total_brut']:,.0f} €", False),
            ("  Abattement salaires D1 (10% ou frais réels)", f"−{res['abattement_salaires_1']:,.0f} €", False),
            ("  Abattement pensions D1 (10%)", f"−{res['abattement_pensions_1']:,.0f} €", False),
            ("  Abattement salaires D2", f"−{res['abattement_salaires_2']:,.0f} €", False),
            ("  Abattement pensions D2", f"−{res['abattement_pensions_2']:,.0f} €", False),
            ("  Déduction versements PER", f"−{res['deduction_per']:,.0f} €", False),
            ("= REVENU NET IMPOSABLE (RNI)", f"{res['revenu_imposable']:,.0f} €", True),
        ]
        rows_imp = [
            (f"Quotient familial (RNI ÷ {res['nb_parts']:.1f} parts)", f"{res['quotient_familial']:,.0f} €", False),
            ("Impôt sur 1 part (barème 2024)", f"{res['impot_une_part']:,.0f} €", False),
            (f"× {res['nb_parts']:.1f} parts → avant plafonnement", f"{res['impot_avant_plafond']:,.0f} €", False),
            ("Plafonnement QF (1 791 €/½-part)", f"−{res['plafonnement_qf']:,.0f} €", False),
            ("= Impôt brut après QF", f"{res['impot_brut']:,.0f} €", True),
            ("Décote (constante − 45,25% × impôt)", f"−{res['decote']:,.0f} €", False),
            ("Réductions et crédits", f"−{res['reduction_dons_75']+res['reduction_dons_66']+res['credit_garde']+res['credit_emploi']:,.0f} €", False),
            ("= IMPÔT NET À PAYER", f"{res['impot_net']:,.0f} €", True),
        ]

        c1x, c2x = 10, 105
        y_start = pdf.get_y()
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_fill_color(*self.BLEU_M)
        pdf.set_text_color(*self.BLANC)
        pdf.set_xy(c1x, y_start); pdf.cell(93, 6, "  Revenu imposable", fill=True)
        pdf.set_xy(c2x, y_start); pdf.cell(95, 6, "  Calcul de l'impôt", fill=True, ln=1)

        max_rows = max(len(rows_rni), len(rows_imp))
        for j in range(max_rows):
            y = pdf.get_y()
            # RNI
            if j < len(rows_rni):
                label, val, bold = rows_rni[j]
                bg = self.BLEU if bold else (self.GRIS if j % 2 == 0 else self.BLANC)
                pdf.set_fill_color(*bg)
                pdf.set_text_color(*self.BLANC if bold else self.NOIR)
                pdf.set_font('Helvetica', 'B' if bold else '', 8)
                pdf.set_xy(c1x, y)
                pdf.cell(68, 5, f"  {label}", fill=True)
                pdf.cell(25, 5, val, fill=True, align='R')
            # Impôt
            if j < len(rows_imp):
                label, val, bold = rows_imp[j]
                bg = self.BLEU if bold else (self.GRIS if j % 2 == 0 else self.BLANC)
                pdf.set_fill_color(*bg)
                pdf.set_text_color(*self.BLANC if bold else self.NOIR)
                pdf.set_font('Helvetica', 'B' if bold else '', 8)
                pdf.set_xy(c2x, y)
                pdf.cell(70, 5, f"  {label}", fill=True)
                pdf.cell(25, 5, val, fill=True, align='R')
            pdf.ln(5)

        # Tranches
        pdf.ln(3)
        pdf.set_font('Helvetica', 'B', 9); pdf.set_text_color(*self.BLEU)
        pdf.cell(190, 5, "Détail par tranche d'imposition 2024 :", ln=1)

        pdf.set_fill_color(*self.BLEU_M); pdf.set_text_color(*self.BLANC)
        pdf.set_font('Helvetica', 'B', 8)
        for h, w in [("Tranche", 90), ("Base imposable", 40), ("Taux", 20), ("Impôt tranche", 35)]:
            pdf.cell(w, 5, f"  {h}", fill=True)
        pdf.ln()

        for j, t in enumerate(res['detail_tranches']):
            if t['base'] > 0:
                pdf.set_fill_color(*(self.GRIS if j%2==0 else self.BLANC))
                pdf.set_text_color(*self.NOIR)
                pdf.set_font('Helvetica', '', 8)
                pdf.cell(90, 5, f"  {t['label']}", fill=True)
                pdf.cell(40, 5, f"{t['base']:,.0f} €", fill=True, align='R')
                pdf.cell(20, 5, f"{t['taux']}%", fill=True, align='C')
                pdf.cell(35, 5, f"{t['impot_tranche']:,.0f} €", fill=True, align='R')
                pdf.ln()

    def _section_reductions(self, pdf, res):
        self._titre(pdf, "3. RÉDUCTIONS ET CRÉDITS D'IMPÔT")
        rows = [
            ("Réduction dons 75% (aide aux personnes en difficulté)", f"−{res['reduction_dons_75']:,.0f} €", False),
            ("Réduction dons 66% (associations d'utilité publique)", f"−{res['reduction_dons_66']:,.0f} €", False),
            ("Crédit d'impôt frais de garde (50%, plafond 3 500 €)", f"−{res['credit_garde']:,.0f} €", False),
            ("Crédit d'impôt emploi à domicile (50%, plafond 12 000 €)", f"−{res['credit_emploi']:,.0f} €", False),
            ("Décote (889/1470 − 45,25% × impôt brut)", f"−{res['decote']:,.0f} €", False),
            ("TOTAL avantages fiscaux obtenus",
             f"−{res['reduction_dons_75']+res['reduction_dons_66']+res['credit_garde']+res['credit_emploi']+res['decote']:,.0f} €", True),
        ]
        self._tableau2(pdf, ["Mécanisme fiscal", "Économie"], rows, [150, 35])
        pdf.ln(3)

    def _section_comparaison(self, pdf, comp, profil):
        self._titre(pdf, "4. COMPARAISON STRATÉGIQUE — ENFANT MAJEUR")
        pdf.set_font('Helvetica', 'I', 8); pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(190, 4,
            "Pension alimentaire 2024 — Plafond de déduction : 6 794 € par enfant (CGI art.156, Brochure DGFiP 2025).", ln=1)
        pdf.ln(2)

        sc_a, sc_b = comp['scenario_a'], comp['scenario_b']
        rows = [
            ("Parts fiscales du foyer", f"{sc_a['nb_parts']:.1f}", f"{sc_b['nb_parts']:.1f}", False),
            ("Impôt du foyer", f"{sc_a['impot_net']:,.0f} €", f"{sc_b['impot_net']:,.0f} €", False),
            ("Avantage spécifique", f"Réd. scolarité : −{sc_a['reduction_scolarite']:,.0f} €",
             f"Pension déduite : {sc_b['pension_deduite']:,.0f} €", False),
            ("COÛT FISCAL TOTAL", f"{sc_a['cout_total']:,.0f} €", f"{sc_b['cout_total']:,.0f} €", True),
        ]
        self._tableau3(pdf, ["Critère", "A — Rattachement", "B — Pension alim."],
                       rows, [75, 55, 55])

        pdf.ln(3)
        m, eco = comp['meilleur_scenario'], comp['economie']
        if m == 'A':
            verdict = f"RECOMMANDATION : Scénario A (Rattachement) — Économie : {eco:,.0f} €"
            col = self.BLEU_M
        else:
            verdict = f"RECOMMANDATION : Scénario B (Pension alimentaire) — Économie : {eco:,.0f} €"
            col = self.VERT
        pdf.set_fill_color(240, 245, 255); pdf.rect(10, pdf.get_y(), 190, 10, 'F')
        pdf.set_font('Helvetica', 'B', 9); pdf.set_text_color(*col)
        pdf.set_xy(12, pdf.get_y() + 2)
        pdf.cell(186, 6, f"✓ {verdict}")
        pdf.ln(14)

    def _section_conseils(self, pdf, conseils):
        self._titre(pdf, "5. CONSEILS D'OPTIMISATION FISCALE PERSONNALISÉS")
        pdf.set_font('Helvetica', 'I', 8); pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(190, 4,
            "Conseils générés automatiquement. Consultez un expert-comptable ou un conseiller fiscal "
            "pour valider leur applicabilité à votre situation personnelle.", ln=1)
        pdf.ln(3)
        for i, c in enumerate(conseils):
            if pdf.get_y() > 240:
                pdf.add_page()
            pdf.set_font('Helvetica', 'B', 9); pdf.set_text_color(*self.BLEU)
            pdf.cell(8, 6, f"{i+1}."); pdf.cell(182, 6, f"{c.get('icone','•')} {c['titre']}", ln=1)
            detail = c['detail'].replace('<strong>','').replace('</strong>','')
            pdf.set_font('Helvetica', '', 8); pdf.set_text_color(*self.NOIR)
            pdf.set_x(18); pdf.multi_cell(182, 4, detail, ln=1)
            pdf.ln(2)

    def _footer_legal(self, pdf):
        if pdf.get_y() > 245:
            pdf.add_page()
        pdf.ln(5)
        pdf.set_draw_color(*self.GRIS); pdf.set_line_width(0.3)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(3)
        pdf.set_font('Helvetica', 'I', 6.5); pdf.set_text_color(160, 160, 160)
        pdf.multi_cell(190, 3.5,
            "AVERTISSEMENT : Ce document est fourni à titre informatif uniquement. Il ne constitue pas un conseil "
            "fiscal ou juridique. Les calculs sont basés sur la Brochure Pratique DGFiP 2025 (Revenus 2024), "
            "Tableau 5, Aide-mémoire pp.52-59. Vérifiez votre situation sur impots.gouv.fr ou consultez "
            "un expert-comptable agréé.", ln=1)

    # ─── Helpers ────────────────────────────────────────────────────
    def _titre(self, pdf, txt):
        pdf.set_fill_color(*self.BLEU); pdf.set_text_color(*self.BLANC)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(190, 7, f"  {txt}", fill=True, ln=1); pdf.ln(2)

    def _tableau2(self, pdf, headers, rows, widths):
        pdf.set_fill_color(*self.BLEU_M); pdf.set_text_color(*self.BLANC)
        pdf.set_font('Helvetica', 'B', 8)
        for h, w in zip(headers, widths):
            pdf.cell(w, 6, f"  {h}", fill=True)
        pdf.ln()
        for j, (lab, val, bold) in enumerate(rows):
            bg = self.BLEU if bold else (self.GRIS if j%2==0 else self.BLANC)
            pdf.set_fill_color(*bg)
            pdf.set_text_color(*self.BLANC if bold else self.NOIR)
            pdf.set_font('Helvetica', 'B' if bold else '', 8)
            pdf.cell(widths[0], 5, f"  {lab}", fill=True)
            pdf.cell(widths[1], 5, val, fill=True, align='R')
            pdf.ln()

    def _tableau3(self, pdf, headers, rows, widths):
        pdf.set_fill_color(*self.BLEU_M); pdf.set_text_color(*self.BLANC)
        pdf.set_font('Helvetica', 'B', 8)
        for h, w in zip(headers, widths):
            pdf.cell(w, 6, f"  {h}", fill=True)
        pdf.ln()
        for j, (lab, va, vb, bold) in enumerate(rows):
            bg = self.BLEU if bold else (self.GRIS if j%2==0 else self.BLANC)
            pdf.set_fill_color(*bg)
            pdf.set_text_color(*self.BLANC if bold else self.NOIR)
            pdf.set_font('Helvetica', 'B' if bold else '', 8)
            pdf.cell(widths[0], 5, f"  {lab}", fill=True)
            pdf.cell(widths[1], 5, va, fill=True, align='C')
            pdf.cell(widths[2], 5, vb, fill=True, align='C')
            pdf.ln()
