import math # Importa o módulo math para funções matemáticas como pi, sqrt e log
import numpy as np # Importa a biblioteca NumPy para operações com arrays e matrizes, especialmente úteis para números complexos
import unittest

def Metodo_Carson_long(ra, rb, rc, xa, xb, xc, ha, hb, hc, rho, R=None, Rmg_val=None):
    """
    Método de Carson com correção para cálculo de impedâncias longitudinais
    em linhas de transmissão trifásicas, sem cabo para-raio.

    Esta função calcula a matriz de impedância por unidade de comprimento
    (Ohms/km) da linha, considerando os efeitos do solo via correção de Carson.
    O comprimento total da linha ('l') NÃO é um parâmetro desta função,
    pois a impedância por unidade de comprimento é uma propriedade intrínseca
    da configuração da linha e do solo, independente do seu comprimento total.
    A impedância total da linha (em Ohms) deve ser calculada separadamente,
    multiplicando a matriz de impedância por km pelo comprimento ('l' em km)
    na camada da interface ou aplicação que a invoca.

    Parâmetros:
    ra, rb, rc (float): Resistência ôhmica por unidade de comprimento dos condutores A, B, C (Ohms/metro).
                        É crucial que estas resistências estejam em Ohms por metro para consistência com as constantes físicas.
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
    f = 60                                     # Frequência do sistema (Hz). Padrão no Brasil e em outras regiões.
    mi_0 = 4 * math.pi * (10**(-7))            # Permeabilidade magnética do vácuo (H/m). Constante física fundamental.
    w = 2 * math.pi * f                        # Frequência angular (rad/s). Usada nos cálculos de reatância indutiva.

    # --- Termos de Correção do Método de Carson para o Solo ---
    # rd: Termo de resistência de Carson (Ohms/m) que representa a parcela de resistência adicionada
    # devido ao retorno da corrente pelo solo com resistividade finita. É um termo constante.
    # Esta é uma aproximação amplamente usada para 50/60 Hz.
    rd = 9.869 * (10**(-7)) * f                # Ohms/m. 

    # De: Distância de retorno equivalente do solo (metros).
    # É uma profundidade fictícia do plano de retorno da corrente no solo,
    # que encapsula o efeito da resistividade finita do solo.
    # A constante 659 é apropriada para rho em Ohm-m e f em Hz, resultando em De em metros.
    De = 659 * (math.sqrt(rho / f))            # Metros

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

    # --- Cálculo das Impedâncias Próprias e Mútuas (em Ohms/metro) ---
    # As fórmulas de Carson resultam em impedâncias por metro.
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

    # --- Construção da Matriz de Impedância (Ohms/metro) e Conversão para Ohms/km ---
    # Monta a matriz 3x3 de impedâncias de fase em Ohms/metro.
    # Em seguida, a matriz inteira é multiplicada por 1000 para converter para Ohms/km.
    Z = np.array([
        [Zaa, Zab, Zac],
        [Zba, Zbb, Zbc],
        [Zca, Zcb, Zcc]
    ]) * 1000 # 'Z' agora representa a matriz de impedância longitudinal em Ohms/km

    return Z # Retorna a matriz de impedância longitudinal da linha em Ohms/km

# --- FIM DA FUNÇÃO Metodo_Carson_long ---

# --- TESTE UNITARIO do Metodo_Carson_long ---
class TestMetodoCarsonLong(unittest.TestCase):

    def setUp(self):
        """
        Configurações que são executadas antes de cada método de teste.
        Define parâmetros de entrada comuns para os testes.
        """
        self.params_base = {
            'ra': 0.1 / 1000,  # Convertendo para Ohms/metro (0.1 Ohm/km)
            'rb': 0.1 / 1000,
            'rc': 0.1 / 1000,
            'xa': 0.0,
            'xb': 3.0,
            'xc': 6.0,
            'ha': 15.0,
            'hb': 15.0,
            'hc': 15.0,
            'rho': 100.0,
            'R': 0.01 # Raio físico em metros
        }
        self.tolerance = 1e-6 # Tolerância para comparações de ponto flutuante

    def test_valores_padrao_simetricos(self):
        """
        Testa o cálculo da impedância para uma configuração simétrica de linha
        e verifica se os valores resultantes são sensatos e simétricos.
        """
        # Assumindo que Metodo_Carson_long está disponível no escopo (importada ou definida anteriormente)
        Z_result = Metodo_Carson_long(**self.params_base)

        # 1. Verifica o tipo e a forma da saída
        self.assertIsInstance(Z_result, np.ndarray)
        self.assertEqual(Z_result.shape, (3, 3))

        # 2. Verifica se a matriz é complexa
        self.assertTrue(np.iscomplexobj(Z_result))

        # 3. Verifica a simetria (Zij == Zji)
        # Comparar com tolerância para números complexos
        for i in range(3):
            for j in range(i + 1, 3):
                self.assertAlmostEqual(Z_result[i, j].real, Z_result[j, i].real, places=6)
                self.assertAlmostEqual(Z_result[i, j].imag, Z_result[j, i].imag, places=6)

        # 4. Verifica valores próprios (impedâncias na diagonal)
        # Em uma linha simétrica (mesmos condutores, mesmas alturas)
        # Zaa, Zbb e Zcc devem ser aproximadamente iguais.
        self.assertAlmostEqual(Z_result[0, 0].real, Z_result[1, 1].real, places=6)
        self.assertAlmostEqual(Z_result[0, 0].imag, Z_result[1, 1].imag, places=6)
        self.assertAlmostEqual(Z_result[0, 0].real, Z_result[2, 2].real, places=6)
        self.assertAlmostEqual(Z_result[0, 0].imag, Z_result[2, 2].imag, places=6)

        # 5. Verifica que a parte real e imaginária são positivas (resistência e reatância indutiva)
        self.assertGreater(Z_result[0,0].real, 0)
        self.assertGreater(Z_result[0,0].imag, 0)


    def test_raise_value_error_rmg_none(self):
        """
        Testa se um ValueError é levantado quando nem R nem Rmg_val são fornecidos.
        """
        params = self.params_base.copy()
        params['R'] = None # Remove R
        
        # Levanta o erro se Rmg_val também não for fornecido
        self.assertRaises(ValueError, Metodo_Carson_long,
                          ra=params['ra'], rb=params['rb'], rc=params['rc'],
                          xa=params['xa'], xb=params['xb'], xc=params['xc'],
                          ha=params['ha'], hb=params['hb'], hc=params['hc'],
                          rho=params['rho'], R=params['R'], Rmg_val=None)

    def test_raise_value_error_rmg_non_positive(self):
        """
        Testa se um ValueError é levantado quando RMG é não positivo.
        """
        params = self.params_base.copy()
        params['Rmg_val'] = 0.0 # RMG inválido
        params['R'] = None # Garante que Rmg_val será usado
        self.assertRaises(ValueError, Metodo_Carson_long,
                          **{k: v for k, v in params.items() if k != 'R'}) # Remove 'R' para Rmg_val ser usado
        
        params['Rmg_val'] = -0.5 # RMG inválido
        self.assertRaises(ValueError, Metodo_Carson_long,
                          **{k: v for k, v in params.items() if k != 'R'})


    def test_raise_value_error_rho_non_positive(self):
        """
        Testa se um ValueError é levantado quando rho é não positivo.
        """
        params = self.params_base.copy()
        params['rho'] = 0.0
        self.assertRaises(ValueError, Metodo_Carson_long, **params)
        params['rho'] = -10.0
        self.assertRaises(ValueError, Metodo_Carson_long, **params)

    def test_raise_value_error_height_non_positive(self):
        """
        Testa se um ValueError é levantado quando qualquer altura é não positiva.
        """
        params = self.params_base.copy()
        params['ha'] = 0.0
        self.assertRaises(ValueError, Metodo_Carson_long, **params)
        params = self.params_base.copy()
        params['hb'] = -5.0
        self.assertRaises(ValueError, Metodo_Carson_long, **params)

    def test_rmg_val_precedence(self):
        """
        Testa se Rmg_val é usado quando fornecido, ignorando R.
        """
        params = self.params_base.copy()
        params['R'] = 0.05 # Um R diferente
        params['Rmg_val'] = 0.008 # Um RMG_val específico

        # Calcule com RMG_val
        Z_result_rmg_val = Metodo_Carson_long(**params)

        # Calcule apenas com RMG_val (R = None)
        params_only_rmg_val = params.copy()
        params_only_rmg_val['R'] = None
        Z_result_only_rmg_val = Metodo_Carson_long(**params_only_rmg_val)

        # Os resultados devem ser iguais, pois Rmg_val tem precedência
        np.testing.assert_allclose(Z_result_rmg_val, Z_result_only_rmg_val, atol=self.tolerance)

    def test_assimetric_configuration(self):
        """
        Testa uma configuração assimétrica para garantir que os cálculos
        mútuos e próprios sejam distintos ou iguais conforme esperado pela geometria.
        """
        asym_params = self.params_base.copy()
        asym_params['ha'] = 10.0
        asym_params['hb'] = 12.0
        asym_params['hc'] = 14.0
        asym_params['ra'] = 0.1 / 1000
        asym_params['rb'] = 0.12 / 1000
        asym_params['rc'] = 0.15 / 1000

        Z_result = Metodo_Carson_long(**asym_params)

        self.assertIsInstance(Z_result, np.ndarray)
        self.assertEqual(Z_result.shape, (3, 3))
        self.assertTrue(np.iscomplexobj(Z_result))

        # Verifica que as partes reais das diagonais são diferentes (resistências diferentes)
        self.assertNotAlmostEqual(Z_result[0,0].real, Z_result[1,1].real, places=6)
        self.assertNotAlmostEqual(Z_result[1,1].real, Z_result[2,2].real, places=6)
        
        # Verifica que as partes imaginárias das diagonais são diferentes (devido a alturas diferentes)
        # Note que a parte imaginária própria também depende do RMG, mas as alturas impactam 'De',
        # o que não é o caso aqui (De é global). Mas resistências diferentes já garantem Zii diferentes.
        # Poderíamos verificar as partes imaginárias também.
        # self.assertNotAlmostEqual(Z_result[0,0].imag, Z_result[1,1].imag, places=6)
        
        # --- Alterações IMPORTANTES aqui: ---
        # A parte REAL dos termos mútuos (Zij.real) é SEMPRE rd (após conversão para km).
        # Então, elas DEVERIAM ser quase iguais.
        self.assertAlmostEqual(Z_result[0,1].real, Z_result[0,2].real, places=6) # Zab.real == Zac.real (ambos = rd_km)
        self.assertAlmostEqual(Z_result[0,1].real, Z_result[1,2].real, places=6) # Zab.real == Zbc.real (ambos = rd_km)

        # A parte IMAGINÁRIA dos termos mútuos (Zij.imag) DEVE ser diferente
        # se as distâncias forem diferentes (log(De/dij)).
        # dab = sqrt(13), dac = sqrt(52), dbc = sqrt(13)
        # Então, Zab.imag e Zbc.imag devem ser iguais, mas diferentes de Zac.imag.
        self.assertNotAlmostEqual(Z_result[0,1].imag, Z_result[0,2].imag, places=6) # Zab.imag != Zac.imag (sqrt(13) != sqrt(52))
        self.assertAlmostEqual(Z_result[0,1].imag, Z_result[1,2].imag, places=6) # Zab.imag == Zbc.imag (sqrt(13) == sqrt(13))

        # Teste de simetria para todos os termos mútuos
        self.assertAlmostEqual(Z_result[0, 1].real, Z_result[1, 0].real, places=6)
        self.assertAlmostEqual(Z_result[0, 1].imag, Z_result[1, 0].imag, places=6)
        self.assertAlmostEqual(Z_result[0, 2].real, Z_result[2, 0].real, places=6)
        self.assertAlmostEqual(Z_result[0, 2].imag, Z_result[2, 0].imag, places=6)
        self.assertAlmostEqual(Z_result[1, 2].real, Z_result[2, 1].real, places=6)
        self.assertAlmostEqual(Z_result[1, 2].imag, Z_result[2, 1].imag, places=6)


    def test_known_values(self):
        """
        Testa a função com um conjunto de valores de entrada conhecidos e compara
        com valores esperados obtidos de uma fonte EXTERNA e validada.
        """
        # Parâmetros de entrada para este teste
        ra_val = 0.05 / 1000 
        rb_val = 0.05 / 1000
        rc_val = 0.05 / 1000
        xa_val = 0.0
        xb_val = 4.0
        xc_val = 8.0
        ha_val = 10.0
        hb_val = 10.0
        hc_val = 10.0
        rho_val = 500.0
        R_val = 0.015

        # --- VALORES ESPERADOS OBTIDOS DE UMA FONTE EXTERNA E CONFIÁVEL ---
        # Exemplo: Calculado manualmente com cuidado, ou exportado de OpenDSS, etc.
        # Estes são apenas EXEMPLOS e devem ser substituídos pelos SEUS VALORES VALIDADOS.
        Z_expected_validated = np.array([
            [complex(0.109214, 0.904870), complex(0.059214, 0.589882), complex(0.059214, 0.528434)],
            [complex(0.059214, 0.589882), complex(0.109214, 0.904870), complex(0.059214, 0.589882)],
            [complex(0.059214, 0.528434), complex(0.059214, 0.589882), complex(0.109214, 0.904870)]
        ])
        
        # Agora, chame a função para obter os valores 'calculados'
        Z_calculated = Metodo_Carson_long(
            ra=ra_val, rb=rb_val, rc=rc_val,
            xa=xa_val, xb=xb_val, xc=xc_val,
            ha=ha_val, hb=ha_val, hc=ha_val,
            rho=rho_val,
            R=R_val
        )
        
        # Comparar a matriz calculada com a matriz esperada validada externamente
        np.testing.assert_allclose(Z_calculated, Z_expected_validated, atol=self.tolerance,
                                   err_msg="A matriz de impedância calculada não corresponde aos valores esperados validados.")

# --- Executar os testes ---
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False) # Usar argv e exit=False para rodar em IDEs