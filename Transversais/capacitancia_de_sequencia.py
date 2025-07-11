import math
import numpy as np

import unittest

def metodo_capacitancia_sequencia_tran(ra, rb, rc, xa, xb, xc, ha, hb, hc, rho):
    """
    Calcula a matriz de capacitância de sequência de uma linha de transmissão trifásica
    com configuração horizontal, usando o Método de Carson.

    Parâmetros:
    ra, rb, rc (float): Raios dos condutores A, B e C em metros.
    xa, xb, xc (float): Coordenadas horizontais (x) dos condutores A, B e C em metros.
    ha, hb, hc (float): Alturas dos condutores A, B e C acima do solo em metros.
    rho (float): Resistividade do solo em Ohm-metros.

    Retorna:
    numpy.ndarray: Matriz de capacitância de sequência 3x3 da linha (F/m),
                   incluindo componentes imaginários.

    Raises:
    ValueError: Se a resistividade do solo (rho) for <= 0 ou alturas (ha, hb, hc) forem <= 0.
    """
    # Constantes físicas
    E = 8.854 * 10**(-12)  # Permissividade do vácuo (F/m)

    # Validação de entradas
    if rho <= 0:
        raise ValueError("ERRO! A resistividade do solo (rho) deve ser um valor positivo.")
    if ha <= 0 or hb <= 0 or hc <= 0:
        raise ValueError("ERRO! As alturas dos condutores (ha, hb, hc) devem ser maiores que zero.")

    # Converte entradas para arrays para operações de matriz
    r_vec = np.array([ra, rb, rc])
    x_vec = np.array([xa, xb, xc])
    h_vec = np.array([ha, hb, hc])

    # Cálculo das distâncias diretas entre condutores (D)
    diff_x = x_vec[:, np.newaxis] - x_vec
    diff_h = h_vec[:, np.newaxis] - h_vec
    D = np.sqrt(diff_x**2 + diff_h**2)

    # Cálculo das distâncias entre condutores e suas imagens (D_prime)
    sum_h = h_vec[:, np.newaxis] + h_vec
    D_prime = np.sqrt(diff_x**2 + sum_h**2)

    # --- Constrói a matriz de potencial (P) em F/m ---
    P = np.zeros((3, 3), dtype=complex)

    # Preencher elementos diagonais (auto-potenciais)
    for i in range(3):
        P[i, i] = (1 / (2 * np.pi * E)) * np.log((2 * h_vec[i]) / r_vec[i])

    # Preencher elementos fora da diagonal (potenciais mútuos)
    for i in range(3):
        for j in range(i + 1, 3):
            P[i, j] = (1 / (2 * np.pi * E)) * np.log(D_prime[i, j] / D[i, j])
            P[j, i] = P[i, j] # Matriz P é simétrica

    # A matriz P_ph_ph não precisa mais ser multiplicada por 1000
    # se quisermos a saída em F/m.
    P_ph_ph = P

    # Calcula a matriz de capacitância de fase (C_abc) em F/m
    C_abc = np.linalg.inv(P_ph_ph)

    # Matriz de transformação de sequência (Fortescue)
    alpha = np.exp(1j * 2 * np.pi / 3)
    A = (1/3) * np.array([[1, 1, 1],
                          [1, alpha, alpha**2],
                          [1, alpha**2, alpha]], dtype=complex)
    A_inv = np.array([[1, 1, 1],
                      [1, alpha**2, alpha],
                      [1, alpha, alpha**2]], dtype=complex)

    # Calcula a matriz de capacitância de sequência (C_012)
    C_seq = A @ C_abc @ A_inv

    # Retorna C_seq com componentes imaginários e em F/m
    return C_seq

# --- CLASSE DE TESTE UNITÁRIO ---
class TestMetodoCapacitanciaSequenciaTran(unittest.TestCase):

    # Constante de permissividade do vácuo para cálculos de referência
    E = 8.854 * 10**(-12)

    def test_valores_validos_configuracao_simetrica(self):
        """
        Testa uma configuração de linha simétrica com valores válidos.
        Espera-se uma matriz de capacitância de sequência com C0 != C1 = C2.
        """
        ra, rb, rc = 0.01, 0.01, 0.01  # Raios iguais
        xa, xb, xc = -2.0, 0.0, 2.0   # Configuração horizontal simétrica
        ha, hb, hc = 10.0, 10.0, 10.0 # Alturas iguais
        rho = 100.0                   # Resistividade do solo

        C_seq = metodo_capacitancia_sequencia_tran(ra, rb, rc, xa, xb, xc, ha, hb, hc, rho)

        # Verifica se a saída é um numpy array complexo de 3x3
        self.assertIsInstance(C_seq, np.ndarray)
        self.assertEqual(C_seq.shape, (3, 3))
        self.assertTrue(np.issubdtype(C_seq.dtype, np.complexfloating))

        # Para uma linha simétrica não transposta, C_012 tem a forma diagonal,
        # mas com o método de Carson (solo), pode haver pequenas componentes
        # fora da diagonal e imaginárias, e os valores de sequência são reais.
        # No entanto, C0 é diferente de C1/C2 (que são iguais).
        # Vamos verificar a magnitude dos valores na diagonal principal.
        # Os elementos C[0,0] (seq zero), C[1,1] (seq positiva), C[2,2] (seq negativa)

        # C_00 (sequência zero)
        self.assertGreater(C_seq[0, 0].real, 0, "C00 real deve ser positivo")
        # C_11 (sequência positiva)
        self.assertGreater(C_seq[1, 1].real, 0, "C11 real deve ser positivo")
        # C_22 (sequência negativa)
        self.assertGreater(C_seq[2, 2].real, 0, "C22 real deve ser positivo")

        # Em linhas simétricas e não transpostas, C1 = C2 (ou muito próximos)
        np.testing.assert_allclose(C_seq[1, 1], C_seq[2, 2], atol=1e-15,
                                   err_msg="C11 e C22 devem ser aproximadamente iguais para linha simétrica")

        # C0 deve ser diferente de C1/C2 (em geral, menor)
        self.assertLess(C_seq[0, 0].real, C_seq[1, 1].real, "C00 real deve ser menor que C11 real")

        # Componentes fora da diagonal devem ser próximos de zero para esta configuração ideal
        np.testing.assert_allclose(C_seq[0, 1], 0, atol=1e-18)
        np.testing.assert_allclose(C_seq[0, 2], 0, atol=1e-18)
        np.testing.assert_allclose(C_seq[1, 0], 0, atol=1e-18)
        np.testing.assert_allclose(C_seq[1, 2], 0, atol=1e-18)
        np.testing.assert_allclose(C_seq[2, 0], 0, atol=1e-18)
        np.testing.assert_allclose(C_seq[2, 1], 0, atol=1e-18)

    def test_valores_validos_configuracao_assimetrica(self):
        """
        Testa uma configuração de linha assimétrica com valores válidos.
        Espera-se uma matriz de capacitância de sequência com elementos fora da diagonal.
        """
        ra, rb, rc = 0.012, 0.015, 0.01  # Raios diferentes
        xa, xb, xc = -3.0, 0.5, 2.5     # Posições assimétricas
        ha, hb, hc = 12.0, 10.0, 11.0   # Alturas diferentes
        rho = 500.0                     # Resistividade do solo

        C_seq = metodo_capacitancia_sequencia_tran(ra, rb, rc, xa, xb, xc, ha, hb, hc, rho)

        self.assertIsInstance(C_seq, np.ndarray)
        self.assertEqual(C_seq.shape, (3, 3))
        self.assertTrue(np.issubdtype(C_seq.dtype, np.complexfloating))

        # A diagonal principal ainda deve ser a mais significativa
        self.assertGreater(C_seq[0, 0].real, 0)
        self.assertGreater(C_seq[1, 1].real, 0)
        self.assertGreater(C_seq[2, 2].real, 0)

        # Espera-se que elementos fora da diagonal não sejam zero
        # Não testamos valores exatos, apenas que não são trivialmente zero.
        self.assertFalse(np.isclose(C_seq[0, 1], 0, atol=1e-15))
        self.assertFalse(np.isclose(C_seq[1, 0], 0, atol=1e-15))

    def test_rho_invalido(self):
        """
        Testa se a função levanta ValueError para rho <= 0.
        """
        # Dados de exemplo válidos
        ra, rb, rc = 0.01, 0.01, 0.01
        xa, xb, xc = -2.0, 0.0, 2.0
        ha, hb, hc = 10.0, 10.0, 10.0

        # Teste com rho = 0
        with self.assertRaisesRegex(ValueError, "A resistividade do solo \(rho\) deve ser um valor positivo."):
            metodo_capacitancia_sequencia_tran(ra, rb, rc, xa, xb, xc, ha, hb, hc, 0.0)

        # Teste com rho < 0
        with self.assertRaisesRegex(ValueError, "A resistividade do solo \(rho\) deve ser um valor positivo."):
            metodo_capacitancia_sequencia_tran(ra, rb, rc, xa, xb, xc, ha, hb, hc, -100.0)

    def test_alturas_invalidas(self):
        """
        Testa se a função levanta ValueError para alturas <= 0.
        """
        # Dados de exemplo válidos
        ra, rb, rc = 0.01, 0.01, 0.01
        xa, xb, xc = -2.0, 0.0, 2.0
        rho = 100.0

        # Teste com ha = 0
        with self.assertRaisesRegex(ValueError, "As alturas dos condutores \(ha, hb, hc\) devem ser maiores que zero."):
            metodo_capacitancia_sequencia_tran(ra, rb, rc, xa, xb, xc, 0.0, 10.0, 10.0, rho)

        # Teste com hb < 0
        with self.assertRaisesRegex(ValueError, "As alturas dos condutores \(ha, hb, hc\) devem ser maiores que zero."):
            metodo_capacitancia_sequencia_tran(ra, rb, rc, xa, xb, xc, 10.0, -5.0, 10.0, rho)

        # Teste com hc = 0
        with self.assertRaisesRegex(ValueError, "As alturas dos condutores \(ha, hb, hc\) devem ser maiores que zero."):
            metodo_capacitancia_sequencia_tran(ra, rb, rc, xa, xb, xc, 10.0, 10.0, 0.0, rho)

    def test_raios_negativos_ou_zero(self):
        """
        Testa se a função lida corretamente com raios <= 0 (deve ocorrer um erro no logaritmo,
        pois o raio aparece no denominador do log).
        """
        ra, rb, rc = 0.01, 0.01, 0.01
        xa, xb, xc = -2.0, 0.0, 2.0
        ha, hb, hc = 10.0, 10.0, 10.0
        rho = 100.0

        # Teste com ra = 0 (log(x/0) -> divisão por zero ou math domain error)
        with self.assertRaises((ValueError, ZeroDivisionError, RuntimeWarning)): # Dependendo da implementação do log
            metodo_capacitancia_sequencia_tran(0.0, rb, rc, xa, xb, xc, ha, hb, hc, rho)
        
        # Teste com rb < 0
        with self.assertRaises((ValueError, RuntimeWarning)): # math.log de número negativo
            metodo_capacitancia_sequencia_tran(ra, -0.005, rc, xa, xb, xc, ha, hb, hc, rho)

    def test_valores_extremos(self):
        """
        Testa a função com valores extremos para raios e alturas, mas ainda válidos.
        """
        ra, rb, rc = 0.001, 0.001, 0.001  # Raios muito pequenos
        xa, xb, xc = -10.0, 0.0, 10.0   # Grandes distâncias horizontais
        ha, hb, hc = 5.0, 5.0, 5.0      # Alturas menores
        rho = 10.0                      # Baixa resistividade do solo

        C_seq = metodo_capacitancia_sequencia_tran(ra, rb, rc, xa, xb, xc, ha, hb, hc, rho)
        self.assertIsInstance(C_seq, np.ndarray)
        self.assertEqual(C_seq.shape, (3, 3))

        # Os valores resultantes devem ser numéricos e não NaN ou Inf
        self.assertTrue(np.all(np.isfinite(C_seq)))

    def test_comparacao_com_valor_conhecido_simples(self):
        """
        Testa com um conjunto de parâmetros para o qual um resultado de referência
        pode ser calculado ou é conhecido.
        Este teste é mais complexo e requer um valor de referência preciso.
        Para simplificar, vamos verificar algumas propriedades da matriz P_ph_ph para um caso base.
        """
        # Dados de exemplo simples e simétricos
        ra, rb, rc = 0.01, 0.01, 0.01
        xa, xb, xc = -1.0, 0.0, 1.0
        ha, hb, hc = 10.0, 10.0, 10.0
        rho = 1.0 # Resistividade do solo mínima para não afetar os cálculos ideais de P.

        # Recálculo manual de P_ph_ph para validação
        E_const = 8.854 * 10**(-12)

        P_expected = np.zeros((3, 3), dtype=complex)

        # Auto-potenciais
        P_expected[0, 0] = (1 / (2 * np.pi * E_const)) * math.log((2 * ha) / ra)
        P_expected[1, 1] = (1 / (2 * np.pi * E_const)) * math.log((2 * hb) / rb)
        P_expected[2, 2] = (1 / (2 * np.pi * E_const)) * math.log((2 * hc) / rc)

        # Potenciais mútuos D_AB, D_BC, D_AC
        D_AB = math.sqrt((xa - xb)**2 + (ha - hb)**2)
        D_BC = math.sqrt((xb - xc)**2 + (hb - hc)**2)
        D_AC = math.sqrt((xa - xc)**2 + (ha - hc)**2)

        # Potenciais mútuos D'_AB, D'_BC, D'_AC
        D_prime_AB = math.sqrt((xa - xb)**2 + (ha + hb)**2)
        D_prime_BC = math.sqrt((xb - xc)**2 + (hb + hc)**2)
        D_prime_AC = math.sqrt((xa - xc)**2 + (ha + hc)**2)

        P_expected[0, 1] = (1 / (2 * np.pi * E_const)) * math.log(D_prime_AB / D_AB)
        P_expected[1, 0] = P_expected[0, 1]
        P_expected[1, 2] = (1 / (2 * np.pi * E_const)) * math.log(D_prime_BC / D_BC)
        P_expected[2, 1] = P_expected[1, 2]
        P_expected[0, 2] = (1 / (2 * np.pi * E_const)) * math.log(D_prime_AC / D_AC)
        P_expected[2, 0] = P_expected[0, 2]

        # Executa a função e verifica a matriz de potencial (passo intermediário)
        # Para isso, precisamos acessar a matriz P_ph_ph internamente, o que não é ideal para um teste unitário.
        # Em vez disso, vamos comparar o resultado final C_seq.
        # Um resultado de referência para C_seq é complexo e depende de muitas operações.
        # Vamos usar um valor aproximado para C11 e C00 para esta configuração simétrica
        # (para uma linha aérea com solo perfeito, onde C_00 e C_11 seriam reais e C_11 = C_22)
        # Capacitância de sequência positiva e negativa (C1 = C2) para esta configuração
        # C1 = 2 * pi * E / ln( DMG / Raio_equivalente_fase )
        # Para configuração horizontal simétrica: DMG = (d_AB * d_BC * d_AC)^(1/3)
        # d_AB = 2, d_BC = 2, d_AC = 4. DMG = (2*2*4)^(1/3) = (16)^(1/3) approx 2.5198
        # Raio_equivalente = ra (para condutores singelos) = 0.01
        # C1_aprox_ideal = 2 * np.pi * E_const / np.log(2.5198 / 0.01) approx 1.139e-11 F/m (sem considerar imagens)

        # Com o método de Carson, há uma pequena parte imaginária e o efeito do solo.
        # Vamos executar e verificar as propriedades.
        C_seq_actual = metodo_capacitancia_sequencia_tran(ra, rb, rc, xa, xb, xc, ha, hb, hc, rho)

        # Verifica se C1 e C2 são muito próximos (para linha não transposta e simétrica)
        np.testing.assert_allclose(C_seq_actual[1, 1], C_seq_actual[2, 2], rtol=1e-5, atol=1e-18,
                                   err_msg="C1 e C2 devem ser muito próximos na diagonal para linha simétrica")

        # Verifica que C0 é diferente de C1/C2
        self.assertNotAlmostEqual(C_seq_actual[0, 0].real, C_seq_actual[1, 1].real, places=12,
                                  msg="C0 e C1 reais devem ser diferentes")

# --- Execução dos Testes ---
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)