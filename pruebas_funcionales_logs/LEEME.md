# Casos normales y fallidos para el agente de logs

## Por qué se añade este conjunto

Los 43 casos de `pruebas_robustez_logs` no son exclusivamente archivos dañados: incluyen controles completos y legibles de logs con éxito y con fallo. Por tanto, no era necesario duplicar 43 archivos para comenzar a probar PASS/FAIL. Sin embargo, esos casos fueron diseñados principalmente para ingestión y no cubren de forma explícita una prueba limpia, warning sin fallo, fatal, assertion, transporte de transacciones y fallo de herramienta con resultados esperados por escenario.

Este complemento añade ocho escenarios sintéticos pequeños y dos copias exactas de referencias reales que ya teníamos. Los sintéticos son datos controlados para desarrollo del parser/API, no resultados de simulaciones ejecutadas, ni casos atribuidos a un repositorio. Los nombres `fixture_*.sv` y `/fixture_top/dut` son referencias ficticias dentro del texto. No existen archivos HDL asociados a esas referencias.

## Ubicación

Guardar esta carpeta directamente dentro de `proyecto_residencia`, al mismo nivel que `pruebas_robustez_logs` y `semana_1`. Las rutas de `manifest.json` se resuelven desde esta carpeta.

```text
proyecto_residencia/
├── pruebas_robustez_logs/        # 43 casos de ingestión ya existentes
├── pruebas_funcionales_logs/
│   ├── casos/                   # 8 escenarios nuevos, sintéticos
│   ├── referencias_reales/      # 2 logs ya publicados, copiados sin cambios
│   ├── manifest.json
│   ├── verificacion.json
│   ├── LEEME.md
│   ├── preparar_casos.py
│   └── casos_funcionales_logs.zip
└── semana_1/
```

## Casos y resultados esperados

| ID | Escenario | Lectura | Resultado funcional | Correlación |
| --- | --- | --- | --- | --- |
| N01_pass_limpio | Comparación correcta, TEST PASSED y cierre; cero warnings y errores. | OK | PASS | NOT_OBSERVABLE |
| N02_pass_con_warning | Una advertencia de warmup, comparación correcta y cierre exitoso. | OK | PASS | NOT_OBSERVABLE |
| N03_pass_transporte_match | Dos publicaciones y dos recepciones con claves y datos coincidentes. | OK | PASS | MATCH |
| F01_error_scoreboard | Dos mensajes UVM_ERROR por dos bytes del mismo beat, resumen y TEST FAILED. El resumen de herramienta informa cero errores. | OK | FAIL | NOT_OBSERVABLE |
| F02_fatal_configuracion | UVM_FATAL por interfaz no configurada; termina por fatal sin UVM Report Summary. | OK | FAIL | NOT_OBSERVABLE |
| F03_assertion_fallida | Un aviso nativo de assertion y un UVM_ERROR describen el mismo fallo. | OK | FAIL | NOT_OBSERVABLE |
| F04_transporte_dato_alterado | La misma transacción llega al scoreboard con data diferente; hay un checker explícito de divergencia. | OK | FAIL | DIVERGENCE |
| I01_error_herramienta | Falta licencia, no comienza la simulación y el proceso termina. | OK | INDETERMINADO | NOT_OBSERVABLE |
| R01_axi4_pass | Log publicado AXI4 PASS, copia exacta sin salto final. | OK | PASS | NOT_OBSERVABLE |
| R02_axi4_fail | Log publicado AXI4 FAIL, copia exacta con cinco mensajes UVM_ERROR. | OK | FAIL | NOT_OBSERVABLE |

Normal significa que las comprobaciones funcionales de la prueba terminan exitosamente. No significa necesariamente que no existan advertencias. Fallido describe la verificación o su entorno según la evidencia; no demuestra automáticamente un defecto del DUT ni su causa raíz.

El caso I01 es un control adicional: que falle una herramienta no prueba que falle el diseño. Su archivo es texto UTF-8 válido y completo como reporte de lanzamiento; la verificación funcional no llegó a ejecutarse.

## Expectativas que conviene comprobar

- Separar lectura del archivo, estado de ejecución, resultado funcional y correlación. Todos los archivos de este conjunto son legibles; algunos describen fallos.
- Contar mensajes UVM individuales sin sumar otra vez las filas del UVM Report Summary. Los conteos esperados completos sólo se fijan aquí para los ocho sintéticos.
- No convertir un warning aislado en FAIL: N02 debe conservar PASS funcional.
- En F01, dos mensajes de error no equivalen a dos beats incorrectos, y los conteos de herramienta no anulan el fallo UVM.
- En F02, distinguir fallo de configuración del testbench de defecto del DUT; la ausencia de resumen no borra el fatal observado. La terminación por fatal no representa truncamiento del archivo.
- En F03, conservar ambos registros y sus dominios, pero agruparlos como evidencia de una assertion fallida. No duplicar incidentes al contar mensajes.
- En N03 y F04, emparejar por corrida, canal, sentido, TID, ocurrencia y segmento; comparar data. Los tiempos de publicación y recepción pueden diferir.
- F04 tiene un envío y una recepción, pero distinto contenido. La igualdad de cantidades no basta para MATCH.
- N01, N02 y R01 tienen PASS funcional en su alcance, pero no demuestran el transporte monitor → scoreboard. Si la aceptación del test exige esa correlación, su aceptación global debe quedar INDETERMINADO.
- No interpretar las rutas ficticias de los sintéticos como referencias reales a señales o archivos del repositorio. No hay causa raíz del DUT etiquetada.

## Procedencia de las referencias reales

R01 y R02 se copian byte a byte desde `pruebas_robustez_logs/originales_publicados/`. El manifiesto conserva URL fijada por revisión, SHA del objeto Git y SHA-256 del archivo. No son nuevas corridas ni observaciones independientes del par AXI4 existente.

Se incluyen copias de las anotaciones previas C04/C03 para consulta. Son anotaciones propuestas, no exhaustivas y sin revisión independiente registrada. Las rutas relativas que contienen conservan el significado de sus ubicaciones originales en `semana_1/etiquetas`; no deben resolverse desde las copias. El manifiesto nuevo identifica el log local correspondiente.

## Uso durante las actividades posteriores

Para pruebas de lectura y fallos de formato, usar el manifiesto de `pruebas_robustez_logs`. Para reglas funcionales y consultas con respuestas conocidas, usar el manifiesto de esta carpeta. Se pueden ejecutar ambos conjuntos con la misma implementación, manteniendo separadas las dimensiones evaluadas.

Los conteos de los sintéticos están en `esperado.conteos_eventos_uvm`. Los registros de evidencia dan identificadores, texto y números de línea. Este formato es un manifiesto de fixtures, no una sustitución del contrato de API previsto para la segunda semana.

Las ocho muestras sintéticas usan UTF-8 sin BOM, saltos LF y salto final, y no están truncadas. Eso permite aislar el comportamiento funcional de los defectos de ingestión. No se generó un producto cartesiano de estos escenarios con todas las codificaciones y recortes.

Las referencias reales y sus derivados ya aparecen en otros conjuntos. No repartir copias del mismo log entre entrenamiento y evaluación como si fueran corridas independientes. Los sintéticos sirven para desarrollar y depurar, pero no reemplazan una validación posterior con logs reales no utilizados en el desarrollo.

## Verificación realizada

`verificacion.json` comprueba hashes y coherencia estructural: cantidades de mensajes UVM sintéticos, diferencia o igualdad de datos entre pares, UTF-8, salto final e integridad del ZIP. No se ejecutó el futuro parser ni se validó una causa raíz. Se preservaron los 43 casos de robustez y las anotaciones originales de semana_1.

No es necesario ejecutar `preparar_casos.py` para usar los archivos ya incluidos. No guardar resultados del parser sobre los logs de entrada; crear salidas separadas durante la segunda semana.
