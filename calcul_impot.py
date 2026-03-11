"""
Moteur de calcul de l'impôt sur le revenu français
Revenus 2024 — Brochure Pratique 2025 — Barème officiel DGFiP

TOUTES les constantes sont issues de la Brochure Pratique 2025 (revenus 2024).
Source : Direction Générale des Finances Publiques (DGFiP) — Tableau 5, Aide-mémoire

Corrections vs version précédente :
  ✓ Barème 2024 : 11 497 / 29 315 / 83 823 / 180 294 € (au lieu de 2023)
  ✓ Décote 2024 : formule 45,25% (889-0.4525×I et 1470-0.4525×I)
  ✓ Plafonnement QF : 1 791 €/demi-part (au lieu de 1 759 €)
  ✓ Abattement salaires : plancher 504 €, plafond 14 426 €
  ✓ Abattement pensions : plancher 450 €, plafond 4 399 €
  ✓ Pension alimentaire : plafond 6 794 € (au lieu de 6 855 €)
  ✓ PASS 2024 : 46 368 €
  ✓ Distinction salaires / pensions pour l'abattement
  ✓ Barème kilométrique 2024 complet (auto, moto, cyclomoteur, électrique)
  ✓ Module frais réels détaillé
"""


class FraisReels:
    """
    Calculateur de frais professionnels réels justifiés.
    Source : BOI-RSA-BASE-30-50-30, Brochure Pratique 2025 p.105-107
    """

    # ─── Barème kilométrique 2024 — Automobiles thermiques/hydrogène/hybrides ───
    # Format : {cv_max: (coef_<=5000km, (coef_5001-20000, constante), coef_>20000)}
    BAREME_AUTO_THERMIQUE = {
        3:  (0.529, (0.316, 1065),  0.370),
        4:  (0.606, (0.340, 1330),  0.407),
        5:  (0.636, (0.357, 1395),  0.427),
        6:  (0.665, (0.374, 1457),  0.447),
        7:  (0.697, (0.394, 1515),  0.470),  # 7 CV et plus
    }

    # ─── Barème kilométrique 2024 — Véhicules 100% électriques (+20% vs thermique) ───
    BAREME_AUTO_ELECTRIQUE = {
        3:  (0.635, (0.379, 1278),  0.444),
        4:  (0.727, (0.408, 1596),  0.488),
        5:  (0.763, (0.428, 1674),  0.512),
        6:  (0.798, (0.449, 1748),  0.536),
        7:  (0.836, (0.473, 1818),  0.564),
    }

    # ─── Barème motos 2024 — Thermiques ───
    BAREME_MOTO_THERMIQUE = {
        2:  (0.395, (0.099, 891),   0.248),
        5:  (0.468, (0.082, 1158),  0.275),
        99: (0.606, (0.079, 1583),  0.343),
    }

    # ─── Barème motos 2024 — Électriques ───
    BAREME_MOTO_ELECTRIQUE = {
        2:  (0.474, (0.119, 1069),  0.298),
        5:  (0.562, (0.098, 1390),  0.330),
        99: (0.727, (0.095, 1900),  0.412),
    }

    # ─── Cyclomoteurs (< 50 cm³) ───
    BAREME_CYCLO_THERMIQUE  = (0.315, (0.079, 711),  0.198)
    BAREME_CYCLO_ELECTRIQUE = (0.378, (0.095, 853),  0.238)

    # Frais de repas 2024
    REPAS_VALEUR_FOYER = 5.35   # Valeur d'un repas au foyer pour 2024 (MG)

    # Télétravail 2024 — allocation forfaitaire exonérée
    TELETRAVAIL_FORFAIT_JOUR = 2.70   # € par jour de télétravail
    TELETRAVAIL_MAX_MOIS     = 59.40  # € par mois (plafond)

    @staticmethod
    def calculer_bareme_km(km: float, cv: int, type_vehicule: str) -> float:
        """
        Calcule les frais kilométriques déductibles selon le barème officiel 2024.

        Paramètres :
        - km             : km professionnels annuels
        - cv             : puissance administrative du véhicule
        - type_vehicule  : "thermique" | "electrique" | "moto" | "moto_electrique" | "cyclo"
        """
        if type_vehicule in ("thermique", "electrique"):
            bareme = (FraisReels.BAREME_AUTO_ELECTRIQUE
                      if type_vehicule == "electrique"
                      else FraisReels.BAREME_AUTO_THERMIQUE)
            cv_cle = min([k for k in sorted(bareme.keys()) if k >= min(cv, 7)])
            c1, (c2, k), c3 = bareme[cv_cle]
            if km <= 5000:
                return km * c1
            elif km <= 20000:
                return km * c2 + k
            else:
                return km * c3

        elif type_vehicule in ("moto", "moto_electrique"):
            bareme = (FraisReels.BAREME_MOTO_ELECTRIQUE
                      if type_vehicule == "moto_electrique"
                      else FraisReels.BAREME_MOTO_THERMIQUE)
            cv_cle = min([k for k in sorted(bareme.keys()) if k >= min(cv, 99)])
            c1, (c2, k), c3 = bareme[cv_cle]
            if km <= 3000:
                return km * c1
            elif km <= 6000:
                return km * c2 + k
            else:
                return km * c3

        else:  # cyclomoteur
            c1, (c2, k), c3 = (FraisReels.BAREME_CYCLO_ELECTRIQUE
                                if "electrique" in type_vehicule
                                else FraisReels.BAREME_CYCLO_THERMIQUE)
            if km <= 3000:
                return km * c1
            elif km <= 6000:
                return km * c2 + k
            else:
                return km * c3

    @staticmethod
    def calculer_teletravail(nb_jours: int) -> float:
        """Frais de télétravail déductibles : 2,70 €/jour (max 59,40 €/mois)."""
        return min(nb_jours * FraisReels.TELETRAVAIL_FORFAIT_JOUR,
                   FraisReels.TELETRAVAIL_MAX_MOIS * 12)


class MoteurImpot:
    """
    Moteur principal de calcul de l'impôt sur le revenu 2024.
    Source : Brochure Pratique DGFiP 2025 (Revenus 2024).
    """

    # ─────────────────────────────────────────────────────────────────────
    # BARÈME PROGRESSIF 2024 — Tableau 5, Brochure Pratique 2025, p.361
    # Revalorisation de +1,8% par rapport au barème 2023 (LF 2025, art. 2)
    # ─────────────────────────────────────────────────────────────────────
    BAREME = [
        (11_497,        0.00),   # Tranche 0%  : jusqu'à 11 497 €
        (29_315,        0.11),   # Tranche 11% : 11 498 → 29 315 €
        (83_823,        0.30),   # Tranche 30% : 29 316 → 83 823 €
        (180_294,       0.41),   # Tranche 41% : 83 824 → 180 294 €
        (float('inf'), 0.45),   # Tranche 45% : > 180 294 €
    ]

    # ─────────────────────────────────────────────────────────────────────
    # ABATTEMENTS 10% — Aide-mémoire 2024, Brochure 2025 p.52
    # ─────────────────────────────────────────────────────────────────────
    ABATTEMENT_SALAIRES_MIN  = 504        # Plancher abattement salaires 2024
    ABATTEMENT_SALAIRES_MAX  = 14_426     # Plafond abattement salaires 2024

    ABATTEMENT_PENSIONS_MIN  = 450        # Plancher abattement pensions 2024
    ABATTEMENT_PENSIONS_MAX  = 4_399      # Plafond abattement pensions 2024

    # ─────────────────────────────────────────────────────────────────────
    # PLAFONNEMENT QUOTIENT FAMILIAL 2024 — Aide-mémoire p.52
    # ─────────────────────────────────────────────────────────────────────
    PLAFOND_DEMI_PART                  = 1_791   # € par demi-part supplémentaire
    PLAFOND_PREMIER_ENFANT_PARENT_SEUL = 4_224   # Cas des 2 premières ½-parts, parent seul
    PLAFOND_DEMI_PART_VIEUX_GARCON     = 1_069   # Demi-part « parent isolé sans enfant »

    # ─────────────────────────────────────────────────────────────────────
    # DÉCOTE 2024 — Brochure 2025 p.361 + note 70
    # Formule : Décote = Constante − 45,25 % × Impôt brut
    # ─────────────────────────────────────────────────────────────────────
    DECOTE_SEUIL_APP_CELIBATAIRE = 1_964   # Si impôt < 1 964 € → décote pour célibataire
    DECOTE_SEUIL_APP_COUPLE      = 3_249   # Si impôt < 3 249 € → décote pour couple
    DECOTE_FORMULE_CELIBATAIRE   = 889     # Constante formule célibataire
    DECOTE_FORMULE_COUPLE        = 1_470   # Constante formule couple

    # ─────────────────────────────────────────────────────────────────────
    # PER — Plan Épargne Retraite
    # PASS 2024 = 46 368 € → Plafond min PER = 10% PASS = 4 637 €
    # ─────────────────────────────────────────────────────────────────────
    PASS_2024       = 46_368
    PER_PLAFOND_MIN = 4_637

    # ─────────────────────────────────────────────────────────────────────
    # DONS — Aide-mémoire 2024, Brochure 2025 p.55-56
    # ─────────────────────────────────────────────────────────────────────
    DONS_75_PLAFOND        = 1_000   # Plafond base de calcul (75% — droit commun)
    DONS_75_MAYOTTE_PLAFOND = 2_000  # Dons Mayotte urgence (cyclone Chido, 14/12/24→17/05/25)
    DONS_66_PLAFOND_PCT    = 0.20    # 20% du revenu imposable

    # ─────────────────────────────────────────────────────────────────────
    # CRÉDITS D'IMPÔT — Aide-mémoire 2024, Brochure 2025 p.59
    # ─────────────────────────────────────────────────────────────────────
    GARDE_PLAFOND          = 3_500   # Plafond par enfant (< 6 ans)
    GARDE_TAUX             = 0.50    # 50%

    EMPLOI_DOMICILE_BASE   = 12_000  # Plafond de base
    EMPLOI_DOMICILE_1ERE_ANNEE = 15_000  # Première année d'emploi direct
    EMPLOI_DOMICILE_MAJORATION = 1_500   # +1 500 € / enfant à charge
    EMPLOI_DOMICILE_MAX    = 15_000  # Plafond après majorations
    EMPLOI_DOMICILE_TAUX   = 0.50    # 50%

    # ─────────────────────────────────────────────────────────────────────
    # FRAIS DE SCOLARITÉ (enfant rattaché) — Aide-mémoire p.56
    # ─────────────────────────────────────────────────────────────────────
    SCOLARITE = {
        'Collège':                                    61,
        'Lycée / BTS / Classe prépa':                153,
        'Enseignement supérieur (Université, IUT…)': 183,
    }

    # ─────────────────────────────────────────────────────────────────────
    # PENSION ALIMENTAIRE ENFANT MAJEUR — CGI art.156, Brochure 2025 p.42303
    # ─────────────────────────────────────────────────────────────────────
    PENSION_ALIMENTAIRE_MAX = 6_794   # Plafond de déduction par enfant (2024)

    SEUIL_RECOUVREMENT = 61   # Impôt < 61 € → non mis en recouvrement

    # ─────────────────────────────────────────────────────────────────────

    def _nb_parts(self, situation, nb_enfants, invalide, parent_isole=False):
        """
        Nombre de parts fiscales — CGI art. 194.

        Parts de base :
          - Célibataire / Divorcé(e) / Séparé(e)  : 1 part
          - Marié(e) / Pacsé(e)                   : 2 parts
          - Veuf(ve) avec enfant à charge          : 2 parts (maintien conjugal)

        Parts supplémentaires pour enfants :
          1er et 2e enfant  : + 0,5 part chacun
          3e et suivants    : + 1 part chacun

        Parent isolé (case T) :
          1er enfant donne 1 part (au lieu de 0,5) → régime de plafonnement spécial

        Invalidité : +0,5 part par personne invalide dans le foyer
        """
        parts = (2.0 if situation in ("Marié(e) / Pacsé(e)",)
                 else (2.0 if situation == "Veuf(ve)" and nb_enfants > 0
                       else 1.0))

        if nb_enfants > 0:
            if parent_isole:
                parts += 1.0   # 1er enfant = 1 part entière
                if nb_enfants >= 2: parts += 0.5
                if nb_enfants >= 3: parts += (nb_enfants - 2) * 1.0
            else:
                if nb_enfants <= 2:
                    parts += nb_enfants * 0.5
                else:
                    parts += 1.0 + (nb_enfants - 2) * 1.0

        if invalide:
            parts += 0.5

        return parts

    def _appliquer_bareme(self, quotient: float):
        """Barème progressif tranche par tranche sur le quotient (RNI ÷ N)."""
        labels = [
            "Tranche 0%  (≤ 11 497 €)",
            "Tranche 11% (11 498 – 29 315 €)",
            "Tranche 30% (29 316 – 83 823 €)",
            "Tranche 41% (83 824 – 180 294 €)",
            "Tranche 45% (> 180 294 €)",
        ]
        impot, tmi, tranches = 0.0, 0, []
        borne_prec = 0

        for i, (limite, taux) in enumerate(self.BAREME):
            base = max(0.0, min(quotient, limite) - borne_prec)
            impot_t = base * taux
            tranches.append({'label': labels[i], 'taux': int(taux*100),
                              'base': base, 'impot_tranche': round(impot_t, 2)})
            if base > 0 and taux > 0:
                tmi = int(taux * 100)
            impot += impot_t
            borne_prec = limite
            if min(quotient, limite) >= quotient:
                break

        return impot, tmi, tranches

    def _abattement(self, revenu, type_rev, frais_reels=False, montant_fr=0):
        """
        Abattement 10% ou frais réels.
        type_rev : 'salaire' | 'pension'
        """
        if frais_reels and montant_fr > 0:
            return montant_fr
        a = revenu * 0.10
        if type_rev == 'pension':
            return max(self.ABATTEMENT_PENSIONS_MIN,
                       min(a, self.ABATTEMENT_PENSIONS_MAX))
        return max(self.ABATTEMENT_SALAIRES_MIN,
                   min(a, self.ABATTEMENT_SALAIRES_MAX))

    def _decote(self, impot_brut, situation):
        """
        Décote 2024 — formule officielle note 70, Brochure 2025.
        Décote = Constante − 45,25 % × Impôt brut
        (si impôt brut < seuil d'application)
        """
        if situation == "Marié(e) / Pacsé(e)":
            seuil, constante = self.DECOTE_SEUIL_APP_COUPLE, self.DECOTE_FORMULE_COUPLE
        else:
            seuil, constante = self.DECOTE_SEUIL_APP_CELIBATAIRE, self.DECOTE_FORMULE_CELIBATAIRE
        if impot_brut < seuil:
            return max(0.0, min(constante - 0.4525 * impot_brut, impot_brut))
        return 0.0

    def _plafond_per(self, rni):
        """Plafond PER 2024 = max(10% PASS, 10% revenus). Min = 4 637 €."""
        return max(self.PER_PLAFOND_MIN, min(rni * 0.10, 8 * self.PASS_2024 * 0.10))

    def _impot_plafonner_qf(self, rni, nb_parts, situation, parent_isole=False):
        """
        Calcule l'impôt brut après plafonnement du quotient familial.
        Retourne (impôt_brut, plafonnement_appliqué, économie_qf).
        """
        quotient = rni / nb_parts if nb_parts > 0 else 0
        imp_1part, tmi, tranches = self._appliquer_bareme(quotient)
        imp_avant_plafond = imp_1part * nb_parts

        parts_base = 2.0 if situation == "Marié(e) / Pacsé(e)" else 1.0
        if situation == "Veuf(ve)":
            parts_base = 2.0  # maintien du quotient conjugal si enfant

        demi_parts_supp = (nb_parts - parts_base) * 2
        plafonnement = 0.0
        impot_brut = imp_avant_plafond

        if demi_parts_supp > 0:
            q_base = rni / parts_base
            imp_base, _, _ = self._appliquer_bareme(q_base)
            imp_sans_qf = imp_base * parts_base
            avantage = imp_sans_qf - imp_avant_plafond
            avantage_max = demi_parts_supp * self.PLAFOND_DEMI_PART

            if avantage > avantage_max:
                plafonnement = avantage - avantage_max
                impot_brut = imp_sans_qf - avantage_max
            else:
                impot_brut = imp_avant_plafond

        economie_qf = 0.0
        if demi_parts_supp > 0:
            q_base = rni / parts_base
            imp_base, _, _ = self._appliquer_bareme(q_base)
            economie_qf = max(0.0, imp_base * parts_base - impot_brut)

        return impot_brut, plafonnement, economie_qf, tmi, tranches, imp_avant_plafond, imp_1part

    def calculer(self, profil: dict) -> dict:
        """
        Calcule l'impôt sur le revenu 2024 pour un profil fiscal donné.

        Le profil peut contenir :
          revenu_salaire_declarant, revenu_pension_declarant  (déclarant 1)
          revenu_salaire_conjoint,  revenu_pension_conjoint   (déclarant 2)
          frais_reels / montant_frais_reels_1                 (frais réels déclarant 1)
          frais_reels_2 / montant_frais_reels_2               (frais réels déclarant 2)
          versement_per, dons_60_75, dons_60, dons_mayotte
          frais_garde, nb_enfants_moins_6
          emploi_domicile, premiere_annee_emploi
        """
        sit = profil['situation']
        nb_enf = profil['nb_enfants']
        inv = profil['invalide_declarant']
        pi  = profil.get('parent_isole', False)

        # Revenus bruts
        sal1 = profil.get('revenu_salaire_declarant', 0)
        pen1 = profil.get('revenu_pension_declarant', 0)
        sal2 = profil.get('revenu_salaire_conjoint', 0)
        pen2 = profil.get('revenu_pension_conjoint', 0)
        total_brut = sal1 + pen1 + sal2 + pen2

        # Abattements
        fr1 = profil.get('frais_reels', False)
        mfr1 = profil.get('montant_frais_reels_1', 0)
        fr2 = profil.get('frais_reels_2', False)
        mfr2 = profil.get('montant_frais_reels_2', 0)

        ab_sal1 = self._abattement(sal1, 'salaire', fr1, mfr1)
        ab_pen1 = self._abattement(pen1, 'pension')
        ab_sal2 = self._abattement(sal2, 'salaire', fr2, mfr2)
        ab_pen2 = self._abattement(pen2, 'pension')
        abatt_total = ab_sal1 + ab_pen1 + ab_sal2 + ab_pen2

        rev_ap_abatt = total_brut - abatt_total

        # PER
        per = profil.get('versement_per', 0)
        plaf_per = self._plafond_per(rev_ap_abatt)
        ded_per = min(per, plaf_per)
        rni = max(0.0, rev_ap_abatt - ded_per)

        # Quotient familial + barème
        nb_parts = self._nb_parts(sit, nb_enf, inv, pi)
        (impot_brut, plafonnement_qf, economie_qf,
         tmi, tranches, imp_avant_plafond, imp_1part) = self._impot_plafonner_qf(rni, nb_parts, sit, pi)

        # Décote
        decote = self._decote(impot_brut, sit)
        imp_ap_decote = impot_brut - decote

        # Réductions
        dons_75 = profil.get('dons_60_75', 0)
        dons_mayo = profil.get('dons_mayotte', 0)
        dons_66_m = profil.get('dons_60', 0)
        red_75 = min(dons_75, self.DONS_75_PLAFOND) * 0.75
        red_mayo = min(dons_mayo, self.DONS_75_MAYOTTE_PLAFOND) * 0.75
        red_75_total = red_75 + red_mayo
        red_66 = min(dons_66_m, rni * self.DONS_66_PLAFOND_PCT) * 0.66

        # Crédits
        nbenf6 = profil.get('nb_enfants_moins_6', 0)
        garde = profil.get('frais_garde', 0)
        plaf_garde = self.GARDE_PLAFOND * max(nbenf6, 1) if nbenf6 > 0 else self.GARDE_PLAFOND
        credit_garde = min(garde, plaf_garde) * self.GARDE_TAUX

        emploi = profil.get('emploi_domicile', 0)
        is_1ere = profil.get('premiere_annee_emploi', False)
        plaf_emp = self.EMPLOI_DOMICILE_1ERE_ANNEE if is_1ere else self.EMPLOI_DOMICILE_BASE
        plaf_emp += nb_enf * self.EMPLOI_DOMICILE_MAJORATION
        plaf_emp = min(plaf_emp, 18_000 if is_1ere else self.EMPLOI_DOMICILE_MAX)
        credit_emploi = min(emploi, plaf_emp) * self.EMPLOI_DOMICILE_TAUX

        # Impôt net
        impot_avant_seuil = max(0.0, imp_ap_decote - red_75_total - red_66
                                 - credit_garde - credit_emploi)
        impot_net = 0.0 if impot_avant_seuil < self.SEUIL_RECOUVREMENT else round(impot_avant_seuil)

        economie_per = ded_per * (tmi / 100) if tmi > 0 else 0.0
        taux_moyen = (impot_net / total_brut * 100) if total_brut > 0 else 0.0

        return {
            'revenu_total_brut':      total_brut,
            'abattement_salaires_1':  ab_sal1,
            'abattement_pensions_1':  ab_pen1,
            'abattement_salaires_2':  ab_sal2,
            'abattement_pensions_2':  ab_pen2,
            'abattement_applique':    abatt_total,
            'deduction_per':          ded_per,
            'plafond_per':            plaf_per,
            'revenu_imposable':       rni,
            'nb_parts':               nb_parts,
            'quotient_familial':      rni / nb_parts if nb_parts else 0,
            'impot_une_part':         imp_1part,
            'impot_avant_plafond':    imp_avant_plafond,
            'plafonnement_qf':        plafonnement_qf,
            'economie_qf':            economie_qf,
            'impot_brut':             round(impot_brut),
            'decote':                 round(decote, 2),
            'taux_marginal':          tmi,
            'taux_moyen':             round(taux_moyen, 2),
            'reduction_dons_75':      round(red_75_total, 2),
            'reduction_dons_66':      round(red_66, 2),
            'credit_garde':           round(credit_garde, 2),
            'credit_emploi':          round(credit_emploi, 2),
            'economie_per':           round(economie_per, 2),
            'impot_net':              impot_net,
            'detail_tranches':        tranches,
        }

    def generer_conseils(self, profil: dict, resultat: dict) -> list:
        """Conseils d'optimisation fiscale personnalisés."""
        conseils = []
        tmi = resultat['taux_marginal']
        rni = resultat['revenu_imposable']
        inet = resultat['impot_net']
        ibrut = resultat['impot_brut']

        # PER
        reste_per = resultat['plafond_per'] - profil.get('versement_per', 0)
        if reste_per > 100 and tmi >= 30:
            eco = reste_per * tmi / 100
            conseils.append({'icone': '💰',
                'titre': f'PER — Économie potentielle : {eco:,.0f} € (TMI {tmi}%)',
                'detail': (f'Capacité PER restante : <strong>{reste_per:,.0f} €</strong>. '
                           f'À votre taux marginal de {tmi}%, ce versement réduirait votre '
                           f'impôt de <strong>{eco:,.0f} €</strong> tout en préparant votre retraite. '
                           f'Plafond annuel disponible : {resultat["plafond_per"]:,.0f} €.')})

        # Frais réels
        sal_total = (profil.get('revenu_salaire_declarant', 0) +
                     profil.get('revenu_salaire_conjoint', 0))
        if not profil.get('frais_reels', False) and sal_total > 0:
            forfait = resultat['abattement_salaires_1'] + resultat['abattement_salaires_2']
            conseils.append({'icone': '📋',
                'titre': 'Frais réels : comparez avec votre forfait actuel',
                'detail': (f'Votre abattement forfaitaire salaires actuel est de {forfait:,.0f} €. '
                           f'Si vos frais réels (déplacements, repas, formation, télétravail, '
                           f'matériel…) dépassent ce montant, optez pour les frais réels. '
                           f'Utilisez le calculateur kilométrique intégré dans la barre latérale.')})

        # Dons
        if profil.get('dons_60', 0) == 0 and inet > 0:
            plaf_d = rni * self.DONS_66_PLAFOND_PCT
            if plaf_d > 200:
                conseils.append({'icone': '❤️',
                    'titre': 'Dons associations — Réduction 66%',
                    'detail': (f'Pour 100 € donnés à une association d\'utilité publique, '
                               f'votre impôt baisse de 66 €. Plafond max : {plaf_d:,.0f} € '
                               f'(réduction max : {plaf_d*0.66:,.0f} €).')})

        # Emploi à domicile
        if profil.get('emploi_domicile', 0) == 0:
            conseils.append({'icone': '🏠',
                'titre': 'Emploi à domicile — Crédit 50%',
                'detail': ('Ménage, jardinage, garde d\'enfants, soutien scolaire, assistante '
                            'de vie… 50% des sommes versées en crédit d\'impôt (plafond : '
                            '12 000 € de dépenses, soit 6 000 € de crédit max).')})

        # Tranche
        if tmi == 30 and inet > 0:
            surplus = resultat['quotient_familial'] - 29_315
            if 0 < surplus < 8_000:
                eco_possible = surplus * resultat['nb_parts']
                conseils.append({'icone': '📉',
                    'titre': f'Passer en tranche 11% — Économie possible : {eco_possible*0.19:,.0f} €',
                    'detail': (f'Vous êtes à {surplus:,.0f} € au-dessus de la limite de la tranche '
                               f'à 11%. Un versement PER de {eco_possible:,.0f} € '
                               f'vous ferait entièrement redescendre en tranche à 11%.')})

        # Décote
        seuil_d = (self.DECOTE_SEUIL_APP_COUPLE if profil['situation'] == "Marié(e) / Pacsé(e)"
                   else self.DECOTE_SEUIL_APP_CELIBATAIRE)
        if resultat['decote'] == 0 and 0 < ibrut < seuil_d * 1.4:
            conseils.append({'icone': '📊',
                'titre': 'Proche du seuil de décote',
                'detail': (f'Votre impôt brut ({ibrut:,.0f} €) dépasse légèrement le seuil '
                           f'de décote ({seuil_d:,.0f} €). Un versement PER ou un don pourrait '
                           f'faire baisser votre impôt sous ce seuil et déclencher la décote.')})

        return conseils


class ScenarioEnfantMajeur:
    """
    Comparaison rattachement vs pension alimentaire — Brochure 2025 p.81+103.
    Plafond pension 2024 : 6 794 €
    """

    def __init__(self, moteur: MoteurImpot):
        self.moteur = moteur

    def comparer(self, profil: dict, enfant_data: dict) -> dict:
        m = self.moteur

        # ─── SCÉNARIO A : Rattachement ───
        pa = profil.copy()
        pa['nb_enfants'] = profil['nb_enfants'] + 1
        ra = m.calculer(pa)
        niveau = enfant_data.get('niveau_etude', 'Enseignement supérieur (Université, IUT…)')
        red_scol = m.SCOLARITE.get(niveau, 183)
        impot_a = max(0, ra['impot_net'] - red_scol)

        # ─── SCÉNARIO B : Pension alimentaire ───
        pension = min(enfant_data.get('pension_versee', m.PENSION_ALIMENTAIRE_MAX),
                      m.PENSION_ALIMENTAIRE_MAX)

        sal1 = profil.get('revenu_salaire_declarant', 0)
        pen1 = profil.get('revenu_pension_declarant', 0)
        sal2 = profil.get('revenu_salaire_conjoint', 0)
        pen2 = profil.get('revenu_pension_conjoint', 0)
        total_b = sal1 + pen1 + sal2 + pen2

        fr1 = profil.get('frais_reels', False)
        mfr1 = profil.get('montant_frais_reels_1', 0)
        fr2 = profil.get('frais_reels_2', False)
        mfr2 = profil.get('montant_frais_reels_2', 0)

        ab = (m._abattement(sal1,'salaire',fr1,mfr1) + m._abattement(pen1,'pension')
              + m._abattement(sal2,'salaire',fr2,mfr2) + m._abattement(pen2,'pension'))

        rev_ap_ab = total_b - ab
        ded_per = min(profil.get('versement_per', 0), m._plafond_per(rev_ap_ab))
        rni_b = max(0.0, rev_ap_ab - ded_per - pension)  # déduction pension du revenu global

        nb_parts_b = m._nb_parts(profil['situation'], profil['nb_enfants'],
                                  profil['invalide_declarant'], profil.get('parent_isole', False))

        (ibrut_b, _, _, tmi_b, _, _, imp1_b) = m._impot_plafonner_qf(rni_b, nb_parts_b, profil['situation'])
        decote_b = m._decote(ibrut_b, profil['situation'])

        red_75_b  = min(profil.get('dons_60_75', 0), m.DONS_75_PLAFOND) * 0.75
        red_66_b  = min(profil.get('dons_60', 0), rni_b * m.DONS_66_PLAFOND_PCT) * 0.66
        c_garde_b = min(profil.get('frais_garde', 0), m.GARDE_PLAFOND) * m.GARDE_TAUX
        plaf_e_b  = min(m.EMPLOI_DOMICILE_BASE + profil['nb_enfants'] * m.EMPLOI_DOMICILE_MAJORATION,
                         m.EMPLOI_DOMICILE_MAX)
        c_emp_b   = min(profil.get('emploi_domicile', 0), plaf_e_b) * m.EMPLOI_DOMICILE_TAUX

        inet_b_raw = max(0.0, ibrut_b - decote_b - red_75_b - red_66_b - c_garde_b - c_emp_b)
        inet_b = 0.0 if inet_b_raw < m.SEUIL_RECOUVREMENT else round(inet_b_raw)
        cout_b = inet_b + pension

        meilleur = 'A' if impot_a <= cout_b else 'B'
        economie = abs(cout_b - impot_a)

        return {
            'scenario_a': {
                'nb_parts': ra['nb_parts'], 'impot_net': impot_a,
                'reduction_scolarite': red_scol, 'cout_total': impot_a,
            },
            'scenario_b': {
                'nb_parts': nb_parts_b, 'pension_deduite': pension,
                'impot_net': inet_b, 'cout_total': cout_b,
            },
            'meilleur_scenario': meilleur,
            'economie': economie,
        }
