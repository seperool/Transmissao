import numpy as np
import math

def metodo_transposicao_tran(ra, rb, rc, xa_pos1, ha_pos1, xb_pos2, hb_pos2, xc_pos3, hc_pos3, rho, l1, l2, l3):
    """
    Calcula a matriz de capacitância de fase para uma linha de transmissão trifásica
    totalmente transposta, incorporando diretamente o Método das Imagens para cada seção.

    Esta função considera um ciclo completo de transposição da linha, dividindo-o
    em três seções de comprimentos l1, l2 e l3. A capacitância total da linha
    é a soma das capacitâncias de cada uma dessas seções.

    Parâmetros:
    ra, rb, rc (float): Raios físicos dos condutores das fases A, B e C (em metros).
    xa_pos1, ha_pos1 (float): Coordenadas horizontais (X) e verticais (H) da Posição Física 1 (em metros).
    xb_pos2, hb_pos2 (float): Coordenadas horizontais (X) e verticais (H) da Posição Física 2 (em metros).
    xc_pos3, hc_pos3 (float): Coordenadas horizontais (X) e verticais (H) da Posição Física 3 (em metros).
                              As alturas devem ser positivas.
    rho (float): Resistividade do solo (em Ohm.m).
    l1, l2, l3 (float): Comprimentos das três seções da transposição (em metros).

    Retorna:
    numpy.ndarray: Matriz de capacitância de fase (3x3) da linha transposta (em Farads).
                   A capacitância é calculada para o comprimento total da linha (l1 + l2 + l3).
    """

    # --- Constantes Físicas ---
    E = 8.854 * 10 ** (-12)  # Permissividade do vácuo (F/m)

    # --- Validações de Entrada ---
    if rho <= 0:
        raise ValueError("ERRO! A resistividade do solo (rho) deve ser um valor positivo.")
    if ha_pos1 <= 0 or hb_pos2 <= 0 or hc_pos3 <= 0:
        raise ValueError(
            "ERRO! As alturas das posições físicas (Ha_pos1, Hb_pos2, Hc_pos3) devem ser maiores que zero.")
    if l1 < 0 or l2 < 0 or l3 < 0:
        raise ValueError("ERRO! Os comprimentos das seções (l1, l2, l3) devem ser não-negativos.")
    if (l1 + l2 + l3) == 0:
        raise ValueError("ERRO! O comprimento total da linha (l1+l2+l3) não pode ser zero.")

    # --- Inicializa a matriz de capacitância total transposta ---
    C_transp_total = np.zeros((3, 3))

    # --- Seção 1 (l1): Fases A, B, C nas Posições 1, 2, 3 respectivamente ---
    # Coordenadas dos condutores A, B, C nesta seção
    xa, ha = xa_pos1, ha_pos1
    xb, hb = xb_pos2, hb_pos2
    xc, hc = xc_pos3, hc_pos3

    # Raios dos condutores A, B, C nesta seção (são sempre os mesmos)
    ra_sec, rb_sec, rc_sec = ra, rb, rc

    # Cálculo das Distâncias para a Seção 1
    dab = np.sqrt(((xa - xb) ** 2) + ((ha - hb) ** 2))
    dac = np.sqrt(((xa - xc) ** 2) + ((ha - hc) ** 2))
    dbc = np.sqrt(((xb - xc) ** 2) + ((hb - hc) ** 2))

    dab_1 = np.sqrt(((xa - xb) ** 2) + ((ha + hb) ** 2))
    dac_1 = np.sqrt(((xa - xc) ** 2) + ((ha + hc) ** 2))
    dbc_1 = np.sqrt(((xb - xc) ** 2) + ((hb + hc) ** 2))

    # Construção da Matriz de Potencial (P) para a Seção 1
    Paa = 1 / (2 * math.pi * E) * math.log((2 * ha) / ra_sec)
    Pbb = 1 / (2 * math.pi * E) * math.log((2 * hb) / rb_sec)
    Pcc = 1 / (2 * math.pi * E) * math.log((2 * hc) / rc_sec)

    Pab = 1 / (2 * math.pi * E) * math.log(dab_1 / dab)
    Pba = Pab
    Pac = 1 / (2 * math.pi * E) * math.log(dac_1 / dac)
    Pca = Pac
    Pbc = 1 / (2 * math.pi * E) * math.log(dbc_1 / dbc)
    Pcb = Pbc

    P_matrix_sec1 = np.array([
        [Paa, Pab, Pac],
        [Pba, Pbb, Pbc],
        [Pca, Pcb, Pcc]
    ])

    # Cálculo da Matriz de Capacitância para a Seção 1 (por unidade de comprimento)
    C_matrix_sec1_per_m = np.linalg.inv(P_matrix_sec1)
    C_transp_total += C_matrix_sec1_per_m * l1  # Adiciona a capacitância total da seção 1

    # --- Seção 2 (l2): Fases A, B, C nas Posições 2, 3, 1 respectivamente ---
    # Condutor A (ra) nas coordenadas (xb_pos2, hb_pos2)
    # Condutor B (rb) nas coordenadas (xc_pos3, hc_pos3)
    # Condutor C (rc) nas coordenadas (xa_pos1, ha_pos1)
    xa, ha = xb_pos2, hb_pos2
    xb, hb = xc_pos3, hc_pos3
    xc, hc = xa_pos1, ha_pos1

    # Raios dos condutores A, B, C nesta seção (são sempre os mesmos)
    ra_sec, rb_sec, rc_sec = ra, rb, rc

    # Cálculo das Distâncias para a Seção 2
    dab = np.sqrt(((xa - xb) ** 2) + ((ha - hb) ** 2))
    dac = np.sqrt(((xa - xc) ** 2) + ((ha - hc) ** 2))
    dbc = np.sqrt(((xb - xc) ** 2) + ((hb - hc) ** 2))

    dab_1 = np.sqrt(((xa - xb) ** 2) + ((ha + hb) ** 2))
    dac_1 = np.sqrt(((xa - xc) ** 2) + ((ha + hc) ** 2))
    dbc_1 = np.sqrt(((xb - xc) ** 2) + ((hb + hc) ** 2))

    # Construção da Matriz de Potencial (P) para a Seção 2
    Paa = 1 / (2 * math.pi * E) * math.log((2 * ha) / ra_sec)
    Pbb = 1 / (2 * math.pi * E) * math.log((2 * hb) / rb_sec)
    Pcc = 1 / (2 * math.pi * E) * math.log((2 * hc) / rc_sec)

    Pab = 1 / (2 * math.pi * E) * math.log(dab_1 / dab)
    Pba = Pab
    Pac = 1 / (2 * math.pi * E) * math.log(dac_1 / dac)
    Pca = Pac
    Pbc = 1 / (2 * math.pi * E) * math.log(dbc_1 / dbc)
    Pcb = Pbc

    P_matrix_sec2 = np.array([
        [Paa, Pab, Pac],
        [Pba, Pbb, Pbc],
        [Pca, Pcb, Pcc]
    ])

    # Cálculo da Matriz de Capacitância para a Seção 2 (por unidade de comprimento)
    C_matrix_sec2_per_m = np.linalg.inv(P_matrix_sec2)
    C_transp_total += C_matrix_sec2_per_m * l2  # Adiciona a capacitância total da seção 2

    # --- Seção 3 (l3): Fases A, B, C nas Posições 3, 1, 2 respectivamente ---
    # Condutor A (ra) nas coordenadas (xc_pos3, hc_pos3)
    # Condutor B (rb) nas coordenadas (xa_pos1, ha_pos1)
    # Condutor C (rc) nas coordenadas (xb_pos2, hb_pos2)
    xa, ha = xc_pos3, hc_pos3
    xb, hb = xa_pos1, ha_pos1
    xc, hc = xb_pos2, hb_pos2

    # Raios dos condutores A, B, C nesta seção (são sempre os mesmos)
    ra_sec, rb_sec, rc_sec = ra, rb, rc

    # Cálculo das Distâncias para a Seção 3
    dab = np.sqrt(((xa - xb) ** 2) + ((ha - hb) ** 2))
    dac = np.sqrt(((xa - xc) ** 2) + ((ha - hc) ** 2))
    dbc = np.sqrt(((xb - xc) ** 2) + ((hb - hc) ** 2))

    dab_1 = np.sqrt(((xa - xb) ** 2) + ((ha + hb) ** 2))
    dac_1 = np.sqrt(((xa - xc) ** 2) + ((ha + hc) ** 2))
    dbc_1 = np.sqrt(((xb - xc) ** 2) + ((hb + hc) ** 2))

    # Construção da Matriz de Potencial (P) para a Seção 3
    Paa = 1 / (2 * math.pi * E) * math.log((2 * ha) / ra_sec)
    Pbb = 1 / (2 * math.pi * E) * math.log((2 * hb) / rb_sec)
    Pcc = 1 / (2 * math.pi * E) * math.log((2 * hc) / rc_sec)

    Pab = 1 / (2 * math.pi * E) * math.log(dab_1 / dab)
    Pba = Pab
    Pac = 1 / (2 * math.pi * E) * math.log(dac_1 / dac)
    Pca = Pac
    Pbc = 1 / (2 * math.pi * E) * math.log(dbc_1 / dbc)
    Pcb = Pbc

    P_matrix_sec3 = np.array([
        [Paa, Pab, Pac],
        [Pba, Pbb, Pbc],
        [Pca, Pcb, Pcc]
    ])

    # Cálculo da Matriz de Capacitância para a Seção 3 (por unidade de comprimento)
    C_matrix_sec3_per_m = np.linalg.inv(P_matrix_sec3)
    C_transp_total += C_matrix_sec3_per_m * l3  # Adiciona a capacitância total da seção 3

    return C_transp_total

