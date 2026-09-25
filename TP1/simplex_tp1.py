"""TP N.º 1 - Mezcla de producción (datos hoja 5).

Resuelve el modelo mixto (binarias de preparación + cantidades continuas)
enumerando las combinaciones de productos admitidas y resolviendo cada
subproblema lineal con el método simplex tabular (aritmética exacta).
Imprime todos los tableaux intermedios.

Uso: python3 simplex_tp1.py
"""
from fractions import Fraction as F
from itertools import combinations

# ---------------- Datos (hoja 5) ----------------
P = ["B", "L", "T"]  # Bidón, botella (Litro), Tapa
nombre = {"B": "bidones", "L": "botellas", "T": "tapas"}
precio = {"B": 560, "L": 150, "T": 30}
cvar = {"B": 320, "L": 95, "T": 22}
horas = {"B": F("0.3"), "L": F("0.12"), "T": F("0.02")}
polim = {"B": F("1.2"), "L": F("0.25"), "T": F("0.05")}
setup = {"B": 31400, "L": 5000, "T": 2500}
dem = {"B": 900, "L": 4500, "T": 10000}
LOTE_MIN = 200
HORAS_DISP = 600
POLIM_DISP = 3000
TOPE_SETUP = 60000

margen = {p: precio[p] - cvar[p] for p in P}


def fmt(x):
    x = F(x)
    if x.denominator == 1:
        return str(x.numerator)
    return f"{float(x):.4f}".rstrip("0")


def print_tableau(T, base, cols, titulo):
    print(f"\n  {titulo}")
    w = 11
    print("  " + "Base".ljust(6) + "".join(c.rjust(w) for c in cols) + "LD".rjust(w))
    for i, fila in enumerate(T[:-1]):
        print("  " + base[i].ljust(6) + "".join(fmt(v).rjust(w) for v in fila))
    print("  " + "Z".ljust(6) + "".join(fmt(v).rjust(w) for v in T[-1]))


def simplex(c, A, b, var_names, slack_names, verbose=True):
    """max c·x  s.a.  A x <= b, x >= 0, con b >= 0 (base inicial = holguras)."""
    m, n = len(A), len(c)
    cols = var_names + slack_names
    T = []
    for i in range(m):
        fila = [F(v) for v in A[i]] + [F(1 if j == i else 0) for j in range(m)] + [F(b[i])]
        T.append(fila)
    T.append([F(-v) for v in c] + [F(0)] * m + [F(0)])  # fila Z: Z - c x = 0
    base = list(slack_names)
    it = 0
    if verbose:
        print_tableau(T, base, cols, f"Tableau inicial (iteración {it})")
    while True:
        zrow = T[-1][:-1]
        piv_c = min(range(n + m), key=lambda j: zrow[j])
        if zrow[piv_c] >= 0:
            break
        ratios = [(T[i][-1] / T[i][piv_c], i) for i in range(m) if T[i][piv_c] > 0]
        if not ratios:
            raise ValueError("no acotado")
        _, piv_r = min(ratios)
        it += 1
        if verbose:
            print(f"\n  -> Entra {cols[piv_c]} (costo reducido {fmt(zrow[piv_c])}); "
                  "cocientes: " + ", ".join(f"{base[i]}={fmt(r)}" for r, i in ratios)
                  + f"; sale {base[piv_r]}; pivote {fmt(T[piv_r][piv_c])}")
        pv = T[piv_r][piv_c]
        T[piv_r] = [v / pv for v in T[piv_r]]
        for i in range(m + 1):
            if i != piv_r and T[i][piv_c] != 0:
                f = T[i][piv_c]
                T[i] = [a - f * bb for a, bb in zip(T[i], T[piv_r])]
        base[piv_r] = cols[piv_c]
        if verbose:
            print_tableau(T, base, cols, f"Tableau iteración {it}")
    sol = {v: F(0) for v in cols}
    for i, v in enumerate(base):
        sol[v] = T[i][-1]
    duales = {slack_names[j]: T[-1][n + j] for j in range(m)}
    return T[-1][-1], sol, duales


def resolver_subproblema(S, horas_disp=HORAS_DISP, setup_mod=None, verbose=True):
    """Resuelve el PL de la combinación S (productos que se preparan).

    Se sustituye x_p = 200 + x'_p para eliminar el lote mínimo; así todas las
    restricciones quedan <= con LD >= 0 y la base inicial son las holguras.
    """
    su = dict(setup)
    if setup_mod:
        su.update(setup_mod)
    fijo = sum(su[p] for p in S)
    if fijo > TOPE_SETUP:
        return None
    vars_ = [p + "'" for p in S]
    c = [margen[p] for p in S]
    A, b, sl = [], [], []
    for p in S:  # demanda: x'_p <= D_p - 200
        A.append([1 if q == p else 0 for q in S]); b.append(dem[p] - LOTE_MIN); sl.append("s_D" + p)
    A.append([horas[p] for p in S]); b.append(horas_disp - LOTE_MIN * sum(horas[p] for p in S)); sl.append("s_H")
    A.append([polim[p] for p in S]); b.append(POLIM_DISP - LOTE_MIN * sum(polim[p] for p in S)); sl.append("s_K")
    if min(b) < 0:
        return None
    const = LOTE_MIN * sum(margen[p] for p in S) - fijo
    if verbose:
        print(f"\n  Z = {' + '.join(f'{c[i]}·{vars_[i]}' for i in range(len(S)))} + {const}"
              f"   (constante = 200·márgenes − preparación {fijo})")
    z, sol, du = simplex(c, A, b, vars_, sl, verbose)
    x = {p: LOTE_MIN + sol[p + "'"] for p in S}
    return z + const, x, du


def resolver(kmax, horas_disp=HORAS_DISP, setup_mod=None, verbose=True, titulo=""):
    print("\n" + "=" * 78 + f"\n{titulo}  (máx. {kmax} producto/s, {horas_disp} h)\n" + "=" * 78)
    mejor = None
    for k in range(1, kmax + 1):
        for S in combinations(P, k):
            etiqueta = "+".join(nombre[p] for p in S)
            if "B" in S and "T" not in S:
                print(f"\n* {etiqueta}: INFACTIBLE (si hay bidones debe haber tapas: y_B <= y_T)")
                continue
            print(f"\n* Combinación {etiqueta}:")
            r = resolver_subproblema(S, horas_disp, setup_mod, verbose)
            if r is None:
                print("  INFACTIBLE (tope de preparaciones o recursos)")
                continue
            z, x, du = r
            print(f"  => Utilidad neta = {fmt(z)}  | plan: "
                  + ", ".join(f"{nombre[p]}={fmt(v)}" for p, v in x.items())
                  + f"  | precio sombra hora = {fmt(du['s_H'])} $/h")
            if mejor is None or z > mejor[0]:
                mejor = (z, x, S)
    z, x, S = mejor
    print(f"\n>>> ÓPTIMO: utilidad neta = {round(z)} $ ; plan = "
          + ", ".join(f"{nombre[p]}={round(x.get(p, 0))}" for p in P))
    return mejor


if __name__ == "__main__":
    print("Márgenes de contribución ($/u):", margen)
    print("Margen por hora de extrusora ($/h):",
          {p: fmt(F(margen[p]) / horas[p]) for p in P})
    for K in (1, 2):
        z1 = resolver(K, titulo=f"P1 - Estado original K={K}")[0]
        z3 = resolver(3, titulo="P3 - Con empleado adicional (K=3)")[0]
        print(f"\n>>> P3 (K={K}): sueldo máximo = {round(z3)} - {round(z1)} = {round(z3 - z1)} $")
        z4 = resolver(K, horas_disp=700, titulo=f"P4 - +100 h extrusora K={K}")[0]
        print(f"\n>>> P4 (K={K}): máximo a pagar por 100 h = {round(z4 - z1)} $")
        resolver(K, setup_mod={"B": F(31400) * F(3, 4)}, titulo=f"P5 - Preparación bidones -25% K={K}")
