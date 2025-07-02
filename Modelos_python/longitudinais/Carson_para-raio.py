import unittest
import numpy as np
import math

# A função metodo_carson_para_raio (seu código) deve estar aqui
# ou ser importada de um módulo. Para este exemplo, a estou colando aqui para completude.
def metodo_carson_para_raio(ra, rb, rc, rp, xa, xb, xc, xp, ha, hb, hc, hp, rho, R=None, Rmg_val=None):
    """
    Calcula a impedância longitudinal de uma linha de transmissão trifásica
    considerando a presença de um cabo para-raios (cabo de guarda),
    utilizando o Método de Carson e a redução de Kron.

    A função retorna a matriz de impedância de fase (3x3) já considerando
    o efeito de acoplamento e eliminação do cabo para-raios.

    Parâmetros:
    ra, rb, rc (float): Resistências CA dos condutores das fases A, B e C (em Ohm/m).
    rp (float): Resistência CA do condutor do cabo para-raios (em Ohm/m).
    xa, xb, xc (float): Coordenadas horizontais (X) dos condutores A, B e C (em metros).
    xp (float): Coordenada horizontal (X) do condutor do cabo para-raios (em metros).
    ha, hb, hc (float): Coordenadas verticais (H) dos condutores A, B e C (em metros).
    hp (float): Coordenada vertical (H) do condutor do cabo para-raios (em metros).
                As alturas devem ser positivas.
    rho (float): Resistividade do solo (em Ohm.m).
    R (float, opcional): Raio físico do condutor (em metros). Se fornecido e Rmg_val não for,
                         o RMG será calculado como R * exp(-1/4). Assume-se o mesmo R para todos.
    Rmg_val (float, opcional): Raio Médio Geométrico (RMG) dos condutores (em metros).
                               Se fornecido, tem prioridade sobre o cálculo a partir de 'R'.
                               Assume-se o mesmo RMG para todos os condutores (fases e para-raios).

    Retorna:
    numpy.ndarray: Matriz de impedância de fase (3x3) da linha (em Ohm/m),
                   com o efeito do cabo para-raios já incorporado via redução de Kron.
    """
    
    # --- Constantes Físicas e Elétricas ---
    f = 60                                       # Frequência do sistema (Hz).
    mi_0 = 4 * math.pi * (10**(-7))              # Permeabilidade magnética do vácuo (H/m).
    w = 2 * math.pi * f                          # Frequência angular (rad/s).

    # --- Cálculo e Validação do Raio Médio Geométrico (RMG) ---
    Rmg = None # Inicializa RMG como None para verificar se foi calculado ou fornecido
    if Rmg_val is not None:
        Rmg = Rmg_val # Se o RMG já foi fornecido, usa-o diretamente
    elif R is not None:
        # Se o raio físico (R) foi fornecido, calcula o RMG.
        # Para condutores sólidos ou simples, RMG = R * e^(-1/4).
        # Para condutores trançados (como ACSR), o RMG geralmente é um valor tabelado pelo fabricante.
        Rmg = R * math.exp(-1/4)
    
    # --- Validações de Entrada ---
    # É crucial validar 'rho' antes de usá-lo na função math.sqrt para evitar 'math domain error'.
    if rho <= 0:
        raise ValueError("ERRO! A resistividade do solo (rho) deve ser um valor positivo.")

    # Estas verificações garantem que os valores de entrada são válidos para o cálculo.
    if Rmg is None:
        raise ValueError("ERRO! É necessário fornecer o raio do condutor (R) OU o Raio Médio Geométrico (Rmg_val).")
    if Rmg <= 0:
        raise ValueError("ERRO! O Raio Médio Geométrico (RMG) deve ser um valor positivo.")
    if ha <= 0 or hb <= 0 or hc <= 0 or hp <= 0: # Inclui a altura do cabo para-raios na validação
        # As alturas devem ser positivas, pois o método de Carson assume condutores acima do solo.
        raise ValueError("ERRO! As alturas de TODOS os condutores (Ha, Hb, Hc, Hp) devem ser maiores que zero.")

    # --- Termos de Correção do Método de Carson para o Solo ---
    # rd: Termo de resistência de Carson (Ohms/m).
    rd = 9.869 * (10**(-7)) * f                  # Ohms/m.

    # De: Distância de retorno equivalente do solo (metros).
    De = 659 * (math.sqrt(rho / f))              # Metros

    # --- Cálculo das Distâncias Geométricas entre os condutores ---
    # As distâncias entre os centros dos condutores reais são calculadas usando a fórmula da distância euclidiana 2D.
    dab = np.sqrt(((xa - xb)**2) + ((ha - hb)**2)) # Distância entre condutores A e B
    dac = np.sqrt(((xa - xc)**2) + ((ha - hc)**2)) # Distância entre condutores A e C
    dbc = np.sqrt(((xb - xc)**2) + ((hb - hc)**2)) # Distância entre condutores B e C
    
    # Distâncias entre as fases e o cabo para-raios (p)
    dap = np.sqrt(((xa - xp)**2) + ((ha - hp)**2)) # Distância entre A e para-raios
    dbp = np.sqrt(((xb - xp)**2) + ((hb - hp)**2)) # Distância entre B e para-raios
    dcp = np.sqrt(((xc - xp)**2) + ((hc - hp)**2)) # Distância entre C e para-raios

    # --- Cálculo das Impedâncias Próprias e Mútuas por Unidade de Comprimento (Ohm/m) ---
    # As fórmulas de Carson resultam em impedâncias por metro.
    # Impedâncias Próprias (Zii): Representam a impedância de um condutor em relação ao retorno pelo solo.
    # Zii = Ri_condutor + R_terra_Carson + j * X_terra_propria_Carson
    # R_terra_Carson é 'rd'. X_terra_propria_Carson é a parte logarítmica com De/RMG.
    Zaa = ra + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)
    Zbb = rb + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)
    Zcc = rc + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)
    Zpp = rp + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg) # Impedância própria do cabo para-raios

    # Impedâncias Mútuas (Zij): Representam o acoplamento eletromagnético entre dois condutores,
    # considerando o retorno pelo solo.
    # Zij = R_terra_Carson + j * X_terra_mutua_Carson
    # R_terra_Carson é 'rd'. X_terra_mutua_Carson é a parte logarítmica com De/dij.
    Zab = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dab) # Mútua entre A e B
    Zac = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dac) # Mútua entre A e C
    Zbc = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dbc) # Mútua entre B e C
    
    # Impedâncias mútuas entre as fases e o cabo para-raios (p)
    Zap = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dap) # Mútua entre A e para-raios
    Zbp = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dbp) # Mútua entre B e para-raios
    Zcp = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dcp) # Mútua entre C e para-raios

    # As impedâncias mútuas são simétricas na matriz de impedância (Zij = Zji).
    Zba = Zab
    Zca = Zac
    Zcb = Zbc
    Zpa = Zap # Mútua entre para-raios e A
    Zpb = Zbp # Mútua entre para-raios e B
    Zpc = Zcp # Mútua entre para-raios e C

    # --- Construção das Submatrizes para Redução de Kron ---
    # Z_1: Submatriz de impedâncias próprias e mútuas entre as fases (Zff) - 3x3
    Z_1 = np.array([[Zaa, Zab, Zac],
                    [Zba, Zbb, Zbc],
                    [Zca, Zcb, Zcc]])

    # Z_2: Submatriz de impedâncias mútuas entre as fases e o cabo para-raios (Zfp) - 3x1
    Z_2 = np.array([[Zap],
                    [Zbp],
                    [Zcp]])

    # Z_3: Submatriz de impedâncias mútuas entre o cabo para-raios e as fases (Zpf) - 1x3
    Z_3 = np.array([[Zpa, Zpb, Zpc]])

    # Z_4: Submatriz de impedância própria do cabo para-raios (Zpp) - 1x1
    Z_4 = np.array([[Zpp]])

    # --- Redução de Kron para Eliminação do Cabo Para-Raios ---
    # A fórmula é: Z_p = Z_1 - (Z_2 @ Z_4_inversa @ Z_3)
    # Como Z_4 é 1x1, Z_4_inversa é 1/Z_4[0,0].
    # Usamos np.dot para multiplicação de matrizes.
    termo_correcao = np.dot(Z_2, Z_3) / Z_4[0,0]

    # Calcula a impedância final da matriz de fase com o efeito do cabo para-raios.
    Zp = Z_1 - termo_correcao

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