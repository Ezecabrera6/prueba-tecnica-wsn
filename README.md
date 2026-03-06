# WNS Challenge - Solucion (Python)

## 0) Cumplimiento de la consigna

Esta entrega cumple con los requisitos del challenge:

- La logica principal esta implementada en Python.
- Se usan los inputs originales sin modificarlos (`inputs/`).
- Se consume un unico servicio externo: la API de currency indicada en la consigna.
- La aplicacion permite elegir receta + fecha (ultimos 30 dias) y devuelve costos en ARS y USD.
- Se incluye documentacion de decisiones, supuestos, limitaciones, ejecucion y escalabilidad.

Tambien se respetan las restricciones:

- No hay llamadas a servicios externos adicionales.
- No se alteran los archivos provistos de entrada.
- El codigo esta dividido en modulos simples de explicar en entrevista.

## 1) Arquitectura del proyecto

```text
.
|-- README.md                      # Consigna original (no modificada)
|-- inputs/                        # Inputs originales (read-only)
|   |-- Recetas.md
|   |-- verduleria.pdf
|   `-- Carnes y Pescados.xlsx
`-- challenge_solution/
    |-- app.py                     # CLI principal
    |-- web_fastapi.py             # Backend API (FastAPI)
    |-- frontend/                  # Frontend (Next.js)
    |-- requirements.txt
    |-- requirements-dev.txt
    |-- Dockerfile
    |-- docker-compose.yml
    |-- src/wns_challenge/         # Dominio, parsers, servicio, errores
    |-- tests/
    `-- README.md
```

## 2) Decisiones de diseno

- Separacion de responsabilidades:
  - `parsers.py`: ingestion de fuentes MD/PDF/XLSX.
  - `service.py`: reglas de negocio y cotizacion.
  - `exchange_rate.py`: integracion con API de moneda.
- Normalizacion de nombres para resolver diferencias menores entre fuentes.
- Errores de dominio explicitos para fallas comunes (fecha invalida, receta no encontrada, etc.).
- Cache simple en memoria para tipo de cambio por fecha (optimiza llamadas repetidas).

## 3) Modelos de dominio

Modelos principales en `src/wns_challenge/models.py`:

- `Recipe`
- `Ingredient` (alias semantico de `IngredientRequirement`)
- `PriceItem` (alias semantico de `PriceEntry`)
- `IngredientQuote` y `QuoteResult` para la salida de cotizacion

## 4) Reglas de negocio

- Compra en multiplos de 250 g, redondeando hacia arriba.
  - Ejemplo: 800 g -> 1000 g.
- Fecha valida en rango inclusivo `[hoy - 30 dias, hoy]`.
  - No se permiten fechas futuras.
- Conversion a USD usando solo:
  - `https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@[FECHA]/v1/currencies/usd.json`
  - Campo usado: `usd.ars`.

## 5) Supuestos

- Los precios de PDF/XLSX estan expresados en ARS por kg.
- Los precios de ingredientes no cambian en el periodo considerado (segun consigna).
- El formato de los archivos de entrada se mantiene compatible con los archivos entregados.

## 6) Recetas cubiertas (fuente `inputs/Recetas.md`)

La aplicacion parsea y cotiza las 10 recetas del archivo:

1. Asado con ensalada criolla
2. Pollo al horno con papas y zanahorias
3. Ensalada de atun (merluza) con espinaca
4. Lomo salteado con brocoli y morron
5. Cerdo con batatas al horno
6. Berenjenas rellenas con carne picada
7. Supremas de pollo con pure de zapallo y brocoli
8. Entrana con ensalada tibia de remolacha
9. Pejerrey al horno con verduras de estacion
10. Salteado de carne con choclo y acelga

El parser contempla listas con guiones, numeradas, letras y formato `ingrediente: cantidad`.

## 7) Limitaciones

- El parser de PDF depende del texto extraible del documento.
- La cache de FX es en memoria del proceso (no persistente).
- No hay persistencia en base de datos (aplicacion stateless en runtime local).

## 8) Como ejecutar

### CLI (modo requerido por consigna)

```bash
cd challenge_solution
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py --recipe "Asado con ensalada criolla" --date 2026-03-04
```

### Backend API (FastAPI)

```bash
cd challenge_solution
uvicorn web_fastapi:app --host 0.0.0.0 --port 8000
```

Endpoint de prueba:
`http://localhost:8000/api/recipes`

### Frontend opcional (Next.js)

```bash
cd challenge_solution/frontend
npm install
npm run dev
```

Abrir:
`http://localhost:3000`

La UI hace solo lo necesario para la consigna:

- seleccionar receta,
- seleccionar fecha valida (min: hoy-30, max: hoy),
- cotizar,
- mostrar ingredientes, cantidades y total en ARS/USD.

### Docker

```bash
docker compose -f challenge_solution/docker-compose.yml up --build
```

- Frontend: `http://localhost:3011`
- Backend API: `http://localhost:8002`

## 9) Manejo de errores

Errores de dominio definidos en `errors.py`:

- `RecipeNotFoundError`
- `IngredientPriceNotFoundError`
- `InvalidQuoteDateError`
- `FXApiError`

El CLI (`app.py`) devuelve codigo de salida no-cero cuando falla y registra el motivo en logs.

## 10) Tests

Instalar dependencias de desarrollo:

```bash
cd challenge_solution
pip install -r requirements-dev.txt
```

Ejecutar:

```bash
cd challenge_solution
pytest -q
```

## 11) Como la escalaria a produccion

Si esto pasara de prueba tecnica a entorno productivo, haria estos cambios:

- Persistir catalogos normalizados en una base de datos (ingredientes, precios, versionado de fuentes).
- Usar cache distribuida para FX (por ejemplo Redis) con TTL por fecha.
- Separar ingestion (ETL) de la API de cotizacion para controlar calidad de datos y trazabilidad.
- Agregar observabilidad (logs estructurados, metricas y alertas) y pruebas de integracion end-to-end.
