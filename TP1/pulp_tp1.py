# TP1 – Mezcla de producción con costos fijos, resuelto con PuLP
# (mismo estilo que el notebook Pulp.ipynb de la cátedra)

from pulp import *

productos = ['Bidon', 'Botella', 'Tapa']

precio       = {'Bidon': 560,   'Botella': 150,  'Tapa': 30}
costo_var    = {'Bidon': 320,   'Botella': 95,   'Tapa': 22}
horas        = {'Bidon': 0.3,   'Botella': 0.12, 'Tapa': 0.02}
polimero     = {'Bidon': 1.2,   'Botella': 0.25, 'Tapa': 0.05}
costo_fijo   = {'Bidon': 31400, 'Botella': 5000, 'Tapa': 2500}
demanda      = {'Bidon': 900,   'Botella': 4500, 'Tapa': 10000}

lote_minimo      = 200
horas_disp       = 600
polimero_disp    = 3000
tope_preparacion = 60000

margen = {p: precio[p] - costo_var[p] for p in productos}


def resolver(K=1, horas_disp=horas_disp, costo_fijo=costo_fijo, mostrar=True):
    """K = cantidad máxima de productos distintos en el mes."""
    modelo = LpProblem('TP1', sense=LpMaximize)

    X = LpVariable.dicts('X', productos, lowBound=0, cat='Continuous')  # unidades
    Y = LpVariable.dicts('Y', productos, cat='Binary')                  # 1 si se prepara la línea

    # Funcional: utilidad neta = margen de contribución - costos fijos de preparación
    modelo += lpSum(margen[p] * X[p] - costo_fijo[p] * Y[p] for p in productos), 'Utilidad_neta'

    for p in productos:
        modelo += X[p] <= demanda[p] * Y[p], f'Demanda_{p}'        # si Y = 0 no se fabrica
        modelo += X[p] >= lote_minimo * Y[p], f'Lote_minimo_{p}'   # 0 o al menos el lote

    modelo += lpSum(horas[p] * X[p] for p in productos) <= horas_disp, 'Horas_extrusora'
    modelo += lpSum(polimero[p] * X[p] for p in productos) <= polimero_disp, 'Polimero'
    modelo += lpSum(costo_fijo[p] * Y[p] for p in productos) <= tope_preparacion, 'Tope_preparacion'
    modelo += lpSum(Y[p] for p in productos) <= K, 'Productos_distintos'
    modelo += Y['Bidon'] <= Y['Tapa'], 'Bidones_con_tapa'

    modelo.solve(PULP_CBC_CMD(msg=False))

    z = modelo.objective.value()
    plan = {p: X[p].varValue for p in productos}
    if mostrar:
        print(f'Estado: {LpStatus[modelo.status]}')
        for p in productos:
            print(f'  {p:8s} = {plan[p]:8.0f} u')
        print(f'  Utilidad neta = ${z:,.0f}')
    return z, plan


print('=== 1. Estado original (solo un producto al mes, K = 1) ===')
z_orig, _ = resolver(K=1)

print('\n=== 2. Margen de contribución por hora de extrusora ===')
for p in productos:
    print(f'  {p:8s}: {margen[p]} / {horas[p]} = {margen[p] / horas[p]:.0f} $/h')

print('\n=== 3. Empleado adicional (K = 3) ===')
z3, _ = resolver(K=3)
print(f'  Sueldo máximo = {z3:,.0f} - {z_orig:,.0f} = ${z3 - z_orig:,.0f}')

print('\n=== 4. 100 horas extra de extrusora (700 h) ===')
z4, _ = resolver(K=1, horas_disp=horas_disp + 100)
print(f'  Máximo a pagar = {z4:,.0f} - {z_orig:,.0f} = ${z4 - z_orig:,.0f}')

print('\n=== 5. Preparación de bidones 25 % más barata ===')
cf5 = dict(costo_fijo, Bidon=costo_fijo['Bidon'] * 0.75)
resolver(K=1, costo_fijo=cf5)
