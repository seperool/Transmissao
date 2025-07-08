import unittest
import numpy as np
import math

def metodo_carson_para_raio(ra, rb, rc, rp, xa, xb, xc, xp, ha, hb, hc, hp, rho, R=None, Rmg_val=None):
    """
    Calcula a impedância longitudinal de uma linha de transmissão trifásica com cabo para-raios,
    usando o Método de Carson e a redução de Kron.

    Retorna a matriz de impedância de fase (3x3) em Ohm/m, com o efeito do para-raios incorporado.

    Parâmetros:
    ra, rb, rc (float): Resistências CA das fases A, B, C (Ohm/m).
    rp (float): Resistência CA do para-raios (Ohm/m).
    xa, xb, xc, xp (float): Coordenadas horizontais (X) dos condutores (metros).
    ha, hb, hc, hp (float): Coordenadas verticais (H) dos condutores (metros). Devem ser positivas.
    rho (float): Resistividade do solo (Ohm.m).
    R (float, opcional): Raio físico do condutor (metros). Usado para calcular RMG se Rmg_val não for dado.
    Rmg_val (float, opcional): Raio Médio Geométrico (RMG) dos condutores (metros). Prioritário sobre 'R'.
                                Assume-se o mesmo RMG para todos os condutores.
    """
    
    # --- Constantes Físicas ---
    f = 60                       # Frequência do sistema (Hz).
    mi_0 = 4 * math.pi * (10**(-7)) # Permeabilidade magnética do vácuo (H/m).
    w = 2 * math.pi * f          # Frequência angular (rad/s).

    # --- Cálculo/Validação do Raio Médio Geométrico (RMG) ---
    Rmg = None 
    if Rmg_val is not None:
        Rmg = Rmg_val
    elif R is not None:
        Rmg = R * math.exp(-1/4) # Cálculo padrão de RMG a partir do raio físico.
    
    # --- Validações de Entrada ---
    if rho <= 0:
        raise ValueError("ERRO! A resistividade do solo (rho) deve ser um valor positivo.")
    if Rmg is None:
        raise ValueError("ERRO! É necessário fornecer o raio do condutor (R) OU o Raio Médio Geométrico (Rmg_val).")
    if Rmg <= 0:
        raise ValueError("ERRO! O Raio Médio Geométrico (RMG) deve ser um valor positivo.")
    if ha <= 0 or hb <= 0 or hc <= 0 or hp <= 0:
        raise ValueError("ERRO! As alturas de TODOS os condutores (Ha, Hb, Hc, Hp) devem ser maiores que zero.")

    # --- Termos de Correção do Método de Carson ---
    rd = 9.869 * (10**(-7)) * f    # Termo de resistência de Carson (Ohms/m).
    De = 659 * (math.sqrt(rho / f)) # Distância de retorno equivalente do solo (metros).

    # --- Cálculo das Distâncias Geométricas ---
    # Distâncias euclidianas 2D entre condutores reais.
    dab = np.sqrt(((xa - xb)**2) + ((ha - hb)**2))
    dac = np.sqrt(((xa - hc)**2) + ((ha - hc)**2))
    dbc = np.sqrt(((xb - xc)**2) + ((hb - hc)**2))
    dap = np.sqrt(((xa - xp)**2) + ((ha - hp)**2))
    dbp = np.sqrt(((xb - xp)**2) + ((hb - hp)**2))
    dcp = np.sqrt(((xc - xp)**2) + ((hc - hp)**2))

    # --- Cálculo das Impedâncias Próprias e Mútuas (Ohm/m) ---
    # Zii: Impedâncias próprias (condutor para retorno no solo).
    Zaa = ra + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)
    Zbb = rb + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)
    Zcc = rc + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)
    Zpp = rp + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)

    # Zij: Impedâncias mútuas (acoplamento entre dois condutores e retorno no solo).
    Zab = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dab)
    Zac = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dac)
    Zbc = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dbc)
    Zap = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dap)
    Zbp = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dbp)
    Zcp = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dcp)

    # Assimetria natural das mútuas na matriz de impedância (Zij = Zji).
    Zba = Zab
    Zca = Zac
    Zcb = Zbc
    Zpa = Zap
    Zpb = Zbp
    Zpc = Zcp

    # --- Construção das Submatrizes para Redução de Kron ---
    Z_1 = np.array([[Zaa, Zab, Zac], [Zba, Zbb, Zbc], [Zca, Zcb, Zcc]]) # Impedâncias fase-fase (Zff)
    Z_2 = np.array([[Zap], [Zbp], [Zcp]])                               # Impedâncias fase-para-raios (Zfp)
    Z_3 = np.array([[Zpa, Zpb, Zpc]])                                   # Impedâncias para-raios-fase (Zpf)
    Z_4 = np.array([[Zpp]])                                             # Impedância para-raios-para-raios (Zpp)

    # --- Redução de Kron para Eliminação do Para-Raios ---
    # Fórmula: Z_reduzida = Z_1 - (Z_2 @ inv(Z_4) @ Z_3)
    # inv(Z_4) é 1/Z_4[0,0] para matriz 1x1.
    termo_correcao = np.dot(Z_2, Z_3) / Z_4[0,0]

    Zp = Z_1 - termo_correcao # Matriz de impedância de fase final.

    return Zp

### Classe de Teste `TestMetodoCarsonParaRaio` (Com a Correção)

class TestMetodoCarsonParaRaio(unittest.TestCase):

    def setUp(self):
        # Parâmetros de entrada comuns para os testes
        self.ra = 0.05 / 1000  # Ohm/m (0.05 Ohm/km)
        self.rb = 0.05 / 1000
        self.rc = 0.05 / 1000
        self.rp = 0.10 / 1000  # Resistência do cabo para-raios

        self.xa = 0.0          # Coordenada X do condutor A (metros)
        self.xb = 4.0          # Coordenada X do condutor B (metros)
        self.xc = 8.0          # Coordenada X do condutor C (metros)
        self.xp = 4.0          # Coordenada X do cabo para-raios (metros, tipicamente acima do centro)

        self.ha = 15.0         # Altura do condutor A (metros)
        self.hb = 14.0         # Altura do condutor B (metros)
        self.hc = 15.0         # Altura do condutor C (metros)
        self.hp = 20.0         # Altura do cabo para-raios (metros, acima das fases)

        self.rho = 100.0       # Resistividade do solo (Ohm.m)
        self.R = 0.01          # Raio físico do condutor (metros)
        self.Rmg_val = None    # Iniciar como None para testar o cálculo a partir de R

        self.tolerance = 1e-9  # Tolerância para comparações de números complexos

    def test_output_matrix_shape(self):
        """
        Verifica se a função retorna uma matriz 3x3.
        """
        Z_result = metodo_carson_para_raio(
            self.ra, self.rb, self.rc, self.rp,
            self.xa, self.xb, self.xc, self.xp,
            self.ha, self.hb, self.hc, self.hp,
            self.rho, R=self.R, Rmg_val=self.Rmg_val
        )
        self.assertEqual(Z_result.shape, (3, 3))

    def test_value_error_no_R_or_Rmg_val(self):
        """
        Verifica se a função levanta ValueError quando nem R nem Rmg_val são fornecidos.
        """
        with self.assertRaises(ValueError) as cm:
            metodo_carson_para_raio(
                self.ra, self.rb, self.rc, self.rp,
                self.xa, self.xb, self.xc, self.xp,
                self.ha, self.hb, self.hc, self.hp,
                self.rho, R=None, Rmg_val=None
            )
        self.assertIn("ERRO! É necessário fornecer o raio do condutor (R) OU o Raio Médio Geométrico (Rmg_val).", str(cm.exception))

    def test_value_error_negative_Rmg_val(self):
        """
        Verifica se a função levanta ValueError para RMG não positivo.
        """
        with self.assertRaises(ValueError) as cm:
            metodo_carson_para_raio(
                self.ra, self.rb, self.rc, self.rp,
                self.xa, self.xb, self.xc, self.xp,
                self.ha, self.hb, self.hc, self.hp,
                self.rho, Rmg_val=-0.001
            )
        self.assertIn("ERRO! O Raio Médio Geométrico (RMG) deve ser um valor positivo.", str(cm.exception))

    def test_value_error_negative_rho(self):
        """
        Verifica se a função levanta ValueError para rho não positivo.
        """
        with self.assertRaises(ValueError) as cm:
            metodo_carson_para_raio(
                self.ra, self.rb, self.rc, self.rp,
                self.xa, self.xb, self.xc, self.xp,
                self.ha, self.hb, self.hc, self.hp,
                # AQUI ESTAVA O POSSÍVEL ERRO: "rho=-50.0, R=self.R"
                # A ordem dos argumentos posicionais deve seguir a definição da função.
                # Como 'rho' é um argumento posicional antes de 'R' na definição,
                # não se deve nomear 'rho' e depois passar um 'R' nomeado,
                # a menos que TODOS os argumentos anteriores a 'R' também sejam nomeados.
                # A forma mais segura é manter a ordem posicional para 'rho' e
                # só usar nomeados para os parâmetros opcionais 'R' e 'Rmg_val'.
                # OU nomear TUDO a partir de 'rho'.

                # OPÇÃO 1 (mantendo 'rho' posicional):
                -50.0, # Este é o valor para 'rho'
                R=self.R # Este é o valor para 'R'

                # OPÇÃO 2 (nomeando 'rho' também, o que é mais claro mas exige nomear todos os anteriores se misturar com posicionais)
                # rho=-50.0,
                # R=self.R
            )
        self.assertIn("ERRO! A resistividade do solo (rho) deve ser um valor positivo.", str(cm.exception))

    def test_value_error_zero_height_phase(self):
        """
        Verifica se a função levanta ValueError para altura de fase zero.
        """
        with self.assertRaises(ValueError) as cm:
            metodo_carson_para_raio(
                self.ra, self.rb, self.rc, self.rp,
                self.xa, self.xb, self.xc, self.xp,
                ha=0.0, hb=self.hb, hc=self.hc, hp=self.hp,
                rho=self.rho, R=self.R
            )
        self.assertIn("ERRO! As alturas de TODOS os condutores (Ha, Hb, Hc, Hp) devem ser maiores que zero.", str(cm.exception))

    def test_value_error_zero_height_pararaio(self):
        """
        Verifica se a função levanta ValueError para altura do para-raios zero.
        """
        with self.assertRaises(ValueError) as cm:
            metodo_carson_para_raio(
                self.ra, self.rb, self.rc, self.rp,
                self.xa, self.xb, self.xc, self.xp,
                ha=self.ha, hb=self.hb, hc=self.hc, hp=0.0, # hp = 0
                rho=self.rho, R=self.R
            )
        self.assertIn("ERRO! As alturas de TODOS os condutores (Ha, Hb, Hc, Hp) devem ser maiores que zero.", str(cm.exception))

    def test_Rmg_val_priority(self):
        """
        Verifica se Rmg_val é usado em vez de R quando ambos são fornecidos.
        """
        test_Rmg_val = 0.003 # Um valor de RMG diferente
        Z_result_with_Rmg_val = metodo_carson_para_raio(
            self.ra, self.rb, self.rc, self.rp,
            self.xa, self.xb, self.xc, self.xp,
            self.ha, self.hb, self.hc, self.hp,
            rho=self.rho, R=self.R, Rmg_val=test_Rmg_val
        )
        
        Z_result_only_R = metodo_carson_para_raio(
            self.ra, self.rb, self.rc, self.rp,
            self.xa, self.xb, self.xc, self.xp,
            self.ha, self.hb, self.hc, self.hp,
            self.rho, R=self.R, Rmg_val=None # Apenas R
        )
        
        self.assertFalse(np.allclose(Z_result_with_Rmg_val, Z_result_only_R, atol=self.tolerance))

# Permite que os testes sejam executados diretamente ao rodar o script
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)