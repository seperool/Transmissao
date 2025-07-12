import numpy as np
import math
import cmath

import unittest

def comp_sim_sintese(Zan0_modulo, Zan0_angulo, Zan1_modulo, Zan1_angulo, Zan2_modulo, Zan2_angulo):
    """
    Realiza a síntese das componentes simétricas para obter as tensões de fase.
    
    A função converte as componentes de sequência zero, positiva e negativa
    (dadas em módulo e ângulo) em suas formas complexas e, em seguida,
    as transforma em tensões de fase (Va, Vb, Vc) usando a matriz de transformação.

    Parâmetros:
    Van0_modulo (float): Módulo da componente de sequência zero.
    Van0_angulo (float): Ângulo (em graus) da componente de sequência zero.
    Van1_modulo (float): Módulo da componente de sequência positiva.
    Van1_angulo (float): Ângulo (em graus) da componente de sequência positiva.
    Van2_modulo (float): Módulo da componente de sequência negativa.
    Van2_angulo (float): Ângulo (em graus) da componente de sequência negativa.

    Retorna:
    numpy.ndarray: Um array NumPy (3x1) contendo as tensões de fase [Va, Vb, Vc].
    """
    
    # Convertendo as componentes de sequência para números complexos (fasores)
    angulo_rad_0 = math.radians(Zan0_angulo)
    Zan0 = cmath.rect(Zan0_modulo, angulo_rad_0)
    # print(f"Van0 (complexo): {Van0:.4f}") 

    angulo_rad_1 = math.radians(Zan1_angulo)
    Zan1 = cmath.rect(Zan1_modulo, angulo_rad_1)
    # print(f"Van1 (complexo): {Van1:.4f}")

    angulo_rad_2 = math.radians(Zan2_angulo)
    Zan2 = cmath.rect(Zan2_modulo, angulo_rad_2)
    # print(f"Van2 (complexo): {Van2:.4f}")

    # Criando a matriz coluna das componentes de sequência [Van0; Van1; Van2]
    Zan = np.array([[Zan0], [Zan1], [Zan2]])
    # print("\nMatriz Van (Componentes de Sequência):")
    # print(Van)

    # Calculando o operador 'a' (1 ângulo 120 graus)
    magnitude_a = 1
    angulo_graus_a = 120
    angulo_rad_a = math.radians(angulo_graus_a)
    a = cmath.rect(magnitude_a, angulo_rad_a)
    # print(f"\nOperador 'a': {a:.4f}")

    # Criando a matriz de transformação A (matriz de síntese)
    A = np.array([[1, 1, 1],
                  [1, a**2, a],
                  [1, a, a**2]])
    # print("\nMatriz de Transformação A:")
    # print(A)

    # Realizando a multiplicação matricial para obter as tensões de fase
    Zabc = A @ Zan
    # print("\nMatriz Vabc (Tensões de Fase):")
    # print(Vabc)

    return Zabc

class TestCompSimSintese(unittest.TestCase):

    # Define uma tolerância para comparações de números complexos
    # Operações com ponto flutuante geram pequenas imprecisões.
    def setUp(self):
        self.tolerance = 1e-9 # Uma tolerância de 1 nano (0.000000001) é boa para tensões

    # Função auxiliar para comparar dois números complexos com tolerância
    def assertComplexAlmostEqual(self, actual, expected, delta):
        self.assertAlmostEqual(actual.real, expected.real, delta=delta, 
                               msg=f"Parte real difere. Esperado: {expected.real}, Obtido: {actual.real}")
        self.assertAlmostEqual(actual.imag, expected.imag, delta=delta,
                               msg=f"Parte imaginária difere. Esperado: {expected.imag}, Obtido: {actual.imag}")

    # --- Testes de Casos Válidos (Cálculos Corretos) ---

    def test_sistema_equilibrado_sequencia_positiva(self):
        # Teste para um sistema trifásico equilibrado de sequência positiva
        # Espera-se: Van0 = 0, Van2 = 0
        # Van1 = 100 < 0 graus (referência)
        # Va = 100 < 0, Vb = 100 < -120, Vc = 100 < 120
        
        Van0_mod = 0.0
        Van0_ang = 0.0 # O ângulo não importa se o módulo é 0

        Van1_mod = 100.0
        Van1_ang = 0.0

        Van2_mod = 0.0
        Van2_ang = 0.0 # O ângulo não importa se o módulo é 0

        result_vabc = comp_sim_sintese(Van0_mod, Van0_ang,
                                        Van1_mod, Van1_ang,
                                        Van2_mod, Van2_ang)
        
        # Valores esperados
        Va_expected = cmath.rect(100.0, math.radians(0.0))
        Vb_expected = cmath.rect(100.0, math.radians(-120.0))
        Vc_expected = cmath.rect(100.0, math.radians(120.0))

        self.assertComplexAlmostEqual(result_vabc[0, 0], Va_expected, self.tolerance)
        self.assertComplexAlmostEqual(result_vabc[1, 0], Vb_expected, self.tolerance)
        self.assertComplexAlmostEqual(result_vabc[2, 0], Vc_expected, self.tolerance)
        
        # Verifica se o formato da matriz de saída é (3, 1)
        self.assertEqual(result_vabc.shape, (3, 1))


    def test_sistema_com_sequencia_zero_e_positiva(self):
        # Teste com contribuição de sequência zero e positiva
        # Van0 = 10 < 0, Van1 = 100 < 0, Van2 = 0
        # Va = Van0 + Van1 + Van2 = 10 + 100 + 0 = 110 < 0
        # Vb = Van0 + a^2*Van1 + a*Van2 = 10 + 100 * (1<-120) + 0 = 10 + 100*(-0.5 - j0.866) = 10 - 50 - j86.6 = -40 - j86.6
        # Vc = Van0 + a*Van1 + a^2*Van2 = 10 + 100 * (1<120) + 0 = 10 + 100*(-0.5 + j0.866) = 10 - 50 + j86.6 = -40 + j86.6
        
        Van0_mod = 10.0
        Van0_ang = 0.0

        Van1_mod = 100.0
        Van1_ang = 0.0

        Van2_mod = 0.0
        Van2_ang = 0.0

        result_vabc = comp_sim_sintese(Van0_mod, Van0_ang,
                                        Van1_mod, Van1_ang,
                                        Van2_mod, Van2_ang)
        
        # Calculando os valores esperados manualmente ou com a fórmula
        a = cmath.rect(1, math.radians(120))
        Van0_complex = cmath.rect(Van0_mod, math.radians(Van0_ang))
        Van1_complex = cmath.rect(Van1_mod, math.radians(Van1_ang))
        Van2_complex = cmath.rect(Van2_mod, math.radians(Van2_ang))

        Va_expected = Van0_complex + Van1_complex + Van2_complex
        Vb_expected = Van0_complex + (a**2) * Van1_complex + a * Van2_complex
        Vc_expected = Van0_complex + a * Van1_complex + (a**2) * Van2_complex

        self.assertComplexAlmostEqual(result_vabc[0, 0], Va_expected, self.tolerance)
        self.assertComplexAlmostEqual(result_vabc[1, 0], Vb_expected, self.tolerance)
        self.assertComplexAlmostEqual(result_vabc[2, 0], Vc_expected, self.tolerance)


    def test_sistema_desequilibrado_completo(self):
        # Teste com todas as componentes de sequência
        # Van0 = 10 < 180, Van1 = 50 < 0, Van2 = 20 < 90 (seus valores de exemplo)
        
        Van0_mod = 10.0
        Van0_ang = 180.0 # -10 + j0

        Van1_mod = 50.0
        Van1_ang = 0.0   # 50 + j0

        Van2_mod = 20.0
        Van2_ang = 90.0  # 0 + j20

        result_vabc = comp_sim_sintese(Van0_mod, Van0_ang,
                                        Van1_mod, Van1_ang,
                                        Van2_mod, Van2_ang)
        
        # Calculando os valores esperados manualmente
        a = cmath.rect(1, math.radians(120))
        Van0_complex = cmath.rect(Van0_mod, math.radians(Van0_ang))
        Van1_complex = cmath.rect(Van1_mod, math.radians(Van1_ang))
        Van2_complex = cmath.rect(Van2_mod, math.radians(Van2_ang))

        Va_expected = Van0_complex + Van1_complex + Van2_complex
        Vb_expected = Van0_complex + (a**2) * Van1_complex + a * Van2_complex
        Vc_expected = Van0_complex + a * Van1_complex + (a**2) * Van2_complex
        
        self.assertComplexAlmostEqual(result_vabc[0, 0], Va_expected, self.tolerance)
        self.assertComplexAlmostEqual(result_vabc[1, 0], Vb_expected, self.tolerance)
        self.assertComplexAlmostEqual(result_vabc[2, 0], Vc_expected, self.tolerance)


    def test_modulo_zero(self):
        # Teste com todos os módulos zero
        # Todas as tensões de fase devem ser zero
        result_vabc = comp_sim_sintese(0, 0, 0, 0, 0, 0)
        
        Va_expected = 0j
        Vb_expected = 0j
        Vc_expected = 0j

        self.assertComplexAlmostEqual(result_vabc[0, 0], Va_expected, self.tolerance)
        self.assertComplexAlmostEqual(result_vabc[1, 0], Vb_expected, self.tolerance)
        self.assertComplexAlmostEqual(result_vabc[2, 0], Vc_expected, self.tolerance)

    # --- Testes de Edge Cases (Valores Limite ou Específicos) ---

    def test_angulos_negativos(self):
        # Teste com ângulos negativos para todas as componentes
        # Van0 = 10 < -90, Van1 = 50 < -30, Van2 = 20 < -180
        
        Van0_mod = 10.0
        Van0_ang = -90.0 

        Van1_mod = 50.0
        Van1_ang = -30.0 

        Van2_mod = 20.0
        Van2_ang = -180.0

        result_vabc = comp_sim_sintese(Van0_mod, Van0_ang,
                                        Van1_mod, Van1_ang,
                                        Van2_mod, Van2_ang)
        
        # Calculando os valores esperados
        a = cmath.rect(1, math.radians(120))
        Van0_complex = cmath.rect(Van0_mod, math.radians(Van0_ang))
        Van1_complex = cmath.rect(Van1_mod, math.radians(Van1_ang))
        Van2_complex = cmath.rect(Van2_mod, math.radians(Van2_ang))

        Va_expected = Van0_complex + Van1_complex + Van2_complex
        Vb_expected = Van0_complex + (a**2) * Van1_complex + a * Van2_complex
        Vc_expected = Van0_complex + a * Van1_complex + (a**2) * Van2_complex
        
        self.assertComplexAlmostEqual(result_vabc[0, 0], Va_expected, self.tolerance)
        self.assertComplexAlmostEqual(result_vabc[1, 0], Vb_expected, self.tolerance)
        self.assertComplexAlmostEqual(result_vabc[2, 0], Vc_expected, self.tolerance)

# Bloco para rodar os testes quando o script é executado diretamente
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)