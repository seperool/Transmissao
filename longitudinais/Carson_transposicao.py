import numpy as np
import math
import unittest

def metodo_carson_transp(ra,rb,rc,xa,ha,xb,hb,xc,hc,rho,l1,l2,l3,R=None,Rmg_val=None):
    """
    Calcula a impedância longitudinal de uma linha de transmissão trifásica
    transposta usando o Método de Carson.

    Esta função considera um ciclo completo de transposição da linha, dividindo-o
    em três seções de comprimentos l1, l2 e l3. A impedância total da linha
    é a soma das impedâncias de cada uma dessas seções.

    Parâmetros:
    ra, rb, rc (float): Resistências CA dos condutores das fases A, B e C (em Ohm/m).
                        A unidade deve ser consistente com a unidade de comprimento (metros).
    xa, xb, xc (float): Coordenadas horizontais (X) dos condutores A, B e C (em metros).
    ha, hb, hc (float): Coordenadas verticais (H) dos condutores A, B e C (em metros).
                        As alturas devem ser positivas.
    rho (float): Resistividade do solo (em Ohm.m).
    l1, l2, l3 (float): Comprimentos das três seções da transposição (em metros).
    R (float, opcional): Raio físico do condutor (em metros).
                         Usado para calcular o RMG se 'Rmg_val' não for fornecido.
    Rmg_val (float, opcional): Raio Médio Geométrico do condutor (em metros).
                               Se fornecido, tem prioridade sobre 'R'.

    Retorna:
    numpy.ndarray: Matriz de impedância de fase (3x3) da linha transposta (em Ohms).
                   A impedância é calculada para o comprimento total da linha (l1 + l2 + l3).
    """

    # --- Constantes Físicas e Elétricas ---
    f = 60                                       # Frequência do sistema em Hertz (Hz).
    mi_0 = 4 * math.pi * (10**(-7))              # Permeabilidade magnética do vácuo em Henry/metro (H/m).
    w = 2 * math.pi * f                          # Frequência angular em radianos/segundo (rad/s).

    # --- Termos de Correção do Método de Carson para o Solo ---
    # `rd`: Termo de resistência de Carson (Ohm/m) que modela a resistência do retorno da corrente pelo solo.
    # É uma aproximação amplamente usada para frequências de 50/60 Hz.
    rd = 9.869 * (10**(-7)) * f                  # Ohm/m

    # --- Cálculo e Validação do Raio Médio Geométrico (RMG) ---
    Rmg = None # Inicializa a variável RMG.
    if Rmg_val is not None:
        # Se um valor de RMG foi fornecido diretamente, use-o.
        Rmg = Rmg_val
    elif R is not None:
        # Se o raio físico (R) foi fornecido, calcula o RMG a partir dele.
        # A fórmula RMG = R * exp(-1/4) é para condutores sólidos. Para condutores trançados,
        # o RMG é um valor tabelado pelo fabricante.
        Rmg = R * math.exp(-1/4)
    
    # --- Validações de Entrada ---
    # Essas verificações garantem que os valores de entrada são fisicamente válidos para o cálculo.
    if Rmg is None:
        # Lança um erro se nem o raio físico (R) nem o RMG foram fornecidos.
        raise ValueError("ERRO! É necessário fornecer o raio do condutor (R) OU o Raio Médio Geométrico (Rmg_val).")
    if Rmg <= 0:
        # O RMG deve ser um valor positivo.
        raise ValueError("ERRO! O Raio Médio Geométrico (RMG) deve ser um valor positivo.")
    if rho <= 0:
        # A resistividade do solo deve ser um valor positivo.
        raise ValueError("ERRO! A resistividade do solo (rho) deve ser um valor positivo.")
    if ha <= 0 or hb <= 0 or hc <= 0:
        # As alturas dos condutores devem ser maiores que zero, pois o método de Carson assume condutores acima do solo.
        raise ValueError("ERRO! As alturas dos condutores (Ha, Hb, Hc) devem ser maiores que zero.")
    if l1 < 0 or l2 < 0 or l3 < 0:
        # Os comprimentos das seções não podem ser negativos.
        raise ValueError("ERRO! Os comprimentos das seções (l1, l2, l3) devem ser não-negativos.")
    if (l1 + l2 + l3) == 0:
        # O comprimento total da linha não pode ser zero.
        raise ValueError("ERRO! O comprimento total da linha (l1+l2+l3) não pode ser zero.")

    # `De`: Distância de retorno equivalente do solo (metros).
    # É uma profundidade fictícia do plano de retorno da corrente que captura o efeito da resistividade finita do solo.
    De = 659 * (math.sqrt(rho / f))              # Metros

    # --- Cálculo das Distâncias Geométricas entre os condutores ---
    # As distâncias entre os centros dos condutores são calculadas usando a fórmula euclidiana 2D.
    dab = np.sqrt(((xa - xb)**2) + ((ha - hb)**2)) # Distância entre condutores A e B
    dac = np.sqrt(((xa - xc)**2) + ((ha - hc)**2)) # Distância entre condutores A e C
    dbc = np.sqrt(((xb - xc)**2) + ((hb - hc)**2)) # Distância entre condutores B e C

    # --- Cálculo das Impedâncias Próprias e Mútuas por unidade de comprimento (Ohm/m) ---
    # `Zii`: Impedância própria do condutor `i` em relação ao retorno pelo solo.
    # `Zii` = (resistência do condutor) + `rd` + j * (reatância própria de Carson)
    Zaa = ra + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)
    Zbb = rb + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)
    Zcc = rc + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)

    # `Zij`: Impedância mútua entre os condutores `i` e `j`, considerando o retorno pelo solo.
    # `Zij` = `rd` + j * (reatância mútua de Carson)
    Zab = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dab) # Mútua entre A e B
    Zac = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dac) # Mútua entre A e C
    Zbc = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dbc) # Mútua entre B e C

    # A matriz de impedância de fase é simétrica, então Zij = Zji.
    Zba = Zab
    Zca = Zac
    Zcb = Zbc

    # --- Composição das Matrizes das Seções da Transposição ---
    # Cada matriz representa a impedância por unidade de comprimento para o arranjo de fases em uma seção.

    # Seção 1 (l1): Arranjo padrão (A na pos1, B na pos2, C na pos3)
    Z_1 = np.array([
        [Zaa, Zab, Zac],
        [Zba, Zbb, Zbc],
        [Zca, Zcb, Zcc]
    ]) * l1 # Multiplica pela comprimento da seção para obter a impedância total da seção

    # Seção 2 (l2): Arranjo rotacionado (B na pos1, C na pos2, A na pos3)
    # A matriz é rearranjada para mapear as impedâncias das posições físicas para as fases A, B e C.
    # A está na posição 3, B na 1, C na 2.
    Z_2 = np.array([
        [Zcc, Zca, Zcb], # Linha da Fase A (corresponde à posição 3)
        [Zac, Zaa, Zab], # Linha da Fase B (corresponde à posição 1)
        [Zbc, Zba, Zbb]  # Linha da Fase C (corresponde à posição 2)
    ]) * l2

    # Seção 3 (l3): Segundo arranjo rotacionado (C na pos1, A na pos2, B na pos3)
    # Mapeamento: A está na posição 2, B na 3, C na 1.
    Z_3 = np.array([
        [Zbb, Zbc, Zba], # Linha da Fase A (corresponde à posição 2)
        [Zcb, Zcc, Zca], # Linha da Fase B (corresponde à posição 3)
        [Zab, Zac, Zaa]  # Linha da Fase C (corresponde à posição 1)
    ]) * l3

    # --- Cálculo da Impedância Total da Linha Transposta ---
    # A impedância da linha transposta é a soma das impedâncias de cada seção.
    Z_transp = Z_1 + Z_2 + Z_3

    return Z_transp

### Classe de Teste `TestMetodoCarsonTransp`
class TestMetodoCarsonTransp(unittest.TestCase):

    def setUp(self):
        # Configuração inicial para cada teste. Define os parâmetros de entrada comuns.
        self.ra = 0.05 / 1000  # Resistência da fase A em Ohm/m (equivalente a 0.05 Ohm/km)
        self.rb = 0.05 / 1000  # Resistência da fase B em Ohm/m
        self.rc = 0.05 / 1000  # Resistência da fase C em Ohm/m

        self.xa = 0.0          # Coordenada X do condutor A em metros
        self.ha = 10.0         # Coordenada H (altura) do condutor A em metros
        self.xb = 3.0          # Coordenada X do condutor B em metros
        self.hb = 10.0         # Coordenada H (altura) do condutor B em metros
        self.xc = 6.0          # Coordenada X do condutor C em metros
        self.hc = 10.0         # Coordenada H (altura) do condutor C em metros

        self.rho = 100.0       # Resistividade do solo em Ohm.m
        
        self.l1 = 10000.0      # Comprimento da primeira seção transposta em metros (10 km)
        self.l2 = 10000.0      # Comprimento da segunda seção transposta em metros (10 km)
        self.l3 = 10000.0      # Comprimento da terceira seção transposta em metros (10 km)
        
        self.R = 0.01          # Raio físico do condutor em metros
        self.Rmg_val = None    # Inicialmente não fornecemos RMG, para testar o cálculo a partir de R

        # Calcula o RMG esperado, que a função deveria obter se R for fornecido
        self.expected_RMG = self.R * math.exp(-1/4)

        # Tolerância para comparações de números de ponto flutuante (complexos)
        self.tolerance = 1e-6

    def test_impedance_symmetry_transposed_line(self):
        """
        Verifica se a matriz de impedância resultante de uma linha transposta
        apresenta a simetria esperada (elementos da diagonal iguais e elementos
        fora da diagonal iguais), indicando um sistema equilibrado.
        """
        Z_transp = metodo_carson_transp(
            self.ra, self.rb, self.rc,
            self.xa, self.ha, self.xb, self.hb, self.xc, self.hc,
            self.rho, self.l1, self.l2, self.l3,
            R=self.R, Rmg_val=self.Rmg_val # Usando R, Rmg_val permanece None
        )

        # As impedâncias próprias (elementos na diagonal principal) devem ser aproximadamente iguais
        # Compara a parte real e imaginária separadamente para maior precisão
        self.assertAlmostEqual(Z_transp[0,0].real, Z_transp[1,1].real, delta=self.tolerance)
        self.assertAlmostEqual(Z_transp[0,0].imag, Z_transp[1,1].imag, delta=self.tolerance)
        self.assertAlmostEqual(Z_transp[0,0].real, Z_transp[2,2].real, delta=self.tolerance)
        self.assertAlmostEqual(Z_transp[0,0].imag, Z_transp[2,2].imag, delta=self.tolerance)

        # As impedâncias mútuas (elementos fora da diagonal principal) devem ser aproximadamente iguais
        # E também verifica a propriedade de simetria (Zij == Zji)
        self.assertAlmostEqual(Z_transp[0,1].real, Z_transp[0,2].real, delta=self.tolerance)
        self.assertAlmostEqual(Z_transp[0,1].imag, Z_transp[0,2].imag, delta=self.tolerance)
        self.assertAlmostEqual(Z_transp[0,1].real, Z_transp[1,0].real, delta=self.tolerance)
        self.assertAlmostEqual(Z_transp[0,1].imag, Z_transp[1,0].imag, delta=self.tolerance)
        self.assertAlmostEqual(Z_transp[0,1].real, Z_transp[1,2].real, delta=self.tolerance)
        self.assertAlmostEqual(Z_transp[0,1].imag, Z_transp[1,2].imag, delta=self.tolerance)
        self.assertAlmostEqual(Z_transp[0,1].real, Z_transp[2,0].real, delta=self.tolerance)
        self.assertAlmostEqual(Z_transp[0,1].imag, Z_transp[2,0].imag, delta=self.tolerance)
        self.assertAlmostEqual(Z_transp[0,1].real, Z_transp[2,1].real, delta=self.tolerance)
        self.assertAlmostEqual(Z_transp[0,1].imag, Z_transp[2,1].imag, delta=self.tolerance)

    def test_value_error_no_R_or_Rmg_val(self):
        """
        Verifica se a função levanta um ValueError quando nem o raio físico (R)
        nem o Raio Médio Geométrico (Rmg_val) são fornecidos.
        """
        with self.assertRaises(ValueError) as cm:
            metodo_carson_transp(
                self.ra, self.rb, self.rc,
                self.xa, self.ha, self.xb, self.hb, self.xc, self.hc,
                self.rho, self.l1, self.l2, self.l3,
                R=None, Rmg_val=None # Nenhum dos parâmetros de raio é fornecido
            )
        self.assertIn("ERRO! É necessário fornecer o raio do condutor (R) OU o Raio Médio Geométrico (Rmg_val).", str(cm.exception))

    def test_value_error_negative_Rmg_val(self):
        """
        Verifica se a função levanta um ValueError quando um valor de RMG
        negativo ou zero é fornecido.
        """
        with self.assertRaises(ValueError) as cm:
            metodo_carson_transp(
                self.ra, self.rb, self.rc,
                self.xa, self.ha, self.xb, self.hb, self.xc, self.hc,
                self.rho, self.l1, self.l2, self.l3,
                Rmg_val=-0.01 # RMG negativo
            )
        self.assertIn("ERRO! O Raio Médio Geométrico (RMG) deve ser um valor positivo.", str(cm.exception))

    def test_value_error_negative_rho(self):
        """
        Verifica se a função levanta um ValueError quando a resistividade do solo (rho)
        é negativa ou zero.
        """
        with self.assertRaises(ValueError) as cm:
            metodo_carson_transp(
                self.ra, self.rb, self.rc,
                self.xa, self.ha, self.xb, self.hb, self.xc, self.hc,
                rho=-100.0, l1=self.l1, l2=self.l2, l3=self.l3, # rho negativo
                R=self.R
            )
        self.assertIn("ERRO! A resistividade do solo (rho) deve ser um valor positivo.", str(cm.exception))

    def test_value_error_zero_height(self):
        """
        Verifica se a função levanta um ValueError quando uma das alturas
        dos condutores é zero ou negativa.
        """
        with self.assertRaises(ValueError) as cm:
            metodo_carson_transp(
                self.ra, self.rb, self.rc,
                self.xa, 0.0, self.xb, self.hb, self.xc, self.hc, # ha = 0
                self.rho, self.l1, self.l2, self.l3,
                R=self.R
            )
        self.assertIn("ERRO! As alturas dos condutores (Ha, Hb, Hc) devem ser maiores que zero.", str(cm.exception))

    def test_value_error_negative_length(self):
        """
        Verifica se a função levanta um ValueError quando um dos comprimentos
        das seções (l1, l2, l3) é negativo.
        """
        with self.assertRaises(ValueError) as cm:
            metodo_carson_transp(
                self.ra, self.rb, self.rc,
                self.xa, self.ha, self.xb, self.hb, self.xc, self.hc,
                self.rho, l1=-100.0, l2=self.l2, l3=self.l3, # l1 negativo
                R=self.R
            )
        self.assertIn("ERRO! Os comprimentos das seções (l1, l2, l3) devem ser não-negativos.", str(cm.exception))
    
    def test_value_error_zero_total_length(self):
        """
        Verifica se a função levanta um ValueError quando o comprimento total da linha
        (soma de l1, l2, l3) é zero.
        """
        with self.assertRaises(ValueError) as cm:
            metodo_carson_transp(
                self.ra, self.rb, self.rc,
                self.xa, self.ha, self.xb, self.hb, self.xc, self.hc,
                self.rho, l1=0.0, l2=0.0, l3=0.0, # Comprimento total zero
                R=self.R
            )
        self.assertIn("ERRO! O comprimento total da linha (l1+l2+l3) não pode ser zero.", str(cm.exception))

    def test_specific_Rmg_val_usage(self):
        """
        Verifica se a função utiliza corretamente o RMG fornecido diretamente (Rmg_val),
        priorizando-o sobre o cálculo a partir do raio físico (R).
        """
        specific_Rmg_val = 0.005 # Um valor de RMG diferente para teste
        Z_transp_RMG = metodo_carson_transp(
            self.ra, self.rb, self.rc,
            self.xa, self.ha, self.xb, self.hb, self.xc, self.hc,
            self.rho, self.l1, self.l2, self.l3,
            R=self.R, Rmg_val=specific_Rmg_val # Rmg_val é fornecido, R deve ser ignorado
        )

        # Recalcula a impedância própria unitária manualmente usando o 'specific_Rmg_val'
        # para comparar com o resultado da função.
        f = 60
        mi_0 = 4 * math.pi * (10**(-7))
        w = 2 * math.pi * f
        rd = 9.869 * (10**(-7)) * f
        De = 659 * (math.sqrt(self.rho / f))

        expected_Zaa_unit = self.ra + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / specific_Rmg_val)
        
        # A impedância própria resultante da matriz transposta (Zss) é
        # a impedância própria unitária multiplicada pelo comprimento total da linha.
        total_length = self.l1 + self.l2 + self.l3
        self.assertAlmostEqual(Z_transp_RMG[0,0].real, (expected_Zaa_unit * total_length).real, delta=self.tolerance)
        self.assertAlmostEqual(Z_transp_RMG[0,0].imag, (expected_Zaa_unit * total_length).imag, delta=self.tolerance)

# Permite que os testes sejam executados diretamente ao rodar o script
if __name__ == '__main__':
    # 'argv=['first-arg-is-ignored']' e 'exit=False' são usados para
    # permitir que o unittest.main() seja executado em ambientes como notebooks
    # ou IDEs sem levantar SystemExit após a execução dos testes.
    unittest.main(argv=['first-arg-is-ignored'], exit=False)