import numpy as np
from longitudinais.imagem import metodo_imagem_long

# Parâmetros que correspondem à Z_test
# ra, rb, rc (Ohm/m)
# xa, ha, xb, hb, xc, hc (metros)
# l (metros)
# R (metros)
Z = metodo_imagem_long(0.0001,0.0001,0.0001,0,15,3,15,6,15,10000,0.01)

Z_test = np.array([
    [(1.000000 + 6.225154j), (0.000000 + 1.739859j), (0.000000 + 1.228273j)],
    [(0.000000 + 1.739859j), (1.000000 + 6.225154j), (0.000000 + 1.739859j)],
    [(0.000000 + 1.228273j), (0.000000 + 1.739859j), (1.000000 + 6.225154j)]
])

if np.allclose(Z, Z_test, atol=1e-4, rtol=1e-5): # Mantendo atol e rtol para robustez
    print("Matriz Z calculada:")
    print(Z)
    print("\nMatriz Z de teste (esperada):")
    print(Z_test)
    print("\nAs matrizes são iguais dentro da tolerância! ✅")
else:
    print("Matriz Z calculada:")
    print(Z)
    print("\nMatriz Z de teste (esperada):")
    print(Z_test)
    print("\nAs matrizes são diferentes (fora da tolerância)! ❌")
    print("\nDiferença absoluta (abs(Z - Z_test)):")
    print(np.abs(Z - Z_test))
    print("\nDiferença relativa (abs((Z - Z_test)/Z_test)):")
    print(np.abs((Z - Z_test)/Z_test))