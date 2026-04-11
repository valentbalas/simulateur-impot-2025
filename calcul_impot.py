"""
Moteur IR 2024 — Brochure Pratique DGFiP 2025
Exoneration emploi etudiant (art. 81 bis CGI) : 3 x SMIC mensuel = 5 301 EUR
Heures supplementaires (art. 81 quater CGI) : plafond 7 500 EUR
"""


class FraisReels:
    BAREME_AUTO_THERMIQUE = {
        3: (0.529, (0.316, 1065), 0.370),
        4: (0.606, (0.340, 1330), 0.407),
        5: (0.636, (0.357, 1395), 0.427),
        6: (0.665, (0.374, 1457), 0.447),
        7: (0.697, (0.394, 1515), 0.470),
    }
    BAREME_AUTO_ELECTRIQUE = {
        3: (0.635, (0.379, 1278), 0.444),
        4: (0.727, (0.408, 1596), 0.488),
        5: (0.763, (0.428, 1674), 0.512),
        6: (0.798, (0.449, 1748), 0.536),
        7: (0.836, (0.473, 1818), 0.564),
    }
    BAREME_MOTO_THERMIQUE = {
        2:  (0.395, (0.099, 891),  0.248),
        5:  (0.468, (0.082, 1158), 0.275),
        99: (0.606, (0.079, 1583), 0.343),
    }
    BAREME_MOTO_ELECTRIQUE = {
        2:  (0.474, (0.119, 1069), 0.298),
        5:  (0.562, (0.098, 1390), 0.330),
        99: (0.727, (0.095, 1900), 0.412),
    }
    BAREME_CYCLO      = (0.315, (0.079, 711),  0.198)
    BAREME_CYCLO_ELEC = (0.378, (0.095, 853),  0.238)

    REPAS_VALEUR_FOYER       = 5.35
    TELETRAVAIL_FORFAIT_JOUR = 2.70
    TELETRAVAIL_MAX_MOIS     = 59.40

    @staticmethod
    def calculer_bareme_km(km, cv, type_vehicule):
        if type_vehicule in ("thermique", "electrique"):
            b = (FraisReels.BAREME_AUTO_ELECTRIQUE if type_vehicule == "electrique"
                 else FraisReels.BAREME_AUTO_THERMIQUE)
            ck = min(k for k in sorted(b) if k >= min(cv, 7))
            c1, (c2, k), c3 = b[ck]
            return km * c1 if km <= 5000 else (km * c2 + k if km <= 20000 else km * c3)
        elif type_vehicule in ("moto", "moto_electrique"):
            b = (FraisReels.BAREME_MOTO_ELECTRIQUE if type_vehicule == "moto_electrique"
                 else FraisReels.BAREME_MOTO_THERMIQUE)
            ck = min(k for k in sorted(b) if k >= min(cv, 99))
            c1, (c2, k), c3 = b[ck]
            return km * c1 if km <= 3000 else (km * c2 + k if km <= 6000 else km * c3)
        else:
            c1, (c2, k), c3 = (FraisReels.BAREME_CYCLO_ELEC
                                if "electrique" in type_vehicule else FraisReels.BAREME_CYCLO)
            return km * c1 if km <= 3000 else (km * c2 + k if km <= 6000 else km * c3)

    @staticmethod
    def calculer_teletravail(nb_jours):
        return min(nb_jours * FraisReels.TELETRAVAIL_FORFAIT_JOUR,
                   FraisReels.TELETRAVAIL_MAX_MOIS * 12)


class MoteurImpot:
    """Calcul IR 2025 complet — Brochure DGFiP 2026"""

    BAREME = [
        (11_600,       0.00),
        (29_579,       0.11),
        (84_577,       0.30),
        (181_917,      0.41),
        (float('inf'), 0.45),
    ]

    ABATTEMENT_SALAIRES_MIN  = 509
    ABATTEMENT_SALAIRES_MAX  = 14_555
    ABATTEMENT_PENSIONS_MIN  = 454
    ABATTEMENT_PENSIONS_MAX  = 4_439

    PLAFOND_DEMI_PART        = 1_807

    DECOTE_SEUIL_CEL = 1_982
    DECOTE_SEUIL_CPL = 3_277
    DECOTE_CST_CEL   = 897
    DECOTE_CST_CPL   = 1_483

    PASS_2025        = 47_100
    PER_PLAFOND_MIN  = 4_637

    DONS_75_PLAFOND         = 1_000
    DONS_75_MAYOTTE_PLAFOND = 2_000
    DONS_66_PLAFOND_PCT     = 0.20

    GARDE_PLAFOND  = 3_500
    GARDE_TAUX     = 0.50
    EMPLOI_BASE    = 12_000
    EMPLOI_1ERE    = 15_000
    EMPLOI_MAJ     = 1_500
    EMPLOI_MAX     = 15_000
    EMPLOI_TAUX    = 0.50

    SYNDICAT_PCT   = 0.01
    SYNDICAT_TAUX  = 0.66

    # Heures supplementaires (art. 81 quater CGI)
    HEURES_SUP_PLAFOND = 7_500

    # Emploi etudiant < 26 ans (art. 81 bis CGI) : 3 x SMIC mensuel brut 2024
    JOBS_ETUDIANTS_EXONERATION = 5_406

    SCOLARITE = {
        'College':              61,
        'Lycee / BTS / Prepa': 153,
        'Superieur (Univ, IUT, Grande Ecole)': 183,
    }

    PENSION_MAX        = 6_855
    SEUIL_RECOUVREMENT = 61

    def _nb_parts(self, sit, nb_enf, inv, pi=False):
        if sit in ("Marie(e) / Pacse(e)",):
            parts = 2.0
        elif sit == "Veuf(ve)" and nb_enf > 0:
            parts = 2.0
        else:
            parts = 1.0
        if nb_enf > 0:
            if pi:
                parts += 1.0
                if nb_enf >= 2: parts += 0.5
                if nb_enf >= 3: parts += (nb_enf - 2) * 1.0
            else:
                parts += nb_enf * 0.5 if nb_enf <= 2 else 1.0 + (nb_enf - 2) * 1.0
        if inv:
            parts += 0.5
        return parts

    def _appliquer_bareme(self, q):
        labels = [
            "Tranche 0 % (<= 11 497 EUR)",
            "Tranche 11 % (11 498 - 29 315 EUR)",
            "Tranche 30 % (29 316 - 83 823 EUR)",
            "Tranche 41 % (83 824 - 180 294 EUR)",
            "Tranche 45 % (> 180 294 EUR)",
        ]
        impot, tmi, tranches, borne = 0.0, 0, [], 0
        for i, (lim, taux) in enumerate(self.BAREME):
            base = max(0.0, min(q, lim) - borne)
            it = base * taux
            tranches.append({'label': labels[i], 'taux': int(taux*100),
                             'base': base, 'impot_tranche': round(it, 2)})
            if base > 0 and taux > 0:
                tmi = int(taux * 100)
            impot += it
            borne = lim
            if min(q, lim) >= q:
                break
        return impot, tmi, tranches

    def _abattement(self, revenu, type_rev, frais_reels=False, montant_fr=0):
        if frais_reels and montant_fr > 0:
            return montant_fr
        a = revenu * 0.10
        if type_rev == 'pension':
            return max(self.ABATTEMENT_PENSIONS_MIN, min(a, self.ABATTEMENT_PENSIONS_MAX))
        return max(self.ABATTEMENT_SALAIRES_MIN, min(a, self.ABATTEMENT_SALAIRES_MAX))

    def _decote(self, ibrut, sit):
        if sit == "Marie(e) / Pacse(e)":
            seuil, cst = self.DECOTE_SEUIL_CPL, self.DECOTE_CST_CPL
        else:
            seuil, cst = self.DECOTE_SEUIL_CEL, self.DECOTE_CST_CEL
        if ibrut < seuil:
            return max(0.0, min(cst - 0.4525 * ibrut, ibrut))
        return 0.0

    def _impot_qf(self, rni, nb_parts, sit):
        q = rni / nb_parts if nb_parts > 0 else 0
        imp1, tmi, tranches = self._appliquer_bareme(q)
        imp_av = imp1 * nb_parts
        parts_base = 2.0 if sit in ("Marie(e) / Pacse(e)", "Veuf(ve)") else 1.0
        if sit == "Veuf(ve)" and nb_parts < 2.0:
            parts_base = 1.0
        dsp = (nb_parts - parts_base) * 2
        ibrut, plaf_qf = imp_av, 0.0
        if dsp > 0:
            q_base = rni / parts_base
            i_base, _, _ = self._appliquer_bareme(q_base)
            i_sans = i_base * parts_base
            avantage = i_sans - imp_av
            avantage_max = dsp * self.PLAFOND_DEMI_PART
            if avantage > avantage_max:
                plaf_qf = avantage - avantage_max
                ibrut = i_sans - avantage_max
        eco_qf = 0.0
        if dsp > 0:
            i2, _, _ = self._appliquer_bareme(rni / parts_base)
            eco_qf = max(0.0, i2 * parts_base - ibrut)
        return ibrut, plaf_qf, eco_qf, tmi, tranches, imp_av, imp1

    def calculer(self, p: dict) -> dict:
        sit    = p.get('situation', 'Celibataire / Divorce(e)')
        nb_enf = p.get('nb_enfants', 0)
        inv    = p.get('invalide_declarant', False)
        pi     = p.get('parent_isole', False)

        sal1 = p.get('revenu_salaire_declarant', 0)
        pen1 = p.get('revenu_pension_declarant', 0)
        sal2 = p.get('revenu_salaire_conjoint',  0)
        pen2 = p.get('revenu_pension_conjoint',  0)

        # Declarants 3+ : enfants majeurs rattaches (liste de dicts)
        enfants_rattaches = p.get('enfants_rattaches', [])
        nb_enf_rat = len(enfants_rattaches)
        sal_rat = sum(e.get('salaire', 0) for e in enfants_rattaches)
        pen_rat = sum(e.get('pension', 0) for e in enfants_rattaches)
        hs_rat  = sum(min(e.get('heures_sup', 0), self.HEURES_SUP_PLAFOND)
                      for e in enfants_rattaches)
        exo_rat = sum(min(e.get('exoneration_etudiant', 0), self.JOBS_ETUDIANTS_EXONERATION)
                      for e in enfants_rattaches)

        hs1      = min(p.get('heures_sup_declarant', 0), self.HEURES_SUP_PLAFOND)
        hs2      = min(p.get('heures_sup_conjoint',  0), self.HEURES_SUP_PLAFOND)
        exo_etud = min(p.get('exoneration_emploi_etudiant', 0), self.JOBS_ETUDIANTS_EXONERATION)

        sal1_imp    = max(0, sal1 - hs1 - exo_etud)
        sal2_imp    = max(0, sal2 - hs2)
        sal_rat_imp = max(0, sal_rat - hs_rat - exo_rat)
        total_brut  = sal1 + pen1 + sal2 + pen2 + sal_rat + pen_rat

        fr1  = p.get('frais_reels', False)
        mfr1 = p.get('montant_frais_reels_1', 0)
        fr2  = p.get('frais_reels_2', False)
        mfr2 = p.get('montant_frais_reels_2', 0)

        ab_sal1 = self._abattement(sal1_imp, 'salaire', fr1, mfr1)
        ab_pen1 = self._abattement(pen1, 'pension')
        ab_sal2 = self._abattement(sal2_imp, 'salaire', fr2, mfr2)
        ab_pen2 = self._abattement(pen2, 'pension')
        ab_rat  = sum(self._abattement(
            max(0, e.get('salaire',0)
                - min(e.get('heures_sup',0), self.HEURES_SUP_PLAFOND)
                - min(e.get('exoneration_etudiant',0), self.JOBS_ETUDIANTS_EXONERATION)),
            'salaire', e.get('frais_reels', False), e.get('montant_fr', 0)
        ) + self._abattement(e.get('pension',0), 'pension')
                  for e in enfants_rattaches)
        abatt   = ab_sal1 + ab_pen1 + ab_sal2 + ab_pen2 + ab_rat

        rev_ap = (sal1_imp + pen1 + sal2_imp + pen2 + sal_rat_imp + pen_rat) - abatt

        per      = p.get('versement_per', 0)
        plaf_per = max(self.PER_PLAFOND_MIN,
                       min(rev_ap * 0.10, 8 * self.PASS_2025 * 0.10))
        ded_per  = min(per, plaf_per)

        pen_vers = min(p.get('pension_alimentaire_versee', 0), self.PENSION_MAX)
        pen_recu = p.get('pension_alimentaire_recue', 0)
        ab_pr    = self._abattement(pen_recu, 'pension')

        # Abattement rattachement 6 794 EUR par enfant majeur rattache
        abatt_rat_total = nb_enf_rat * 6794
        rni = max(0.0, rev_ap - ded_per - pen_vers + pen_recu - ab_pr - abatt_rat_total)

        nb_parts = self._nb_parts(sit, nb_enf + nb_enf_rat, inv, pi)
        (ibrut, plaf_qf, eco_qf,
         tmi, tranches, imp_av, imp1) = self._impot_qf(rni, nb_parts, sit)

        decote = self._decote(ibrut, sit)
        i_ap   = ibrut - decote

        red_75  = min(p.get('dons_60_75', 0), self.DONS_75_PLAFOND) * 0.75
        red_mayo = min(p.get('dons_mayotte', 0), self.DONS_75_MAYOTTE_PLAFOND) * 0.75
        red_66  = min(p.get('dons_60', 0), rni * self.DONS_66_PLAFOND_PCT) * 0.66

        sal_t   = sal1_imp + sal2_imp + pen1 + pen2
        cot     = p.get('cotisations_syndicales', 0)
        cr_synd = min(cot, sal_t * self.SYNDICAT_PCT) * self.SYNDICAT_TAUX

        nb6   = p.get('nb_enfants_moins_6', 0)
        ralt  = p.get('residence_alternee', False)
        garde = p.get('frais_garde', 0)
        plaf_g = (self.GARDE_PLAFOND / (2 if ralt else 1)) * max(nb6, 1) if nb6 > 0 else 0
        cr_gde = min(garde, plaf_g) * self.GARDE_TAUX

        emp     = p.get('emploi_domicile', 0)
        is_1ere = p.get('premiere_annee_emploi', False)
        plaf_e  = min((self.EMPLOI_1ERE if is_1ere else self.EMPLOI_BASE) + nb_enf * self.EMPLOI_MAJ,
                      18_000 if is_1ere else self.EMPLOI_MAX)
        cr_emp  = min(emp, plaf_e) * self.EMPLOI_TAUX

        total_red = red_75 + red_mayo + red_66 + cr_gde + cr_emp + cr_synd
        i_avant   = max(0.0, i_ap - total_red)
        inet      = 0.0 if i_avant < self.SEUIL_RECOUVREMENT else round(i_avant)
        eco_per   = ded_per * (tmi / 100) if tmi > 0 else 0.0
        taux_moy  = (inet / total_brut * 100) if total_brut > 0 else 0.0

        return {
            'revenu_total_brut':     total_brut,
            'nb_enfants_rattaches':   nb_enf_rat,
            'heures_sup_1':          hs1,
            'heures_sup_2':          hs2,
            'exoneration_etudiant':  exo_etud,
            'abattement_salaires_1': ab_sal1,
            'abattement_pensions_1': ab_pen1,
            'abattement_salaires_2': ab_sal2,
            'abattement_pensions_2': ab_pen2,
            'abattement_applique':   abatt,
            'deduction_per':         ded_per,
            'plafond_per':           plaf_per,
            'pension_versee_ded':    pen_vers,
            'pension_recue_imp':     pen_recu,
            'revenu_imposable':      rni,
            'nb_parts':              nb_parts,
            'quotient_familial':     rni / nb_parts if nb_parts else 0,
            'impot_une_part':        imp1,
            'impot_avant_plafond':   imp_av,
            'plafonnement_qf':       plaf_qf,
            'economie_qf':           eco_qf,
            'impot_brut':            round(ibrut),
            'decote':                round(decote, 2),
            'taux_marginal':         tmi,
            'taux_moyen':            round(taux_moy, 2),
            'reduction_dons_75':     round(red_75 + red_mayo, 2),
            'reduction_dons_66':     round(red_66, 2),
            'credit_garde':          round(cr_gde, 2),
            'credit_emploi':         round(cr_emp, 2),
            'credit_syndicat':       round(cr_synd, 2),
            'economie_per':          round(eco_per, 2),
            'impot_net':             inet,
            'detail_tranches':       tranches,
        }

    def generer_conseils(self, p: dict, r: dict) -> list:
        conseils = []
        tmi  = r['taux_marginal']
        rni  = r['revenu_imposable']
        inet = r['impot_net']
        sal1 = p.get('revenu_salaire_declarant', 0)
        sal2 = p.get('revenu_salaire_conjoint',  0)

        reste_per = r['plafond_per'] - p.get('versement_per', 0)
        if reste_per > 100 and tmi >= 30:
            eco = reste_per * tmi / 100
            conseils.append({'icone': 'PER',
                'titre': f'PER - Economie potentielle : {eco:,.0f} EUR (TMI {tmi} %)',
                'detail': f'Capacite restante : {reste_per:,.0f} EUR. Cases 6NS / 6NT / 6NU.'})

        if not p.get('frais_reels') and sal1 > 0:
            forfait = r['abattement_salaires_1'] + r['abattement_salaires_2']
            conseils.append({'icone': 'FR',
                'titre': 'Frais reels : comparez avec le forfait actuel',
                'detail': f'Abattement forfaitaire actuel : {forfait:,.0f} EUR. Case 1AK / 1BK.'})

        if p.get('dons_60', 0) == 0 and inet > 0:
            plaf_d = rni * self.DONS_66_PLAFOND_PCT
            if plaf_d > 200:
                conseils.append({'icone': 'DONS',
                    'titre': f'Dons associations - Reduction 66 %',
                    'detail': f'Pour 100 EUR donnes => -66 EUR d impot. Plafond : {plaf_d:,.0f} EUR. Case 7VC.'})

        if p.get('emploi_domicile', 0) == 0:
            conseils.append({'icone': 'DOM',
                'titre': 'Emploi a domicile - Credit 50 %',
                'detail': 'Menage, garde, jardinage, soutien scolaire... Cases 7DB a 7DQ.'})

        if tmi == 30 and inet > 0:
            surplus = r['quotient_familial'] - 29_315
            if 0 < surplus < 8_000:
                eco_p = surplus * r['nb_parts']
                conseils.append({'icone': 'TMI',
                    'titre': f'Passer en tranche 11 %',
                    'detail': f'Un versement PER de {eco_p:,.0f} EUR vous ferait redescendre en tranche 11 %. Case 6NS.'})

        if p.get('cotisations_syndicales', 0) == 0 and (sal1 + sal2) > 500:
            plaf_s = (sal1 + sal2) * 0.01
            conseils.append({'icone': 'SYND',
                'titre': 'Cotisations syndicales - Credit 66 %',
                'detail': f'Plafond : {plaf_s:,.0f} EUR. Case 7AC.'})

        if p.get('heures_sup_declarant', 0) == 0 and sal1 > 0 and tmi >= 11:
            conseils.append({'icone': 'HS',
                'titre': 'Heures supplementaires - Exoneration IR',
                'detail': f'Heures sup et complementaires exonerees IR jusqu\'a 7 500 EUR/an. Cases 1GH / 1HH.'})

        return conseils


class ScenarioEnfantMajeur:
    """
    Comparaison rattachement vs foyer independant.

    SCENARIO A (Rattachement) :
      - Revenus enfant integres dans le foyer parental
      - +0,5 part pour l'enfant rattache
      - Si etudiant : exoneration jobs etudiants (5 301 EUR) + reduction scolarite

    SCENARIO B (Foyer independant) :
      - Parents declarent SANS l'enfant (leurs parts inchangees)
      - Parents peuvent deduire une pension (case 6GI, plafond 6 794 EUR)
      - Enfant fait sa propre declaration :
          revenus propres + pension recue (imposable case 1AS)
          si etudiant : exoneration jobs etudiants
    """

    def __init__(self, moteur: MoteurImpot):
        self.m = moteur

    def comparer(self, profil_parents: dict, profil_enfant: dict) -> dict:
        m   = self.m
        etudiant = profil_enfant.get('etudiant', False)
        niveau   = profil_enfant.get('niveau_etude', 'Superieur (Univ, IUT, Grande Ecole)')
        sal_enf  = profil_enfant.get('revenu_salaire_declarant', 0)
        exo_etud = min(sal_enf, m.JOBS_ETUDIANTS_EXONERATION) if etudiant else 0

        # ── SCENARIO A : Rattachement ─────────────────────────────────────
        pa = profil_parents.copy()
        pa['nb_enfants'] = profil_parents.get('nb_enfants', 0) + 1  # +0.5 part

        # Agregation revenus de l'enfant dans le foyer
        pa['revenu_salaire_declarant'] = (
            profil_parents.get('revenu_salaire_declarant', 0) + sal_enf)
        pa['revenu_pension_declarant'] = (
            profil_parents.get('revenu_pension_declarant', 0) +
            profil_enfant.get('revenu_pension_declarant', 0))
        pa['heures_sup_declarant'] = (
            profil_parents.get('heures_sup_declarant', 0) +
            profil_enfant.get('heures_sup_declarant', 0))
        pa['versement_per'] = (
            profil_parents.get('versement_per', 0) +
            profil_enfant.get('versement_per', 0))
        # Exoneration emploi etudiant si applicable
        pa['exoneration_emploi_etudiant'] = (
            profil_parents.get('exoneration_emploi_etudiant', 0) + exo_etud)

        res_a = m.calculer(pa)

        # Reduction scolarite uniquement si etudiant
        red_scol = m.SCOLARITE.get(niveau, 183) if etudiant else 0
        impot_a  = max(0, res_a['impot_net'] - red_scol)

        # ── SCENARIO B : Foyer independant ───────────────────────────────
        pension = min(profil_enfant.get('pension_recue', 0), m.PENSION_MAX)

        # Parents : meme situation, PLUS deduction pension versee
        pb_parents = profil_parents.copy()
        pb_parents['pension_alimentaire_versee'] = (
            profil_parents.get('pension_alimentaire_versee', 0) + pension)
        res_pb = m.calculer(pb_parents)

        # Enfant : sa propre declaration
        pb_enfant = {k: v for k, v in profil_enfant.items()
                     if k not in ('niveau_etude', 'pension_recue', 'etudiant')}
        pb_enfant['pension_alimentaire_recue']    = pension
        pb_enfant['exoneration_emploi_etudiant']  = exo_etud
        res_pe = m.calculer(pb_enfant)

        cout_b   = res_pb['impot_net'] + res_pe['impot_net']
        meilleur = 'A' if impot_a <= cout_b else 'B'

        return {
            'scenario_a': {
                'nb_parts':                 res_a['nb_parts'],
                'rni':                      res_a['revenu_imposable'],
                'impot_brut':               res_a['impot_brut'],
                'decote':                   res_a['decote'],
                'impot_net_avant_scol':     res_a['impot_net'],
                'reduction_scolarite':      red_scol,
                'niveau_etude':             niveau,
                'impot_net':                impot_a,
                'cout_total':               impot_a,
                'revenus_enfant_integres':  sal_enf + profil_enfant.get('revenu_pension_declarant', 0),
                'exoneration_etudiant':     exo_etud,
                'tmi':                      res_a['taux_marginal'],
                'taux_moyen':               res_a['taux_moyen'],
                'detail':                   res_a,
            },
            'scenario_b': {
                'parents': {**res_pb, 'pension_versee': pension},
                'enfant':  {**res_pe, 'pension_recue': pension,
                            'exoneration_etudiant': exo_etud},
                'cout_total': cout_b,
            },
            'meilleur_scenario': meilleur,
            'economie':          abs(cout_b - impot_a),
            'etudiant':          etudiant,
            'niveau_etude':      niveau,
        }
