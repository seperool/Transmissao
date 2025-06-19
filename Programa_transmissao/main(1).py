from kivy.config import Config
Config.set('graphics', 'fullscreen', 'auto')  # Tela cheia

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from math import pi, log, sqrt

class TransmissaoScreen(BoxLayout):

    def calcular(self):
        try:
            ra = float(self.ids.input_ra.text)
            rb = float(self.ids.input_rb.text)
            rc = float(self.ids.input_rc.text)

            rmga = float(self.ids.input_rmga.text)
            rmgb = float(self.ids.input_rmgb.text)
            rmgc = float(self.ids.input_rmgc.text)

            f = float(self.ids.input_f.text)
            w = 2 * pi * f

            ha = float(self.ids.input_ha.text)
            hb = float(self.ids.input_hb.text)
            hc = float(self.ids.input_hc.text)

            mi0 = 4 * pi * 10 ** -7

            i = complex(0, 1)

            Zaa = ra + i * w * mi0 / (2 * pi) * log(2 * ha / rmga)
            Zbb = rb + i * w * mi0 / (2 * pi) * log(2 * hb / rmgb)
            Zcc = rc + i * w * mi0 / (2 * pi) * log(2 * hc / rmgc)

            Zab = i * w * mi0 / (2 * pi) * log(sqrt(50 ** 2 + 6 ** 2) / sqrt(10 ** 2 + 6 ** 2))
            Zba = Zab

            Zac = i * w * mi0 / (2 * pi) * log(sqrt(40 ** 2 + 12 ** 2) / sqrt(12))
            Zca = Zac

            Zcb = i * w * mi0 / (2 * pi) * log(sqrt(50 ** 2 + 6 ** 2) / sqrt(10 ** 2 + 6 ** 2))
            Zbc = Zcb

            Z = [[Zaa, Zab, Zac],
                 [Zba, Zbb, Zbc],
                 [Zca, Zcb, Zcc]]

            resultado = "Matriz da Linha Trifásica:\n"
            for linha in Z:
                linha_str = ["{0.real:.4e}{0.imag:+.4e}j".format(z) for z in linha]
                resultado += "\t".join(linha_str) + "\n"

            self.ids.output_label.text = resultado
        except Exception as e:
            self.ids.output_label.text = f"Erro: {str(e)}"

    def limpar(self):
        self.ids.output_label.text = ""
        self.ids.input_ra.text = "0.1"
        self.ids.input_rb.text = "0.1"
        self.ids.input_rc.text = "0.1"
        self.ids.input_rmga.text = "0.15"
        self.ids.input_rmgb.text = "0.15"
        self.ids.input_rmgc.text = "0.15"
        self.ids.input_f.text = "60"
        self.ids.input_ha.text = "20"
        self.ids.input_hb.text = "30"
        self.ids.input_hc.text = "20"


class TransmissaoApp(App):
    def build(self):
        return TransmissaoScreen()


if __name__ == "__main__":
    TransmissaoApp().run()
