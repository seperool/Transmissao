import numpy as np  # Operações numéricas e matriciais
import math         # Funções matemáticas (pi, log, exp)
import unittest

def metodo_imagem_long(ra, rb, rc, xa, ha, xb, hb, xc, hc, l, R=None, Rmg_val=None):
    """
    Calcula a matriz de impedância série por unidade de comprimento de uma linha de transmissão trifásica,
    usando o Método das Imagens para efeito do solo.

    Parâmetros:
    ra, rb, rc (float): Resistências de fase dos condutores a, b, c (Ohm/unidade de comprimento).
    xa, xb, xc (float): Coordenadas horizontais (X) dos condutores a, b, c (metros).
    ha, hb, hc (float): Alturas verticais (H) dos condutores a, b, c acima do solo (metros).
    l (float): Comprimento total da linha (metros).
    R (float, opcional): Raio físico do condutor (metros).
    Rmg_val (float, opcional): Raio Médio Geométrico (RMG) do condutor (metros).

    Retorna:
    numpy.ndarray: Matriz de impedância série 3x3 complexa para o comprimento total da linha (Ohms).

    Raises:
    ValueError: Para entradas inválidas (RMG não fornecido/inválido, alturas <= 0).
    """

    # --- Constantes Físicas e Frequência ---
    mi_0 = 4 * math.pi * (10**(-7))       # Permeabilidade magnética do vácuo (H/m)
    f = 60                                # Frequência do sistema (Hz)
    w = 2 * math.pi * f                   # Frequência angular (rad/s)

    # --- Cálculo e Validação do Raio Médio Geométrico (RMG) ---
    Rmg = None
    if Rmg_val is not None:
        Rmg = Rmg_val
    elif R is not None:
        Rmg = R * math.exp(-1/4) # Cálculo do RMG a partir do raio físico
    
    if Rmg is None or Rmg <= 0:
        if R is None and Rmg_val is None:
            raise ValueError("ERRO! Forneça o Raio (R) OU o Raio Médio Geométrico (Rmg_val).")
        else:
            raise ValueError("ERRO! O Raio (R) ou o Raio Médio Geométrico (Rmg_val) deve ser positivo.")
    
    # --- Validação das Alturas ---
    if ha <= 0 or hb <= 0 or hc <= 0:
        raise ValueError("ERRO! As alturas dos condutores (ha, hb, hc) devem ser maiores que zero.")

    # --- Cálculo das Distâncias Geométricas ---
    # Distâncias entre condutores reais (d_ij)
    dab = np.sqrt(((xa - xb)**2) + ((ha - hb)**2))
    dac = np.sqrt(((xa - xc)**2) + ((ha - hc)**2))
    dbc = np.sqrt(((xb - xc)**2) + ((hb - hc)**2))
    
    # Distâncias entre condutores e suas imagens (d_i,j')
    dab_l = np.sqrt(((xa - xb)**2) + ((ha + hb)**2))
    dac_l = np.sqrt(((xa - xc)**2) + ((ha + hc)**2))
    dbc_l = np.sqrt(((xb - xc)**2) + ((hb + hc)**2))
    
    # --- Cálculo das Impedâncias Série por unidade de comprimento ---
    # Impedâncias Próprias (diagonal: Zaa, Zbb, Zcc)
    Zaa = ra + (((1j * mi_0 * w) / (2 * math.pi)) * math.log((2 * ha) / Rmg))
    Zbb = rb + (((1j * mi_0 * w) / (2 * math.pi)) * math.log((2 * hb) / Rmg))
    Zcc = rc + (((1j * mi_0 * w) / (2 * math.pi)) * math.log((2 * hc) / Rmg))
    
    # Impedâncias Mútuas (fora da diagonal: Zab, Zac, Zbc e suas simetrias)
    Zab = ((1j * w * mi_0) / (2 * math.pi)) * (math.log(dab_l / dab))
    Zac = ((1j * w * mi_0) / (2 * math.pi)) * (math.log(dac_l / dac))
    Zbc = ((1j * w * mi_0) / (2 * math.pi)) * (math.log(dbc_l / dbc))
    
    # Pela simetria da linha (Z_ij = Z_ji)
    Zba = Zab
    Zca = Zac
    Zcb = Zbc
    
    # --- Montagem da Matriz de Impedância da Linha ---
    Z = np.array([ # Matriz de impedância por unidade de comprimento
        [Zaa, Zab, Zac],
        [Zba, Zbb, Zbc],
        [Zca, Zcb, Zcc]
    ])

    return Z * l # Retorna a matriz de impedância total da linha

# --- CLASSE DE TESTE UNITÁRIO ---
class TestMetodoImagemLong(unittest.TestCase):

    def test_parametros_validos_R(self):
        """Testa com parâmetros válidos, fornecendo R."""
        ra, rb, rc = 0.1, 0.1, 0.1
        xa, xb, xc = -5.0, 0.0, 5.0
        ha, hb, hc = 10.0, 10.0, 10.0
        l = 10000.0  # 10 km
        R = 0.01     # Raio físico

        Z_result = metodo_imagem_long(ra, rb, rc, xa, ha, xb, hb, xc, hc, l, R=R)

        # Verifica tipo e forma da saída
        self.assertIsInstance(Z_result, np.ndarray)
        self.assertEqual(Z_result.shape, (3, 3))
        self.assertTrue(np.issubdtype(Z_result.dtype, np.complexfloating))

        # Valores esperados para uma configuração simétrica (apenas diagonal significativa)
        Rmg_expected = R * math.exp(-1/4)
        Xii_expected_per_m = (2 * math.pi * 60 * 4 * math.pi * 10**(-7) / (2 * math.pi)) * math.log((2 * 10.0) / Rmg_expected)
        Zii_expected_per_m = 0.1 + 1j * Xii_expected_per_m

        atol = 1e-6 # Tolerância absoluta

        # Verifica diagonal (Zaa, Zbb, Zcc)
        np.testing.assert_allclose(Z_result[0, 0], Zii_expected_per_m * l, atol=atol)
        np.testing.assert_allclose(Z_result[1, 1], Zii_expected_per_m * l, atol=atol)
        np.testing.assert_allclose(Z_result[2, 2], Zii_expected_per_m * l, atol=atol)

        # Verifica elementos fora da diagonal (Zab, Zac, Zbc)
        dab_expected = np.sqrt((-5.0 - 0.0)**2 + (10.0 - 10.0)**2)
        dac_expected = np.sqrt((-5.0 - 5.0)**2 + (10.0 - 10.0)**2)
        dbc_expected = np.sqrt((0.0 - 5.0)**2 + (10.0 - 10.0)**2)

        dab_l_expected = np.sqrt((-5.0 - 0.0)**2 + (10.0 + 10.0)**2)
        dac_l_expected = np.sqrt((-5.0 - 5.0)**2 + (10.0 + 10.0)**2)
        dbc_l_expected = np.sqrt((0.0 - 5.0)**2 + (10.0 + 10.0)**2)

        Xab_expected_per_m = (2 * math.pi * 60 * 4 * math.pi * 10**(-7) / (2 * math.pi)) * math.log(dab_l_expected / dab_expected)
        Xac_expected_per_m = (2 * math.pi * 60 * 4 * math.pi * 10**(-7) / (2 * math.pi)) * math.log(dac_l_expected / dac_expected)
        Xbc_expected_per_m = (2 * math.pi * 60 * 4 * math.pi * 10**(-7) / (2 * math.pi)) * math.log(dbc_l_expected / dbc_expected)

        np.testing.assert_allclose(Z_result[0, 1], 1j * Xab_expected_per_m * l, atol=atol)
        np.testing.assert_allclose(Z_result[1, 0], 1j * Xab_expected_per_m * l, atol=atol)
        np.testing.assert_allclose(Z_result[0, 2], 1j * Xac_expected_per_m * l, atol=atol)
        np.testing.assert_allclose(Z_result[2, 0], 1j * Xac_expected_per_m * l, atol=atol)
        np.testing.assert_allclose(Z_result[1, 2], 1j * Xbc_expected_per_m * l, atol=atol)
        np.testing.assert_allclose(Z_result[2, 1], 1j * Xbc_expected_per_m * l, atol=atol)


    def test_parametros_validos_Rmg_val(self):
        """Testa com parâmetros válidos, fornecendo Rmg_val."""
        ra, rb, rc = 0.05, 0.05, 0.05
        xa, xb, xc = -3.0, 0.0, 3.0
        ha, hb, hc = 12.0, 12.0, 12.0
        l = 5000.0
        Rmg_val = 0.008

        Z_result = metodo_imagem_long(ra, rb, rc, xa, ha, xb, hb, xc, hc, l, Rmg_val=Rmg_val)

        self.assertIsInstance(Z_result, np.ndarray)
        self.assertEqual(Z_result.shape, (3, 3))
        self.assertTrue(np.issubdtype(Z_result.dtype, np.complexfloating))
        
        self.assertTrue(np.all(Z_result != 0))

    def test_R_e_Rmg_val_ausentes(self):
        """Testa erro se R e Rmg_val estiverem ausentes."""
        with self.assertRaisesRegex(ValueError, "Forneça o Raio \(R\) OU o Raio Médio Geométrico \(Rmg_val\)."):
            metodo_imagem_long(0.1, 0.1, 0.1, -5.0, 10.0, 0.0, 10.0, 5.0, 10.0, 1000.0)

    def test_R_negativo(self):
        """Testa erro se R for negativo."""
        with self.assertRaisesRegex(ValueError, "O Raio \(R\) ou o Raio Médio Geométrico \(Rmg_val\) deve ser positivo."):
            metodo_imagem_long(0.1, 0.1, 0.1, -5.0, 10.0, 0.0, 10.0, 5.0, 10.0, 1000.0, R=-0.01)

    def test_Rmg_val_zero(self):
        """Testa erro se Rmg_val for zero."""
        with self.assertRaisesRegex(ValueError, "O Raio \(R\) ou o Raio Médio Geométrico \(Rmg_val\) deve ser positivo."):
            metodo_imagem_long(0.1, 0.1, 0.1, -5.0, 10.0, 0.0, 10.0, 5.0, 10.0, 1000.0, Rmg_val=0.0)

    def test_alturas_negativas(self):
        """Testa erro se alturas forem negativas."""
        with self.assertRaisesRegex(ValueError, "As alturas dos condutores \(ha, hb, hc\) devem ser maiores que zero."):
            metodo_imagem_long(0.1, 0.1, 0.1, -5.0, -10.0, 0.0, 10.0, 5.0, 10.0, 1000.0, R=0.01)
        
        with self.assertRaisesRegex(ValueError, "As alturas dos condutores \(ha, hb, hc\) devem ser maiores que zero."):
            metodo_imagem_long(0.1, 0.1, 0.1, -5.0, 10.0, 0.0, 0.0, 5.0, 10.0, 1000.0, R=0.01)

    def test_comprimento_linha_zero(self):
        """Testa se a matriz é zero quando o comprimento da linha é zero."""
        ra, rb, rc = 0.1, 0.1, 0.1
        xa, xb, xc = -5.0, 0.0, 5.0
        ha, hb, hc = 10.0, 10.0, 10.0
        l = 0.0
        R = 0.01

        Z_result = metodo_imagem_long(ra, rb, rc, xa, ha, xb, hb, xc, hc, l, R=R)
        np.testing.assert_allclose(Z_result, np.zeros((3, 3), dtype=complex), atol=1e-9)

# --- Execução dos Testes ---
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)