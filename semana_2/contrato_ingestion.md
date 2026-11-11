# Semana 2 · Ingestión y trazabilidad

## Definición

`ingest_log(paths, *, allowed_root, storage, metadata=None)` recibe una ruta o una lista de rutas locales en orden. Las rutas relativas se resuelven desde `allowed_root`. Se rechazan rutas inexistentes, duplicadas, directorios y rutas cuyo destino resuelto queda fuera de la raíz. La raíz y el almacenamiento los configura el programa llamador, no el contenido del log; usar directorios locales de confianza y no modificar los archivos durante la captura.

`metadata` admite `encoding` (opcional, aplicado a todos los archivos de la llamada) y `known_truncated` (booleano, falso por defecto). Para entradas con distintas codificaciones explícitas, usar llamadas separadas. La lectura detecta BOM UTF-8 y UTF-16 LE/BE; sin BOM ni indicación usa UTF-8 estricto. Para Windows-1252 o UTF-16 sin BOM, indicar la codificación. Un BOM incompatible, bytes inválidos o NUL en el texto producen `decode_error`: se conserva la copia binaria y se descarta el índice incompleto del archivo; los otros archivos pueden procesarse. No se reemplazan caracteres ni se adivina una codificación alternativa.

La respuesta cumple [ingestion.schema.json](esquemas/ingestion.schema.json). Cada fila JSONL cumple [linea.schema.json](esquemas/linea.schema.json). Campos principales:

| Campo | Regla |
|---|---|
| `schema_version` | Versión del contrato producido, actualmente `1.0`. Es independiente de la versión de fichas manuales. |
| `run_id` | UUID aleatorio con prefijo `R-`. Una llamada aceptada registra una instantánea nueva, aunque el contenido sea idéntico; no se deduplica por hash. |
| `event_id` | Identidad provisional de captura: `run_id:file_id:número_de_línea`. Identifica una línea, no un evento semántico UVM ni un ID de la ficha manual. El parser futuro podrá referenciar intervalos de estas líneas. |
| `test_name` | Valor único observado de `+UVM_TESTNAME` en texto decodificado. Se registra valor, línea, archivo e ID de captura por aparición. Ausente o en conflicto: `null`; conflicto produce advertencia. No autentica comandos ni ejecuta texto del log. RNTST se conserva en la línea original; su interpretación no forma parte de este extractor. |
| `status` | `ok`: captura aceptada sin errores de decodificación, recorte conocido ni conflicto de test. `partial`: alguna de esas condiciones, con evidencia disponible. `invalid_input`: no se crea corrida. No representa PASS/FAIL de simulación. |
| `data`, `warnings`, `provenance` | Totales de captura, observaciones del nombre y pista de formato UVM si aparece el argumento; advertencias de ingestión; ruta original relativa, archivos de salida, SHA-256, tamaño, codificación y líneas por archivo. La pista no certifica el formato y las advertencias de captura no son UVM_WARNING. |

Una entrada vacía, sólo BOM o sólo espacios produce `empty_content` sin inventar eventos. Se conservan líneas en blanco cuando existen. La ausencia de terminador final se reporta aparte y **no demuestra truncamiento**. Los recortes controlados usan el metadato del manifiesto; para un archivo desconocido no se infiere el estado de la simulación a partir del fin del archivo. Los fallos de E/S al copiar o guardar se propagan al llamador; no se publica una corrida a medio escribir.

## Construcción y ejecución

Python 3.10 o superior. Ingestión con biblioteca estándar; las pruebas usan `jsonschema` para validar los contratos. Desde la raíz del proyecto:

```powershell
python -B -m unittest semana_2.test_ingestion -v
```

Uso desde Python:

```python
from semana_2.ingestion import ingest_log

resultado = ingest_log(
    "pruebas_funcionales_logs/casos/N01_pass_limpio.log",
    allowed_root=".",
    storage="semana_2/capturas_locales",
)
```

No requiere una interfaz de comandos propia. Los conjuntos de entrada y sus `manifest.json` permanecen en sus carpetas originales. La suite lee 43 casos de robustez, 8 sintéticos funcionales y 2 controles AXI4; en el complemento sólo comprueba lectura, bytes y líneas de evidencia, no el resultado funcional esperado.

## Capturar y verificar una referencia

Cada directorio `<storage>/<run_id>/` contiene `manifest.json`, copias binarias `F0001.log` y, cuando la decodificación es válida, registros `F0001.jsonl` (un objeto JSON UTF-8 por línea física). Se prepara en un directorio temporal y se publica al terminar. El programa no sobrescribe corridas publicadas; el hash permite detectar modificaciones externas, no impide editarlas manualmente.

Las líneas se numeran desde 1, cuentan líneas vacías y conservan espacios, prefijos y terminador separado (LF, CRLF, CR o ninguno). El BOM es metadato de codificación y no parte del mensaje. La copia original permite verificar los bytes completos. Para rastrear una referencia, buscar `file_id` en el manifiesto, comprobar SHA-256 de la copia y leer el intervalo inclusivo señalado. Los ejemplos generados se encuentran en `ejemplos/`.

Las cinco fichas de semana 1 siguen siendo anotaciones independientes. La prueba de trazabilidad lee el log de cada ficha, comprueba su hash y reconstruye por intervalos los 24 fragmentos seleccionados. Esto no certifica inventario exhaustivo ni clasificación.

## Diseño de correlación (sólo contrato conceptual)

- Identidad propuesta: corrida, test y seed si constan, interfaz/canal y sentido, ID de transacción, ocurrencia y segmento de reset/flush; beat si aplica. Una dirección de memoria o un dato igual no identifica por sí solo una transacción.
- Comparar únicamente campos acordados por protocolo (datos/huella y control), con reglas de transformación, reordenamiento, reintentos, descartes y relaciones 1:N documentadas. Referenciar ambas evidencias por archivo y líneas.
- `NOT_OBSERVABLE` cuando falta evidencia suficiente de publicación o recepción. `ambiguous` describe un emparejamiento no resoluble aun con mensajes de ambos lados. `MATCH`, `LOSS` y `DIVERGENCE` requieren evidencia comparable; la falta de un log no es pérdida de transacción. La obligatoriedad para aceptación depende del test y es independiente del resultado funcional.
- La ingestión no emite estados de correlación: todavía no reconoce publicaciones, recepciones ni campos semánticos. Las cinco fichas de desarrollo conservan su observabilidad anotada de la semana 1.

## Organización final

La estructura existente ya separa anotaciones, fuentes y conjuntos de pruebas. No se movieron carpetas ni se duplicaron los conjuntos. Se añadió únicamente `semana_2/`, con implementación, pruebas, contrato, esquemas y un ejemplo reproducible de captura. Quedan fuera el parser UVM, las consultas, la clasificación funcional y el correlacionador.
