# Agente de análisis de logs de simulación para apoyar RCA

Proyecto de residencia profesional orientado a facilitar el análisis de causa raíz (RCA) en verificación digital. El agente busca recuperar evidencia trazable de logs de simulación y regresión, como mensajes UVM, fallos de assertions y marcadores de prueba, para que una persona u otra herramienta pueda investigar un fallo.

## Estado del proyecto

El prototipo ya incluye un módulo de ingestión en Python que conserva una copia del log y genera registros JSONL con referencias a las líneas originales. La hoja de ruta contempla incorporar consultas sobre los eventos y correlacionar transacciones del monitor con su recepción en el scoreboard.

## Estructura

- `semana_1/` contiene la guía de etiquetado y los materiales de preparación de casos.
- `semana_2/` contiene el módulo de ingestión, los esquemas JSON, ejemplos y pruebas.
- `pruebas_funcionales_logs/` contiene casos de prueba y sus resultados de referencia.
- `pruebas_robustez_logs/` contiene casos para evaluar la ingestión con entradas variadas.

## Ejecutar la demostración

Desde la raíz del proyecto, con Python 3 disponible, ejecuta uno de los siguientes comandos:

```powershell
python -m semana_2.demo_manual PASS
python -m semana_2.demo_manual FAIL
python -m semana_2.demo_manual INDETERMINADO
```

Cada ejecución muestra la evidencia encontrada en el log y el resultado funcional de referencia del caso. Las etiquetas provienen del manifiesto de pruebas.
