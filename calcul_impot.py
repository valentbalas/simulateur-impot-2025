"""
Moteur de calcul IR 2024 — Brochure Pratique DGFiP 2025
Corrections barème, décote, abattements, QF appliquées.
Heures supplémentaires : exonération IR plafond 7 500 € (art. 81 quater CGI)
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
    BAREME_CYCLO = (0.315, (0.079, 711), 0.198)
    BAREME_CYCLO_ELEC = (0.378, (0.095, 853), 0.238)

    REPAS_VALEUR_FOYER = 5.35
    TELETRAVAIL_FORFAIT_JOUR = 2.70
    TELETRAVAIL_MAX_MOIS = 59.40

    @staticmethod
    def calculer_bareme_km(km, cv, type_vehicule):
        if type_vehicule in ("thermique", "electrique"):
            b = (FraisReels.BAREME_AUTO_ELECTRIQUE if type_vehicule == "electrique"
                 else FraisReels.BAREME_AUTO_THERMIQUE)
            ck = min(k for k in sorted(b) if k >= min(cv, 7))
            c1, (c2, k), c3 = b[ck]
            if km <= 5000: return km * c1
            elif km <= 20000: return km * c2 + k
            else: return km * c3
        elif type_vehicule in ("moto", "moto_electrique"):
            b = (FraisReels.BAREME_MOTO_ELECTRIQUE if type_vehicule == "moto_electrique"
                 else FraisReels.BAREME_MOTO_THERMIQUE)
            ck = min(k for k in sorted(b) if k >= min(cv, 99))
            c1, (c2, k), c3 = b[ck]
            if km <= 3000: return km * c1
            elif km <= 6000: return km * c2 + k
            else: return km * c3
        else:
            c1, (c2, k), c3 = (FraisReels.BAREME_CYCLO_ELEC
                                if "electrique" in type_vehicule
                                else FraisReels.BAREME_CYCLO)
            if km <= 3000: return km * c1
            elif km <= 6000: return km * c2 + k
            else: return km * c3

    @staticmethod
    def calculer_teletravail(nb_jours):
        return min(nb_jours * FraisReels.TELETRAVAIL_FORFAIT_JOUR,
                   FraisReels.TELETRAVAIL_MAX_MOIS * 12)


class MoteurImpot:
    # Barème 2024
    BAREME = [
        (11_497,       0.00),
        (29_315,       0.11),
        (83_823,       0.30),
        (180_294,      0.41),
        (float('inf'), 0.45),
    ]
    ABATTEMENT_SALAIRES_MIN  = 504
    ABATTEMENT_SALAIRES_MAX  = 14_426
    ABATTEMENT_PENSIONS_MIN  = 450
    ABATTEMENT_PENSIONS_MAX  = 4_399

    PLAFOND_DEMI_PART        = 1_791
    PLAFOND_PARENT_ISOLE_1ER = 4_224

    DECOTE_SEUIL_CEL  = 1_964
    DECOTE_SEUIL_CPL  = 3_249
    DECOTE_CST_CEL    = 889
    DECOTE_CST_CPL    = 1_470

    PASS_2024         = 46_368
    PER_PLAFOND_MIN   = 4_637

    DONS_75_PLAFOND         = 1_000
    DONS_75_MAYOTTE_PLAFOND = 2_000
    DONS_66_PLAFOND_PCT     = 0.20

    GARDE_PLAFOND      = 3_500
    GARDE_TAUX         = 0.50
    EMPLOI_BASE        = 12_000
    EMPLOI_1ERE        = 15_000
    EMPLOI_MAJ         = 1_500
    EMPLOI_MAX         = 15_000
    EMPLOI_TAUX        = 0.50

    SYNDICAT_PCT       = 0.01
    SYNDICAT_TAUX      = 0.66

    # Heures supplémentaires — exonération IR (art. 81 quater CGI, depuis 2019)
    HEURES_SUP_PLAFOND = 7_500

    SCOLARITE = {
        'Collège':                  61,
        'Lycée / BTS / Prépa':     153,
        'Enseignement supérieur':  183,
    }
    PENSION_MAX       = 6_794
    SEUIL_RECOUVREMENT = 61

    def _nb_parts(self, sit, nb_enf, inv, pi=False):
        parts = (2.0 if sit in ("Marié(e) / Pacsé(e)", "Veuf(ve)") and nb_enf > 0
                 else (2.0 if sit == "Marié(e) / Pacsé(e)" else 1.0))
        if sit == "Veuf(ve)" and nb_enf == 0:
            parts = 1.0
        if nb_enf > 0:
            if pi:
                parts += 1.0
                if nb_enf >= 2: parts += 0.5
                if nb_enf >= 3: parts += (nb_enf - 2) * 1.0
            else:
                if nb_enf <= 2: parts += nb_enf * 0.5
                else: parts += 1.0 + (nb_enf - 2) * 1.0
        if inv:
            parts += 0.5
        return parts

    def _appliquer_bareme(self, quotient):
        labels = [
            "Tranche 0 % (≤ 11 497 €)",
            "Tranche 11 % (11 498 – 29 315 €)",
            "Tranche 30 % (29 316 – 83 823 €)",
            "Tranche 41 % (83 824 – 180 294 €)",
            "Tranche 45 % (> 180 294 €)",
        ]
        impot, tmi, tranches, borne = 0.0, 0, [], 0
        for i, (lim, taux) in enumerate(self.BAREME):
            base = max(0.0, min(quotient, lim) - borne)
            it = base * taux
            tranches.append({'label': labels[i], 'taux': int(taux*100),
                             'base': base, 'impot_tranche': round(it, 2)})
            if base > 0 and taux > 0:
                tmi = int(taux * 100)
            impot += it
            borne = lim
            if min(quotient, lim) >= quotient:
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
        if sit == "Marié(e) / Pacsé(e)":
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
        parts_base = 2.0 if sit in ("Marié(e) / Pacsé(e)", "Veuf(ve)") else 1.0
        # Veuf sans enfant → 1 part
        if sit == "Veuf(ve)" and nb_parts < 2.0:
            parts_base = 1.0
        dsp = (nb_parts - parts_base) * 2
        ibrut, plaf_qf = imp_av, 0.0
        if dsp > 0:
            q_base = rni / parts_base
            i_base, _, _ = self._appliquer_bareme(q_base)
            i_sans_qf = i_base * parts_base
            avantage = i_sans_qf - imp_av
            avantage_max = dsp * self.PLAFOND_DEMI_PART
            if avantage > avantage_max:
                plaf_qf = avantage - avantage_max
                ibrut = i_sans_qf - avantage_max
        eco_qf = 0.0
        if dsp > 0:
            q2 = rni / parts_base
            i2, _, _ = self._appliquer_bareme(q2)
            eco_qf = max(0.0, i2 * parts_base - ibrut)
        return ibrut, plaf_qf, eco_qf, tmi, tranches, imp_av, imp1

    def calculer(self, p: dict) -> dict:
        sit = p['situation']
        nb_enf = p.get('nb_enfants', 0)
        inv = p.get('invalide_declarant', False)
        pi = p.get('parent_isole', False)

        sal1 = p.get('revenu_salaire_declarant', 0)
        pen1 = p.get('revenu_pension_declarant', 0)
        sal2 = p.get('revenu_salaire_conjoint', 0)
        pen2 = p.get('revenu_pension_conjoint', 0)

        # Heures supplémentaires exonérées (déduits des salaires imposables)
        hsup1 = min(p.get('heures_sup_declarant', 0), self.HEURES_SUP_PLAFOND)
        hsup2 = min(p.get('heures_sup_conjoint', 0), self.HEURES_SUP_PLAFOND)
        # Les heures sup sont incluses dans sal1/sal2 mais exonérées → on les déduit
        sal1_imp = max(0, sal1 - hsup1)
        sal2_imp = max(0, sal2 - hsup2)

        total_brut = sal1 + pen1 + sal2 + pen2
        total_brut_imposable = sal1_imp + pen1 + sal2_imp + pen2

        fr1  = p.get('frais_reels', False)
        mfr1 = p.get('montant_frais_reels_1', 0)
        fr2  = p.get('frais_reels_2', False)
        mfr2 = p.get('montant_frais_reels_2', 0)

        ab_sal1 = self._abattement(sal1_imp, 'salaire', fr1, mfr1)
        ab_pen1 = self._abattement(pen1, 'pension')
        ab_sal2 = self._abattement(sal2_imp, 'salaire', fr2, mfr2)
        ab_pen2 = self._abattement(pen2, 'pension')
        abatt = ab_sal1 + ab_pen1 + ab_sal2 + ab_pen2

        rev_ap = total_brut_imposable - abatt

        per = p.get('versement_per', 0)
        plaf_per = max(self.PER_PLAFOND_MIN,
                       min(rev_ap * 0.10, 8 * self.PASS_2024 * 0.10))
        ded_per = min(per, plaf_per)

        pension_versee = min(p.get('pension_alimentaire_versee', 0), self.PENSION_MAX)
        pension_recue  = p.get('pension_alimentaire_recue', 0)
        ab_pr = self._abattement(pension_recue, 'pension')

        rni = max(0.0, rev_ap - ded_per - pension_versee + pension_recue - ab_pr)

        nb_parts = self._nb_parts(sit, nb_enf, inv, pi)
        (ibrut, plaf_qf, eco_qf, tmi,
         tranches, imp_av, imp1) = self._impot_qf(rni, nb_parts, sit)

        decote = self._decote(ibrut, sit)
        i_ap = ibrut - decote

        # Dons
        red_75   = min(p.get('dons_60_75', 0), self.DONS_75_PLAFOND) * 0.75
        red_mayo = min(p.get('dons_mayotte', 0), self.DONS_75_MAYOTTE_PLAFOND) * 0.75
        red_66   = min(p.get('dons_60', 0), rni * self.DONS_66_PLAFOND_PCT) * 0.66

        # Cotisations syndicales
        sal_total = sal1_imp + sal2_imp + pen1 + pen2
        cot = p.get('cotisations_syndicales', 0)
        cr_synd = min(cot, sal_total * self.SYNDICAT_PCT) * self.SYNDICAT_TAUX

        # Garde
        nb6    = p.get('nb_enfants_moins_6', 0)
        ralt   = p.get('residence_alternee', False)
        garde  = p.get('frais_garde', 0)
        div_g  = 2 if ralt else 1
        plaf_g = (self.GARDE_PLAFOND / div_g) * max(nb6, 1) if nb6 > 0 else 0
        cr_gde = min(garde, plaf_g) * self.GARDE_TAUX

        # Emploi domicile
        emp     = p.get('emploi_domicile', 0)
        is_1ere = p.get('premiere_annee_emploi', False)
        plaf_e  = self.EMPLOI_1ERE if is_1ere else self.EMPLOI_BASE
        plaf_e += nb_enf * self.EMPLOI_MAJ
        plaf_e  = min(plaf_e, 18_000 if is_1ere else self.EMPLOI_MAX)
        cr_emp  = min(emp, plaf_e) * self.EMPLOI_TAUX

        total_red = red_75 + red_mayo + red_66 + cr_gde + cr_emp + cr_synd
        i_avant   = max(0.0, i_ap - total_red)
        inet      = 0.0 if i_avant < self.SEUIL_RECOUVREMENT else round(i_avant)

        eco_per   = ded_per * (tmi / 100) if tmi > 0 else 0.0
        taux_moy  = (inet / total_brut * 100) if total_brut > 0 else 0.0

        return {
            'revenu_total_brut':      total_brut,
            'heures_sup_1':           hsup1,
            'heures_sup_2':           hsup2,
            'abattement_salaires_1':  ab_sal1,
            'abattement_pensions_1':  ab_pen1,
            'abattement_salaires_2':  ab_sal2,
            'abattement_pensions_2':  ab_pen2,
            'abattement_applique':    abatt,
            'deduction_per':          ded_per,
            'plafond_per':            plaf_per,
            'pension_versee_ded':     pension_versee,
            'pension_recue_imp':      pension_recue,
            'revenu_imposable':       rni,
            'nb_parts':               nb_parts,
            'quotient_familial':      rni / nb_parts if nb_parts else 0,
            'impot_une_part':         imp1,
            'impot_avant_plafond':    imp_av,
            'plafonnement_qf':        plaf_qf,
            'economie_qf':            eco_qf,
            'impot_brut':             round(ibrut),
            'decote':                 round(decote, 2),
            'taux_marginal':          tmi,
            'taux_moyen':             round(taux_moy, 2),
            'reduction_dons_75':      round(red_75 + red_mayo, 2),
            'reduction_dons_66':      round(red_66, 2),
            'credit_garde':           round(cr_gde, 2),
            'credit_emploi':          round(cr_emp, 2),
            'credit_syndicat':        round(cr_synd, 2),
            'economie_per':           round(eco_per, 2),
            'impot_net':              inet,
            'detail_tranches':        tranches,
        }

    def generer_conseils(self, p: dict, r: dict) -> list:
        conseils = []
        tmi  = r['taux_marginal']
        rni  = r['revenu_imposable']
        inet = r['impot_net']
        sal1 = p.get('revenu_salaire_declarant', 0)
        sal2 = p.get('revenu_salaire_conjoint', 0)

        reste_per = r['plafond_per'] - p.get('versement_per', 0)
        if reste_per > 100 and tmi >= 30:
            eco = reste_per * tmi / 100
            conseils.append({'icone': '💰',
                'titre': f'PER — Économie potentielle : {eco:,.0f} € (TMI {tmi} %)',
                'detail': (f'Capacité restante : {reste_per:,.0f} €. '
                           f'Cases 6NS / 6NT / 6NU selon votre situation.')})

        if not p.get('frais_reels') and sal1 > 0:
            forfait = r['abattement_salaires_1'] + r['abattement_salaires_2']
            conseils.append({'icone': '📋',
                'titre': 'Frais réels : comparez avec le forfait actuel',
                'detail': f'Abattement forfaitaire actuel : {forfait:,.0f} €. Case 1AK (D1) / 1BK (D2).'})

        if p.get('dons_60', 0) == 0 and inet > 0:
            plaf_d = rni * self.DONS_66_PLAFOND_PCT
            if plaf_d > 200:
                conseils.append({'icone': '❤️',
                    'titre': 'Dons associations — Réduction 66 %',
                    'detail': f'Pour 100 € donnés → −66 € d\'impôt. Plafond : {plaf_d:,.0f} €. Case 7VC.'})

        if p.get('emploi_domicile', 0) == 0:
            conseils.append({'icone': '🏠',
                'titre': 'Emploi à domicile — Crédit 50 %',
                'detail': 'Ménage, garde, jardinage, soutien scolaire… Cases 7DB à 7DQ.'})

        if tmi == 30 and inet > 0:
            surplus = r['quotient_familial'] - 29_315
            if 0 < surplus < 8_000:
                eco_p = surplus * r['nb_parts']
                conseils.append({'icone': '📉',
                    'titre': 'Passer en tranche 11 %',
                    'detail': f'Un versement PER de {eco_p:,.0f} € vous ferait redescendre en tranche 11 %. Case 6NS.'})

        if p.get('cotisations_syndicales', 0) == 0 and (sal1 + sal2) > 500:
            plaf_s = (sal1 + sal2) * 0.01
            conseils.append({'icone': '🤝',
                'titre': 'Cotisations syndicales — Crédit 66 %',
                'detail': f'Plafond : {plaf_s:,.0f} €. Case 7AC.'})

        if (p.get('heures_sup_declarant', 0) == 0 and sal1 > 0 and tmi >= 11):
            conseils.append({'icone': '⏰',
                'titre': 'Heures supplémentaires — Exonération IR',
                'detail': 'Les heures sup et complémentaires sont exonérées d\'IR jusqu\'à 7 500 €/an. Cases 1GH / 1HH.'})

        return conseils


class ScenarioEnfantMajeur:
    """Rattachement vs foyer indépendant — comparaison fiscale."""

    def __init__(self, moteur: MoteurImpot):
        self.m = moteur

    def comparer(self, profil_parents: dict, profil_enfant: dict) -> dict:
        m = self.m

        # ── SCÉNARIO A : Rattachement ─────────────────────────────────────
        pa = profil_parents.copy()
        pa['nb_enfants'] = profil_parents.get('nb_enfants', 0) + 1
        # Fusion revenus enfant dans foyer parents
        for k in ('revenu_salaire_declarant', 'revenu_pension_declarant',
                  'heures_sup_declarant'):
            pa[k] = profil_parents.get(k, 0) + profil_enfant.get(k, 0)
        pa['versement_per'] = (profil_parents.get('versement_per', 0) +
                                profil_enfant.get('versement_per', 0))
        res_a_raw = m.calculer(pa)
        # Abattement enfant rattaché : 6 794 €
        rni_a = max(0.0, res_a_raw['revenu_imposable'] - m.PENSION_MAX)
        nb_p_a = res_a_raw['nb_parts']
        (ib_a, pqf_a, _, tmi_a, tr_a, _, _) = m._impot_qf(rni_a, nb_p_a, pa['situation'])
        dec_a = m._decote(ib_a, pa['situation'])
        reds_a = (res_a_raw['reduction_dons_75'] + res_a_raw['reduction_dons_66'] +
                  res_a_raw['credit_garde'] + res_a_raw['credit_emploi'] +
                  res_a_raw['credit_syndicat'])
        i_av_a = max(0.0, ib_a - dec_a - reds_a)
        inet_a = 0.0 if i_av_a < m.SEUIL_RECOUVREMENT else round(i_av_a)
        # Réduction scolarité
        niveau = profil_enfant.get('niveau_etude', 'Enseignement supérieur')
        red_scol = m.SCOLARITE.get(niveau, 183)
        impot_a = max(0, inet_a - red_scol)

        # ── SCÉNARIO B : Foyer indépendant ───────────────────────────────
        pension = min(profil_enfant.get('pension_recue', 0), m.PENSION_MAX)
        pb = profil_parents.copy()
        pb['pension_alimentaire_versee'] = pension
        res_pb = m.calculer(pb)

        pe = {k: v for k, v in profil_enfant.items()
              if k not in ('niveau_etude', 'pension_recue')}
        pe['pension_alimentaire_recue'] = pension
        res_pe = m.calculer(pe)

        cout_b = res_pb['impot_net'] + res_pe['impot_net']
        meilleur = 'A' if impot_a <= cout_b else 'B'

        return {
            'scenario_a': {
                'nb_parts': nb_p_a,
                'rni': rni_a,
                'impot_brut': round(ib_a),
                'decote': round(dec_a),
                'reduction_scolarite': red_scol,
                'niveau_etude': niveau,
                'impot_net': impot_a,
                'cout_total': impot_a,
                'revenus_enfant_integres': (profil_enfant.get('revenu_salaire_declarant', 0) +
                                            profil_enfant.get('revenu_pension_declarant', 0)),
            },
            'scenario_b': {
                'parents': {**res_pb, 'pension_versee': pension},
                'enfant':  {**res_pe, 'pension_recue': pension},
                'cout_total': cout_b,
            },
            'meilleur_scenario': meilleur,
            'economie': abs(cout_b - impot_a),
            'res_parents_b': res_pb,
            'res_enfant_b':  res_pe,
        }
