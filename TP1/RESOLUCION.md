# TP N.º 1 – Mezcla de producción (datos de la hoja 5)

> **Supuesto clave.** El enunciado agrega: *"Por decisión comercial solo se puede fabricar
> un producto al mes (…) obviando el enunciado anterior"*. Por eso el **estado original se
> resuelve con K = 1 producto distinto**, aunque la hoja de datos diga 2. Como es un punto
> ambiguo, al final (sección 8) están también los resultados con K = 2.

Todos los tableaux completos se generan con `python3 simplex_tp1.py` (la salida está en `salida.txt`).

---

## 1. Datos y márgenes de contribución

| | Bidón (B) | Botella (L) | Tapa (T) |
|---|---:|---:|---:|
| Precio ($/u) | 560 | 150 | 30 |
| Costo variable ($/u) | 320 | 95 | 22 |
| **Margen de contribución ($/u)** | **240** | **55** | **8** |
| Horas de extrusora (h/u) | 0,30 | 0,12 | 0,02 |
| Polímero (kg/u) | 1,20 | 0,25 | 0,05 |
| Costo fijo de preparación ($) | 31.400 | 5.000 | 2.500 |
| Demanda máxima (u) | 900 | 4.500 | 10.000 |

Lote mínimo: 200 u · Horas disponibles: 600 h · Polímero: 3.000 kg · Tope de preparaciones: $60.000.

## 2. Modelo

**Variables**
- `x_B, x_L, x_T ≥ 0` (continuas): unidades a fabricar en el mes.
- `y_B, y_L, y_T ∈ {0,1}`: 1 si se prepara la línea para ese producto.

**Función objetivo** (utilidad neta = margen de contribución − costos fijos de preparación)

```
max Z = 240 x_B + 55 x_L + 8 x_T − 31400 y_B − 5000 y_L − 2500 y_T
```

**Restricciones**

```
x_B ≤ 900 y_B        x_L ≤ 4500 y_L        x_T ≤ 10000 y_T     (demanda; si y=0 ⇒ x=0)
x_B ≥ 200 y_B        x_L ≥ 200 y_L         x_T ≥ 200 y_T       (lote mínimo)
0,3 x_B + 0,12 x_L + 0,02 x_T ≤ 600                            (horas de extrusora)
1,2 x_B + 0,25 x_L + 0,05 x_T ≤ 3000                           (polímero)
31400 y_B + 5000 y_L + 2500 y_T ≤ 60000                        (tope de preparaciones)
y_B + y_L + y_T ≤ K                                            (productos distintos; K = 1)
y_B ≤ y_T                                                      (si hay bidones, hay tapas)
```

## 3. Método: enumeración de las binarias + simplex

Las `y` son binarias, así que el simplex no se aplica directo. Pero cuando fijás qué productos
se preparan (una combinación de `y`), lo que queda es un **programa lineal puro**, y ese sí se
resuelve con simplex. Hay solo 7 combinaciones posibles: se resuelve cada una y se queda la de
mayor Z. Es lo mismo que hace un Branch & Bound, pero a mano.

**Truco para el lote mínimo.** Para cada producto que se fabrica, sustituimos `x = 200 + x'`
con `x' ≥ 0`. Así todas las restricciones quedan de la forma `≤` con lado derecho positivo, y la
base inicial son las holguras (no hace falta Big‑M ni dos fases). Por ejemplo, para botellas:

- demanda: `200 + x'_L ≤ 4500` → `x'_L ≤ 4300`
- horas: `0,12(200 + x'_L) ≤ 600` → `0,12 x'_L ≤ 576`
- objetivo: `55(200 + x'_L) − 5000 = 55 x'_L + 6000`

**Regla de pivoteo** (maximización): entra la variable con el coeficiente más negativo en la
fila Z; sale la que tiene el menor cociente `LD / coeficiente` (solo coeficientes positivos).
El tableau es óptimo cuando la fila Z no tiene negativos.

---

## 4. Pregunta 1 – Estado original (K = 1)

Con un solo producto permitido, **fabricar bidones es imposible**: exigirían tapas (`y_B ≤ y_T`)
y serían dos productos. Quedan dos candidatos.

### 4.1 Solo botellas

`max Z = 55 x'_L + 6000` s.a. `x'_L ≤ 4300` (s_DL), `0,12 x'_L ≤ 576` (s_H), `0,25 x'_L ≤ 2950` (s_K)

Tableau inicial:

| Base | x'_L | s_DL | s_H | s_K | LD |
|---|---:|---:|---:|---:|---:|
| s_DL | 1 | 1 | 0 | 0 | 4300 |
| s_H | 0,12 | 0 | 1 | 0 | 576 |
| s_K | 0,25 | 0 | 0 | 1 | 2950 |
| Z | −55 | 0 | 0 | 0 | 0 |

Entra `x'_L` (−55). Cocientes: s_DL = 4300/1 = **4300**, s_H = 576/0,12 = 4800, s_K = 2950/0,25 = 11800.
Sale **s_DL** (pivote = 1). Operaciones: F_H ← F_H − 0,12·F_DL; F_K ← F_K − 0,25·F_DL; F_Z ← F_Z + 55·F_DL.

| Base | x'_L | s_DL | s_H | s_K | LD |
|---|---:|---:|---:|---:|---:|
| x'_L | 1 | 1 | 0 | 0 | 4300 |
| s_H | 0 | −0,12 | 1 | 0 | 60 |
| s_K | 0 | −0,25 | 0 | 1 | 1875 |
| Z | 0 | 55 | 0 | 0 | 236500 |

Fila Z sin negativos ⇒ **óptimo**. `x_L = 200 + 4300 = 4500`, `Z = 236500 + 6000 = 242.500`.

Lectura del tableau: sobran **60 h** de extrusora (s_H = 60) y **1.875 kg** de polímero; el
límite activo es la **demanda de botellas**, cuyo precio sombra es 55 $/u (cada botella más de
demanda sumaría $55). El precio sombra de la hora es **0** porque sobran horas.

### 4.2 Solo tapas

Mismo procedimiento: entra `x'_T`, sale la demanda (9800 < 29400 horas < 59400 polímero).
`x_T = 10.000`, `Z = 8·10000 − 2500 = 77.500`.

### 4.3 Resultado

| Combinación | Plan | Utilidad neta |
|---|---|---:|
| Solo bidones | infactible (necesita tapas) | – |
| **Solo botellas** | **L = 4.500** | **$242.500** |
| Solo tapas | T = 10.000 | $77.500 |

> **Respuesta 1:** utilidad neta óptima **$242.500**; plan: **0 bidones, 4.500 botellas, 0 tapas**.
>
> Significa que conviene dedicar el mes entero a botellas y vender toda su demanda. La línea
> no llega a saturarse (usa 540 de 600 h), así que lo que frena la utilidad es el mercado y la
> regla de "un solo producto", no la capacidad.

---

## 5. Pregunta 2 – Margen de contribución por hora de extrusora

```
Bidón:   240 / 0,30 = 800 $/h
Botella:  55 / 0,12 = 458,33 ≈ 458 $/h
Tapa:      8 / 0,02 = 400 $/h
```

> **Respuesta 2:** bidón **$800/h**, botella **$458/h**, tapa **$400/h**.
>
> Cuando la extrusora es el cuello de botella, este indicador dice en qué orden conviene
> asignarle horas: primero bidones, después botellas y por último tapas. Es exactamente el orden
> en que el simplex hace entrar las variables en los casos con varios productos (sección 6).

---

## 6. Pregunta 3 – Empleado adicional (K = 3)

Con K = 3 se pueden fabricar los tres productos. Preparación = 31.400 + 5.000 + 2.500 = 38.900 ≤ 60.000 ✔.

Sustitución `x = 200 + x'` para los tres:

```
max Z = 240 x'_B + 55 x'_L + 8 x'_T + 21700        (21700 = 200·(240+55+8) − 38900)
x'_B ≤ 700   x'_L ≤ 4300   x'_T ≤ 9800
0,3 x'_B + 0,12 x'_L + 0,02 x'_T ≤ 600 − 200·0,44 = 512      (s_H)
1,2 x'_B + 0,25 x'_L + 0,05 x'_T ≤ 3000 − 200·1,5 = 2700     (s_K)
```

**Iteración 0**

| Base | x'_B | x'_L | x'_T | s_DB | s_DL | s_DT | s_H | s_K | LD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| s_DB | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 700 |
| s_DL | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 4300 |
| s_DT | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 9800 |
| s_H | 0,3 | 0,12 | 0,02 | 0 | 0 | 0 | 1 | 0 | 512 |
| s_K | 1,2 | 0,25 | 0,05 | 0 | 0 | 0 | 0 | 1 | 2700 |
| Z | −240 | −55 | −8 | 0 | 0 | 0 | 0 | 0 | 0 |

Entra **x'_B** (−240). Cocientes: s_DB = **700**, s_H = 512/0,3 = 1706,7, s_K = 2700/1,2 = 2250. Sale **s_DB**.
F_H ← F_H − 0,3·F_DB; F_K ← F_K − 1,2·F_DB; F_Z ← F_Z + 240·F_DB.

**Iteración 1**

| Base | x'_B | x'_L | x'_T | s_DB | s_DL | s_DT | s_H | s_K | LD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| x'_B | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 700 |
| s_DL | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 4300 |
| s_DT | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 9800 |
| s_H | 0 | 0,12 | 0,02 | −0,3 | 0 | 0 | 1 | 0 | 302 |
| s_K | 0 | 0,25 | 0,05 | −1,2 | 0 | 0 | 0 | 1 | 1860 |
| Z | 0 | −55 | −8 | 240 | 0 | 0 | 0 | 0 | 168000 |

Entra **x'_L** (−55). Cocientes: s_DL = 4300, s_H = 302/0,12 = **2516,67**, s_K = 1860/0,25 = 7440. Sale **s_H** (pivote 0,12).
F_H ← F_H / 0,12; F_DL ← F_DL − F_H(nueva); F_K ← F_K − 0,25·F_H(nueva); F_Z ← F_Z + 55·F_H(nueva).

**Iteración 2**

| Base | x'_B | x'_L | x'_T | s_DB | s_DL | s_DT | s_H | s_K | LD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| x'_B | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 700 |
| s_DL | 0 | 0 | −0,1667 | 2,5 | 1 | 0 | −8,333 | 0 | 1783,33 |
| s_DT | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 9800 |
| x'_L | 0 | 1 | 0,1667 | −2,5 | 0 | 0 | 8,333 | 0 | 2516,67 |
| s_K | 0 | 0 | 0,0083 | −0,575 | 0 | 0 | −2,083 | 1 | 1230,83 |
| Z | 0 | 0 | 1,1667 | 102,5 | 0 | 0 | 458,33 | 0 | 306416,67 |

Fila Z sin negativos ⇒ **óptimo**:
`x_B = 900`, `x_L = 200 + 2516,67 = 2716,67`, `x_T = 200` (x'_T no básica = 0),
`Z = 306416,67 + 21700 = 328.116,67`.

Lectura del tableau:
- **s_H = 0**: la extrusora queda saturada; su precio sombra es **458,33 $/h** (una hora más se
  usaría para más botellas).
- **Costo reducido de x'_T = 1,1667**: cada tapa por encima del mínimo le quita 0,02 h a las
  botellas (0,02·458,33 = 9,17 $) y deja solo 8 $ ⇒ pierde 1,17 $. Por eso las tapas quedan en el
  lote mínimo: se fabrican solo porque los bidones las exigen.
- **Precio sombra de la demanda de bidones = 102,5 $/u** = 240 − 0,3·458,33: vale la pena un
  bidón más aunque se le saquen horas a las botellas.

Las demás combinaciones con K = 3 dan menos (botellas + tapas: 264.000; bidones + tapas: 262.100).

> **Respuesta 3:** sueldo máximo = 328.117 − 242.500 = **$85.617** por mes.
>
> Es lo que la empresa gana de más al poder fabricar los tres productos
> (900 bidones, 2.717 botellas, 200 tapas). Si le pagara más al empleado, contratarlo haría
> perder plata respecto del plan original.

---

## 7. Pregunta 4 – 100 horas extra de extrusora

En el óptimo original (solo botellas) la holgura de horas es **s_H = 60 h**: la restricción no
está activa y su **precio sombra es 0**. Pasar de 600 a 700 h solo agrega más holgura (160 h),
y la base óptima no cambia (el script lo re-resuelve con 700 h y da otra vez $242.500).

> **Respuesta 4:** la empresa estaría dispuesta a pagar **$0** por esas 100 h.
>
> No le sirven: lo que frena la producción es la demanda de botellas y la regla de un solo
> producto, no la máquina.

---

## 8. Pregunta 5 – Preparación de bidones 25 % más barata

Nuevo costo fijo del bidón: 31.400 · 0,75 = **23.550**. Pero con K = 1 los bidones siguen siendo
infactibles (necesitan tapas, o sea dos productos). El costo fijo del bidón no aparece en
ninguna combinación factible, así que el óptimo no cambia.

> **Respuesta 5:** utilidad neta **$242.500**; plan **0 bidones, 4.500 botellas, 0 tapas**
> (igual que el original).

---

## 9. Si el estado original fuera K = 2 (sin la nota de "un solo producto")

Si el docente toma la hoja de datos (máx. 2 productos), los resultados son estos
(el script los calcula igual):

| Pregunta | K = 2 |
|---|---|
| 1 | **$264.000**; 0 bidones, 4.500 botellas, 3.000 tapas (bidones + tapas daría 262.100). La extrusora se satura: precio sombra 400 $/h |
| 2 | 800 / 458 / 400 $/h (no cambia) |
| 3 | 328.117 − 264.000 = **$64.117** |
| 4 | Precio sombra 400 $/h × 100 h = **$40.000** (las horas extra van a tapas: T pasa de 3.000 a 8.000, Z = 304.000; T ≤ 10.000, así que la base sigue siendo válida) |
| 5 | Bidones + tapas = 216.000 + 80.000 − 23.550 − 2.500 = **$269.950** > 264.000 ⇒ nuevo plan: **900 bidones, 0 botellas, 10.000 tapas** |

## 10. Resumen (estado original K = 1)

| # | Respuesta |
|---|---|
| 1 | Utilidad neta **$242.500**; plan B = 0, L = 4.500, T = 0 |
| 2 | Bidón **800 $/h**, botella **458 $/h**, tapa **400 $/h** |
| 3 | Sueldo máximo **$85.617** |
| 4 | **$0** (las horas no son recurso escaso) |
| 5 | Utilidad **$242.500**; plan B = 0, L = 4.500, T = 0 (sin cambios) |
