"""
Moteur fiscal Dirigeant v2 — Tous statuts
AE BNC/BIC, EI, EURL IR/IS, SARL TNS, SAS, SEL, Gérant art.62
Sources : CGI 2024, BOI-BIC, BOI-BNC, Brochure IR 2025 DGFiP
"""

# ─── CATALOGUE DES STATUTS ──────────────────────────────────────────────────
STATUTS = {
    "ae_bnc": {
        "label": "Auto-entrepreneur BNC (libérale / services)",
        "categorie": "Indépendant TNS",
        "icone": "🔵",
        "fiscal": "BNC",
        "regime_fiscal": "micro_bnc",
        "societe_is": False,
        "remuneration_separee": False,
        "dividendes": False,
        "cotisations_type": "ae_bnc",
        "taux_cotis": 0.214,
        "abattement_fiscal": 0.34,
        "seuil": 77_700,
        "cases_2042": "5HQ / 5IQ (micro-BNC — Déclarant 1 / 2)",
        "description": "Consultants, formateurs, développeurs freelance, professions libérales non réglementées.",
        "points_cles": [
            "Abattement forfaitaire 34 % sur recettes",
            "Cotisations sociales : 21,4 % sur CA",
            "Plafond CA : 77 700 €/an",
            "Pas de TVA (franchise) sous les seuils",
        ],
    },
    "bnc_reel": {
        "label": "Profession libérale BNC — régime réel (décl. 2035)",
        "categorie": "Indépendant TNS",
        "icone": "🔵",
        "fiscal": "BNC",
        "regime_fiscal": "bnc_reel",
        "societe_is": False,
        "remuneration_separee": False,
        "dividendes": False,
        "cotisations_type": "tns_reel",
        "taux_cotis": 0.43,
        "abattement_fiscal": None,
        "seuil": None,
        "cases_2042": "5QC / 5RC (déclaration contrôlée — Déclarant 1 / 2)",
        "description": "Professions libérales réglementées ou non, au-dessus du seuil micro ou sur option réel.",
        "points_cles": [
            "Charges réelles déductibles (déclaration 2035)",
            "Cotisations TNS ~ 43 % du bénéfice",
            "Madelin santé / prévoyance / retraite déductible",
            "PER déductible jusqu'à 10 % du bénéfice net",
        ],
    },
    "sel_bnc": {
        "label": "Associé de SEL (SELARL / SELAS / SELAFA)",
        "categorie": "Indépendant TNS",
        "icone": "🔵",
        "fiscal": "BNC",
        "regime_fiscal": "sel_bnc",
        "societe_is": False,
        "remuneration_separee": False,
        "dividendes": True,
        "cotisations_type": "tns_reel",
        "taux_cotis": 0.43,
        "abattement_fiscal": None,
        "seuil": 77_700,
        "cases_2042": "5QC / 5RC (BNC — pas d'abattement 10 %)",
        "description": "Avocat, médecin, expert-comptable, notaire associé d'une SEL. Rémunérations imposées en BNC depuis 2023.",
        "points_cles": [
            "Rémunérations d'activité libérale imposées en BNC (art. 92 CGI)",
            "Pas d'abattement de 10 % contrairement aux salaires",
            "Option micro-BNC possible si recettes ≤ 77 700 €",
            "Dividendes de la SEL soumis au PFU 30 %",
        ],
    },
    "ae_bic_services": {
        "label": "Auto-entrepreneur BIC — prestations de services",
        "categorie": "Indépendant TNS",
        "icone": "🟠",
        "fiscal": "BIC",
        "regime_fiscal": "micro_bic_services",
        "societe_is": False,
        "remuneration_separee": False,
        "dividendes": False,
        "cotisations_type": "ae_bic",
        "taux_cotis": 0.129,
        "abattement_fiscal": 0.50,
        "seuil": 77_700,
        "cases_2042": "5KP / 5LP (micro-BIC services — Déclarant 1 / 2)",
        "description": "Artisan, prestataire de services, réparateur, coiffeur, plombier, électricien, etc.",
        "points_cles": [
            "Abattement forfaitaire 50 % sur CA",
            "Cotisations sociales : 12,9 % sur CA",
            "Plafond CA : 77 700 €/an",
        ],
    },
    "ae_bic_ventes": {
        "label": "Auto-entrepreneur BIC — ventes / commerce",
        "categorie": "Indépendant TNS",
        "icone": "🟠",
        "fiscal": "BIC",
        "regime_fiscal": "micro_bic_ventes",
        "societe_is": False,
        "remuneration_separee": False,
        "dividendes": False,
        "cotisations_type": "ae_bic",
        "taux_cotis": 0.129,
        "abattement_fiscal": 0.71,
        "seuil": 188_700,
        "cases_2042": "5KO / 5LO (micro-BIC ventes — Déclarant 1 / 2)",
        "description": "Commerçant, e-commerce, revendeur, restaurateur (vente à emporter), hébergement.",
        "points_cles": [
            "Abattement forfaitaire 71 % sur CA",
            "Cotisations sociales : 12,9 % sur CA",
            "Plafond CA : 188 700 €/an",
        ],
    },
    "ei_bic_reel": {
        "label": "EI / EURL à l'IR — BIC régime réel",
        "categorie": "Indépendant TNS",
        "icone": "🟠",
        "fiscal": "BIC",
        "regime_fiscal": "bic_reel",
        "societe_is": False,
        "remuneration_separee": False,
        "dividendes": False,
        "cotisations_type": "tns_reel",
        "taux_cotis": 0.43,
        "abattement_fiscal": None,
        "seuil": None,
        "cases_2042": "5KC / 5LC (BIC réel — décl. 2031)",
        "description": "Commerçant, artisan BIC au-dessus des seuils micro, ou EURL non soumise à l'IS.",
        "points_cles": [
            "Charges réelles déductibles (déclaration 2031)",
            "Cotisations TNS ~ 43 % du bénéfice",
            "Amortissements déductibles",
            "Madelin et PER déductibles",
        ],
    },
    "gerant_maj_sarl": {
        "label": "Gérant majoritaire SARL / EURL à l'IS",
        "categorie": "Dirigeant société IS",
        "icone": "🟣",
        "fiscal": "Traitements & salaires (art. 62 CGI)",
        "regime_fiscal": "gerance_art62",
        "societe_is": True,
        "remuneration_separee": True,
        "dividendes": True,
        "cotisations_type": "gerant_majoritaire_sarl",
        "taux_cotis": 0.45,
        "abattement_fiscal": 0.10,
        "seuil": None,
        "cases_2042": "1GB / 1HB (gérants art. 62 CGI)",
        "description": "Gérant détenant > 50 % des parts d'une SARL/EURL soumise à l'IS.",
        "points_cles": [
            "Rémunération imposée comme salaire (abattement 10 %)",
            "Statut social TNS — cotisations ~ 45 % de la rémunération",
            "IS sur le bénéfice société (15 % ≤ 42 500 €, 25 % au-delà)",
            "Dividendes : PFU 30 % (ou barème + abattement 40 %)",
            "Madelin et PER Madelin déductibles",
        ],
    },
    "president_sas": {
        "label": "Président SAS / SASU à l'IS",
        "categorie": "Dirigeant société IS",
        "icone": "🟣",
        "fiscal": "Traitements & salaires",
        "regime_fiscal": "gerance_assimile",
        "societe_is": True,
        "remuneration_separee": True,
        "dividendes": True,
        "cotisations_type": "president_sas",
        "taux_cotis": 0.75,
        "abattement_fiscal": 0.10,
        "seuil": None,
        "cases_2042": "1AJ / 1BJ (traitements et salaires)",
        "description": "Président ou directeur général d'une SAS/SASU soumise à l'IS.",
        "points_cles": [
            "Rémunération imposée comme salaire (abattement 10 %)",
            "Assimilé salarié — cotisations patronales ~ 45 % + salariales ~ 22 %",
            "Protection sociale équivalente aux salariés",
            "Dividendes : PFU 30 % sans cotisations (si ≤ 10 % du capital)",
        ],
    },
    "gerant_min_sarl": {
        "label": "Gérant minoritaire / égalitaire SARL à l'IS",
        "categorie": "Dirigeant société IS",
        "icone": "🟣",
        "fiscal": "Traitements & salaires",
        "regime_fiscal": "gerance_assimile",
        "societe_is": True,
        "remuneration_separee": True,
        "dividendes": True,
        "cotisations_type": "president_sas",
        "taux_cotis": 0.75,
        "abattement_fiscal": 0.10,
        "seuil": None,
        "cases_2042": "1AJ / 1BJ (traitements et salaires)",
        "description": "Gérant détenant ≤ 50 % des parts d'une SARL à l'IS — assimilé salarié.",
        "points_cles": [
            "Rémunération imposée comme salaire (abattement 10 %)",
            "Statut assimilé salarié — cotisations ~ 75 % du brut",
            "Meilleure protection sociale qu'un gérant majoritaire",
            "PER déductible (pas de contrat Madelin)",
        ],
    },
}


class MoteurDirigeant:

    # ── Constantes fiscales 2024 (CGI) ──────────────────────────────────────
    IS_SEUIL_REDUIT   = 42_500
    IS_TAUX_REDUIT    = 0.15
    IS_TAUX_NORMAL    = 0.25

    PFU_IR    = 0.128
    PFU_PS    = 0.172
    PFU_TOTAL = 0.30
    ABATT_DIV = 0.40

    MICRO_BIC_VENTE_SEUIL   = 188_700
    MICRO_BIC_VENTE_ABATT   = 0.71
    MICRO_BIC_SERVICE_SEUIL = 77_700
    MICRO_BIC_SERVICE_ABATT = 0.50

    MICRO_BNC_SEUIL = 77_700
    MICRO_BNC_ABATT = 0.34

    MICRO_FONCIER_SEUIL = 15_000
    MICRO_FONCIER_ABATT = 0.30

    LMNP_NC_SEUIL = 77_700
    LMNP_NC_ABATT = 0.50
    LMNP_CL_SEUIL = 188_700
    LMNP_CL_ABATT = 0.71
    LMP_SEUIL_RECETTES = 23_000

    DEFICIT_FONCIER_PLAFOND = 10_700
    PS = 0.172
    ABATT_SAL_MIN = 504
    ABATT_SAL_MAX = 14_426
    PASS_2024 = 46_368

    # ── Compatibilité ancienne API (TNS_COTISATIONS) ─────────────────────────
    TNS_COTISATIONS = {
        "gerant_majoritaire_sarl": {
            "label": "Gérant majoritaire SARL (TNS)",
            "taux_global": 0.45,
            "detail": {
                "Maladie-maternité": "6,35 %", "Retraite de base": "17,75 %",
                "Retraite complémentaire": "7,00 %", "Invalidité-décès": "1,30 %",
                "Alloc. familiales": "0 à 3,10 %", "CSG/CRDS": "9,70 %", "CFP": "0,25 %",
            },
            "avantages": ["Charges ~ 45 % vs ~ 75 % salarié", "PER Madelin déductible"],
            "inconvenients": ["Arrêt maladie à partir J8", "Retraite souvent inférieure"],
        },
        "president_sas": {
            "label": "Président SAS/SASU (assimilé salarié)",
            "taux_global": 0.75,
            "detail": {"Cotisations patronales": "~ 45 %", "Cotisations salariales": "~ 22 %", "Total sur brut": "~ 75 %"},
            "avantages": ["Meilleure protection sociale", "Retraite alignée salariés"],
            "inconvenients": ["Charges très élevées (~ 75 %)", "Pas de Madelin"],
        },
        "ae_bic": {
            "label": "Auto-entrepreneur BIC (commerce/vente)",
            "taux_global": 0.129,
            "detail": {"Cotisations sociales": "12,8 %", "CFP": "0,1 %", "Total sur CA": "12,9 %"},
            "avantages": ["Charges minimales", "Gestion simplifiée"],
            "inconvenients": ["Plafond CA 188 700 €", "Retraite très faible"],
        },
        "ae_bnc": {
            "label": "Auto-entrepreneur BNC (libérale/services)",
            "taux_global": 0.214,
            "detail": {"Cotisations sociales": "21,2 %", "CFP": "0,2 %", "Total sur CA": "21,4 %"},
            "avantages": ["Simplicité administrative", "Charges sur recettes réelles"],
            "inconvenients": ["Plafond CA 77 700 €", "Protection sociale limitée"],
        },
        "tns_reel": {
            "label": "TNS régime réel (EI, EURL, SNC)",
            "taux_global": 0.43,
            "detail": {
                "Maladie-maternité": "6,35 %", "Retraite base+compl.": "24,75 %",
                "Prévoyance": "1,30 %", "Alloc. familiales": "0 à 3,10 %",
                "CSG/CRDS": "9,70 %", "CFP": "0,25 %",
            },
            "avantages": ["Cotisations sur bénéfice réel", "Madelin déductible"],
            "inconvenients": ["Régularisation sur N-2", "Cotisations minimales si déficit"],
        },
    }

    # ── Méthodes principales ─────────────────────────────────────────────────

    def get_statut(self, key: str) -> dict:
        return STATUTS.get(key, STATUTS["ae_bnc"])

    def calculer_revenu_tns_sans_is(self, statut_key: str, recettes: float,
                                     charges: float = 0,
                                     amortissements: float = 0) -> dict:
        """Calcul unifié pour tous les TNS sans IS."""
        s = STATUTS.get(statut_key, STATUTS["ae_bnc"])
        regime = s["regime_fiscal"]

        if regime == "micro_bnc":
            abatt = self.MICRO_BNC_ABATT
            imposable = max(0, round(recettes * (1 - abatt)))
            cotisations = round(recettes * s["taux_cotis"])
            return {
                "recettes": recettes,
                "abattement_pct": int(abatt * 100),
                "abattement_montant": round(recettes * abatt),
                "benefice_imposable": imposable,
                "cotisations": cotisations,
                "net_avant_ir": max(0, round(recettes - cotisations)),
                "type": "BNC micro",
                "case_2042": s["cases_2042"],
                "eligible_micro": recettes <= self.MICRO_BNC_SEUIL,
                "seuil": self.MICRO_BNC_SEUIL,
            }

        elif regime in ("bnc_reel", "sel_bnc"):
            benefice = recettes - charges
            imposable = max(0, round(benefice))
            cotisations = round(max(0, benefice) * s["taux_cotis"])
            return {
                "recettes": recettes,
                "charges": charges,
                "benefice": round(benefice),
                "benefice_imposable": imposable,
                "deficit": max(0, round(-benefice)),
                "cotisations": cotisations,
                "net_avant_ir": max(0, round(benefice - cotisations)),
                "type": "BNC réel (2035)",
                "case_2042": s["cases_2042"],
            }

        elif regime == "micro_bic_services":
            abatt = self.MICRO_BIC_SERVICE_ABATT
            imposable = max(0, round(recettes * (1 - abatt)))
            cotisations = round(recettes * s["taux_cotis"])
            return {
                "recettes": recettes,
                "abattement_pct": int(abatt * 100),
                "abattement_montant": round(recettes * abatt),
                "benefice_imposable": imposable,
                "cotisations": cotisations,
                "net_avant_ir": max(0, round(recettes - cotisations)),
                "type": "BIC micro (services)",
                "case_2042": s["cases_2042"],
                "eligible_micro": recettes <= self.MICRO_BIC_SERVICE_SEUIL,
                "seuil": self.MICRO_BIC_SERVICE_SEUIL,
            }

        elif regime == "micro_bic_ventes":
            abatt = self.MICRO_BIC_VENTE_ABATT
            imposable = max(0, round(recettes * (1 - abatt)))
            cotisations = round(recettes * s["taux_cotis"])
            return {
                "recettes": recettes,
                "abattement_pct": int(abatt * 100),
                "abattement_montant": round(recettes * abatt),
                "benefice_imposable": imposable,
                "cotisations": cotisations,
                "net_avant_ir": max(0, round(recettes - cotisations)),
                "type": "BIC micro (ventes)",
                "case_2042": s["cases_2042"],
                "eligible_micro": recettes <= self.MICRO_BIC_VENTE_SEUIL,
                "seuil": self.MICRO_BIC_VENTE_SEUIL,
            }

        else:  # bic_reel (EI, EURL IR)
            benefice = recettes - charges - amortissements
            imposable = max(0, round(benefice))
            cotisations = round(max(0, benefice) * s["taux_cotis"])
            return {
                "recettes": recettes,
                "charges": charges,
                "amortissements": amortissements,
                "benefice": round(benefice),
                "benefice_imposable": imposable,
                "deficit": max(0, round(-benefice)),
                "cotisations": cotisations,
                "net_avant_ir": max(0, round(benefice - cotisations)),
                "type": "BIC réel",
                "case_2042": s["cases_2042"],
            }

    def calculer_remuneration_dirigeant_is(self, statut_key: str,
                                            remuneration: float,
                                            frais_reels: bool = False,
                                            montant_fr: float = 0) -> dict:
        """Calcul rémunération pour dirigeant société IS."""
        s = STATUTS.get(statut_key, STATUTS["gerant_maj_sarl"])
        taux_cotis = s["taux_cotis"]

        if frais_reels and montant_fr > 0:
            abatt = montant_fr
            type_abatt = "Frais réels"
        else:
            abatt = max(self.ABATT_SAL_MIN, min(remuneration * 0.10, self.ABATT_SAL_MAX))
            type_abatt = "Forfait 10 %"

        imposable = max(0.0, remuneration - abatt)
        cotisations = round(remuneration * taux_cotis)
        cotis_data = self.TNS_COTISATIONS.get(s["cotisations_type"],
                                               self.TNS_COTISATIONS["tns_reel"])
        return {
            "remuneration": remuneration,
            "abattement": round(abatt),
            "type_abattement": type_abatt,
            "imposable": round(imposable),
            "cotisations": cotisations,
            "net_avant_ir": round(remuneration - cotisations),
            "case_2042": s["cases_2042"],
            "type": s["fiscal"],
            "detail_cotisations": cotis_data.get("detail", {}),
            "label_cotisations": cotis_data.get("label", ""),
            "avantages": cotis_data.get("avantages", []),
            "inconvenients": cotis_data.get("inconvenients", []),
        }

    # ── Calculs IS & Dividendes ──────────────────────────────────────────────

    def calculer_is(self, resultat_fiscal: float) -> dict:
        if resultat_fiscal <= 0:
            return {"resultat": resultat_fiscal, "is_total": 0, "is_reduit": 0,
                    "is_normal": 0, "benefice_net": 0, "taux_effectif": 0}
        b_red = min(resultat_fiscal, self.IS_SEUIL_REDUIT)
        b_nor = max(0.0, resultat_fiscal - self.IS_SEUIL_REDUIT)
        is_r = b_red * self.IS_TAUX_REDUIT
        is_n = b_nor * self.IS_TAUX_NORMAL
        is_t = round(is_r + is_n)
        return {
            "resultat": resultat_fiscal,
            "base_reduit": b_red, "is_reduit": round(is_r),
            "base_normal": b_nor, "is_normal": round(is_n),
            "is_total": is_t,
            "benefice_net": round(resultat_fiscal - is_t),
            "taux_effectif": round(is_t / resultat_fiscal * 100, 2) if resultat_fiscal else 0,
        }

    def calculer_dividendes(self, dividendes_bruts: float, tmi_pct: int) -> dict:
        ir_pfu = dividendes_bruts * self.PFU_IR
        ps_pfu = dividendes_bruts * self.PFU_PS
        tot_pfu = ir_pfu + ps_pfu
        net_pfu = dividendes_bruts - tot_pfu
        base_bar = dividendes_bruts * (1 - self.ABATT_DIV)
        ir_bar = base_bar * (tmi_pct / 100)
        ps_bar = dividendes_bruts * self.PS
        tot_bar = ir_bar + ps_bar
        net_bar = dividendes_bruts - tot_bar
        meilleur = "PFU" if tot_pfu <= tot_bar else "Barème"
        return {
            "dividendes_bruts": dividendes_bruts,
            "pfu": {
                "label": "PFU (Flat Tax 30 %)",
                "ir": round(ir_pfu), "ps": round(ps_pfu),
                "total_imposition": round(tot_pfu),
                "net_percu": round(net_pfu),
                "taux_effectif": 30.0,
            },
            "bareme": {
                "label": f"Option barème IR ({tmi_pct} %) + abatt. 40 %",
                "base_imposable": round(base_bar),
                "ir": round(ir_bar), "ps": round(ps_bar),
                "total_imposition": round(tot_bar),
                "net_percu": round(net_bar),
                "taux_effectif": round(tot_bar / dividendes_bruts * 100, 1) if dividendes_bruts else 0,
            },
            "meilleur": meilleur,
            "economie": round(abs(tot_pfu - tot_bar)),
        }

    def simuler_remuneration_vs_dividendes(self, benefice_avant_impot: float,
                                            remuneration: float, tmi_pct: int,
                                            statut_key: str = "gerant_maj_sarl") -> dict:
        s = STATUTS.get(statut_key, STATUTS["gerant_maj_sarl"])
        taux_cotis = s["taux_cotis"]
        # Stratégie A : Tout rémunération
        res_is_a = max(0, benefice_avant_impot - remuneration)
        is_a = self.calculer_is(res_is_a)["is_total"]
        abatt_a = max(self.ABATT_SAL_MIN, min(remuneration * 0.10, self.ABATT_SAL_MAX))
        ir_a = max(0, remuneration - abatt_a) * (tmi_pct / 100)
        cotis_a = round(remuneration * taux_cotis)
        cout_a = round(is_a + ir_a + cotis_a)
        net_a = round(remuneration - cotis_a - ir_a)
        # Stratégie B : Dividendes depuis bénéfice net IS
        is_b_data = self.calculer_is(benefice_avant_impot)
        is_b = is_b_data["is_total"]
        div_dispo = is_b_data["benefice_net"]
        pfu_div = round(div_dispo * self.PFU_TOTAL)
        cout_b = round(is_b + pfu_div)
        net_b = round(div_dispo - pfu_div)
        return {
            "benefice_avant_impot": benefice_avant_impot,
            "strategie_a": {
                "label": "Tout en rémunération",
                "remuneration": remuneration,
                "cotisations": cotis_a,
                "is_societe": is_a,
                "ir_personnel": round(ir_a),
                "cout_total": cout_a,
                "net_percu": net_a,
            },
            "strategie_b": {
                "label": "Dividendes (PFU 30 %)",
                "is_societe": is_b,
                "dividendes_bruts": div_dispo,
                "pfu": pfu_div,
                "cout_total": cout_b,
                "net_percu": net_b,
            },
            "meilleure": "A" if cout_a <= cout_b else "B",
            "economie": abs(cout_a - cout_b),
        }

    # ── Cotisations TNS (compatibilité) ──────────────────────────────────────

    def calculer_cotisations_tns(self, remuneration: float, statut: str) -> dict:
        data = self.TNS_COTISATIONS.get(statut, self.TNS_COTISATIONS["tns_reel"])
        taux = data["taux_global"]
        cot = round(remuneration * taux)
        return {
            "statut": data["label"], "remuneration": remuneration,
            "taux_global": taux, "cotisations": cot,
            "net_avant_ir": round(remuneration - cot),
            "detail": data["detail"],
            "avantages": data["avantages"],
            "inconvenients": data["inconvenients"],
        }

    def comparer_statuts(self, remuneration: float, tmi_pct: int) -> list:
        resultats = []
        for key, data in self.TNS_COTISATIONS.items():
            cot = round(remuneration * data["taux_global"])
            net_sc = remuneration - cot
            ir = round(max(0, net_sc * 0.90) * tmi_pct / 100)
            net_fin = round(net_sc - ir)
            resultats.append({
                "statut": key, "label": data["label"],
                "taux_charges": int(data["taux_global"] * 100),
                "cotisations": cot, "ir_estime": ir, "net_final": net_fin,
            })
        resultats.sort(key=lambda x: -x["net_final"])
        return resultats

    # ── Immobilier ───────────────────────────────────────────────────────────

    def calculer_foncier_micro(self, revenus_bruts: float) -> dict:
        imposable = round(revenus_bruts * (1 - self.MICRO_FONCIER_ABATT))
        return {
            "revenus_bruts": revenus_bruts,
            "abattement_pct": 30,
            "abattement_montant": round(revenus_bruts * self.MICRO_FONCIER_ABATT),
            "imposable": imposable,
            "eligible": revenus_bruts <= self.MICRO_FONCIER_SEUIL,
            "seuil": self.MICRO_FONCIER_SEUIL,
            "type": "Micro-foncier",
            "ps": round(imposable * self.PS),
        }

    def calculer_foncier_reel(self, revenus_bruts: float, interets_emprunt: float = 0,
                               charges_courantes: float = 0, travaux: float = 0,
                               taxe_fonciere: float = 0, frais_gestion: float = 0) -> dict:
        total_charges = interets_emprunt + charges_courantes + travaux + taxe_fonciere + frais_gestion
        resultat = revenus_bruts - total_charges
        deficit = max(0.0, -resultat)
        deficit_global = min(max(0.0, deficit - interets_emprunt),
                             self.DEFICIT_FONCIER_PLAFOND) if deficit > 0 else 0
        imposable = max(0, round(resultat))
        return {
            "revenus_bruts": revenus_bruts,
            "interets_emprunt": interets_emprunt,
            "charges_courantes": charges_courantes,
            "travaux": travaux,
            "taxe_fonciere": taxe_fonciere,
            "frais_gestion": frais_gestion,
            "total_charges": round(total_charges),
            "resultat": round(resultat),
            "imposable": imposable,
            "deficit_total": round(deficit),
            "deficit_imputable_rng": round(deficit_global),
            "deficit_report_foncier": round(max(0, deficit - deficit_global)),
            "type": "Foncier réel",
            "ps": round(imposable * self.PS),
        }

    def calculer_lmnp(self, recettes: float, classe: bool = False,
                      regime: str = "micro", charges: float = 0,
                      amortissements: float = 0) -> dict:
        if regime == "micro":
            abatt = self.LMNP_CL_ABATT if classe else self.LMNP_NC_ABATT
            seuil = self.LMNP_CL_SEUIL if classe else self.LMNP_NC_SEUIL
            imposable = round(recettes * (1 - abatt))
            return {
                "recettes": recettes, "type_bien": "Classé" if classe else "Non classé",
                "regime": "Micro-BIC LMNP",
                "abattement_pct": int(abatt * 100),
                "imposable": imposable,
                "eligible": recettes <= seuil,
                "seuil": seuil,
                "ps": round(imposable * self.PS),
            }
        else:
            benefice = recettes - charges - amortissements
            imposable = max(0, round(benefice))
            return {
                "recettes": recettes, "charges": charges, "amortissements": amortissements,
                "regime": "LMNP Réel",
                "benefice": round(benefice),
                "imposable": imposable,
                "deficit": max(0, round(-benefice)),
                "note": "Déficit reportable 10 ans sur BIC LMNP uniquement",
                "ps": round(imposable * self.PS) if benefice > 0 else 0,
            }

    def calculer_lmp(self, recettes: float, charges: float,
                     amortissements: float, autres_revenus_foyer: float) -> dict:
        lmp_ok = (recettes > self.LMP_SEUIL_RECETTES and recettes > autres_revenus_foyer)
        benefice = recettes - charges - amortissements
        imposable = max(0, round(benefice))
        return {
            "recettes": recettes, "charges": charges, "amortissements": amortissements,
            "statut_lmp": lmp_ok,
            "benefice": round(benefice),
            "imposable": imposable,
            "deficit": max(0, round(-benefice)),
            "avantages": [
                "Déficit imputable sur revenu global sans limite" if lmp_ok else "Statut LMP non atteint",
                "Plus-values régime professionnel (exon. si recettes < 90 000 €)",
            ],
        }

    def calculer_sci_ir(self, quote_part_resultat: float) -> dict:
        imposable = max(0.0, quote_part_resultat)
        deficit = max(0.0, -quote_part_resultat)
        imputable = min(deficit, self.DEFICIT_FONCIER_PLAFOND)
        return {
            "quote_part": quote_part_resultat,
            "imposable": round(imposable),
            "deficit": round(deficit),
            "deficit_imputable_rng": round(imputable),
            "ps": round(imposable * self.PS),
            "note": "Revenus fonciers transparents → reporter déclaration 2044",
        }

    def calculer_sci_is(self, resultat_fiscal: float, quote_part: float = 1.0) -> dict:
        is_data = self.calculer_is(resultat_fiscal)
        ben_net = is_data["benefice_net"]
        div_pot = round(ben_net * quote_part)
        return {
            **is_data,
            "quote_part_detention": quote_part,
            "dividende_potentiel": div_pot,
            "note": "Dividendes distribués soumis au PFU 30 % (ou option barème)",
        }

    # Alias compatibilité
    def calculer_bic_micro(self, ca: float, type_act: str = "services") -> dict:
        key = "ae_bic_ventes" if type_act == "vente" else "ae_bic_services"
        return self.calculer_revenu_tns_sans_is(key, ca)

    def calculer_bic_reel(self, ca: float, charges: float, amortissements: float = 0) -> dict:
        return self.calculer_revenu_tns_sans_is("ei_bic_reel", ca, charges, amortissements)

    def calculer_bnc_micro(self, recettes: float) -> dict:
        return self.calculer_revenu_tns_sans_is("ae_bnc", recettes)

    def calculer_bnc_reel(self, recettes: float, charges: float) -> dict:
        return self.calculer_revenu_tns_sans_is("bnc_reel", recettes, charges)

    def calculer_gerance(self, remuneration: float, frais_reels: bool = False,
                         montant_fr: float = 0) -> dict:
        return self.calculer_remuneration_dirigeant_is(
            "gerant_maj_sarl", remuneration, frais_reels, montant_fr)

    # ── Optimisation fiscale ─────────────────────────────────────────────────

    def optimisation_fiscale(self, profil: dict) -> list:
        recs = []
        statut_key = profil.get("statut_key", profil.get("statut_actuel", "ae_bnc"))
        s = STATUTS.get(statut_key, STATUTS["ae_bnc"])
        ben = profil.get("benefice", 0)
        rem = profil.get("remuneration", 0)
        recettes = profil.get("recettes", profil.get("ca", ben))
        tmi = profil.get("tmi", 30)
        societe_is = s["societe_is"]

        # 1. PER Madelin (TNS uniquement)
        if s["cotisations_type"] in ("ae_bnc", "tns_reel", "gerant_majoritaire_sarl"):
            base_per = rem if rem > 0 else max(ben, recettes * 0.30)
            plaf = min(base_per * 0.10 + 0.25 * self.PASS_2024,
                       8 * self.PASS_2024 * 0.10)
            eco = round(plaf * tmi / 100)
            recs.append({
                "titre": "PER Madelin — Épargne retraite déductible",
                "impact": "Très élevé",
                "gain_estime": eco,
                "icone": "🏦",
                "detail": f"Déductible jusqu'à {plaf:,.0f} € / an (10 % rém. + 25 % PASS). Économie estimée : {eco:,.0f} € à TMI {tmi} %.",
                "action": "Ouvrir un PER Madelin auprès d'un assureur ou d'une banque.",
                "pour": ["Réduction d'impôt immédiate", "Constitution retraite", "Déductible IS"],
                "contre": ["Capital bloqué jusqu'à la retraite", "Imposition à la sortie"],
            })

        # 2. Rémunération optimale IS
        if societe_is and ben > self.IS_SEUIL_REDUIT:
            rem_opt = max(0, ben - self.IS_SEUIL_REDUIT)
            is_opt = self.calculer_is(self.IS_SEUIL_REDUIT)["is_total"]
            ir_opt = max(0, rem_opt * 0.90) * tmi / 100
            cout_opt = is_opt + ir_opt
            is_cur = self.calculer_is(max(0, ben - rem))["is_total"]
            ir_cur = max(0, rem * 0.90) * tmi / 100
            cout_cur = is_cur + ir_cur
            if cout_opt < cout_cur:
                recs.append({
                    "titre": f"Rémunération optimale : {rem_opt:,.0f} €",
                    "impact": "Élevé",
                    "gain_estime": round(cout_cur - cout_opt),
                    "icone": "⚖️",
                    "detail": f"Conserver {self.IS_SEUIL_REDUIT:,.0f} € en bénéfice IS (taux 15 %) et vous verser {rem_opt:,.0f} €. Économie estimée : {cout_cur - cout_opt:,.0f} €.",
                    "action": "Ajuster la rémunération gérant en AG annuelle.",
                    "pour": ["Optimisation IS + IR", "Flexibilité annuelle"],
                    "contre": ["Cotisations sociales sur rémunération"],
                })

        # 3. Distribuer des dividendes
        if societe_is and ben > rem * 1.2:
            ben_net = self.calculer_is(max(0, ben - rem))["benefice_net"]
            if ben_net > 10_000:
                pfu = ben_net * self.PFU_TOTAL
                recs.append({
                    "titre": f"Distribuer des dividendes : {ben_net:,.0f} € disponibles",
                    "impact": "Élevé",
                    "gain_estime": round(ben_net - pfu),
                    "icone": "💰",
                    "detail": f"Bénéfice net après IS : {ben_net:,.0f} €. PFU 30 % = {pfu:,.0f} €. Net perçu : {ben_net - pfu:,.0f} €.",
                    "action": "Voter une distribution en AG. Vérifier le plafond 10 % du capital.",
                    "pour": ["PFU 30 % fixe", "Pas de cotisations (si ≤ 10 % capital)"],
                    "contre": ["Double imposition (IS + IR)"],
                })

        # 4. SARL → SAS si bénéfice élevé
        if statut_key == "gerant_maj_sarl" and ben > 80_000:
            diff_cotis = round(rem * (0.75 - 0.45))
            recs.append({
                "titre": "Évaluer le passage SARL → SAS",
                "impact": "À évaluer",
                "gain_estime": 0,
                "icone": "🔄",
                "detail": f"SAS : cotisations ~ 75 % vs SARL TNS : ~ 45 %. Surcoût : +{diff_cotis:,.0f} € / an MAIS meilleure protection sociale et crédibilité.",
                "action": "Étude chiffrée recommandée avec expert-comptable.",
                "pour": ["Meilleure protection sociale", "Crédibilité investisseurs"],
                "contre": [f"Charges sociales +{diff_cotis:,.0f} € / an", "Coûts juridiques"],
            })

        # 5. Holding si bénéfice > 200k
        if societe_is and ben > 200_000:
            recs.append({
                "titre": "Mise en place d'une holding",
                "impact": "Très élevé (restructuration)",
                "gain_estime": 0,
                "icone": "🏛️",
                "detail": "Régime mère-fille : remontée des dividendes quasi-exonérée d'IS. Réinvestissement des bénéfices sans frottement fiscal.",
                "action": "Créer une holding (SARL ou SAS), apporter les parts de la filiale.",
                "pour": ["IS sur 5 % seulement (mère-fille)", "Optimisation transmission"],
                "contre": ["Coûts juridiques et comptables", "Complexité administrative"],
            })

        # 6. Option micro-BNC pour SEL
        if statut_key == "sel_bnc" and 0 < recettes <= self.MICRO_BNC_SEUIL:
            eco_micro = round(recettes * self.MICRO_BNC_ABATT * tmi / 100)
            recs.append({
                "titre": "Option micro-BNC disponible",
                "impact": "Moyen",
                "gain_estime": eco_micro,
                "icone": "📋",
                "detail": f"Vos recettes ({recettes:,.0f} €) sont sous le seuil micro-BNC (77 700 €). Abattement forfaitaire 34 %.",
                "action": "Comparer micro-BNC vs déclaration contrôlée 2035 avec votre comptable.",
                "pour": ["Simplicité administrative", "Abattement 34 % sans justificatifs"],
                "contre": ["Intéressant seulement si charges réelles < 34 %"],
            })

        # 7. SCI à l'IS pour investissement immobilier
        if societe_is and ben > 100_000 and tmi >= 30:
            recs.append({
                "titre": "Investissement immobilier via SCI à l'IS",
                "impact": "Très élevé (long terme)",
                "gain_estime": 0,
                "icone": "🏠",
                "detail": "SCI à l'IS : amortissement du bien déductible, IS 15 % sur bénéfices. Capitaliser à taux réduit plutôt que distribuer.",
                "action": "Créer une SCI à l'IS, apporter des fonds via compte courant d'associé.",
                "pour": ["Amortissement déductible IS", "Capitalisation à 15 %", "Transmission facilitée"],
                "contre": ["Impôt sur plus-values à la cession (pas de régime privé)", "Comptabilité obligatoire"],
            })

        ordre = {"Très élevé": 0, "Très élevé (restructuration)": 1,
                 "Très élevé (long terme)": 1, "Élevé": 2, "À évaluer": 3, "Moyen": 4}
        recs.sort(key=lambda x: ordre.get(x["impact"], 99))
        return recs
