import math # Importa o módulo math para funções matemáticas como pi, sqrt e log
import numpy as np # Importa a biblioteca NumPy para operações com arrays e matrizes, especialmente úteis para números complexos

def Metodo_Carson_long(ra, rb, rc, xa, xb, xc, ha, hb, hc, rho, R=None, Rmg_val=None):
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

    return Z # Retorna a matriz de impedância longitudinal da linha

# --- Parâmetros do Caso de Teste ---
# Este bloco demonstra como usar a função Metodo_Carson_long com valores de exemplo.
print("--- Executando Caso de Teste ---")

# Resistências dos condutores (Ohms/km) para o usuário.
r_a_km = 0.05
r_b_km = 0.05
r_c_km = 0.05

# Converção das resistências de Ohms/km para Ohms/metro, pois a função espera Ohms/metro.
r_a_m = r_a_km / 1000.0
r_b_m = r_b_km / 1000.0
r_c_m = r_c_km / 1000.0

# Coordenadas dos condutores (metros). Assumindo uma configuração horizontal simétrica.
x_a, h_a = 0.0, 10.0 # Condutor A na origem horizontal, 10m de altura
x_b, h_b = 4.0, 10.0 # Condutor B a 4m de A, mesma altura
x_c, h_c = 8.0, 10.0 # Condutor C a 8m de A, mesma altura

# Raio físico do condutor (metros).
raio_condutor = 0.015 # Exemplo: 1.5 cm de raio

# Resistividade do solo (Ohms-metro). Exemplo de valor típico para solo úmido.
resistividade_solo = 100

try:
    # Chama a função principal Metodo_Carson_long com todos os parâmetros necessários.
    impedancia_calculada = Metodo_Carson_long(
        r_a_m, r_b_m, r_c_m, # Resistências em Ohms/metro
        x_a, x_b, x_c,
        h_a, h_b, h_c,
        resistividade_solo,  # Resistividade do solo em Ohms-metro
        R=raio_condutor      # Raio físico do condutor (se o RMG não for fornecido diretamente)
    )

    print("\nMatriz de Impedância Calculada (Ohms/km):")
    # Configura as opções de impressão do NumPy para exibir números complexos de forma mais legível,
    # com 6 casas decimais e sem notação científica para valores pequenos.
    np.set_printoptions(precision=6, suppress=True)
    print(impedancia_calculada) # Exibe a matriz de impedância resultante

    # --- Verificações de Consistência ---
    # Estas verificações ajudam a validar o cálculo, comparando os resultados esperados para um arranjo simétrico.
    print("\n--- Verificações de Consistência ---")

    # Verificação 1: Checa se as impedâncias próprias da diagonal principal são iguais.
    # Para condutores idênticos e mesma altura (como neste caso de teste), elas deveriam ser iguais.
    proprias_iguais = np.isclose(impedancia_calculada[0,0], impedancia_calculada[1,1]) and \
                      np.isclose(impedancia_calculada[1,1], impedancia_calculada[2,2])
    print(f"Impedâncias próprias (Zaa, Zbb, Zcc) são iguais? {proprias_iguais}")
    if not proprias_iguais: # Se não forem iguais, imprime os valores para depuração
        print(f"   Zaa: {impedancia_calculada[0,0]:.6f}")
        print(f"   Zbb: {impedancia_calculada[1,1]:.6f}")
        print(f"   Zcc: {impedancia_calculada[2,2]:.6f}")

    # Verificação 2: Checa se impedâncias mútuas simétricas pela distância são iguais.
    # Neste arranjo horizontal equidistante (X=0, X=4, X=8), Dab (4m) e Dbc (4m) são iguais,
    # portanto Zab e Zbc também devem ser iguais. Dac (8m) será diferente.
    mutuas_iguais_dist_4m = np.isclose(impedancia_calculada[0,1], impedancia_calculada[1,2]) # Compara Zab e Zbc
    print(f"Impedâncias mútuas entre condutores a 4m (Zab, Zbc) são iguais? {mutuas_iguais_dist_4m}")
    if not mutuas_iguais_dist_4m: # Se não forem iguais, imprime os valores para depuração
        print(f"   Zab: {impedancia_calculada[0,1]:.6f}")
        print(f"   Zbc: {impedancia_calculada[1,2]:.6f}")

    # Verificação 3: Checa se a matriz de impedância é simétrica (Zij = Zji).
    # Esta é uma propriedade fundamental das matrizes de impedância de fase.
    matriz_simetrica = np.allclose(impedancia_calculada, impedancia_calculada.T)
    print(f"Matriz de impedância é simétrica (Zij = Zji)? {matriz_simetrica}")

    print("\n--- Fim do Caso de Teste ---")

except ValueError as e:
    # Captura e exibe qualquer erro de validação de entrada levantado pela função.
    print(f"Erro durante a execução do caso de teste: {e}")