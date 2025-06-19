from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import numpy as np

class TransmissaoScreen(BoxLayout):
    def calcular(self):
        try:
            # Capturando os valores dos inputs
            ra = float(self.ids.input_ra.text)
            rb = float(self.ids.input_rb.text)
            rc = float(self.ids.input_rc.text)
            rmga = float(self.ids.input_rmga.text)
            rmgb = float(self.ids.input_rmgb.text)
            rmgc = float(self.ids.input_rmgc.text)
            f = float(self.ids.input_f.text)
            ha = float(self.ids.input_ha.text)
            hb = float(self.ids.input_hb.text)
            hc = float(self.ids.input_hc.text)

            # Constantes
            mi0 = 4 * np.pi * 10**-7
            w = 2 * np.pi * f
            j = 1j

            # Impedâncias próprias
            Zaa = ra + j * w * mi0 / (2 * np.pi) * np.log(2 * ha / rmga)
            Zbb = rb + j * w * mi0 / (2 * np.pi) * np.log(2 * hb / rmgb)
            Zcc = rc + j * w * mi0 / (2 * np.pi) * np.log(2 * hc / rmgc)

            # Impedâncias mútuas
            Zab = j * w * mi0 / (2 * np.pi) * np.log(np.sqrt(50**2 + 6**2) / np.sqrt(10**2 + 6**2))
            Zba = Zab

            Zac = j * w * mi0 / (2 * np.pi) * np.log(np.sqrt(40**2 + 12**2) / np.sqrt(12))
            Zca = Zac

            Zcb = j * w * mi0 / (2 * np.pi) * np.log(np.sqrt(50**2 + 6**2) / np.sqrt(10**2 + 6**2))
            Zbc = Zcb

            # Matriz final
            Z = np.array([
                [Zaa, Zab, Zac],
                [Zba, Zbb, Zbc],
                [Zca, Zcb, Zcc]
            ])

            # Formatando o resultado
            resultado = "Matriz da Linha Trifásica:\n"
            for linha in Z:
                for valor in linha:
                    resultado += f"{valor.real:.4f} + j{valor.imag:.4f}    "
                resultado += "\n"

            self.ids.output_label.text = resultado

        except Exception as e:
            self.ids.output_label.text = f"Erro: {str(e)}"

    def limpar(self):
        self.ids.output_label.text = "Resultado aparecerá aqui"

class TransmissaoApp(App):
    def build(self):
        return TransmissaoScreen()

if __name__ == '__main__':
    TransmissaoApp().run()
