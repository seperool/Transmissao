import math
import numpy as np

def Metodo_Carson_long(ra, rb, rc, xa, xb, xc, ha, hb, hc, R=None, Rmg_val=None):
    """
    Método de Carson com correção para cálculo de impedâncias longitudinais
    em linhas de transmissão trifásicas, sem cabo para-raio.

    Parâmetros:
    ra, rb, rc (float): Resistência ôhmica por unidade de comprimento dos condutores A, B, C (Ohms/km).
    xa, xb, xc (float): Coordenadas horizontais (X) dos condutores A, B, C (metros).
    ha, hb, hc (float): Coordenadas verticais (altura H) dos condutores A, B, C (metros).
    R (float, opcional): Raio físico do condutor (metros). Usado para calcular o RMG se Rmg_val não for fornecido.
    Rmg_val (float, opcional): Raio Médio Geométrico (RMG) do condutor (metros). Se fornecido, R é ignorado.

    Retorna:
    numpy.ndarray: Matriz de impedância 3x3 complexa (Ohms/km).

    Raises:
    ValueError: Se nem R nem Rmg_val forem fornecidos, ou se Rmg for não positivo.
    """

    # --- Constantes Físicas e Elétricas ---
    f = 60  # Frequência (Hz)
    p = 100 # Permeabilidade relativa do solo (adimensional) - Confirmar o que 'p' representa.
    mi_0 = 4 * math.pi * (10**(-7)) # Permeabilidade magnética do vácuo (H/m)
    w = 2 * math.pi * f # Frequência angular (rad/s)

    # Constantes do Método de Carson para o termo de correção do solo
    rd = 9.869 * (10**(-7)) * f # Termo de resistência de Carson (Ohms/m)
    De = 659 * (math.sqrt(p / f)) # Distância de retorno equivalente do solo (metros)

    # --- Cálculo do Raio Médio Geométrico (RMG) ---
    Rmg = None
    if Rmg_val is not None:
        Rmg = Rmg_val
    elif R is not None:
        # Para condutores sólidos, RMG = R * exp(-1/4).
        # Para condutores trançados (cabo ACSR, etc.), o RMG é um valor tabelado.
        Rmg = R * math.exp(-1/4)
    
    if Rmg is None:
        raise ValueError("ERRO! É necessário fornecer o raio do condutor (R) OU o Raio Médio Geométrico (Rmg_val).")
    if Rmg <= 0:
        raise ValueError("ERRO! O Raio Médio Geométrico (RMG) deve ser um valor positivo.")

    # --- Cálculo das Distâncias Geométricas entre os condutores ---
    # As distâncias são calculadas usando a fórmula da distância euclidiana 2D.
    dab = np.sqrt(((xa - xb)**2) + ((ha - hb)**2))
    dac = np.sqrt(((xa - xc)**2) + ((ha - hc)**2))
    dbc = np.sqrt(((xb - xc)**2) + ((hb - hc)**2))

    # --- Cálculo das Impedâncias Próprias e Mútuas ---
    # Impedâncias Próprias (Zii = Ri + rd + j*Xii)
    # Zii = ri + rd + j*w*(mi_0/(2*pi))*ln(De/RMG)
    Zaa = rd + ra + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)
    Zbb = rd + rb + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)
    Zcc = rd + rc + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)

    # Impedâncias Mútuas (Zij = rd + j*Xij)
    # Zij = rd + j*w*(mi_0/(2*pi))*ln(De/dij)
    Zab = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dab)
    Zac = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dac)
    Zbc = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dbc)

    # As impedâncias mútuas são simétricas (Zij = Zji)
    Zba = Zab
    Zca = Zac
    Zcb = Zbc

    # --- Construção da Matriz de Impedância ---
    # Usando np.array para maior flexibilidade e compatibilidade com o ecossistema NumPy moderno.
    Z = np.array([
        [Zaa, Zab, Zac],
        [Zba, Zbb, Zbc],
        [Zca, Zcb, Zcc]
    ])

    return Z

# --- Parâmetros do Caso de Teste ---
print("--- Executando Caso de Teste ---")

# Resistências dos condutores (Ohms/km)
r_a = 0.05
r_b = 0.05
r_c = 0.05

# Coordenadas dos condutores (metros)
x_a, h_a = 0.0, 10.0
x_b, h_b = 4.0, 10.0
x_c, h_c = 8.0, 10.0

# Raio físico do condutor (metros)
raio_condutor = 0.015 # 1.5 cm

try:
    # Chama a função Metodo_Carson_long com os parâmetros de teste
    impedancia_calculada = Metodo_Carson_long(
        r_a, r_b, r_c,
        x_a, x_b, x_c,
        h_a, h_b, h_c,
        R=raio_condutor
    )

    print("\nMatriz de Impedância Calculada:")
    print(impedancia_calculada)

    # --- Verificações B
    print("\n--- Verificações de Consistência ---")

    # Verificação 1: Impedâncias próprias devem ser iguais
    proprias_iguais = np.isclose(impedancia_calculada[0,0], impedancia_calculada[1,1]) and \
                      np.isclose(impedancia_calculada[1,1], impedancia_calculada[2,2])
    print(f"Impedâncias próprias (Zaa, Zbb, Zcc) são iguais? {proprias_iguais}")
    if not proprias_iguais:
        print(f"  Zaa: {impedancia_calculada[0,0]}")
        print(f"  Zbb: {impedancia_calculada[1,1]}")
        print(f"  Zcc: {impedancia_calculada[2,2]}")

    # Verificação 2: Impedâncias mútuas simétricas pela distância (Zab = Zbc)
    mutuas_iguais_dist4 = np.isclose(impedancia_calculada[0,1], impedancia_calculada[1,2]) # Zab vs Zbc
    print(f"Impedâncias mútuas de distâncias iguais (Zab, Zbc) são iguais? {mutuas_iguais_dist4}")
    if not mutuas_iguais_dist4:
        print(f"  Zab: {impedancia_calculada[0,1]}")
        print(f"  Zbc: {impedancia_calculada[1,2]}")

    # Verificação 3: Simetria da matriz (Zij = Zji)
    matriz_simetrica = np.allclose(impedancia_calculada, impedancia_calculada.T)
    print(f"Matriz de impedância é simétrica (Zij = Zji)? {matriz_simetrica}")

    print("\n--- Fim do Caso de Teste ---")

except ValueError as e:
    print(f"Erro durante a execução do caso de teste: {e}")