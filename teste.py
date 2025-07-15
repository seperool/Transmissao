import math # Importa o módulo math para funções matemáticas como pi, sqrt e log
import numpy as np # Importa a biblioteca NumPy para operações com arrays e matrizes, especialmente úteis para números complexos

import unittest

def Metodo_Carson_long(ra, rb, rc, xa, xb, xc, ha, hb, hc, rho, l, R=None, Rmg_val=None):
    """
    Método de Carson com correção para cálculo de impedâncias longitudinais
    em linhas de transmissão trifásicas, sem cabo para-raio.

    Parâmetros:
    ra, rb, rc (float): Resistência ôhmica por unidade de comprimento dos condutores A, B, C (Ohms/metro).
                        É crucial que estas resistências estejam em Ohms por metro para consistência com as constantes.
    xa, xb, xc (float): Coordenadas horizontais (X) dos condutores A, B, C (metros).
    ha, hb, hc (float): Coordenadas verticais (altura H) dos condutores A, B, C (metros).
    rho (float): Resistividade do solo (Ohms-metro). Variável de entrada crucial para a correção de Carson.
    R (float, opcional): Raio físico do condutor (metros). Usado para calcular o RMG se Rmg_val não for fornecido.
    Rmg_val (float, opcional): Raio Médio Geométrico (RMG) do condutor (metros). Se fornecido, R é ignorado,
                                pois o RMG é mais preciso para cabos trançados.

    Retorna:
    numpy.ndarray: Matriz de impedância 3x3 complexa (Ohms/km).

    Raises:
    ValueError: Se nem R nem Rmg_val forem fornecidos, ou se RMG, rho, ou qualquer altura for não positivo.
    """

    # --- Constantes Físicas e Elétricas ---
    f = 60                                          # Frequência do sistema (Hz). Padrão no Brasil e em outras regiões.
    mi_0 = 4 * math.pi * (10**(-7))                 # Permeabilidade magnética do vácuo (H/m). Constante física fundamental.
    w = 2 * math.pi * f                             # Frequência angular (rad/s). Usada nos cálculos de reatância indutiva.

    # --- Termos de Correção do Método de Carson para o Solo ---
    # rd: Termo de resistência de Carson (Ohms/m) que representa a parcela de resistência adicionada
    # devido ao retorno da corrente pelo solo com resistividade finita. É um termo constante.
    rd = 9.869 * (10**(-7)) * f                     # Ohms/m. Esta é uma aproximação amplamente usada para 50/60 Hz.

    # De: Distância de retorno equivalente do solo (metros).
    # É uma profundidade fictícia do plano de retorno da corrente no solo,
    # que encapsula o efeito da resistividade finita do solo.
    # A constante 659 é apropriada para rho em Ohm-m e f em Hz, resultando em De em metros.
    De = 659 * (math.sqrt(rho / f))                 # Metros

    # --- Cálculo do Raio Médio Geométrico (RMG) ---
    Rmg = None # Inicializa RMG como None para verificar se foi calculado ou fornecido
    if Rmg_val is not None:
        Rmg = Rmg_val # Se o RMG já foi fornecido, usa-o diretamente
    elif R is not None:
        # Se o raio físico (R) foi fornecido, calcula o RMG.
        # Para condutores sólidos ou simples, RMG = R * e^(-1/4).
        # Para condutores trançados (como ACSR), o RMG geralmente é um valor tabelado pelo fabricante.
        Rmg = R * math.exp(-1/4)
    
    # --- Validações de Entrada ---
    # Estas verificações garantem que os valores de entrada são válidos para o cálculo.
    if Rmg is None:
        raise ValueError("ERRO! É necessário fornecer o raio do condutor (R) OU o Raio Médio Geométrico (Rmg_val).")
    if Rmg <= 0:
        raise ValueError("ERRO! O Raio Médio Geométrico (RMG) deve ser um valor positivo.")
    if rho <= 0:
        raise ValueError("ERRO! A resistividade do solo (rho) deve ser um valor positivo.")
    if ha <= 0 or hb <= 0 or hc <= 0:
        # As alturas devem ser positivas, pois o método de Carson assume condutores acima do solo.
        raise ValueError("ERRO! As alturas dos condutores (Ha, Hb, Hc) devem ser maiores que zero.")

    # --- Cálculo das Distâncias Geométricas entre os condutores ---
    # As distâncias entre os centros dos condutores reais são calculadas usando a fórmula da distância euclidiana 2D.
    dab = np.sqrt(((xa - xb)**2) + ((ha - hb)**2)) # Distância entre condutores A e B
    dac = np.sqrt(((xa - xc)**2) + ((ha - hc)**2)) # Distância entre condutores A e C
    dbc = np.sqrt(((xb - xc)**2) + ((hb - hc)**2)) # Distância entre condutores B e C

    # --- Cálculo das Impedâncias Próprias e Mútuas (por metro) ---
    # As fórmulas de Carson geralmente resultam em impedâncias por metro.
    # Impedâncias Próprias (Zii): Representam a impedância de um condutor em relação ao retorno pelo solo.
    # Zii = Ri_condutor + R_terra_Carson + j * X_terra_propria_Carson
    # R_terra_Carson é o termo 'rd'. X_terra_propria_Carson é a parte logarítmica com De/RMG.
    Zaa = ra + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)
    Zbb = rb + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)
    Zcc = rc + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)

    # Impedâncias Mútuas (Zij): Representam o acoplamento eletromagnético entre dois condutores,
    # considerando o retorno pelo solo.
    # Zij = R_terra_Carson + j * X_terra_mutua_Carson
    # R_terra_Carson é o termo 'rd'. X_terra_mutua_Carson é a parte logarítmica com De/dij.
    Zab = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dab) # Impedância mútua entre A e B
    Zac = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dac) # Impedância mútua entre A e C
    Zbc = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dbc) # Impedância mútua entre B e C

    # As impedâncias mútuas são simétricas na matriz de impedância de fase (Zij = Zji).
    Zba = Zab
    Zca = Zac
    Zcb = Zbc

    # --- Construção da Matriz de Impedância ---
    # Monta a matriz 3x3 de impedâncias de fase.
    # Cada elemento [i, j] da matriz representa a impedância entre a fase i e a fase j.
    # Multiplica a matriz inteira por 1000 para converter de Ohms/metro para Ohms/km,
    # já que as resistências de entrada são geralmente fornecidas em Ohms/km.
    Z = np.array([
        [Zaa, Zab, Zac],
        [Zba, Zbb, Zbc],
        [Zca, Zcb, Zcc]
    ]) * 1000 # Converter para Ohms/km

    return Z*l # Retorna a matriz de impedância longitudinal da linha

class TestMetodoCarsonLong(unittest.TestCase):

    # --- Setup para valores comuns ---
    def setUp(self):
        # Parâmetros padrão para a maioria dos testes de sucesso
        self.ra = 0.0001 # Ohm/m
        self.rb = 0.0001 # Ohm/m
        self.rc = 0.0001 # Ohm/m
        self.xa = 0.0    # m
        self.xb = 3.0    # m
        self.xc = 6.0    # m
        self.ha = 15.0   # m
        self.hb = 15.0   # m
        self.hc = 15.0   # m
        self.rho = 100.0 # Ohm-m (Resistividade do solo)
        self.l = 10000.0 # m (Comprimento da linha)
        self.R = 0.01    # m (Raio físico)
        # RMG calculado a partir de R
        self.Rmg_calculated = self.R * math.exp(-1/4)
        
        # Constantes internas da função para cálculos de verificação
        self.f = 60.0
        self.mi_0 = 4 * math.pi * (10**(-7))
        self.w = 2 * math.pi * self.f
        self.rd = 9.869 * (10**(-7)) * self.f
        self.De = 659 * (math.sqrt(self.rho / self.f))
        self.k_indutivo = (1j * self.w * self.mi_0) / (2 * math.pi)

    # --- Testes de Casos de Sucesso ---

    def test_basic_calculation_with_R(self):
        """
        Testa o cálculo básico com todos os parâmetros válidos e R fornecido.
        Verifica contra um valor previamente calculado e validado.
        """
        # Valores esperados calculados manualmente ou por uma referência confiável
        # para os parâmetros padrão definidos no setUp
        expected_Z = np.array([
            [(1.0 + 6.22515449j), (0.0 + 1.73985945j), (0.0 + 1.22827346j)],
            [(0.0 + 1.73985945j), (1.0 + 6.22515449j), (0.0 + 1.73985945j)],
            [(0.0 + 1.22827346j), (0.0 + 1.73985945j), (1.0 + 6.22515449j)]
        ])

        calculated_Z = Metodo_Carson_long(
            ra=self.ra, rb=self.rb, rc=self.rc,
            xa=self.xa, xb=self.xb, xc=self.xc,
            ha=self.ha, hb=self.hb, hc=self.hc,
            rho=self.rho, l=self.l, R=self.R
        )

        # Usar np.allclose para comparar arrays de ponto flutuante/complexos
        self.assertTrue(np.allclose(calculated_Z, expected_Z, atol=1e-7, rtol=1e-7),
                        f"Teste Básico com R falhou.\nEsperado:\n{expected_Z}\nCalculado:\n{calculated_Z}")

    def test_calculation_with_Rmg_val(self):
        """
        Testa o cálculo quando o Rmg_val é fornecido (R deve ser ignorado).
        """
        Rmg_test_val = 0.008 # Um RMG um pouco diferente para testar
        
        # Recalcular as impedâncias próprias e mútuas com o novo RMG
        Zaa_exp = self.ra + self.rd + self.k_indutivo * math.log(self.De / Rmg_test_val)
        Zbb_exp = self.rb + self.rd + self.k_indutivo * math.log(self.De / Rmg_test_val)
        Zcc_exp = self.rc + self.rd + self.k_indutivo * math.log(self.De / Rmg_test_val)

        # Distâncias para mútuas
        dab = np.sqrt(((self.xa - self.xb)**2) + ((self.ha - self.hb)**2))
        dac = np.sqrt(((self.xa - self.xc)**2) + ((self.ha - self.hc)**2))
        dbc = np.sqrt(((self.xb - self.xc)**2) + ((self.hb - self.hc)**2))

        Zab_exp = self.rd + self.k_indutivo * math.log(self.De / dab)
        Zac_exp = self.rd + self.k_indutivo * math.log(self.De / dac)
        Zbc_exp = self.rd + self.k_indutivo * math.log(self.De / dbc)
        
        expected_Z = np.array([
            [Zaa_exp, Zab_exp, Zac_exp],
            [Zab_exp, Zbb_exp, Zbc_exp],
            [Zac_exp, Zbc_exp, Zcc_exp]
        ]) * self.l # Multiplicar pelo comprimento da linha

        calculated_Z = Metodo_Carson_long(
            ra=self.ra, rb=self.rb, rc=self.rc,
            xa=self.xa, xb=self.xb, xc=self.xc,
            ha=self.ha, hb=self.hb, hc=self.hc,
            rho=self.rho, l=self.l, Rmg_val=Rmg_test_val # Passando Rmg_val
        )
        
        self.assertTrue(np.allclose(calculated_Z, expected_Z, atol=1e-7, rtol=1e-7),
                        f"Teste com Rmg_val falhou.\nEsperado:\n{expected_Z}\nCalculado:\n{calculated_Z}")

    def test_different_geometry_triangular(self):
        """
        Testa com uma geometria diferente (triangular) e outros parâmetros.
        """
        # Parâmetros para configuração triangular (mesmos usados em exemplo anterior)
        xa_tri = -2.0
        xb_tri = 0.0
        xc_tri = 2.0
        ha_tri = 18.0
        hb_tri = 15.0
        hc_tri = 18.0
        l_tri = 5000.0 # 5 km

        # Valores esperados calculados e validados anteriormente para esta geometria
        expected_Z = np.array([
            [(0.500000 + 3.011603j), (0.000000 + 0.867490j), (0.000000 + 0.655866j)],
            [(0.000000 + 0.867490j), (0.500000 + 3.125867j), (0.000000 + 0.867490j)],
            [(0.000000 + 0.655866j), (0.000000 + 0.867490j), (0.500000 + 3.011603j)]
        ])

        calculated_Z = Metodo_Carson_long(
            ra=self.ra, rb=self.rb, rc=self.rc,
            xa=xa_tri, xb=xb_tri, xc=xc_tri,
            ha=ha_tri, hb=hb_tri, hc=hc_tri,
            rho=self.rho, l=l_tri, R=self.R
        )
        
        self.assertTrue(np.allclose(calculated_Z, expected_Z, atol=1e-7, rtol=1e-7),
                        f"Teste com geometria triangular falhou.\nEsperado:\n{expected_Z}\nCalculado:\n{calculated_Z}")

    # --- Testes de Casos de Erro (Validações de Entrada) ---

    def test_no_R_or_Rmg_val_provided(self):
        """
        Testa se a função levanta ValueError quando nem R nem Rmg_val são fornecidos.
        """
        with self.assertRaises(ValueError) as cm:
            Metodo_Carson_long(
                ra=self.ra, rb=self.rb, rc=self.rc,
                xa=self.xa, xb=self.xb, xc=self.xc,
                ha=self.ha, hb=self.hb, hc=self.hc,
                rho=self.rho, l=self.l, R=None, Rmg_val=None # Nenhum dos dois
            )
        self.assertIn("ERRO! É necessário fornecer o raio do condutor (R) OU o Raio Médio Geométrico (Rmg_val).", str(cm.exception))

    def test_non_positive_RMG(self):
        """
        Testa se a função levanta ValueError quando RMG (calculado ou fornecido) é <= 0.
        """
        with self.assertRaises(ValueError) as cm:
            Metodo_Carson_long(
                ra=self.ra, rb=self.rb, rc=self.rc,
                xa=self.xa, xb=self.xb, xc=self.xc,
                ha=self.ha, hb=self.hb, hc=self.hc,
                rho=self.rho, l=self.l, R=0.0 # R=0 leva a RMG=0
            )
        self.assertIn("ERRO! O Raio Médio Geométrico (RMG) deve ser um valor positivo.", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            Metodo_Carson_long(
                ra=self.ra, rb=self.rb, rc=self.rc,
                xa=self.xa, xb=self.xb, xc=self.xc,
                ha=self.ha, hb=self.hb, hc=self.hc,
                rho=self.rho, l=self.l, Rmg_val=-0.01 # RMG negativo
            )
        self.assertIn("ERRO! O Raio Médio Geométrico (RMG) deve ser um valor positivo.", str(cm.exception))

    def test_non_positive_rho(self):
        """
        Testa se a função levanta ValueError quando a resistividade do solo (rho) é <= 0.
        """
        with self.assertRaises(ValueError) as cm:
            Metodo_Carson_long(
                ra=self.ra, rb=self.rb, rc=self.rc,
                xa=self.xa, xb=self.xb, xc=self.xc,
                ha=self.ha, hb=self.hb, hc=self.hc,
                rho=0.0, l=self.l, R=self.R # rho = 0
            )
        self.assertIn("ERRO! A resistividade do solo (rho) deve ser um valor positivo.", str(cm.exception))
        
        with self.assertRaises(ValueError) as cm:
            Metodo_Carson_long(
                ra=self.ra, rb=self.rb, rc=self.rc,
                xa=self.xa, xb=self.xb, xc=self.xc,
                ha=self.ha, hb=self.hb, hc=self.hc,
                rho=-100.0, l=self.l, R=self.R # rho negativo
            )
        self.assertIn("ERRO! A resistividade do solo (rho) deve ser um valor positivo.", str(cm.exception))

    def test_non_positive_heights(self):
        """
        Testa se a função levanta ValueError quando qualquer altura (ha, hb, hc) é <= 0.
        """
        with self.assertRaises(ValueError) as cm:
            Metodo_Carson_long(
                ra=self.ra, rb=self.rb, rc=self.rc,
                xa=self.xa, xb=self.xb, xc=self.xc,
                ha=0.0, hb=self.hb, hc=self.hc, # ha = 0
                rho=self.rho, l=self.l, R=self.R
            )
        self.assertIn("ERRO! As alturas dos condutores (Ha, Hb, Hc) devem ser maiores que zero.", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            Metodo_Carson_long(
                ra=self.ra, rb=self.rb, rc=self.rc,
                xa=self.xa, xb=self.xb, xc=self.xc,
                ha=self.ha, hb=-5.0, hc=self.hc, # hb negativo
                rho=self.rho, l=self.l, R=self.R
            )
        self.assertIn("ERRO! As alturas dos condutores (Ha, Hb, Hc) devem ser maiores que zero.", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            Metodo_Carson_long(
                ra=self.ra, rb=self.rb, rc=self.rc,
                xa=self.xa, xb=self.xb, xc=self.xc,
                ha=self.ha, hb=self.hb, hc=0.0, # hc = 0
                rho=self.rho, l=self.l, R=self.R
            )
        self.assertIn("ERRO! As alturas dos condutores (Ha, Hb, Hc) devem ser maiores que zero.", str(cm.exception))


# Para rodar os testes a partir da linha de comando:
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)