"""
Moteur fiscal Dirigeant / Revenus complexes
BIC, BNC, Revenus fonciers, LMNP, LMP, SCI, Dividendes, IS
Sources : BOI-BIC, BOI-BNC, BOI-RFPI, BOI-RPPM, CGI 2024
"""


class MoteurDirigeant:

    # IS 2024 (art. 219 CGI)
    IS_SEUIL_REDUIT = 42_500
    IS_TAUX_REDUIT  = 0.15
    IS_TAUX_NORMAL  = 0.25

    # PFU / Flat Tax (art. 200 A CGI)
    PFU_IR    = 0.128
    PFU_PS    = 0.172
    PFU_TOTAL = 0.30
    ABATT_DIV = 0.40   # Abattement 40 % option bareme

    # Micro-BIC 2024 (art. 50-0 CGI)
    MICRO_BIC_VENTE_SEUIL   = 188_700
    MICRO_BIC_VENTE_ABATT   = 0.71
    MICRO_BIC_SERVICE_SEUIL = 77_700
    MICRO_BIC_SERVICE_ABATT = 0.50

    # Micro-BNC (art. 102 ter CGI)
    MICRO_BNC_SEUIL = 77_700
    MICRO_BNC_ABATT = 0.34

    # Micro-foncier (art. 32 CGI)
    MICRO_FONCIER_SEUIL = 15_000
    MICRO_FONCIER_ABATT = 0.30

    # LMNP micro-BIC
    LMNP_NC_SEUIL  = 77_700
    LMNP_NC_ABATT  = 0.50
    LMNP_CL_SEUIL  = 188_700
    LMNP_CL_ABATT  = 0.71

    # LMP : recettes > 23 000 EUR ET > autres revenus pro du foyer
    LMP_SEUIL_RECETTES = 23_000

    # Deficit foncier imputable sur revenu global (hors interets emprunt)
    DEFICIT_FONCIER_PLAFOND = 10_700

    # Prelevements sociaux capitaux
    PS = 0.172

    # Abattement salaires (gerance)
    ABATT_SAL_MIN = 509
    ABATT_SAL_MAX = 14_555

    def calculer_is(self, resultat_fiscal: float) -> dict:
        """Calcul IS societe."""
        if resultat_fiscal <= 0:
            return {'resultat': resultat_fiscal, 'is_total': 0, 'is_reduit': 0,
                    'is_normal': 0, 'benefice_net': 0, 'taux_effectif': 0}
        b_red = min(resultat_fiscal, self.IS_SEUIL_REDUIT)
        b_nor = max(0.0, resultat_fiscal - self.IS_SEUIL_REDUIT)
        is_r  = b_red * self.IS_TAUX_REDUIT
        is_n  = b_nor * self.IS_TAUX_NORMAL
        is_t  = round(is_r + is_n)
        return {
            'resultat': resultat_fiscal,
            'base_reduit': b_red, 'is_reduit': round(is_r),
            'base_normal': b_nor, 'is_normal': round(is_n),
            'is_total': is_t,
            'benefice_net': round(resultat_fiscal - is_t),
            'taux_effectif': round(is_t / resultat_fiscal * 100, 2) if resultat_fiscal else 0,
        }

    def calculer_dividendes(self, dividendes_bruts: float, tmi_pct: int) -> dict:
        """Comparaison PFU vs option bareme pour les dividendes."""
        # PFU
        ir_pfu  = dividendes_bruts * self.PFU_IR
        ps_pfu  = dividendes_bruts * self.PFU_PS
        tot_pfu = ir_pfu + ps_pfu
        net_pfu = dividendes_bruts - tot_pfu

        # Option bareme (abattement 40 %)
        base_bar = dividendes_bruts * (1 - self.ABATT_DIV)
        ir_bar   = base_bar * (tmi_pct / 100)
        ps_bar   = dividendes_bruts * self.PS
        tot_bar  = ir_bar + ps_bar
        net_bar  = dividendes_bruts - tot_bar

        meilleur = 'PFU' if tot_pfu <= tot_bar else 'Bareme'

        return {
            'dividendes_bruts': dividendes_bruts,
            'pfu': {
                'label': 'PFU (Flat Tax 30 %)',
                'ir': round(ir_pfu), 'ps': round(ps_pfu),
                'total_imposition': round(tot_pfu),
                'net_percu': round(net_pfu),
                'taux_effectif': 30.0,
            },
            'bareme': {
                'label': f'Option bareme IR ({tmi_pct} %) + abattement 40 %',
                'base_imposable': round(base_bar),
                'ir': round(ir_bar), 'ps': round(ps_bar),
                'total_imposition': round(tot_bar),
                'net_percu': round(net_bar),
                'taux_effectif': round(tot_bar / dividendes_bruts * 100, 1) if dividendes_bruts else 0,
            },
            'meilleur': meilleur,
            'economie': round(abs(tot_pfu - tot_bar)),
        }

    def calculer_bic_micro(self, ca: float, type_act: str = 'services') -> dict:
        """BIC micro-entreprise."""
        if type_act == 'vente':
            abatt  = self.MICRO_BIC_VENTE_ABATT
            seuil  = self.MICRO_BIC_VENTE_SEUIL
            label  = 'Ventes / Commerce (abattement 71 %)'
        elif type_act == 'mixte':
            abatt  = 0.50
            seuil  = self.MICRO_BIC_SERVICE_SEUIL
            label  = 'Activite mixte (abattement 50 %)'
        else:
            abatt  = self.MICRO_BIC_SERVICE_ABATT
            seuil  = self.MICRO_BIC_SERVICE_SEUIL
            label  = 'Prestations de services (abattement 50 %)'
        imposable = round(ca * (1 - abatt))
        return {
            'ca': ca, 'label': label,
            'abattement_pct': int(abatt * 100),
            'abattement_montant': round(ca * abatt),
            'benefice_imposable': imposable,
            'seuil_regime': seuil,
            'eligible': ca <= seuil,
            'type': 'BIC micro',
        }

    def calculer_bic_reel(self, ca: float, charges: float,
                           amortissements: float = 0) -> dict:
        """BIC regime reel simplifie (declaration 2031)."""
        benefice = ca - charges - amortissements
        return {
            'ca': ca, 'charges': charges, 'amortissements': amortissements,
            'benefice': round(benefice),
            'benefice_imposable': max(0, round(benefice)),
            'deficit': max(0, round(-benefice)),
            'type': 'BIC reel',
        }

    def calculer_bnc_micro(self, recettes: float) -> dict:
        """BNC micro (declaration 2042 C PRO)."""
        imposable = round(recettes * (1 - self.MICRO_BNC_ABATT))
        return {
            'recettes': recettes,
            'abattement_pct': int(self.MICRO_BNC_ABATT * 100),
            'abattement_montant': round(recettes * self.MICRO_BNC_ABATT),
            'benefice_imposable': imposable,
            'seuil_regime': self.MICRO_BNC_SEUIL,
            'eligible': recettes <= self.MICRO_BNC_SEUIL,
            'type': 'BNC micro',
        }

    def calculer_bnc_reel(self, recettes: float, charges: float) -> dict:
        """BNC regime de la declaration controlee (declaration 2035)."""
        benefice = recettes - charges
        return {
            'recettes': recettes, 'charges': charges,
            'benefice': round(benefice),
            'benefice_imposable': max(0, round(benefice)),
            'deficit': max(0, round(-benefice)),
            'type': 'BNC reel (declaration 2035)',
        }

    def calculer_foncier_micro(self, revenus_bruts: float) -> dict:
        """Micro-foncier (declaration 2042 ligne 4BE)."""
        imposable = round(revenus_bruts * (1 - self.MICRO_FONCIER_ABATT))
        return {
            'revenus_bruts': revenus_bruts,
            'abattement_pct': 30,
            'abattement_montant': round(revenus_bruts * self.MICRO_FONCIER_ABATT),
            'imposable': imposable,
            'eligible': revenus_bruts <= self.MICRO_FONCIER_SEUIL,
            'seuil': self.MICRO_FONCIER_SEUIL,
            'type': 'Micro-foncier',
        }

    def calculer_foncier_reel(self, revenus_bruts: float,
                               interets_emprunt: float = 0,
                               charges_courantes: float = 0,
                               travaux: float = 0,
                               taxe_fonciere: float = 0,
                               frais_gestion: float = 0) -> dict:
        """Regime reel foncier (declaration 2044)."""
        total_charges = interets_emprunt + charges_courantes + travaux + taxe_fonciere + frais_gestion
        resultat = revenus_bruts - total_charges
        deficit = max(0.0, -resultat)
        # Part imputable sur revenu global = deficit - interets emprunt
        deficit_global = min(max(0.0, deficit - interets_emprunt),
                             self.DEFICIT_FONCIER_PLAFOND) if deficit > 0 else 0
        return {
            'revenus_bruts': revenus_bruts,
            'interets_emprunt': interets_emprunt,
            'charges_courantes': charges_courantes,
            'travaux': travaux,
            'taxe_fonciere': taxe_fonciere,
            'frais_gestion': frais_gestion,
            'total_charges': round(total_charges),
            'resultat': round(resultat),
            'imposable': max(0, round(resultat)),
            'deficit_total': round(deficit),
            'deficit_imputable_rng': round(deficit_global),
            'deficit_report_foncier': round(max(0, deficit - deficit_global)),
            'type': 'Foncier reel',
        }

    def calculer_lmnp(self, recettes: float, classe: bool = False,
                      regime: str = 'micro',
                      charges: float = 0, amortissements: float = 0) -> dict:
        """LMNP micro-BIC ou reel."""
        if regime == 'micro':
            abatt = self.LMNP_CL_ABATT if classe else self.LMNP_NC_ABATT
            seuil = self.LMNP_CL_SEUIL if classe else self.LMNP_NC_SEUIL
            imposable = round(recettes * (1 - abatt))
            return {
                'recettes': recettes, 'type_bien': 'Classe' if classe else 'Non classe',
                'regime': 'Micro-BIC LMNP',
                'abattement_pct': int(abatt * 100),
                'imposable': imposable,
                'eligible': recettes <= seuil,
                'seuil': seuil,
                'ps': round(imposable * self.PS),
            }
        else:
            benefice = recettes - charges - amortissements
            return {
                'recettes': recettes, 'charges': charges, 'amortissements': amortissements,
                'regime': 'LMNP Reel',
                'benefice': round(benefice),
                'imposable': max(0, round(benefice)),
                'deficit': max(0, round(-benefice)),
                'note': 'Deficit reportable 10 ans sur BIC LMNP uniquement',
                'ps': round(max(0, benefice) * self.PS) if benefice > 0 else 0,
            }

    def calculer_lmp(self, recettes: float, charges: float,
                     amortissements: float, autres_revenus_foyer: float) -> dict:
        """LMP (Location Meublee Professionnelle)."""
        lmp_ok = (recettes > self.LMP_SEUIL_RECETTES and
                  recettes > autres_revenus_foyer)
        benefice = recettes - charges - amortissements
        return {
            'recettes': recettes, 'charges': charges, 'amortissements': amortissements,
            'statut_lmp': lmp_ok,
            'benefice': round(benefice),
            'imposable': max(0, round(benefice)),
            'deficit': max(0, round(-benefice)),
            'avantages': [
                'Deficit imputable sur revenu global sans limite' if lmp_ok else 'Non applicable',
                'Plus-values regime professionnel (exoneration si recettes < 90 000 EUR)',
                'Charges sociales TNS deductibles',
            ] if lmp_ok else ['Statut LMP non atteint (recettes < 23 000 EUR ou < autres revenus pro)'],
        }

    def calculer_gerance(self, remuneration: float,
                          frais_reels: bool = False,
                          montant_fr: float = 0) -> dict:
        """Remuneration de gerant (traitement et salaires)."""
        if frais_reels and montant_fr > 0:
            ab = montant_fr
        else:
            ab = max(self.ABATT_SAL_MIN, min(remuneration * 0.10, self.ABATT_SAL_MAX))
        imposable = max(0.0, remuneration - ab)
        return {
            'remuneration': remuneration,
            'abattement': round(ab),
            'imposable': round(imposable),
            'type_abattement': 'Frais reels' if (frais_reels and montant_fr) else 'Forfait 10 %',
            'note': 'Deductible de l IS de la societe si SARL/SAS',
        }

    def calculer_sci_is(self, resultat_fiscal: float,
                         quote_part: float = 1.0) -> dict:
        """SCI a l IS : calcul IS + dividendes potentiels."""
        is_data   = self.calculer_is(resultat_fiscal)
        ben_net   = is_data['benefice_net']
        div_pot   = round(ben_net * quote_part)
        return {**is_data,
                'quote_part_detention': quote_part,
                'dividende_potentiel': div_pot,
                'note': 'Les dividendes distribues sont soumis au PFU 30 % (ou option bareme)'}

    def simuler_remuneration_vs_dividendes(self,
                                            benefice_avant_impot: float,
                                            remuneration: float,
                                            tmi_pct: int) -> dict:
        """
        Compare deux strategies de sortie de resultat :
        1. Tout en remuneration (deductible IS, imposable IR comme salaire)
        2. Remuneration minimale + dividendes (IS sur benefice, PFU sur dividendes)
        """
        # Strategie A : Tout remuneration
        resultat_is_a = max(0, benefice_avant_impot - remuneration)
        is_a          = self.calculer_is(resultat_is_a)['is_total']
        ab_rem        = max(self.ABATT_SAL_MIN, min(remuneration * 0.10, self.ABATT_SAL_MAX))
        ir_a          = max(0, remuneration - ab_rem) * (tmi_pct / 100)
        cout_total_a  = round(is_a + ir_a)
        net_a         = round(remuneration - ir_a)

        # Strategie B : Dividendes depuis benefice
        is_b_data     = self.calculer_is(benefice_avant_impot)
        is_b          = is_b_data['is_total']
        div_dispo     = is_b_data['benefice_net']
        pfu_div       = round(div_dispo * self.PFU_TOTAL)
        cout_total_b  = round(is_b + pfu_div)
        net_b         = round(div_dispo - pfu_div)

        return {
            'benefice_avant_impot': benefice_avant_impot,
            'strategie_a': {
                'label': 'Tout en remuneration',
                'remuneration': remuneration,
                'is_societe': is_a,
                'ir_personnel': round(ir_a),
                'cout_total': cout_total_a,
                'net_percu': net_a,
            },
            'strategie_b': {
                'label': 'Dividendes (PFU 30 %)',
                'is_societe': is_b,
                'dividendes_bruts': div_dispo,
                'pfu': pfu_div,
                'cout_total': cout_total_b,
                'net_percu': net_b,
            },
            'meilleure': 'A' if cout_total_a <= cout_total_b else 'B',
            'economie': abs(cout_total_a - cout_total_b),
        }

    # ─── TNS cotisations et sci_ir ────────────────────────────────────
    TNS_COTISATIONS = {
        'gerant_majoritaire_sarl': {
            'label': 'Gerant majoritaire SARL (TNS)',
            'taux_global': 0.45,
            'detail': {'Maladie-maternite':'6,35 %','Retraite de base':'17,75 %',
                'Retraite complementaire':'7,00 %','Invalidite-deces':'1,30 %',
                'Alloc. familiales':'0 a 3,10 %','CSG/CRDS':'9,70 %','CFP':'0,25 %'},
            'avantages':['Charges ~45% vs ~75% salarie','PER Madelin deductible',
                'Sante/prevoyance via contrat Madelin'],
            'inconvenients':['Arret maladie a partir J8','Retraite souvent inferieure',
                'Cotisations calculees sur N-2'],
        },
        'president_sas': {
            'label': 'President SAS/SASU (assimile salarie)',
            'taux_global': 0.75,
            'detail': {'Cotisations patronales':'~45 %','Cotisations salariales':'~22 %',
                'Total sur brut':'~75 %'},
            'avantages':['Meilleure protection sociale','Retraite alignee salaries',
                'Arret maladie J1 avec prevoyance'],
            'inconvenients':['Charges tres elevees (~75 %)','Pas de Madelin',
                'Plus couteux pour la societe'],
        },
        'ae_bic': {
            'label': 'Auto-entrepreneur BIC (commerce/vente)',
            'taux_global': 0.129,
            'detail': {'Cotisations sociales':'12,8 %','CFP':'0,1 %','Total sur CA':'12,9 %'},
            'avantages':['Charges minimales','Gestion simplifiee','Franchise TVA si sous seuils'],
            'inconvenients':['Plafond CA 188 700 EUR','Retraite tres faible',
                'Couverture maladie minimale'],
        },
        'ae_bnc': {
            'label': 'Auto-entrepreneur BNC (liberale/services)',
            'taux_global': 0.214,
            'detail': {'Cotisations sociales':'21,2 %','CFP':'0,2 %','Total sur CA':'21,4 %'},
            'avantages':['Simplicite administrative','Charges sur recettes reelles'],
            'inconvenients':['Plafond CA 77 700 EUR','Protection sociale limitee'],
        },
        'tns_reel': {
            'label': 'TNS regime reel (EI, EURL, SNC)',
            'taux_global': 0.43,
            'detail': {'Maladie-maternite':'6,35 %','Retraite base+compl.':'24,75 %',
                'Prevoyance':'1,30 %','Alloc. familiales':'0 a 3,10 %',
                'CSG/CRDS':'9,70 %','CFP':'0,25 %'},
            'avantages':['Cotisations sur benefice reel','Madelin sante/prevoyance/retraite',
                'Flexibilite remuneration'],
            'inconvenients':['Regularisation sur N-2','Cotisations minimales si deficit',
                'Gestion plus lourde'],
        },
    }

    def calculer_cotisations_tns(self, remuneration: float, statut: str) -> dict:
        data = self.TNS_COTISATIONS.get(statut, self.TNS_COTISATIONS['tns_reel'])
        taux = data['taux_global']
        cot  = round(remuneration * taux)
        return {
            'statut': data['label'], 'remuneration': remuneration,
            'taux_global': taux, 'cotisations': cot,
            'net_avant_ir': round(remuneration - cot),
            'detail': data['detail'],
            'avantages': data['avantages'],
            'inconvenients': data['inconvenients'],
        }

    def comparer_statuts(self, remuneration: float, tmi_pct: int) -> list:
        resultats = []
        for key, data in self.TNS_COTISATIONS.items():
            cot      = round(remuneration * data['taux_global'])
            net_sc   = remuneration - cot
            ir       = round(max(0, net_sc * 0.90) * tmi_pct / 100)
            net_fin  = round(net_sc - ir)
            resultats.append({
                'statut': key, 'label': data['label'],
                'taux_charges': int(data['taux_global'] * 100),
                'cotisations': cot, 'ir_estime': ir, 'net_final': net_fin,
            })
        resultats.sort(key=lambda x: -x['net_final'])
        return resultats

    def calculer_sci_ir(self, quote_part_resultat: float) -> dict:
        imposable = max(0.0, quote_part_resultat)
        deficit   = max(0.0, -quote_part_resultat)
        imputable = min(deficit, self.DEFICIT_FONCIER_PLAFOND)
        return {
            'quote_part': quote_part_resultat,
            'imposable': round(imposable), 'deficit': round(deficit),
            'deficit_imputable_rng': round(imputable),
            'ps': round(imposable * self.PS),
            'note': 'Revenus fonciers transparents - a reporter declaration 2044',
        }

    def optimisation_fiscale(self, profil_societe: dict) -> list:
        """
        Recommandations d'optimisation fiscale pour dirigeant.
        Retourne une liste de recommandations triees par impact.
        """
        recs = []
        ben   = profil_societe.get('benefice', 0)
        rem   = profil_societe.get('remuneration', 0)
        tmi   = profil_societe.get('tmi', 30)
        stat  = profil_societe.get('statut_actuel', 'sarl')
        ca    = profil_societe.get('ca', 0)
        type_act = profil_societe.get('type_activite', 'services')

        # 1. PER Madelin (TNS)
        if stat in ('sarl_tns', 'ei', 'eurl', 'tns_reel'):
            plaf_madelin = min(rem * 0.10 + 0.25 * self.PASS_2025,
                               8 * self.PASS_2025 * 0.10)
            eco_madelin = plaf_madelin * tmi / 100
            recs.append({
                'titre': 'PER Madelin — Deduction charges sociales',
                'impact': 'Tres eleve',
                'gain_estime': round(eco_madelin),
                'detail': f'Deductible jusqu\'a {plaf_madelin:,.0f} EUR/an (10 % rem + 25 % PASS). '
                          f'Economie estimee : {eco_madelin:,.0f} EUR a TMI {tmi} %.',
                'action': 'Ouvrir un PER Madelin aupres d\'un assureur.',
                'pour': ['Reduction d\'impot immediate', 'Constitution retraite', 'Deductible IS'],
                'contre': ['Capital bloque jusqu\'a retraite', 'Imposition a la sortie'],
            })

        # 2. Passage SAS si gerant majoritaire SARL
        if stat == 'sarl_tns' and ben > 80000:
            cot_sarl = rem * 0.45
            cot_sas  = rem * 0.75
            diff = round(cot_sas - cot_sarl)
            is_sarl = self.calculer_is(ben - rem)['is_total']
            is_sas  = self.calculer_is(ben - rem)['is_total']
            recs.append({
                'titre': 'Changement de statut : SARL => SAS',
                'impact': 'A evaluer',
                'gain_estime': 0,
                'detail': (f'Cotisations sociales SAS ({rem * 0.75:,.0f} EUR) '
                           f'vs SARL ({rem * 0.45:,.0f} EUR). '
                           f'SAS = +{diff:,.0f} EUR de charges MAIS meilleure protection sociale.'),
                'action': 'Etude chiffree avec expert-comptable. Pertinent si objectif protection sociale ou dividendes importants.',
                'pour': ['Meilleure protection sociale', 'Plus credible avec investisseurs',
                         'Flexibilite remuneration et dividendes'],
                'contre': [f'Charges sociales +{diff:,.0f} EUR/an', 'Couts juridiques transformation',
                           'Perte regime Madelin'],
            })

        # 3. Remuneration optimale
        seuil_is = self.IS_SEUIL_REDUIT  # 42 500
        if ben > seuil_is:
            rem_opt = max(0, ben - seuil_is)
            is_opt  = self.calculer_is(seuil_is)['is_total']
            ir_opt  = max(0, rem_opt * 0.90) * tmi / 100
            cout_opt = is_opt + ir_opt
            is_cur  = self.calculer_is(ben - rem)['is_total']
            ir_cur  = max(0, rem * 0.90) * tmi / 100
            cout_cur = is_cur + ir_cur
            if cout_opt < cout_cur:
                recs.append({
                    'titre': f'Remuneration optimale : {rem_opt:,.0f} EUR',
                    'impact': 'Eleve',
                    'gain_estime': round(cout_cur - cout_opt),
                    'detail': (f'Conserver {seuil_is:,.0f} EUR en benefice IS (taux 15 %) '
                               f'et vous verser {rem_opt:,.0f} EUR. '
                               f'Economie estimee : {cout_cur - cout_opt:,.0f} EUR.'),
                    'action': 'Ajuster la remuneration gerant en AG annuelle.',
                    'pour': ['Optimisation IS + IR', 'Flexibilite annuelle'],
                    'contre': ['Cotisations sociales sur remuneration', 'Gestion complexe'],
                })

        # 4. Dividendes vs salaire
        if ben > rem * 1.5:
            ben_net = self.calculer_is(ben - rem)['benefice_net']
            if ben_net > 10000:
                pfu_div = ben_net * self.PFU_TOTAL
                recs.append({
                    'titre': f'Distribuer dividendes : {ben_net:,.0f} EUR disponibles',
                    'impact': 'Eleve',
                    'gain_estime': round(ben_net - pfu_div),
                    'detail': (f'Benefice net apres IS : {ben_net:,.0f} EUR. '
                               f'PFU 30 % = {pfu_div:,.0f} EUR. '
                               f'Net percu : {ben_net - pfu_div:,.0f} EUR.'),
                    'action': 'Voter une distribution en AG. Verifier plafond 10 % capital pour eviter cotis. TNS.',
                    'pour': ['PFU 30 % fixe', 'Pas de cotisations sociales (si <= 10 % capital)'],
                    'contre': ['Double imposition (IS + IR)', 'Pas de deductibilite sociale'],
                })

        # 5. Investissement immobilier via societe
        if ben > 100000 and tmi >= 30:
            recs.append({
                'titre': 'Investissement immobilier via SCI IS',
                'impact': 'Tres eleve (long terme)',
                'gain_estime': 0,
                'detail': ('SCI a l\'IS : amortissement du bien deductible, IS 15 % sur benefices. '
                           'Permet de capitaliser a taux reduit plutot que de distribuer.'),
                'action': 'Creer une SCI a l\'IS, apporter des fonds via compte courant d\'associe.',
                'pour': ['Amortissement deductible IS', 'Capitalisation a 15 %', 'Transmission facilitee'],
                'contre': ['Impot sur plus-values a la cession (pas de regime prive)',
                           'Comptabilite obligatoire', 'Couts de structure'],
            })

        # 6. Holding
        if ben > 200000:
            recs.append({
                'titre': 'Mise en place d\'une holding',
                'impact': 'Tres eleve (restructuration)',
                'gain_estime': 0,
                'detail': ('Remonte des dividendes via regime mere-fille (quasi-exoneres IS). '
                           'Reinvestissement des benefices sans frottement fiscal immediat.'),
                'action': 'Creer une holding (SARL ou SAS), ceder les parts de la filiale.',
                'pour': ['Regime mere-fille : IS sur 5 % seulement', 'Optimisation transmission',
                         'Reinvestissement efficace'],
                'contre': ['Couts juridiques et comptables', 'Complexite administrative',
                           'Duree de mise en place'],
            })

        # 7. Auto-entrepreneur si CA faible
        if 0 < ca < 50000 and stat not in ('ae_bic', 'ae_bnc'):
            recs.append({
                'titre': 'Evaluer le statut auto-entrepreneur',
                'impact': 'Moyen',
                'gain_estime': 0,
                'detail': f'Avec un CA de {ca:,.0f} EUR, les charges AE ({int(12.9 if type_act == "vente" else 21.4)} %) '
                          f'peuvent etre inferieures au regime reel. Simulation recommandee.',
                'action': 'Comparer charges AE vs TNS reel avec expert-comptable.',
                'pour': ['Simplicite', 'Charges proportionnelles au CA'],
                'contre': ['Pas de deductibilite des charges reelles', 'Plafond CA'],
            })

        # Trier par impact
        ordre = {'Tres eleve': 0, 'Eleve': 1, 'A evaluer': 2, 'Moyen': 3}
        recs.sort(key=lambda x: ordre.get(x['impact'], 99))
        return recs

    # Constante manquante pour PER Madelin
    PASS_2025 = 47_100
