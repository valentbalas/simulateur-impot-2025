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
    ABATT_SAL_MIN = 504
    ABATT_SAL_MAX = 14_426

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
