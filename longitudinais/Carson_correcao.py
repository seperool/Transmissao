import math # Importa o módulo math para funções matemáticas como pi, sqrt e log
import numpy as np # Importa a biblioteca NumPy para operações com arrays e matrizes, especialmente úteis para números complexos

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