import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.ticker import PercentFormatter

print(os.getcwd())


class EkStCalculator:
    def __init__(self, steuerfreibetrag=9408, methoden_suffix='', einkommen_ende=250000, verbose=True,
                 partielles_grundeinkommen=300.*12, ipge=False, ek_stepsize=100,
                 print_vorstufen=False):
        self.verbose = verbose
        self.steuerfreibetrag = steuerfreibetrag
        self.steuerfreibetrag_aktuell = 9408
        self.methoden_suffix = methoden_suffix
        self.jahreseinkommen_vec = np.arange(1, einkommen_ende, ek_stepsize)
        self.partielles_grundeinkommen = partielles_grundeinkommen
        # ipge: inklusive partiellem Grundeinkommen
        self.ipge = ipge
        self.einkommenssteuersatz_ipge = None
        self.einkommenssteuersatz_ipge_sgs = None
        self.einkommenssteuersatz_ipge_bgs = None
        self.einkommenssteuersatz = None
        self.berechnete_sozialabgaben = None
        self.netto_ipge = None
        self.netto_normal = None
        self.netto_ipge_mitabgaben = None
        self.netto_normal_mitabgaben = None
        self.sozialabgaben_berechnet = False
        self.stufe1_bg = 9409
        self.stufe2_bg = 14533
        self.stufe3_bg = 57052
        self.stufe4_bg = 270500
        self.stufe5_bg = 1e6
        self.stufe6_bg = 1e6 + 4
        self.stufe7_bg = 1e6 + 8
        self.stufe8_bg = 1e6 + 12
        self.stufe1_s = 0.14
        self.stufe2_s = 0.2397
        self.stufe3_s = 0.42
        self.stufe4_s = 0.45
        self.stufe5_s = 1.0
        self.stufe6_s = 1.0
        self.stufe7_s = 1.0
        self.stufe8_s = 1.0
        self.stufe1_proportional = False
        self.stufe2_proportional = False
        self.stufe3_proportional = True
        self.stufe4_proportional = True
        self.stufe5_proportional = True
        self.stufe6_proportional = True
        self.stufe7_proportional = True
        self.stufe8_proportional = True
        self.current_method_name = 'aktuelle EkSt'
        self.ekst_methoden = []
        self.ekst_methoden_berechnet = {}
        self.ekst_methoden_sgs = {}
        self.ekst_methoden_bgs = {}
        self.print_vorstufen = print_vorstufen

    def update_parameter(self, stufe1_bg=9409, stufe2_bg=14533, stufe3_bg=57052, stufe4_bg=270500,
                         stufe5_bg=1e6, stufe6_bg=1e6+4, stufe7_bg=1e6+8, stufe8_bg=1e6+12,
                         stufe1_s=0.14, stufe2_s=0.2397, stufe3_s=0.42, stufe4_s=0.45,
                         stufe5_s=1.0, stufe6_s=1.0, stufe7_s=1.0, stufe8_s=1.0,
                         steuerfreibetrag=9408,
                         stufe1_proportional=False, stufe2_proportional=False,
                         stufe3_proportional=True, stufe4_proportional=True,
                         stufe5_proportional=True, stufe6_proportional=True,
                         stufe7_proportional=True, stufe8_proportional=True,
                         current_method_name='aktuelle EkSt', color='orange'):
        self.stufe1_bg = stufe1_bg
        self.stufe2_bg = stufe2_bg
        self.stufe3_bg = stufe3_bg
        self.stufe4_bg = stufe4_bg
        self.stufe5_bg = stufe5_bg
        self.stufe6_bg = stufe6_bg
        self.stufe7_bg = stufe7_bg
        self.stufe8_bg = stufe8_bg
        self.stufe1_s = stufe1_s
        self.stufe2_s = stufe2_s
        self.stufe3_s = stufe3_s
        self.stufe4_s = stufe4_s
        self.stufe5_s = stufe5_s
        self.stufe6_s = stufe6_s
        self.stufe7_s = stufe7_s
        self.stufe8_s = stufe8_s
        self.steuerfreibetrag = steuerfreibetrag
        self.stufe1_proportional = stufe1_proportional
        self.stufe2_proportional = stufe2_proportional
        self.stufe3_proportional = stufe3_proportional
        self.stufe4_proportional = stufe4_proportional
        self.stufe5_proportional = stufe5_proportional
        self.stufe6_proportional = stufe6_proportional
        self.stufe7_proportional = stufe7_proportional
        self.stufe8_proportional = stufe8_proportional
        self.current_method_name = current_method_name

    @staticmethod
    def sozialabgaben(jahreseinkommen, kinder=False, verbose=False, minijob_grenze=450):
        if jahreseinkommen < 12*minijob_grenze:
            if verbose:
                print('Grenze von 450€ pro Monat nicht unterschritten - keine Abgaben fällig!')
            return 0
        else:
            if jahreseinkommen >= 58050:
                jahreseinkommen_kv_pv = 58050
            else:
                jahreseinkommen_kv_pv = jahreseinkommen
            if verbose:
                print('Das berücksichtigte Jahreseinkommen beträgt: {}'.format(jahreseinkommen_kv_pv))
            # Krankenversicherung
            kv_abgabe_aeB = 0.073 * jahreseinkommen_kv_pv
            kv_abgabe_eeB = 0.07 * jahreseinkommen_kv_pv
            kv_abgabe_zB = 0.013 * jahreseinkommen_kv_pv
            # Pflegeversicherung
            pv_abgabe = 0.01525 * jahreseinkommen_kv_pv
            pv_abgabe_Bz = 0
            if not kinder:
                pv_abgabe_Bz = 0.0025 * jahreseinkommen_kv_pv
            if jahreseinkommen >= 85.200:
                jahreseinkommen_av_rv = 85.200
            else:
                jahreseinkommen_av_rv = jahreseinkommen
            # Rentenversicherung
            rv_abgabe = 0.093 * jahreseinkommen_av_rv
            # Arbeitslosenversicherung
            av_abgabe = 0.012 * jahreseinkommen_av_rv
            if verbose:
                print('folgende Abgaben wurden berechnet: '
                      '\n kv_abgabe_aeB: {:.3f} \n kv_abgabe_eeB: {:.3f} '
                      '\n kv_abgabe_zB: {:.3f} \n pv_abgabe: {:.3f} '
                      '\n pv_abgabe_Bz: {:.3f} \n rv_abgabe: {:.3f} '
                      '\n av_abgabe: {:.3f}'.format(kv_abgabe_aeB, kv_abgabe_eeB, kv_abgabe_zB,
                                                    pv_abgabe, pv_abgabe_Bz, rv_abgabe, av_abgabe))
            abgaben_liste = [kv_abgabe_aeB, kv_abgabe_eeB, kv_abgabe_zB, pv_abgabe, pv_abgabe_Bz, rv_abgabe, av_abgabe]
            abgaben = np.sum(abgaben_liste)
            return abgaben

    @staticmethod
    def p_n(s_1, s_2, e_1, e_2):
        if e_2-e_1 == 0:
            return 0
        else:
            return (s_2 - s_1) / ((e_2 - e_1) * 2)

    @staticmethod
    def steuerfunktion(s, b, p, c=0.):
        # Einkommenssteuerfunktion
        # {\displaystyle S(B)=B\cdot (p_{n}\cdot B+s_{gn})+C_{n} =
        # p_{n}\cdot B^{2}+s_{gn}\cdot B+C_{n}\;\;|\;{\text{ in Zone n}}}
        return s*b + p*(b**2) + c

    def einkommenssteuer(self, x, steuerfreibetrag=9408):
        p_1 = self.p_n(self.stufe1_s, self.stufe2_s, self.stufe1_bg, self.stufe2_bg)
        p_2 = self.p_n(self.stufe2_s, self.stufe3_s, self.stufe2_bg, self.stufe3_bg)
        p_3 = self.p_n(self.stufe3_s, self.stufe4_s, self.stufe3_bg, self.stufe4_bg)
        p_4 = self.p_n(self.stufe4_s, self.stufe5_s, self.stufe4_bg, self.stufe5_bg)
        p_5 = self.p_n(self.stufe5_s, self.stufe6_s, self.stufe5_bg, self.stufe6_bg)
        p_6 = self.p_n(self.stufe6_s, self.stufe7_s, self.stufe6_bg, self.stufe7_bg)
        p_7 = self.p_n(self.stufe7_s, self.stufe8_s, self.stufe7_bg, self.stufe8_bg)
        p_8 = self.p_n(self.stufe8_s, self.stufe8_s, self.stufe8_bg, self.stufe8_bg)
        steuer_vorstufe_1 = self.steuerfunktion(s=self.stufe1_s, b=self.stufe2_bg - self.stufe1_bg, p=p_1,
                                                c=0)
        steuer_vorstufe_2 = self.steuerfunktion(s=self.stufe2_s, b=self.stufe3_bg - self.stufe2_bg, p=p_2,
                                                c=steuer_vorstufe_1)
        steuer_vorstufe_3 = self.steuerfunktion(s=self.stufe3_s, b=self.stufe4_bg - self.stufe3_bg, p=p_3,
                                                c=steuer_vorstufe_2)
        steuer_vorstufe_4 = self.steuerfunktion(s=self.stufe4_s, b=self.stufe5_bg - self.stufe4_bg, p=p_4,
                                                c=steuer_vorstufe_3)
        steuer_vorstufe_5 = self.steuerfunktion(s=self.stufe5_s, b=self.stufe6_bg - self.stufe5_bg, p=p_5,
                                                c=steuer_vorstufe_4)
        steuer_vorstufe_6 = self.steuerfunktion(s=self.stufe6_s, b=self.stufe7_bg - self.stufe6_bg, p=p_6,
                                                c=steuer_vorstufe_5)
        steuer_vorstufe_7 = self.steuerfunktion(s=self.stufe7_s, b=self.stufe8_bg - self.stufe7_bg, p=p_7,
                                                c=steuer_vorstufe_6)
        if x == 1 and self.print_vorstufen:
            print(f'steuer_vorstufe_1 {steuer_vorstufe_1}')
            print(f'steuer_vorstufe_2 {steuer_vorstufe_2}')
            print(f'steuer_vorstufe_3 {steuer_vorstufe_3}')
        # Tarifstufe 0
        if x <= steuerfreibetrag:
            steuer = 0
        # Tarifstufe 1
        elif self.stufe2_bg >= x >= steuerfreibetrag+1:
            b = x - steuerfreibetrag
            if self.stufe1_proportional:
                p_1 = 0
            steuer = self.steuerfunktion(s=self.stufe1_s, b=b, p=p_1,
                                         c=0)
        # Tarifstufe 2
        elif self.stufe3_bg >= x >= self.stufe2_bg+1:
            b = x - self.stufe2_bg-1
            if self.stufe2_proportional:
                p_2 = 0
            steuer = self.steuerfunktion(s=self.stufe2_s, b=b, p=p_2,
                                         c=steuer_vorstufe_1)
        # Tarifstufe 3
        elif self.stufe4_bg >= x >= self.stufe3_bg+1:
            b = x - self.stufe3_bg
            if self.stufe3_proportional:
                p_3 = 0
            steuer = self.steuerfunktion(s=self.stufe3_s, b=b, p=p_3,
                                         c=steuer_vorstufe_2)
        # Tarifstufe 4
        elif self.stufe5_bg >= x >= self.stufe4_bg+1:
            b = x - self.stufe4_bg
            if self.stufe4_proportional:
                p_4 = 0
            steuer = self.steuerfunktion(s=self.stufe4_s, b=b, p=p_4,
                                         c=steuer_vorstufe_3)
        # Tarifstufe 5
        elif self.stufe6_bg >= x >= self.stufe5_bg+1:
            b = x - self.stufe5_bg
            if self.stufe5_proportional:
                p_5 = 0
            steuer = self.steuerfunktion(s=self.stufe5_s, b=b, p=p_5,
                                         c=steuer_vorstufe_4)
        # Tarifstufe 6
        elif self.stufe7_bg >= x >= self.stufe6_bg+1:
            b = x - self.stufe6_bg
            if self.stufe6_proportional:
                p_6 = 0
            steuer = self.steuerfunktion(s=self.stufe6_s, b=b, p=p_6,
                                         c=steuer_vorstufe_5)
        # Tarifstufe 7
        elif self.stufe8_bg >= x >= self.stufe7_bg+1:
            b = x - self.stufe7_bg
            if self.stufe7_proportional:
                p_7 = 0
            steuer = self.steuerfunktion(s=self.stufe7_s, b=b, p=p_7,
                                         c=steuer_vorstufe_6)
        # Tarifstufe 8
        elif x >= self.stufe8_bg+1:
            b = x - self.stufe8_bg
            if self.stufe8_proportional:
                p_8 = 0
            steuer = self.steuerfunktion(s=self.stufe8_s, b=b, p=p_8,
                                         c=steuer_vorstufe_7)
        else:
            steuer = 0
        return steuer

    def calculate_standard_ekst(self):
        old_state = self.verbose
        self.verbose = False
        self.einkommenssteuersatz = [self.einkommenssteuer(x, steuerfreibetrag=self.steuerfreibetrag_aktuell) / x
                                     for x in self.jahreseinkommen_vec]
        self.verbose = old_state
        n_ekst_methoden = len(self.ekst_methoden)
        self.add_method(
            stufe1_bg=0,
            stufe2_bg=self.stufe1_bg - self.partielles_grundeinkommen,
            stufe3_bg=self.stufe2_bg - self.partielles_grundeinkommen,
            stufe4_bg=self.stufe3_bg - self.partielles_grundeinkommen,
            stufe5_bg=self.stufe4_bg - self.partielles_grundeinkommen,
            stufe6_bg=self.stufe5_bg - self.partielles_grundeinkommen,
            stufe7_bg=self.stufe5_bg,
            stufe8_bg=self.stufe5_bg,
            stufe1_s=self.stufe1_s,
            stufe2_s=self.stufe1_s,
            stufe3_s=self.stufe2_s,
            stufe4_s=self.stufe3_s,
            stufe5_s=self.stufe4_s,
            stufe6_s=self.stufe5_s,
            stufe7_s=self.stufe6_s,
            steuerfreibetrag=0,
            stufe1_proportional=False,
            stufe2_proportional=False,
            stufe3_proportional=False,
            stufe4_proportional=False,
            stufe5_proportional=True,
            stufe6_proportional=True,
            stufe7_proportional=True,
            stufe8_proportional=True,
            current_method_name='aktuelle EkSt mit partiellem Grundeinkommen')
        self.calculate_extra_ekst()
        if self.ekst_methoden[n_ekst_methoden]['current_method_name'] == 'aktuelle EkSt mit partiellem Grundeinkommen':
            self.einkommenssteuersatz_ipge = self.ekst_methoden_berechnet['aktuelle EkSt mit partiellem Grundeinkommen']
            self.einkommenssteuersatz_ipge_sgs = self.ekst_methoden_sgs['aktuelle EkSt mit partiellem Grundeinkommen']
            self.einkommenssteuersatz_ipge_bgs = self.ekst_methoden_bgs['aktuelle EkSt mit partiellem Grundeinkommen']
            self.ekst_methoden.pop(-1)

    def add_method(self, stufe1_bg, stufe2_bg, stufe3_bg, stufe4_bg, stufe5_bg,
                   stufe1_s, stufe2_s, stufe3_s, stufe4_s, stufe5_s, steuerfreibetrag,
                   stufe1_proportional, stufe2_proportional, stufe3_proportional, stufe4_proportional,
                   stufe5_proportional, current_method_name, stufe6_bg=1e6+4, stufe7_bg=1e6+8, stufe8_bg=1e6+12,
                   stufe6_s=1.0, stufe7_s=1.0, stufe8_s=1.0, stufe6_proportional=True, stufe7_proportional=True,
                   stufe8_proportional=True, color='blue'):
        self.ekst_methoden.append(
            {'stufe1_bg': stufe1_bg, 'stufe2_bg': stufe2_bg, 'stufe3_bg': stufe3_bg, 'stufe4_bg': stufe4_bg,
             'stufe5_bg': stufe5_bg, 'stufe6_bg': stufe6_bg, 'stufe7_bg': stufe7_bg, 'stufe8_bg': stufe8_bg,
             'stufe1_s': stufe1_s, 'stufe2_s': stufe2_s, 'stufe3_s': stufe3_s, 'stufe4_s': stufe4_s,
             'stufe5_s': stufe5_s, 'stufe6_s': stufe6_s, 'stufe7_s': stufe7_s, 'stufe8_s': stufe8_s,
             'steuerfreibetrag': steuerfreibetrag,
             'stufe1_proportional': stufe1_proportional, 'stufe2_proportional': stufe2_proportional,
             'stufe3_proportional': stufe3_proportional, 'stufe4_proportional': stufe4_proportional,
             'stufe5_proportional': stufe5_proportional, 'stufe6_proportional': stufe6_proportional,
             'stufe7_proportional': stufe7_proportional, 'stufe8_proportional': stufe8_proportional,
             'current_method_name': current_method_name, 'color': color})

    def calculate_extra_ekst(self):
        for method in self.ekst_methoden:
            self.update_parameter(**method)
            self.ekst_methoden_berechnet[method['current_method_name']] = [self.einkommenssteuer(
                x, steuerfreibetrag=method['steuerfreibetrag']) / x for x in self.jahreseinkommen_vec]
            # build the Grenzsteuersatz vector with bgs and sgs
            self.ekst_methoden_sgs[method['current_method_name']] = []
            self.ekst_methoden_bgs[method['current_method_name']] = []
            if method['steuerfreibetrag'] != 0:
                self.ekst_methoden_sgs[method['current_method_name']].append(0)
                self.ekst_methoden_bgs[method['current_method_name']].append(0)
                self.ekst_methoden_sgs[method['current_method_name']].append(0)
                self.ekst_methoden_bgs[method['current_method_name']].append(method['steuerfreibetrag'])
            for i in range(1, 6):
                if method['stufe'+str(i)+'_proportional']:
                    self.ekst_methoden_sgs[method['current_method_name']].append(method['stufe'+str(i)+'_s'])
                    self.ekst_methoden_bgs[method['current_method_name']].append(method['stufe'+str(i)+'_bg'])
                    if i < 5:
                        self.ekst_methoden_sgs[method['current_method_name']].append(method['stufe' + str(i) + '_s'])
                        self.ekst_methoden_bgs[method['current_method_name']].append(method['stufe'+str(i+1)+'_bg']-1)
                else:
                    self.ekst_methoden_sgs[method['current_method_name']].append(method['stufe'+str(i)+'_s'])
                    self.ekst_methoden_bgs[method['current_method_name']].append(method['stufe'+str(i)+'_bg'])

        # return to default parameters
        self.update_parameter()

    def berechne_netto_jahreseinkommen(self):
        if self.einkommenssteuersatz is None:
            self.calculate_standard_ekst()
            if len(self.ekst_methoden) > 0:
                self.calculate_extra_ekst()
        self.berechnete_sozialabgaben = [self.sozialabgaben(x, verbose=False) for x in self.jahreseinkommen_vec]
        if self.ipge:
            self.netto_ipge = [y+self.partielles_grundeinkommen for y in
                              np.subtract(self.jahreseinkommen_vec,
                                          np.multiply(self.jahreseinkommen_vec,
                                                      self.einkommenssteuersatz_ipge))]
            self.netto_ipge_mitabgaben = [y + self.partielles_grundeinkommen
                                          for y in np.subtract(self.netto_ipge,
                                                               self.berechnete_sozialabgaben)]
        self.netto_normal = [y+self.partielles_grundeinkommen for y in
                             np.subtract(self.jahreseinkommen_vec,
                                         np.multiply(self.jahreseinkommen_vec,
                                                     self.einkommenssteuersatz))]
        self.netto_normal_mitabgaben = np.subtract(self.netto_normal,
                                                   self.berechnete_sozialabgaben)
        self.sozialabgaben_berechnet = True

    def plot_einkommenssteuersatz(self, limit=None,
                                  title="Einkommenssteuer_Calculator Vergleich 'Kindergeld für Alle' \n",
                                  plot_ipge=True) -> None:
        if self.einkommenssteuersatz is None:
            self.calculate_standard_ekst()
            if len(self.ekst_methoden) > 0:
                self.calculate_extra_ekst()
        """
        EkSt. Plot
        """
        fig1, ax1 = plt.subplots(figsize=(15, 7))
        if plot_ipge:
            ax1.plot(self.jahreseinkommen_vec, self.einkommenssteuersatz_ipge,
                     label="'Kindergeld für Alle' Ansatz", color='green', linestyle='--')
            ax1.plot(self.einkommenssteuersatz_ipge_bgs,
                     self.einkommenssteuersatz_ipge_sgs,
                     label="'Kindergeld für Alle' Ansatz" + ' Grenzsteuersatz', color='green')
        ax1.plot([0, self.steuerfreibetrag, self.stufe1_bg, self.stufe2_bg, self.stufe3_bg, self.stufe4_bg],
                 [0, 0, self.stufe1_s, self.stufe2_s, self.stufe3_s, self.stufe4_s],
                 label=self.current_method_name + ' Grenzsteuersatz', color='orange')
        ax1.plot(self.jahreseinkommen_vec, self.einkommenssteuersatz,
                 label=self.current_method_name, color='orange', linestyle='--')
        bgs = ['stufe1_bg', 'stufe2_bg', 'stufe3_bg', 'stufe4_bg', 'stufe5_bg']
        sgs = ['stufe1_s', 'stufe2_s', 'stufe3_s', 'stufe4_s', 'stufe5_s']
        for method in self.ekst_methoden:
            label = method['current_method_name']
            color = method['color']
            bg_vec = self.ekst_methoden_bgs[label]
            sg_vec = self.ekst_methoden_sgs[label]
            if bg_vec[-1] < self.jahreseinkommen_vec[-1]:
                bg_vec[-1] = self.jahreseinkommen_vec[-1]
            ax1.plot(bg_vec, sg_vec,
                     label=label+' Grenzsteuersatz', color=color)
            ax1.plot(self.jahreseinkommen_vec, self.ekst_methoden_berechnet[label],
                     label=label, color=color, linestyle='--')
        ax1.grid()
        ax1.set_ylim((0, 0.70))
        start, end = ax1.get_xlim()
        if limit is not None:
            end = limit
            ax1.set_xlim(0, limit)
        ax1.xaxis.set_ticks(np.arange(0, end+int(end/10), int(end/10)))
        ax1.yaxis.set_ticks(np.arange(0, 0.65, 0.05))
        ax1.set_xticklabels(ax1.get_xticks(minor=True), size=12, rotation=20)
        fmt = '{x:,.0f}€'
        tick = mtick.StrMethodFormatter(fmt)
        ax1.xaxis.set_major_formatter(tick)
        ax1.set_yticklabels(ax1.get_yticks(), size=12, rotation=20)
        ax1.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=None, symbol='%'))
        ax1.set_xlabel("zu versteuerndes Einkommen in €", size=15)
        ax1.set_title(title, size=20)
        ax1.legend()
        fig1.tight_layout()
        fig1.savefig("GE_Ansatz_Steuer_prozentual"+self.methoden_suffix+".png")

        """
        NETTO Plot
        """
        if not self.sozialabgaben_berechnet:
            self.berechne_netto_jahreseinkommen()

        fig2, ax2 = plt.subplots(figsize=(15, 7))
        if limit is not None:
            ax2.set_xlim(0, limit)
        ax2.plot(self.jahreseinkommen_vec, self.netto_normal_mitabgaben,
                 color='blue',
                 label="aktuelles Netto inklusive Sozialabgaben")
        if self.ipge:
            ax2.plot(self.jahreseinkommen_vec, self.netto_ipge_mitabgaben,
                     color='green',
                     label="Kindergeld für Alle Ansatz inklusive Sozialabgaben")
        ax2.grid()
        y_values = ax2.get_yticks()
        x_values = ax2.get_xticks()
        start, end = ax2.get_xlim()
        ax2.xaxis.set_ticks(np.arange(0, end+10000, 10000))
        ax2.set_xticklabels(ax2.get_xticks(minor=True), size=12, rotation=20)
        fmt = '{x:,.0f}€'
        tick = mtick.StrMethodFormatter(fmt)
        ax2.xaxis.set_major_formatter(tick)
        ax2.yaxis.set_major_formatter(tick)
        ax2.set_xlabel("Brutto / zu versteuerndes Einkommen in €", size=15)
        ax2.set_ylabel("Netto in €", size=15)
        ax2.set_title("Netto Vergleich", size=20)
        ax2.legend()
        fig2.savefig("GE_Ansatz_BruttoNetto"+self.methoden_suffix+".png")


if __name__ == "__main__":
    testKfA = EkStCalculator(steuerfreibetrag=0, verbose=False, methoden_suffix='_kfa_only', ipge=True,
                             partielles_grundeinkommen=0.33*9408)
    testKfA.add_method(
        stufe1_bg=0,
        stufe2_bg=testKfA.stufe1_bg-9408,
        stufe3_bg=testKfA.stufe2_bg-9408,
        stufe4_bg=testKfA.stufe3_bg-9408,
        stufe5_bg=testKfA.stufe4_bg-9408,
        stufe6_bg=testKfA.stufe5_bg-9408,
        stufe7_bg=testKfA.stufe5_bg,
        stufe8_bg=testKfA.stufe5_bg,
        stufe1_s=testKfA.stufe1_s,
        stufe2_s=testKfA.stufe1_s,
        stufe3_s=testKfA.stufe2_s,
        stufe4_s=testKfA.stufe3_s,
        stufe5_s=testKfA.stufe4_s,
        stufe6_s=testKfA.stufe5_s,
        stufe7_s=testKfA.stufe6_s,
        steuerfreibetrag=0,
        stufe1_proportional=False,
        stufe2_proportional=False,
        stufe3_proportional=False,
        stufe4_proportional=False,
        stufe5_proportional=True,
        stufe6_proportional=True,
        stufe7_proportional=True,
        stufe8_proportional=True,
        current_method_name='"Kindergeld für Alle" Ansatz')
    testKfA.add_method(
        stufe1_bg=0,
        stufe2_bg=testKfA.stufe1_bg,
        stufe3_bg=testKfA.stufe2_bg,
        stufe4_bg=30000,
        stufe5_bg=testKfA.stufe3_bg,
        stufe6_bg=70000,
        stufe7_bg=testKfA.stufe4_bg,
        stufe8_bg=1e6 + 4,
        stufe1_s=0.3,
        stufe2_s=testKfA.stufe1_s + 0.215,
        stufe3_s=testKfA.stufe2_s + 0.215,
        stufe4_s=testKfA.stufe3_s + 0.13,
        stufe5_s=testKfA.stufe3_s + 0.13,
        stufe6_s=testKfA.stufe4_s + 0.10,
        stufe7_s=testKfA.stufe4_s + 0.10,
        stufe8_s=testKfA.stufe4_s + 0.10,
        steuerfreibetrag=0,
        stufe1_proportional=True,
        stufe2_proportional=False,
        stufe3_proportional=False,
        stufe4_proportional=False,
        stufe5_proportional=False,
        stufe6_proportional=True,
        stufe7_proportional=True,
        stufe8_proportional=True,
        current_method_name='Vorschlag Bruene Schloen',
        color='green')
    testKfA.plot_einkommenssteuersatz(limit=250000, plot_ipge=False)

    einkommenssteuer_baukje = EkStCalculator(steuerfreibetrag=9408, methoden_suffix='_baukjes_ueberlegungen',
                                            einkommen_ende=250000)
    baukje_vorschlag_alt = False
    if baukje_vorschlag_alt:
        einkommenssteuer_baukje.add_method(
            stufe1_bg=0,
            stufe2_bg=10000,
            stufe3_bg=12000,
            stufe4_bg=17000,
            stufe5_bg=40000,
            stufe1_s=0.30,
            stufe2_s=0.355,
            stufe3_s=0.45,
            stufe4_s=0.55,
            stufe5_s=0.55,
            steuerfreibetrag=0,
            stufe1_proportional=True,
            stufe2_proportional=False,
            stufe3_proportional=False,
            stufe4_proportional=True,
            stufe5_proportional=True,
            current_method_name='neuer Vorschlag Baukje')
    einkommenssteuer_baukje.add_method(
        stufe1_bg=0,
        stufe2_bg=einkommenssteuer_baukje.stufe1_bg,
        stufe3_bg=einkommenssteuer_baukje.stufe2_bg,
        stufe4_bg=30000,
        stufe5_bg=einkommenssteuer_baukje.stufe3_bg,
        stufe6_bg=70000,
        stufe7_bg=einkommenssteuer_baukje.stufe4_bg,
        stufe8_bg=1e6 + 4,
        stufe1_s=0.3,
        stufe2_s=einkommenssteuer_baukje.stufe1_s + 0.215,
        stufe3_s=einkommenssteuer_baukje.stufe2_s + 0.215,
        stufe4_s=einkommenssteuer_baukje.stufe3_s + 0.13,
        stufe5_s=einkommenssteuer_baukje.stufe3_s + 0.13,
        stufe6_s=einkommenssteuer_baukje.stufe4_s + 0.10,
        stufe7_s=einkommenssteuer_baukje.stufe4_s + 0.10,
        stufe8_s=einkommenssteuer_baukje.stufe4_s + 0.10,
        steuerfreibetrag=0,
        stufe1_proportional=True,
        stufe2_proportional=False,
        stufe3_proportional=False,
        stufe4_proportional=False,
        stufe5_proportional=False,
        stufe6_proportional=True,
        stufe7_proportional=True,
        stufe8_proportional=True,
        current_method_name='Vorschlag Bruene Schloen')
    einkommenssteuer_baukje.plot_einkommenssteuersatz(limit=100000, plot_ipge=False,
                                                      title='neuer Einkommenssteuervorschlag')

