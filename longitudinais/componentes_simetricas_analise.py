import numpy as np # Importa a biblioteca NumPy para operações com arrays e matrizes, essencial para cálculos com fasores.
import math # Importa o módulo math para funções matemáticas como conversão de graus para radianos.
import cmath # Importa o módulo cmath para operações com números complexos (fasores).

import unittest

def comp_sim_analise(Va_modulo, Va_angulo, Vb_modulo, Vb_angulo, Vc_modulo, Vc_angulo):
    """
    Realiza a análise das componentes simétricas, transformando as tensões de fase (Va, Vb, Vc)
    em suas respectivas componentes de sequência (V0 - zero, V1 - positiva, V2 - negativa).

    Parâmetros:
    Va_modulo (float): Módulo da tensão da fase A.
    Va_angulo (float): Ângulo (em graus) da tensão da fase A.
    Vb_modulo (float): Módulo da tensão da fase B.
    Vb_angulo (float): Ângulo (em graus) da tensão da fase B.
    Vc_modulo (float): Módulo da tensão da fase C.
    Vc_angulo (float): Ângulo (em graus) da tensão da fase C.

    Retorna:
    numpy.ndarray: Um array NumPy (3x1) contendo as componentes de sequência [V0, V1, V2].
                   Cada elemento é um número complexo (fasor).
    """
    
    # 1. Conversão das tensões de fase do formato polar (módulo e ângulo) para fasores complexos.
    # Fasor Va
    angulo_rad_Va = math.radians(Va_angulo) # Converte o ângulo de graus para radianos.
    Va = cmath.rect(Va_modulo, angulo_rad_Va) # Cria o número complexo (fasor) a partir do módulo e ângulo em radianos.

    # Fasor Vb
    angulo_rad_Vb = math.radians(Vb_angulo)
    Vb = cmath.rect(Vb_modulo, angulo_rad_Vb)

    # Fasor Vc
    angulo_rad_Vc = math.radians(Vc_angulo)
    Vc = cmath.rect(Vc_modulo, angulo_rad_Vc)

    # 2. Criação da matriz coluna das tensões de fase [Va; Vb; Vc].
    # Esta matriz é essencial para a operação de multiplicação matricial.
    Vabc = np.array([[Va], [Vb], [Vc]])
    
    # As linhas 'print' abaixo são úteis para depuração, mas devem ser comentadas ou removidas
    # em versões finais do código para evitar saídas desnecessárias.
    # print("\nMatriz das tensões de fase [Va; Vb; Vc]:")
    # print(Vabc)

    # 3. Cálculo do operador complexo 'a' (fasor de magnitude 1 e ângulo de 120 graus).
    # O operador 'a' é fundamental nas transformações de componentes simétricas.
    magnitude = 1
    angulo_graus = 120
    angulo_rad = math.radians(angulo_graus)
    a = cmath.rect(magnitude, angulo_rad)
    # print(f"\nOperador 'a': {a:.4f}")

    # 4. Criação da matriz de transformação 'A' para a ANÁLISE de componentes simétricas.
    # Esta matriz é a inversa da matriz de síntese (sem o fator 1/3) e permite a conversão
    # das tensões de fase para as componentes de sequência.
    A = np.array([[1, 1, 1],
                  [1, a, a**2],
                  [1, a**2, a]])
    # print("\nMatriz de Transformação para Análise (A):")
    # print(A)

    # 5. Realização da multiplicação matricial para obter as componentes de sequência.
    # A fórmula para a análise é: [V0; V1; V2] = (1/3) * A @ [Va; Vb; Vc].
    V012 = (1/3) * A @ Vabc
    # print("\nComponentes de Sequência Resultantes [V0; V1; V2]:")
    # print(V012)

    # Retorna o array NumPy contendo as componentes de sequência calculadas.
    return V012

class TestCompSimAnalise(unittest.TestCase):
    
    # O método setUp é executado antes de cada teste.
    # Usamos ele para definir uma tolerância para comparações de números complexos,
    # já que operações de ponto flutuante podem introduzir pequenas imprecisões.
    def setUp(self):
        self.tolerance = 1e-9 # Uma tolerância de 1 nano (0.000000001) é geralmente suficiente para cálculos de engenharia.

    # Função auxiliar para comparar dois números complexos (fasores) com a tolerância definida.
    # Isso é necessário porque 'assertAlmostEqual' do unittest compara apenas números reais.
    def assertComplexAlmostEqual(self, actual, expected, delta):
        self.assertAlmostEqual(actual.real, expected.real, delta=delta, 
                               msg=f"Parte real difere. Esperado: {expected.real}, Obtido: {actual.real}")
        self.assertAlmostEqual(actual.imag, expected.imag, delta=delta,
                               msg=f"Parte imaginária difere. Esperado: {expected.imag}, Obtido: {actual.imag}")

    # --- Testes de Casos Válidos (Verificando a Correção dos Cálculos) ---

    def test_sistema_equilibrado_sequencia_positiva(self):
        # Cenário: Um sistema trifásico equilibrado de sequência positiva.
        # Esperado: V0 (seq. zero) e V2 (seq. negativa) devem ser aproximadamente zero.
        # V1 (seq. positiva) deve ser igual à tensão de fase (e.g., 100<0).
        
        # Tensões de fase de entrada (100V, com defasagem de 120 graus)
        Va_modulo, Va_angulo = 100.0, 0.0
        Vb_modulo, Vb_angulo = 100.0, -120.0
        Vc_modulo, Vc_angulo = 100.0, 120.0

        # Chama a função a ser testada
        resultado_V012 = comp_sim_analise(Va_modulo, Va_angulo, 
                                          Vb_modulo, Vb_angulo, 
                                          Vc_modulo, Vc_angulo)
        
        # Valores esperados das componentes de sequência
        V0_esperado = 0.0 + 0.0j  # Deveria ser zero
        V1_esperado = cmath.rect(100.0, math.radians(0.0)) # V1 = Va (para esse caso equilibrado)
        V2_esperado = 0.0 + 0.0j  # Deveria ser zero

        # Verifica se as dimensões da matriz de saída estão corretas (3 linhas, 1 coluna)
        self.assertEqual(resultado_V012.shape, (3, 1))

        # Compara cada componente de sequência com o valor esperado
        self.assertComplexAlmostEqual(resultado_V012[0, 0], V0_esperado, self.tolerance) # V0
        self.assertComplexAlmostEqual(resultado_V012[1, 0], V1_esperado, self.tolerance) # V1
        self.assertComplexAlmostEqual(resultado_V012[2, 0], V2_esperado, self.tolerance) # V2

    def test_sistema_equilibrado_sequencia_negativa(self):
        # Cenário: Um sistema trifásico equilibrado de sequência negativa.
        # Esperado: V0 e V1 devem ser aproximadamente zero. V2 deve ser igual à tensão de fase.
        
        Va_modulo, Va_angulo = 100.0, 0.0
        Vb_modulo, Vb_angulo = 100.0, 120.0 # Vb adiantado de Va para seq. negativa
        Vc_modulo, Vc_angulo = 100.0, -120.0 # Vc atrasado de Va para seq. negativa

        resultado_V012 = comp_sim_analise(Va_modulo, Va_angulo, 
                                          Vb_modulo, Vb_angulo, 
                                          Vc_modulo, Vc_angulo)
        
        V0_esperado = 0.0 + 0.0j
        V1_esperado = 0.0 + 0.0j
        V2_esperado = cmath.rect(100.0, math.radians(0.0)) # V2 = Va

        self.assertComplexAlmostEqual(resultado_V012[0, 0], V0_esperado, self.tolerance)
        self.assertComplexAlmostEqual(resultado_V012[1, 0], V1_esperado, self.tolerance)
        self.assertComplexAlmostEqual(resultado_V012[2, 0], V2_esperado, self.tolerance)

    def test_sistema_somente_sequencia_zero(self):
        # Cenário: Um sistema onde todas as tensões de fase são iguais (somente componente de sequência zero).
        # Esperado: V1 e V2 devem ser aproximadamente zero. V0 deve ser igual à tensão de fase.
        
        Va_modulo, Va_angulo = 50.0, 30.0
        Vb_modulo, Vb_angulo = 50.0, 30.0
        Vc_modulo, Vc_angulo = 50.0, 30.0

        resultado_V012 = comp_sim_analise(Va_modulo, Va_angulo, 
                                          Vb_modulo, Vb_angulo, 
                                          Vc_modulo, Vc_angulo)
        
        V0_esperado = cmath.rect(50.0, math.radians(30.0)) # V0 = Va
        V1_esperado = 0.0 + 0.0j
        V2_esperado = 0.0 + 0.0j

        self.assertComplexAlmostEqual(resultado_V012[0, 0], V0_esperado, self.tolerance)
        self.assertComplexAlmostEqual(resultado_V012[1, 0], V1_esperado, self.tolerance)
        self.assertComplexAlmostEqual(resultado_V012[2, 0], V2_esperado, self.tolerance)

    def test_sistema_desequilibrado_generico(self):
        # Cenário: Um sistema desequilibrado com todas as componentes (exemplo comum de falta fase-terra).
        # Este teste usa os valores de exemplo que você usou para síntese, mas no sentido inverso.
        # Va = 10<180, Vb = 50<0, Vc = 20<90 (Não, esses eram os Van0, Van1, Van2. Vamos usar valores para Va, Vb, Vc)
        
        # Usando um exemplo mais genérico para desequilíbrio:
        Va_modulo, Va_angulo = 100.0, 0.0
        Vb_modulo, Vb_angulo = 80.0, -100.0
        Vc_modulo, Vc_angulo = 90.0, 130.0

        resultado_V012 = comp_sim_analise(Va_modulo, Va_angulo, 
                                          Vb_modulo, Vb_angulo, 
                                          Vc_modulo, Vc_angulo)
        
        # Cálculo manual dos valores esperados para verificação
        # Transformando as entradas para complexos primeiro
        Va_complex = cmath.rect(Va_modulo, math.radians(Va_angulo))
        Vb_complex = cmath.rect(Vb_modulo, math.radians(Vb_angulo))
        Vc_complex = cmath.rect(Vc_modulo, math.radians(Vc_angulo))

        # Operador 'a'
        a = cmath.rect(1, math.radians(120))
        
        # Matriz de análise A (sem o 1/3)
        A_analise = np.array([[1, 1, 1],
                              [1, a, a**2],
                              [1, a**2, a]])

        # Matriz de tensões de fase
        Vabc_matriz_calc = np.array([[Va_complex], [Vb_complex], [Vc_complex]])

        # Resultado esperado
        esperado_V012 = (1/3) * A_analise @ Vabc_matriz_calc

        self.assertComplexAlmostEqual(resultado_V012[0, 0], esperado_V012[0, 0], self.tolerance)
        self.assertComplexAlmostEqual(resultado_V012[1, 0], esperado_V012[1, 0], self.tolerance)
        self.assertComplexAlmostEqual(resultado_V012[2, 0], esperado_V012[2, 0], self.tolerance)

    def test_valores_zero(self):
        # Cenário: Todas as tensões de fase são zero.
        # Esperado: Todas as componentes de sequência devem ser zero.
        
        Va_modulo, Va_angulo = 0.0, 0.0
        Vb_modulo, Vb_angulo = 0.0, 0.0
        Vc_modulo, Vc_angulo = 0.0, 0.0

        resultado_V012 = comp_sim_analise(Va_modulo, Va_angulo, 
                                          Vb_modulo, Vb_angulo, 
                                          Vc_modulo, Vc_angulo)
        
        V0_esperado = 0.0 + 0.0j
        V1_esperado = 0.0 + 0.0j
        V2_esperado = 0.0 + 0.0j

        self.assertComplexAlmostEqual(resultado_V012[0, 0], V0_esperado, self.tolerance)
        self.assertComplexAlmostEqual(resultado_V012[1, 0], V1_esperado, self.tolerance)
        self.assertComplexAlmostEqual(resultado_V012[2, 0], V2_esperado, self.tolerance)

# Este bloco garante que os testes sejam executados quando o script é chamado diretamente.
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
