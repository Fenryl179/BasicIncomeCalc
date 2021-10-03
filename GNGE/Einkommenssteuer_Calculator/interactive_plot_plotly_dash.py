from lib.Einkommenssteuer_Rechner_GNGE import EkStCalculator
from chart_studio.plotly import plotly as py
import plotly.graph_objs as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

local = True
if local:
    import plotly.io as pio
    pio.renderers.default = "browser"


class EkStCalculatorInteractive(EkStCalculator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def plot_interactive(self,
                         plot_ipge=True, title="Test EkSt Plot",
                         show=True):
        if self.einkommenssteuersatz is None:
            self.calculate_standard_ekst()
            if len(self.ekst_methoden) > 0:
                self.calculate_extra_ekst()
        """
        EkSt. Plot
        """
        traces = []
        if plot_ipge:
            traces.append(go.Scatter(x=self.jahreseinkommen_vec, y=self.einkommenssteuersatz_ipge,
                                     name="'Kindergeld für Alle' Ansatz",
                                     line=dict(color='green', dash='dash')))
            traces.append(go.Scatter(x=self.einkommenssteuersatz_ipge_bgs,
                                     y=self.einkommenssteuersatz_ipge_sgs,
                                     name="'Kindergeld für Alle' Ansatz" + ' Grenzsteuersatz',
                                     line=dict(color='green', dash='dash')))
        traces.append(go.Scatter(
            x=[0, self.steuerfreibetrag, self.stufe1_bg, self.stufe2_bg, self.stufe3_bg, self.stufe4_bg],
            y=[0, 0, self.stufe1_s, self.stufe2_s, self.stufe3_s, self.stufe4_s],
            name=self.current_method_name + ' Grenzsteuersatz',
            line=dict(color='orange')))
        traces.append(go.Scatter(
            x=self.jahreseinkommen_vec,
            y=self.einkommenssteuersatz,
            name=self.current_method_name,
            line=dict(color='orange', dash='dash')))
        bgs = ['stufe1_bg', 'stufe2_bg', 'stufe3_bg', 'stufe4_bg', 'stufe5_bg']
        sgs = ['stufe1_s', 'stufe2_s', 'stufe3_s', 'stufe4_s', 'stufe5_s']
        for method in self.ekst_methoden:
            label = method['current_method_name']
            color = method['color']
            bg_vec = self.ekst_methoden_bgs[label]
            sg_vec = self.ekst_methoden_sgs[label]
            if bg_vec[-1] < self.jahreseinkommen_vec[-1]:
                bg_vec[-1] = self.jahreseinkommen_vec[-1]
            traces.append(go.Scatter(
                x=bg_vec,
                y=sg_vec,
                name=label+' Grenzsteuersatz',
                line=dict(color=color)))
            traces.append(go.Scatter(
                x=self.jahreseinkommen_vec,
                y=self.ekst_methoden_berechnet[label],
                name=label,
                line=dict(color=color, dash='dash')))
        xaxis_template = dict(showgrid=True,
                              zeroline=True,
                              nticks=20,
                              showline=True,
                              title="Jahreseinkommen in €",
                              tickangle=20,
                              range=[0, self.jahreseinkommen_vec[-1]])
        yaxis_template = dict(showgrid=True,
                              zeroline=True,
                              nticks=20,
                              showline=True,
                              title="Steuersatz in %",
                              tickformat=',.0%',
                              mirror=True)
        layout = go.Layout(xaxis=xaxis_template,
                           yaxis=yaxis_template,
                           margin=dict(l=20, r=20, t=20, b=20, pad=20),
                           hovermode='closest',
                           title=title)
        fig = go.Figure(data=traces,
                        layout=layout)
        if show:
            fig.show()
        return fig


einkommenssteuer_baukje = EkStCalculatorInteractive(steuerfreibetrag=9408, methoden_suffix='_baukjes_ueberlegungen',
                                                    einkommen_ende=250000)
baukje_vorschlag_alt = True
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

ekst_fig = einkommenssteuer_baukje.plot_interactive()


"""
DASH
"""
app = dash.Dash()
app.layout = html.Div([dcc.Graph(id='plot_id', figure=ekst_fig)])

if __name__ == '__main__':
    app.run_server(debug=True)

