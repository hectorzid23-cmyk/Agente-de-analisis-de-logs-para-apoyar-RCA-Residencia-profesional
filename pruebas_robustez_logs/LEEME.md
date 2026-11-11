# Logs para pruebas de robustez de ingestión

Fecha de revisión: 4 de noviembre de 2026.

## Hallazgo principal

Se confirmó un caso publicado sin salto de línea final: `originales_publicados/axi4_pass_original.log`. Se recuperó en base64 y se verificó el SHA del objeto Git, por lo que esta condición se observó en los bytes del archivo publicado, sin normalización del conector ni del editor. No tener salto de línea final no acredita truncamiento.

Fuentes nativas recuperadas:

- AXI4 PASS: https://github.com/Tharunreddym/axi4-verification/blob/6e38818007a1e2d4570746000a8e25932200b033/logs/burst_read_test_seed1_questa.log
- AXI4 FAIL: https://github.com/Tharunreddym/axi4-verification/blob/6e38818007a1e2d4570746000a8e25932200b033/logs/burst_read_test_seed1_questa_FAIL.log
- RISC-V antes de corrección: https://github.com/isbogdanov/riscv-core-dv-uvm/blob/0b9a43f9e0f7e79a18e2dd28070f654da325b6a4/bug_story/before_fix.log
- RISC-V después de corrección: https://github.com/isbogdanov/riscv-core-dv-uvm/blob/0b9a43f9e0f7e79a18e2dd28070f654da325b6a4/bug_story/after_fix.log

Los cuatro archivos recuperados son ASCII (también válidos como UTF-8). Eso no prueba que sus productores utilizaran una codificación concreta. No se encontraron muestras de simulación con truncamiento o codificación alternativa acreditados en el material revisado. Por ello las pruebas específicas se construyen como derivados explícitos.

Verilator aporta una salida esperada vacía, `test_regress/t/t_sys_readmem_assoc__empty.mem.out`, y una salida esperada de assertions, `t_assert_ctl_immediate.out`. Se preservan los bytes y el driver de referencia. La primera representa un archivo de datos de memoria esperado vacío dentro de una prueba; NO es el transcript de una simulación ni prueba de PASS. La segunda es una salida golden, no un log íntegro de una corrida nueva.

## Cobertura de las fuentes consideradas

| Fuente | Resultado de la búsqueda |
| --- | --- |
| Tharunreddym/axi4-verification | Cinco .log versionados; se recuperaron PASS y FAIL con bytes verificables. PASS sin salto final. |
| isbogdanov/riscv-core-dv-uvm | Diez .log en el árbol: mezclan UVM, simulación RTL, trazas Spike y verificación formal. Se recuperaron before_fix/after_fix; también se reutiliza la copia UVM local previamente obtenida. |
| chipsalliance/sv-tests | Sin .log/transcript en el árbol fuente. Se verificó el directorio de resultados HTML en chipsalliance/sv-tests-results; para las variantes se usa la extracción scoreboard ya preservada localmente. |
| openhwfoundation/cvfpu-uvm | Sin .log/transcript versionados en el árbol completo inspeccionado. Fuente potencial para generar nuevas corridas, no para obtener estos casos ya publicados. |
| openhwfoundation/core-v-verif | Sin .log/transcript versionados en el árbol completo inspeccionado; no se expandieron submódulos ni artefactos de CI. |
| openhwfoundation/cv32e40p | Sin .log/transcript versionados en el árbol inspeccionado. |
| lowRISC/ibex | Sin .log/transcript versionados en el árbol inspeccionado. Los reportes con extractos revisados anteriormente no se etiquetan como logs completos. |
| lowRISC/opentitan | Se revisaron subárboles util, hw/dv/tools y hw/dv/sv; sin candidatos. El resultado no cubre exhaustivamente todo el monorepo. |
| pulp-platform/common_verification | Sin .log/transcript versionados; biblioteca de componentes. |
| unihd-cag/openhmc | Sin .log/transcript versionados en el árbol inspeccionado. |
| NVlabs/verilog-eval | Sin .log/transcript versionados en el árbol inspeccionado. |
| ben-marshall/awesome-open-hardware-verification | Catálogo sin .log/transcript versionados. |
| verilator/verilator | Se revisó el subárbol test_regress/t completo y se localizaron salidas esperadas .out, incluidas vacías; se conservan por separado de los logs de simulación. |
| OpenCores LPFFIR y ethmac | Acceso no acreditado a archivos completos en esta revisión; la recuperación de sim.log de LPFFIR falló. No se inventan variantes atribuidas a estos proyectos. |
| Dataset RTL Synthetic o3 de Hugging Face | La revisión previa identifica Parquet, no un conjunto de archivos .log. El acceso al árbol actual falló. No se incorporó al paquete. |

`busqueda_fuentes.json` registra revisiones y rutas. Los resultados negativos son búsquedas acotadas en contenido versionado, no una afirmación sobre toda la historia, releases o artefactos de cada proyecto.

## Casos preparados

Se preparan 43 archivos: 13 variantes de cada una de tres bases y cuatro casos especiales. Las bases son AXI4 FAIL, scoreboard UVM de sv-tests y el log UVM largo de RISC-V. Los originales de semana_1 y las etiquetas existentes no se modifican.

| Caso | Qué permite verificar |
| --- | --- |
| control_utf8_lf | Lectura de referencia, con LF y un salto final normalizados explícitamente. |
| sin_salto_final | Procesar la última línea aunque no termine en LF; no atribuir truncamiento sólo por eso. |
| control_utf8_crlf | Separación correcta de líneas de estilo Windows, sin conservar CR dentro del mensaje. |
| utf8_acentos / utf8_bom | Caracteres multibyte, tratamiento de BOM y referencias de líneas/bytes. |
| utf16le_bom / utf16be_bom | Lectura de UTF-16 con orden de bytes indicado por BOM. |
| windows1252 | Lectura explícita de Windows-1252, con caracteres que distinguen sus bytes de UTF-8. |
| truncado_antes_resumen | Recuperar eventos anteriores sin inventar los conteos finales ausentes. |
| truncado_mitad_mensaje | Señalar una última línea incompleta y no completar su contenido. |
| truncado_despues_evento | Mantener un evento completo previo al corte; se prefiere el primer UVM_ERROR si existe. |
| utf8_byte_invalido | Error de decodificación al exigir UTF-8; no perder bytes silenciosamente. |
| utf16le_truncado_un_byte | Unidad UTF-16 incompleta por corte de bytes. |
| especiales/vacio | Cero bytes: sin evidencia de ejecución; resultado funcional INDETERMINADO. |
| especiales/solo_bom_utf8 | Tres bytes, pero texto vacío tras decodificar; distinguirlo de cero bytes. |
| especiales/solo_espacios | Texto presente sin eventos. |
| especiales/utf8_truncado_multibyte | Corte dentro de los bytes de ñ; caso totalmente sintético. |

Las cinco variantes de codificación válida de cada base incluyen el MISMO comentario sintético inicial con acentos y €. Esto permite comprobar equivalencia de texto tras decodificar; el comentario no se atribuye al simulador ni es un mensaje UVM real. Los grupos equivalentes están identificados en el manifiesto. Las comparaciones con las bases sin el comentario deben contemplar esa línea adicional.

UTF-8 inválido es inválido bajo una política UTF-8 explícita; una codificación como Windows-1252 puede asignar caracteres a esos mismos bytes. No se prescribe detección automática infalible. Si el lector usa fallback, debe registrar codificación, motivo y posibles sustituciones. No usar errors=ignore como éxito silencioso. Si el sistema sólo admite UTF-8, las demás codificaciones deben producir un error explícito de formato no admitido: no es necesario soportarlas todas.

## Reglas de interpretación

- Separar estado de lectura, integridad del archivo y resultado funcional de la prueba.
- Vacío o sin eventos no demuestra PASS ni un defecto del DUT.
- Un fallo completo previo a un corte conserva su evidencia de FAIL. No convertir todos los truncados automáticamente en INDETERMINADO.
- Si falta cierre y no hay fallo inequívoco, aplicar la política local de INDETERMINADO; no deducir PASS de la ausencia de ERROR/FATAL.
- Los archivos sin salto final pueden ser completos; la última línea debe procesarse.
- Los recortes y caracteres inválidos de este paquete fueron introducidos localmente, no encontrados en esas corridas originales.
- Estas pruebas son de ingestión y manejo de evidencia. No evalúan por sí mismas causas raíz ni correlación monitor → scoreboard.

## Organización y verificación

- `originales_publicados/`: bytes descargados sin cambios, incluidas salidas de referencia no UVM.
- `bases_locales/`: copias de los logs locales previos con su procedencia.
- `casos/`: variantes derivadas y casos sintéticos; nunca confundirlos con nuevas corridas.
- `manifest.json`: fuente, transformación, tamaño, hash, codificación conocida y expectativas estructurales por archivo.
- `verificacion.json`: resultado de comprobar bytes, equivalencia de texto, fallos esperados de decodificación y conservación dentro del ZIP. No es una ejecución del futuro parser.
- `descargas_base64.json`: contenido de la adquisición y metadatos Git para auditoría.
- `casos_robustez_logs.zip`: paquete completo que preserva los archivos vacíos y sus bytes; no abrir/guardar los casos con un editor que normalice codificación o saltos antes de probarlos.

Los conteos deben compararse dentro del mismo grupo de contenido. Un truncamiento modifica deliberadamente el texto y puede reducir eventos; no se exige que tenga los mismos totales que la corrida completa. El paquete no asigna causas raíz ni reemplaza las anotaciones manuales existentes.
