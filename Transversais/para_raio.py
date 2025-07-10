import math
import numpy as np

def metodo_para_raio_tran(
        ra, rb, rc,
        xa_pos1, ha_pos1, xb_pos2, hb_pos2, xc_pos3, hc_pos3,
        r_pr, x_pr_pos1, h_pr_pos1,
        x_pr_pos2, h_pr_pos2, x_pr_pos3, h_pr_pos3,
        rho, l1, l2, l3
):
    """
    Calcula a matriz de capacitância de fase para uma linha de transmissão trifásica
    totalmente transposta, incluindo o efeito de cabos para-raios aterrados.

    Esta função considera um ciclo completo de transposição da linha, dividindo-o
    em três seções de comprimentos l1, l2 e l3. A capacitância total da linha
    é a soma das capacitâncias de cada uma dessas seções.

    Parâmetros:
    ra, rb, rc (float): Raios físicos dos condutores das fases A, B e C (em metros).
    xa_pos1, ha_pos1 (float): Coordenadas X e H da Posição Física 1 para as fases.
    xb_pos2, hb_pos2 (float): Coordenadas X e H da Posição Física 2 para as fases.
    xc_pos3, hc_pos3 (float): Coordenadas X e H da Posição Física 3 para as fases.
    r_pr (list of float): Lista dos raios físicos de cada cabo para-raios (em metros).
    x_pr_pos1 (list of float): Lista das coordenadas X dos cabos para-raios na Posição 1.
    h_pr_pos1 (list of float): Lista das coordenadas H dos cabos para-raios na Posição 1.
    x_pr_pos2 (list of float): Lista das coordenadas X dos cabos para-raios na Posição 2.
    h_pr_pos2 (list of float): Lista das coordenadas H dos cabos para-raios na Posição 2.
    x_pr_pos3 (list of float): Lista das coordenadas X dos cabos para-raios na Posição 3.
    h_pr_pos3 (list of float): Lista das coordenadas H dos cabos para-raios na Posição 3.
    rho (float): Resistividade do solo (em Ohm.m).
    l1, l2, l3 (float): Comprimentos das três seções da transposição (em metros).

    Retorna:
    numpy.ndarray: Matriz de capacitância de fase (3x3) da linha transposta (em Farads).
                   A capacitância é calculada para o comprimento total da linha (l1 + l2 + l3).

    Raises:
    ValueError: Para entradas inválidas (rho <= 0, alturas <= 0, listas de para-raios inconsistentes, etc.).
    """

    # --- Constantes Físicas ---
    E = 8.854 * 10 ** (-12)  # Permissividade do vácuo (F/m)

    # --- Validações de Entrada ---
    if rho <= 0:
        raise ValueError("ERRO! A resistividade do solo (rho) deve ser um valor positivo.")
    if ha_pos1 <= 0 or hb_pos2 <= 0 or hc_pos3 <= 0:
        raise ValueError("ERRO! As alturas das posições físicas (ha, hb, hc) devem ser maiores que zero.")
    if l1 < 0 or l2 < 0 or l3 < 0:
        raise ValueError("ERRO! Os comprimentos das seções (l1, l2, l3) devem ser não-negativos.")
    if (l1 + l2 + l3) == 0:
        raise ValueError("ERRO! O comprimento total da linha (l1+l2+l3) não pode ser zero.")

    num_pr = len(r_pr)
    if not (len(x_pr_pos1) == len(h_pr_pos1) == num_pr and
            len(x_pr_pos2) == len(h_pr_pos2) == num_pr and
            len(x_pr_pos3) == len(h_pr_pos3) == num_pr):
        raise ValueError(
            "ERRO! As listas de coordenadas X, H e raios dos para-raios devem ter o mesmo número de elementos em todas as posições.")
    for h_pr_list_val in [h_pr_pos1, h_pr_pos2, h_pr_pos3]:
        for h_pr_val in h_pr_list_val:
            if h_pr_val <= 0:
                raise ValueError("ERRO! As alturas dos cabos para-raios devem ser maiores que zero.")
    for r_pr_val in r_pr:
        if r_pr_val <= 0:
            raise ValueError("ERRO! Os raios dos cabos para-raios devem ser positivos.")

    # --- Inicializa a matriz de capacitância total transposta ---
    C_transp_total = np.zeros((3, 3))

    # --- Iterar sobre as 3 Seções da Transposição ---
    for section_idx in range(3):
        # Define as coordenadas e raios para a seção atual da transposição
        if section_idx == 0:  # Seção 1: A na pos1, B na pos2, C na pos3
            current_xa, current_ha = xa_pos1, ha_pos1
            current_xb, current_hb = xb_pos2, hb_pos2
            current_xc, current_hc = xc_pos3, hc_pos3
            current_l = l1
            current_x_pr = x_pr_pos1
            current_h_pr = h_pr_pos1
            cond_r_sec = [ra, rb, rc] + r_pr
        elif section_idx == 1:  # Seção 2: A na pos2, B na pos3, C na pos1
            current_xa, current_ha = xb_pos2, hb_pos2
            current_xb, current_hb = xc_pos3, hc_pos3
            current_xc, current_hc = xa_pos1, ha_pos1
            current_l = l2
            current_x_pr = x_pr_pos2
            current_h_pr = h_pr_pos2
            cond_r_sec = [rc, ra, rb] + r_pr  # C (na pos1), A (na pos2), B (na pos3)
        else:  # Seção 3: A na pos3, B na pos1, C na pos2
            current_xa, current_ha = xc_pos3, hc_pos3
            current_xb, current_hb = xa_pos1, ha_pos1
            current_xc, current_hc = xb_pos2, hb_pos2
            current_l = l3
            current_x_pr = x_pr_pos3
            current_h_pr = h_pr_pos3
            cond_r_sec = [rb, rc, ra] + r_pr  # B (na pos1), C (na pos2), A (na pos3)

        if current_l == 0:  # Pula a seção se o comprimento for zero
            continue

        # Coordenadas de TODOS os condutores (fases + para-raios) para a seção atual
        cond_x_sec = [current_xa, current_xb, current_xc] + current_x_pr
        cond_h_sec = [current_ha, current_hb, current_hc] + current_h_pr

        n_total = len(cond_x_sec)  # Número total de condutores (fases + para-raios)

        # --- Construção da Matriz de Potencial (P) estendida (n_total x n_total) para a seção atual ---
        P_extended_sec = np.zeros((n_total, n_total))
        for i in range(n_total):
            for j in range(n_total):
                xi, hi, ri = cond_x_sec[i], cond_h_sec[i], cond_r_sec[i]
                xj, hj, rj = cond_x_sec[j], cond_h_sec[j], cond_r_sec[j]

                if i == j:  # Elemento P_ii (auto-potencial)
                    P_extended_sec[i, j] = 1 / (2 * math.pi * E) * math.log((2 * hi) / ri)
                else:  # Elemento P_ij (potencial mútuo)
                    d = np.sqrt(((xi - xj) ** 2) + ((hi - hj) ** 2))
                    d_prime = np.sqrt(((xi - xj) ** 2) + ((hi + hj) ** 2))
                    P_extended_sec[i, j] = 1 / (2 * math.pi * E) * math.log(d_prime / d)

        # --- Redução da Matriz de Potencial (Kron Reduction) ---
        # Particiona P_extended_sec em submatrizes: P_ff, P_fg, P_gf, P_gg
        # 'f' são as fases (índices 0, 1, 2); 'g' são os para-raios (índices 3 em diante).

        P_ff = P_extended_sec[0:3, 0:3]
        P_fg = P_extended_sec[0:3, 3:n_total]
        P_gf = P_extended_sec[3:n_total, 0:3]
        P_gg = P_extended_sec[3:n_total, 3:n_total]

        # Verifica se P_gg é invertível para evitar erros, apenas se houver para-raios
        if num_pr > 0:
            if np.linalg.det(P_gg) == 0:
                raise ValueError(
                    f"ERRO! A submatriz P_gg para a seção {section_idx + 1} é singular e não pode ser invertida. Verifique as posições dos para-raios.")
            P_gg_inv = np.linalg.inv(P_gg)
            # P_reduzida = P_ff - P_fg * P_gg_inv * P_gf
            P_reduced_sec = P_ff - np.dot(np.dot(P_fg, P_gg_inv), P_gf)
        else:  # Se não há para-raios, a matriz de potencial reduzida é simplesmente P_ff.
            P_reduced_sec = P_ff

        # Cálculo da Matriz de Capacitância para a Seção (por unidade de comprimento)
        C_matrix_sec_per_m = np.linalg.inv(P_reduced_sec)

        # Adiciona a capacitância total da seção à matriz total transposta
        C_transp_total += C_matrix_sec_per_m * current_l

    return C_transp_total  # Retorna a matriz de capacitância total da linha transposta (em Farads)
