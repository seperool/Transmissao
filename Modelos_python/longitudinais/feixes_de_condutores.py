import math
import numpy as np
import unittest

def calcular_rmg_feixe(n, d, R=None, Rmg_val=None):
    """
    Calcula o Raio Médio Geométrico (RMG) equivalente de um feixe de condutores.

    A função suporta feixes com 2, 3 ou 4 subcondutores em arranjos comuns.

    Parâmetros:
    n (int): Número de subcondutores no feixe (2, 3 ou 4).
    d (float): Distância entre subcondutores adjacentes no feixe (em metros).
    R (float, opcional): Raio físico do subcondutor individual (em metros).
                         Usado para calcular o RMG do subcondutor se 'Rmg_val' não for fornecido.
    Rmg_val (float, opcional): Raio Médio Geométrico (RMG) do subcondutor individual (em metros).
                               Tem prioridade sobre o cálculo a partir de 'R'.

    Retorna:
    float: O Raio Médio Geométrico (RMG) equivalente do feixe (em metros).

    Levanta:
    ValueError: Se 'R' ou 'Rmg_val' não forem fornecidos, forem negativos,
                se 'd' for negativo ou zero, ou se 'n' não for 2, 3 ou 4.
    """
    
    # --- Cálculo do Raio Médio Geométrico (RMG) do subcondutor individual ---
    rmg_subcondutor = None
    if Rmg_val is not None:
        rmg_subcondutor = Rmg_val
    elif R is not None:
        rmg_subcondutor = R * math.exp(-1/4) # RMG para condutor sólido/simples

    # --- Validações de Entrada ---
    if rmg_subcondutor is None:
        raise ValueError("ERRO! É necessário fornecer o raio físico (R) OU o RMG do subcondutor (Rmg_val).")
    if rmg_subcondutor <= 0:
        raise ValueError("ERRO! O RMG do subcondutor deve ser um valor positivo.")
    if d <= 0:
        raise ValueError("ERRO! A distância entre os subcondutores 'd' deve ser maior que zero.")

    # --- Cálculo do RMG do Feixe baseando-se no número de subcondutores (n) ---
    Rmg_feixe = 0.0 # Inicializa Rmg_feixe para garantir que seja sempre definida

    if n == 2:
        # Feixe de 2 subcondutores: RMG_feixe = sqrt(r' * d)
        Rmg_feixe = (rmg_subcondutor * d)**(1/2)
    elif n == 3:
        # Feixe de 3 subcondutores (triângulo equilátero): RMG_feixe = (r' * d^2)^(1/3)
        Rmg_feixe = (rmg_subcondutor * (d**2))**(1/3)
    elif n == 4:
        # Feixe de 4 subcondutores (quadrado): RMG_feixe = (r' * d^3 * sqrt(2))^(1/4)
        Rmg_feixe = (rmg_subcondutor * (d**3) * math.sqrt(2))**(1/4)
    else:
        raise ValueError("ERRO! O número de subcondutores 'n' suportado é 2, 3 ou 4 para este cálculo.")
    
    return Rmg_feixe

class TestCalcularRMGFeixe(unittest.TestCase):

    # Define uma tolerância para comparações de ponto flutuante
    # RMG são valores pequenos, então uma tolerância razoável é importante.
    def setUp(self):
        self.tolerance = 1e-9 # 1 nanômetro, adequado para metros

    # --- Testes de Casos Válidos (Cálculos Corretos) ---

    def test_n_equals_2_with_R(self):
        # Teste para n=2 (feixe de 2 condutores) usando o raio físico R
        # RMG_feixe = sqrt(r' * d)
        R_condutor = 0.01 # 10 mm
        d_feixe = 0.45 # 45 cm
        
        # RMG do subcondutor: r' = R * e^(-1/4)
        rmg_subcondutor_esperado = R_condutor * math.exp(-1/4)
        expected_rmg_feixe = math.sqrt(rmg_subcondutor_esperado * d_feixe)
        
        calculated_rmg_feixe = calcular_rmg_feixe(n=2, d=d_feixe, R=R_condutor)
        self.assertAlmostEqual(calculated_rmg_feixe, expected_rmg_feixe, delta=self.tolerance)

    def test_n_equals_2_with_Rmg_val(self):
        # Teste para n=2 usando o RMG do subcondutor diretamente
        rmg_subcondutor = 0.007788 # Exemplo de RMG
        d_feixe = 0.5
        expected_rmg_feixe = math.sqrt(rmg_subcondutor * d_feixe)
        
        calculated_rmg_feixe = calcular_rmg_feixe(n=2, d=d_feixe, Rmg_val=rmg_subcondutor)
        self.assertAlmostEqual(calculated_rmg_feixe, expected_rmg_feixe, delta=self.tolerance)

    def test_n_equals_3_with_R(self):
        # Teste para n=3 (feixe de 3 condutores - triângulo equilátero) usando R
        # RMG_feixe = (r' * d^2)^(1/3)
        R_condutor = 0.015
        d_feixe = 0.4
        
        rmg_subcondutor_esperado = R_condutor * math.exp(-1/4)
        expected_rmg_feixe = (rmg_subcondutor_esperado * (d_feixe**2))**(1/3)
        
        calculated_rmg_feixe = calcular_rmg_feixe(n=3, d=d_feixe, R=R_condutor)
        self.assertAlmostEqual(calculated_rmg_feixe, expected_rmg_feixe, delta=self.tolerance)

    def test_n_equals_3_with_Rmg_val(self):
        # Teste para n=3 usando Rmg_val
        rmg_subcondutor = 0.011682
        d_feixe = 0.35
        expected_rmg_feixe = (rmg_subcondutor * (d_feixe**2))**(1/3)
        
        calculated_rmg_feixe = calcular_rmg_feixe(n=3, d=d_feixe, Rmg_val=rmg_subcondutor)
        self.assertAlmostEqual(calculated_rmg_feixe, expected_rmg_feixe, delta=self.tolerance)

    def test_n_equals_4_with_R(self):
        # Teste para n=4 (feixe de 4 condutores - quadrado) usando R
        # RMG_feixe = (r' * d^3 * sqrt(2))^(1/4)
        R_condutor = 0.02
        d_feixe = 0.3
        
        rmg_subcondutor_esperado = R_condutor * math.exp(-1/4)
        expected_rmg_feixe = (rmg_subcondutor_esperado * (d_feixe**3) * math.sqrt(2))**(1/4)
        
        calculated_rmg_feixe = calcular_rmg_feixe(n=4, d=d_feixe, R=R_condutor)
        self.assertAlmostEqual(calculated_rmg_feixe, expected_rmg_feixe, delta=self.tolerance)

    def test_n_equals_4_with_Rmg_val(self):
        # Teste para n=4 usando Rmg_val
        rmg_subcondutor = 0.015576
        d_feixe = 0.25
        expected_rmg_feixe = (rmg_subcondutor * (d_feixe**3) * math.sqrt(2))**(1/4)
        
        calculated_rmg_feixe = calcular_rmg_feixe(n=4, d=d_feixe, Rmg_val=rmg_subcondutor)
        self.assertAlmostEqual(calculated_rmg_feixe, expected_rmg_feixe, delta=self.tolerance)

    # --- Testes de Erro (Validações) ---

    def test_no_rmg_or_r_provided(self):
        # Deve levantar ValueError se nem R nem Rmg_val forem fornecidos
        with self.assertRaisesRegex(ValueError, "ERRO! É necessário fornecer o raio físico \\(R\\) OU o RMG do subcondutor \\(Rmg_val\\)."):
            calcular_rmg_feixe(n=2, d=0.45)

    def test_rmg_subcondutor_zero(self):
        # Deve levantar ValueError se RMG do subcondutor for zero
        with self.assertRaisesRegex(ValueError, "ERRO! O RMG do subcondutor deve ser um valor positivo."):
            calcular_rmg_feixe(n=2, d=0.45, R=0)
        
        with self.assertRaisesRegex(ValueError, "ERRO! O RMG do subcondutor deve ser um valor positivo."):
            calcular_rmg_feixe(n=2, d=0.45, Rmg_val=0)

    def test_rmg_subcondutor_negative(self):
        # Deve levantar ValueError se RMG do subcondutor for negativo
        with self.assertRaisesRegex(ValueError, "ERRO! O RMG do subcondutor deve ser um valor positivo."):
            calcular_rmg_feixe(n=2, d=0.45, R=-0.01)

        with self.assertRaisesRegex(ValueError, "ERRO! O RMG do subcondutor deve ser um valor positivo."):
            calcular_rmg_feixe(n=2, d=0.45, Rmg_val=-0.001)

    def test_d_zero(self):
        # Deve levantar ValueError se a distância 'd' for zero
        with self.assertRaisesRegex(ValueError, "ERRO! A distância entre os subcondutores 'd' deve ser maior que zero."):
            calcular_rmg_feixe(n=2, d=0, R=0.01)

    def test_d_negative(self):
        # Deve levantar ValueError se a distância 'd' for negativa
        with self.assertRaisesRegex(ValueError, "ERRO! A distância entre os subcondutores 'd' deve ser maior que zero."):
            calcular_rmg_feixe(n=2, d=-0.45, R=0.01)

    def test_n_unsupported(self):
        # Deve levantar ValueError se 'n' não for 2, 3 ou 4
        with self.assertRaisesRegex(ValueError, "ERRO! O número de subcondutores 'n' suportado é 2, 3 ou 4 para este cálculo."):
            calcular_rmg_feixe(n=1, d=0.5, R=0.01)

        with self.assertRaisesRegex(ValueError, "ERRO! O número de subcondutores 'n' suportado é 2, 3 ou 4 para este cálculo."):
            calcular_rmg_feixe(n=5, d=0.5, R=0.01)
            
        with self.assertRaisesRegex(ValueError, "ERRO! O número de subcondutores 'n' suportado é 2, 3 ou 4 para este cálculo."):
            calcular_rmg_feixe(n=0, d=0.5, R=0.01)

# Bloco para rodar os testes quando o script é executado diretamente
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)