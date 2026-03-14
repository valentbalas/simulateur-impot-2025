"""
Autres revenus du patrimoine : Assurance Vie, PEA, CTO, Livrets
Sources : CGI art. 125-0 A (AV), art. 163 quinquies D (PEA), art. 200 A (PFU)
"""


class AutresRevenus:

    PFU_IR   = 0.128
    PFU_PS   = 0.172
    PFU      = 0.30
    ABATT_DIV = 0.40
    PS        = 0.172

    # Assurance vie 2024
    AV_ABATT_CEL  = 4_600
    AV_ABATT_CPL  = 9_200
    AV_SEUIL_VERS = 150_000   # Seuil versements pour taux 7.5 % ou 12.8 %
    AV_TAUX_COURT = 0.128     # < 8 ans (PFU)
    AV_TAUX_LONG_BAS = 0.075  # >= 8 ans, versements <= 150k
    AV_TAUX_LONG_HAUT = 0.128 # >= 8 ans, versements > 150k

    # Livrets reglemenentes - exoneres d'IR et PS
    LIVRET_A_PLAFOND       = 22_950
    LIVRET_DEV_DURABLE_PLAF = 12_000
    LIVRET_EPARGNE_POP     = 10_000
    LIVRET_A_TAUX          = 0.030  # 3 % en 2024

    def calculer_assurance_vie(self,
                                gain: float,
                                duree_ans: int,
                                versements_totaux: float,
                                situation: str = 'Celibataire / Divorce(e)',
                                tmi_pct: int = 30) -> dict:
        """
        Calcul de la fiscalite d'un rachat d'assurance vie.
        art. 125-0 A CGI
        """
        abatt = self.AV_ABATT_CPL if situation == 'Marie(e) / Pacse(e)' else self.AV_ABATT_CEL

        if duree_ans < 8:
            # Avant 8 ans : PFU 30 % (IR 12.8 % + PS 17.2 %)
            ir_pfu  = gain * self.AV_TAUX_COURT
            ps      = gain * self.AV_PS if hasattr(self, 'AV_PS') else gain * self.PS
            total_pfu = ir_pfu + ps
            # Option bareme
            ir_bar  = gain * (tmi_pct / 100)
            total_bar = ir_bar + ps
            meilleur = 'PFU' if total_pfu <= total_bar else 'Bareme'
            return {
                'gain': gain, 'duree_ans': duree_ans,
                'regime': 'Contrat < 8 ans',
                'abattement_applicable': 0,
                'gain_taxable': gain,
                'pfu': {
                    'ir': round(ir_pfu), 'ps': round(ps),
                    'total': round(total_pfu), 'net': round(gain - total_pfu),
                    'taux_ir': '12,8 %',
                },
                'bareme': {
                    'ir': round(ir_bar), 'ps': round(ps),
                    'total': round(total_bar), 'net': round(gain - total_bar),
                    'taux_ir': f'{tmi_pct} %',
                },
                'meilleur': meilleur,
                'economie': round(abs(total_pfu - total_bar)),
                'note': 'PFU 30 % s\'applique de plein droit avant 8 ans.',
            }
        else:
            # Apres 8 ans : taux reduit + abattement annuel
            taux_ir = (self.AV_TAUX_LONG_BAS
                       if versements_totaux <= self.AV_SEUIL_VERS
                       else self.AV_TAUX_LONG_HAUT)
            gain_apres_abatt = max(0.0, gain - abatt)
            ir      = gain_apres_abatt * taux_ir
            ps      = gain * self.PS
            total   = ir + ps
            # Option bareme
            ir_bar  = gain_apres_abatt * (tmi_pct / 100)
            total_bar = ir_bar + ps
            meilleur = 'PFU reduit' if total <= total_bar else 'Bareme'
            return {
                'gain': gain, 'duree_ans': duree_ans,
                'regime': 'Contrat >= 8 ans',
                'abattement_applicable': abatt,
                'gain_taxable': round(gain_apres_abatt),
                'pfu': {
                    'ir': round(ir), 'ps': round(ps),
                    'total': round(total), 'net': round(gain - total),
                    'taux_ir': f'{int(taux_ir*100)},{'8' if taux_ir == 0.128 else '5'} %',
                },
                'bareme': {
                    'ir': round(ir_bar), 'ps': round(ps),
                    'total': round(total_bar), 'net': round(gain - total_bar),
                    'taux_ir': f'{tmi_pct} %',
                },
                'meilleur': meilleur,
                'economie': round(abs(total - total_bar)),
                'note': (f'Abattement annuel {abatt:,.0f} EUR applique. '
                         f'Taux IR {int(taux_ir*100)} % car versements '
                         f'{"<= 150 000 EUR" if versements_totaux <= self.AV_SEUIL_VERS else "> 150 000 EUR"}.'),
            }

    def calculer_pea(self,
                     gain: float,
                     age_plan_ans: float,
                     cloture: bool = False) -> dict:
        """
        Fiscalite PEA (Plan Epargne en Actions).
        art. 163 quinquies D CGI
        """
        if age_plan_ans >= 5 and not cloture:
            # Exonere d'IR, soumis uniquement aux PS
            ps    = gain * self.PS
            total = ps
            return {
                'gain': gain, 'age_plan_ans': age_plan_ans,
                'regime': 'PEA >= 5 ans',
                'ir': 0, 'ps': round(ps), 'total': round(total),
                'net': round(gain - total),
                'taux_effectif': round(self.PS * 100, 1),
                'avantage_vs_cto': round(gain * self.PFU_IR),
                'note': 'Gains exoneres d\'IR - PS 17,2 % uniquement. Conservation du plan recommandee.',
            }
        elif age_plan_ans < 5:
            ir    = gain * self.PFU_IR
            ps    = gain * self.PS
            total = ir + ps
            return {
                'gain': gain, 'age_plan_ans': age_plan_ans,
                'regime': 'PEA < 5 ans (cloture anticipee)',
                'ir': round(ir), 'ps': round(ps), 'total': round(total),
                'net': round(gain - total),
                'taux_effectif': round(self.PFU * 100, 1),
                'note': 'Cloture avant 5 ans = PFU 30 %. TRES PENALISANT. Attendre les 5 ans si possible.',
            }
        else:  # >= 5 ans mais cloture
            ps    = gain * self.PS
            total = ps
            return {
                'gain': gain, 'age_plan_ans': age_plan_ans,
                'regime': 'PEA >= 5 ans (cloture)',
                'ir': 0, 'ps': round(ps), 'total': round(total),
                'net': round(gain - total),
                'taux_effectif': round(self.PS * 100, 1),
                'note': 'Cloture possible apres 5 ans sans penalite fiscale supplementaire.',
            }

    def calculer_cto(self,
                     plus_values: float,
                     dividendes: float,
                     tmi_pct: int = 30) -> dict:
        """
        Fiscalite Compte-Titres Ordinaire.
        Plus-values et dividendes soumis au PFU ou option bareme.
        """
        # PFU sur plus-values
        pv_ir_pfu = plus_values * self.PFU_IR
        pv_ps     = plus_values * self.PS
        pv_total_pfu = pv_ir_pfu + pv_ps
        pv_ir_bar = plus_values * (tmi_pct / 100)
        pv_total_bar = pv_ir_bar + pv_ps

        # PFU sur dividendes
        div_ir_pfu  = dividendes * self.PFU_IR
        div_ps      = dividendes * self.PS
        div_total_pfu = div_ir_pfu + div_ps
        # Option bareme dividendes : abattement 40 %
        div_base_bar = dividendes * (1 - self.ABATT_DIV)
        div_ir_bar   = div_base_bar * (tmi_pct / 100)
        div_total_bar = div_ir_bar + div_ps

        total_pfu = pv_total_pfu + div_total_pfu
        total_bar = pv_total_bar + div_total_bar
        meilleur  = 'PFU' if total_pfu <= total_bar else 'Bareme'

        return {
            'plus_values': plus_values,
            'dividendes': dividendes,
            'pfu': {
                'pv_ir': round(pv_ir_pfu), 'pv_ps': round(pv_ps),
                'div_ir': round(div_ir_pfu), 'div_ps': round(div_ps),
                'total': round(total_pfu),
                'net': round(plus_values + dividendes - total_pfu),
            },
            'bareme': {
                'pv_ir': round(pv_ir_bar), 'pv_ps': round(pv_ps),
                'div_ir': round(div_ir_bar), 'div_ps': round(div_ps),
                'total': round(total_bar),
                'net': round(plus_values + dividendes - total_bar),
            },
            'meilleur': meilleur,
            'economie': round(abs(total_pfu - total_bar)),
            'note': ('PFU 30 % s\'applique par defaut. Option bareme globale avantageuse '
                     'si TMI <= 11 %. Dividendes : abattement 40 % en option bareme.'),
        }

    def calculer_livrets(self, solde_livret_a: float,
                          solde_ldd: float = 0,
                          solde_lep: float = 0) -> dict:
        """Calcul des interets de livrets reglementes (exoneres d'IR et PS)."""
        int_a   = round(solde_livret_a * self.LIVRET_A_TAUX)
        int_ldd = round(solde_ldd * 0.030)
        int_lep = round(solde_lep * 0.060)  # Taux LEP 2024 = 6 %
        total   = int_a + int_ldd + int_lep
        return {
            'livret_a': {'solde': solde_livret_a, 'interets': int_a, 'taux': '3,0 %'},
            'ldd': {'solde': solde_ldd, 'interets': int_ldd, 'taux': '3,0 %'},
            'lep': {'solde': solde_lep, 'interets': int_lep, 'taux': '6,0 %'},
            'total_interets': total,
            'impot': 0,
            'note': 'Interets de livrets reglementes totalement exoneres d\'IR et PS.',
        }

    def conseils_patrimoine(self, tmi_pct: int, age: int,
                             situation: str) -> list:
        """Conseils patrimoniaux selon le profil."""
        conseils = []
        if tmi_pct >= 30:
            conseils.append({
                'titre': 'Assurance vie : privilegiez les contrats > 8 ans',
                'detail': 'Abattement annuel de 4 600 EUR (9 200 EUR couple) sur les gains. '
                          'Taux IR reduit a 7,5 % si versements <= 150 000 EUR.',
                'impact': 'Eleve', 'facilite': 'Facile',
            })
            conseils.append({
                'titre': 'PEA : plafonnez pour beneficier de l\'exoneration IR',
                'detail': 'Plafond 150 000 EUR (225 000 EUR couple). Apres 5 ans : '
                          'plus-values exonerees d\'IR (PS 17,2 % uniquement).',
                'impact': 'Eleve', 'facilite': 'Facile',
            })
        if tmi_pct <= 11:
            conseils.append({
                'titre': 'Option bareme pour dividendes (CTO)',
                'detail': f'A TMI {tmi_pct} %, l\'option bareme + abattement 40 % '
                          f'est plus avantageuse que le PFU 30 %. Gain potentiel important.',
                'impact': 'Moyen', 'facilite': 'Facile',
            })
        if age < 40:
            conseils.append({
                'titre': 'PER : horizon long = avantage maximal',
                'detail': 'Versements deductibles du revenu imposable. '
                          'Sortie a la retraite souvent en tranche plus basse.',
                'impact': 'Eleve', 'facilite': 'Moyen',
            })
        conseils.append({
            'titre': 'Maximisez Livret A + LDD avant tout placement',
            'detail': f'3 % nets garantis, 0 % de prelevements. '
                      f'Plafonds : Livret A 22 950 EUR + LDD 12 000 EUR.',
            'impact': 'Moyen', 'facilite': 'Tres facile',
        })
        return conseils
