Semana 1 — Etiquetado manual de cinco casos UVM
Guía de trabajo con evidencia verificable · Actualización del 30 de octubre de 2026 · Versión 1.2

1. Objetivo y límites
Etiquetar manualmente significa leer una corrida, seleccionar hechos y registrar dónde aparecen, qué referencias contienen y qué relaciones se pueden sostener. El resultado sirve como referencia humana para desarrollar y comprobar después el agente. No equivale a conocer la causa raíz.
Esta guía desarrolla la tarea 4 de la semana 1. Incluye un procedimiento y cinco fichas de ejemplo basadas en archivos realmente consultados, sin ejecutar simulaciones ni implementar parsers, agrupadores o comparación automática. Las anotaciones son propuestas revisadas contra el texto; queda pendiente una revisión humana independiente.
Un caso será una corrida completa con uno o varios eventos de interés. Usamos cinco corridas, no cinco líneas de un mismo archivo. Los dos casos AXI4 pueden compartir un identificador de incidente candidato, pero mantienen sus identidades de corrida.
Se siguen las políticas LOCAL-PF-1.1 y LOCAL-REF-1.1 del archivo contexto_semana_1.txt: distinguir resultado funcional y ejecución; conservar referencias literales; no inventar señales; no confundir relaciones con causas.

2. Material y procedencia
Las fuentes se seleccionaron tomando como referencia “Conjunto de datos”. Se conservan las dos muestras sv-tests obtenidas anteriormente y tres archivos de AXI4/RISC-V consultados ahora. Todas son salidas públicas publicadas; ninguna fue generada localmente para esta guía.
C01: fuentes_logs_revision/muestras/uvm_test_run_test.log (167 líneas).
C02: fuentes_logs_revision/muestras/uvm_scoreboard_monitor_agent_env.log (248 líneas).
C03: semana_1/fuentes/burst_read_test_seed1_questa_FAIL.log (200 líneas de contenido en la copia local; se omitió una línea vacía final sin alterar las coordenadas citadas).
C04: semana_1/fuentes/burst_read_test_seed1_questa.log (196 líneas).
C05: semana_1/fuentes/riscv_uvm_run.log (2699 líneas de contenido; la separación final de línea no es un evento).
Las líneas se numeran desde 1, contando vacías y prefijos #. En sv-tests corresponden al texto extraído del HTML, no a líneas del HTML ni al stdout original.
Fuentes C01/C02:
https://github.com/chipsalliance/sv-tests-results/blob/gh-pages/logs/Verilator/testbenches/uvm_test_run_test.sv.log.html
https://github.com/chipsalliance/sv-tests-results/blob/gh-pages/logs/Verilator/testbenches/uvm_scoreboard_monitor_agent_env.sv.log.html
Sus versiones y SHA-256 están en procedencia.json y verificacion.json locales.
Fuente C03:
https://github.com/Tharunreddym/axi4-verification/blob/main/logs/burst_read_test_seed1_questa_FAIL.log
SHA del objeto Git consultado: 27bdb9889d7b93ffa5c96b1e0b359cc5f82bd76a.
Fuente C04:
https://github.com/Tharunreddym/axi4-verification/blob/main/logs/burst_read_test_seed1_questa.log
SHA del objeto Git: 0a43a32b68a4b10f3f08b3c02c48f962d750471b.
Fuente C05:
https://github.com/isbogdanov/riscv-core-dv-uvm/blob/main/sample_logs/uvm_classic/uvm_run.log
SHA del objeto Git: a37d3de0f48042554824d38efe10e4cc253818d9.
Los enlaces de rama pueden cambiar: conservar la copia, el SHA del objeto y un hash local. Un SHA de blob identifica contenido, no la revisión exacta de RTL que se ejecutó.

3. Procedimiento paso a paso
Paso 1. Fijar la instantánea.
Abrir una copia de sólo consulta del log completo, conservar el original y registrar origen, fecha de consulta, hash y método de extracción. No quitar líneas para facilitar la lectura. Si se prepara una vista limpia, mantener una correspondencia con las líneas originales. No usar números de línea de una versión distinta.

Paso 2. Delimitar la corrida.
Separar compilación, elaboración y simulación. Buscar inicio, test, seed, versiones y cierre. Si un archivo concatena varias ejecuciones, tratarlas por separado. Una ruta a un archivo de memoria o el nombre del archivo de log no son prueba de seed.
Usar identificadores manuales R01–R05 y C01–C05; los event_id de ejemplo E01, E02, etc. sólo son únicos dentro de cada caso. No fijan todavía el contrato de identificadores de semana 2.

Paso 3. Definir qué se quiere comprobar.
Anotar la pregunta concreta: ¿se ejecutó el test?, ¿coincidieron los datos?, ¿el warning pertenece al entorno?, ¿varios mensajes describen una misma discrepancia? Registrar el criterio de resultado antes de elegir etiquetas para evitar adaptar la regla al resultado deseado.

Paso 4. Recorrer el log y delimitar eventos.
Un evento puede ocupar varias líneas: encabezado UVM más cuerpo hasta el siguiente encabezado o límite de sección. Una fila de resumen es evidencia agregada, no un UVM_ERROR individual. Un warning de Questa puede continuar en líneas que no repiten su severidad.
Conservar un fragmento breve literal y el intervalo completo del evento. Las citas cortas de las fichas siguientes son claves para localizarlo; el archivo completo conserva el contexto.

Paso 5. Llenar una ficha por evento.
Registrar: caso/corrida, event_id, etapa, tipo, severidad original, message_id, mensaje o fragmento, log_file y líneas inicial/final, tiempo literal y unidad si está demostrada, component_path, source_file/source_line y otras referencias.
Registrar test y seed como metadatos con su evidencia. Usar no_observado o no_determinado cuando falten; no rellenar con estimaciones.
Separar hechos observados de interpretación. “El scoreboard imprimió un mismatch” es un hecho; “el driver incumplió el protocolo” requiere evidencia adicional.

Paso 6. Revisar referencias.
Distinguir archivo de log y línea física de archivo fuente y línea de código. En C03, línea 147 del log apunta a testbench.sv(1342). La jerarquía uvm_test_top.env.scoreboard es un componente UVM; addr es una dirección de transacción; ninguna debe convertirse en signal_path.
Conservar el emisor como lugar del reporte, sin concluir que ahí está el defecto. No completar rutas cortas ni cambiar mayúsculas, índices o identificadores escapados.

Paso 7. Proponer relaciones explícitas.
Cada relación registra miembros, tipo, evidencia, calificación y límite. Usar “observada” para una coincidencia textual verificable; “candidata” para una asociación plausible; “no determinada” para causalidad sin prueba. Si no hay evidencia, registrar sin relación demostrable.
Mismo tiempo o ID no basta para una causa común. Un resumen puede referirse a eventos previos sin ser otro defecto. Relaciones entre corridas requieren revisar test, seed, configuración y revisiones; documentar lo desconocido.

Paso 8. Aplicar resultado local.
Primero buscar fallos inequívocos no esperados; después verificar cierre y evidencia positiva de éxito. Si no basta para PASS ni FAIL, INDETERMINADO. Mantener estado de ejecución aparte. No resolver todo con una búsqueda de la palabra ERROR ni con el nombre FAIL del archivo.
No convertir warnings en errores sin regla del test. Cero errores UVM no prueba que un programa haya completado correctamente su objetivo.

Paso 9. Revisar consistencia.
Contrastar eventos individuales y resumen UVM sin sumarlos dos veces. Contar por separado mensajes y beats. Revisar que cada relación cite líneas y que cada señal tenga origen. Para tiempos sin unidad en el encabezado, guardar el literal; no asumir que @ 1025000 significa ns.
Cuando INFO difiera por el mensaje que anuncia el propio resumen, registrar la regla y la diferencia; no modificar el original para hacer coincidir cuentas.

Paso 10. Revisión independiente y cierre.
Otra persona debe poder abrir la misma instantánea y reproducir las etiquetas. Registrar autor, fecha, versión de política, revisor y estado: propuesto/revisado. Resolver desacuerdos con evidencia y conservar historial.
Las cinco fichas son un conjunto de desarrollo pequeño; no son una evaluación independiente ni autorizan porcentajes de precisión general.

4. Caso C01 — Inicio y éxito explícito de simple_test
Archivo: uvm_test_run_test.log. Corrida manual R01; origen sv-tests/Verilator. Test simple_test observado en línea 144; seed no observado.
Seleccionar E01 en L143: warning NO_DPI_USED. Referencia de emisión: third_party/tests/uvm/src/base/uvm_root.svh:549. Tiempo literal 0, unidad no explícita en ese encabezado.
Seleccionar E02 en L144: inicio RNTST de simple_test; componente reporter.
Seleccionar E03 en L146: NO_VISIT_CHECK; uvm_traversal.svh:314. Mantener también L145 como contexto: el chequeo de nombres requiere DPI.
Seleccionar E04 en L147: resultado SUCCESS de llamada a simple_test, componente uvm_test_top, tests/testbenches/uvm_test_run_test.sv:39.
Registrar agregado A01 en L149–162: resumen; ERROR=0 en L154 y FATAL=0 en L155. Cierre L164–167.
Resultado funcional: PASS por el marcador SUCCESS y cierre; ejecución COMPLETA. No acredita correlación de transporte; si se exige para aceptación, ésta es INDETERMINADA. No certificar un DUT industrial.
Relación: E01 y E03 tienen asociación de entorno respaldada por los mensajes sobre DPI; no son dos defectos del circuito. E02 y E04 son hitos del mismo test.
signal_path: no observado. uvm_test_top es componente UVM.
Cómo anotarlo: copiar cada fragmento, comprobar ambas coordenadas, justificar PASS con L144, L147, L154–155 y L164–166. Si se omite el cierre, la ficha queda incompleta.

5. Caso C02 — Estímulo y comparación coincidente
Archivo: uvm_scoreboard_monitor_agent_env.log. Corrida R02. El marcador L224 dice “Running test ...” y no proporciona nombre concreto; no inventarlo a partir del nombre del archivo.
E01 L223: NO_DPI_USED; E02 L226: NO_VISIT_CHECK. E03 L227: escritura del valor 2 a la interfaz de entrada, componente env, archivo tests/testbenches/uvm_scoreboard_monitor_agent_env.sv:184, tiempo literal 0.
E04 L228: comparación coincidente de 2 y 2, componente env.comp, mismo archivo fuente:144, tiempo literal 15.
Agregado A01 L230–243: ERROR=0 en L235 y FATAL=0 en L236. Cierre L245–248; el cierre informa 15 ps, pero no atribuir automáticamente esa unidad a cada encabezado sin validar su formato.
Resultado funcional vigente: INDETERMINADO. Estímulo y comparación coincidente son hechos, pero falta marcador explícito de éxito global o excepción documentada; ejecución COMPLETA. Correlación monitor → scoreboard: NOT_OBSERVABLE.
Relación E03–E04: secuencia candidata de estímulo/comprobación, apoyada por el orden y el valor. No hay transaction_id explícito ni ruta de señal que pruebe conectividad. No afirmar que todo el entorno está verificado.
signal_path: no observado. env.comp es componente UVM. La expresión “input interface” no identifica una señal.
Cómo anotarlo: escribir por separado hechos y asociación; guardar que el nombre del test y el seed no se observaron. No contar el resumen como nuevos eventos de severidad.

6. Caso C03 — Fallo AXI4 con varios mensajes
Archivo: burst_read_test_seed1_questa_FAIL.log. Corrida R03. Test burst_read_test y seed 1 están explícitos en los comandos iniciales; UVM 1.2 y Questa 2025.2 figuran en el log. No confiar únicamente en el nombre FAIL.
E01 L147: primer mismatch, dirección 0x00000100, byte 0, esperado 0xb5 y observado 0xf1. UVM_ERROR; componente uvm_test_top.env.scoreboard; message_id axi4_scoreboard; testbench.sv:1342; tiempo literal 1025000.
E02–E04 L148–150: bytes 1, 2 y 3 en direcciones 0x101, 0x102 y 0x103; mismo tiempo, componente y origen.
E05 L160–168: cuerpo del resumen de scoreboard, con encabezado en L160. Registrar 29 matching beats (L166) y 1 mismatched beat (L167). Es información agregada.
E06 L169: UVM_ERROR final de un beat incorrecto; testbench.sv:1375; tiempo literal 1235000.
E07 L170–171: evento UVM_INFO cuyo cuerpo declara TEST FAILED. Aunque su severidad sea INFO, su contenido respalda el resultado funcional.
Agregado A01 L173–187: UVM_ERROR=5 en L178, FATAL=0 en L179. Cierre L189–191. Resumen de herramienta vsim con Errors=0 en L198.
Resultado: FAIL; ejecución COMPLETA. Hay cinco mensajes UVM_ERROR y un beat incorrecto declarado, no cinco causas raíz comprobadas. Los errores cero de vsim pertenecen a otra categoría.
Relación candidata G01: E01–E04 comparten tiempo, scoreboard, origen y bytes contiguos; E06 y el agregado del scoreboard respaldan que se reporta un beat incorrecto. No hay identificador explícito que vincule cada byte a un beat concreto: conservar ese límite.
Causa raíz: no determinada. Un problema de ensamblado de datos, estímulo, referencia o lógica es una hipótesis a investigar, no una etiqueta correcta ya demostrada.
signal_path: no observado. addr y byte son campos, no señales. El lugar de reporte testbench.sv:1342 no identifica automáticamente la lógica defectuosa.
Cómo anotarlo: hacer una fila por UVM_ERROR, otra por el evento de resultado multilínea y un registro aparte para cada resumen. Relacionar sin duplicar conteos; conservar esta corrida como incidente AXI4 candidato I01.

7. Caso C04 — Corrida AXI4 exitosa asociable
Archivo: burst_read_test_seed1_questa.log. Corrida R04. Test burst_read_test y seed 1 explícitos; no sustituir R03 con esta corrida.
E01 L156–164: resumen de scoreboard, 30 beats coincidentes y cero incorrectos.
E02 L165: mensaje de conformidad de los datos leídos con shadow memory; testbench.sv:1388; componente uvm_test_top.env.scoreboard.
E03 L166–167: evento de resultado TEST PASSED; testbench.sv:2028; tiempo literal 1035000.
Agregado A01 L169–183: ERROR=0 (L174) y FATAL=0 (L175). Cierre L185–196; una advertencia de vopt aparece en el resumen de herramienta, separada de UVM_WARNING=0.
Resultado funcional: PASS para esa prueba; ejecución COMPLETA. La aceptación es INDETERMINADA si se exige correlación monitor → scoreboard no observable. Cobertura registrada no implica que se haya cumplido una meta no acordada.
Relación entre R03 y R04: mismo test y seed respaldan un par candidato I01; el scoreboard cambia de un beat incorrecto a cero, y el resultado declarado cambia de FAILED a PASSED. Esto es una observación manual del par, no implementación de compare_runs.
No etiquetar “corrección causal demostrada”: las líneas de código de los mensajes cambian entre corridas, y faltan commits/configuraciones completos que permitan atribuir el efecto a una modificación específica.
Cómo anotarlo: mantener fichas separadas; registrar el vínculo candidato y la evidencia de comparabilidad y sus vacíos. signal_path no observado.

8. Caso C05 — Warning multilínea y límites del resultado
Archivo: riscv_uvm_run.log. Corrida R05. Test riscv_base_test en L59. No interpretar el sufijo 17216 del archivo de programa como seed demostrado.
E01 L74: carga de memoria por el predictor desde out_2025-06-29/asm_test/riscv_arithmetic_basic_test_17216.o.mem.
E02 L75–77: warning del simulador vsim-PLI-8707 por dirección ausente en la línea 1 del archivo de memoria; continuación en L76 referencia uvm_classic/predictors/cpu_flow_predictor.sv:31. L77 informa tiempo 0 ps. Conservar el evento completo.
E03a L78 y E03b L79: dos eventos distintos, inicio de carga y registro de 810 instrucciones; relacionarlos por la secuencia y el archivo, sin fusionar sus encabezados. El texto con @@memory_seq conserva una referencia de secuencia, sin convertirla en jerarquía RTL.
E04a L2651: aviso de ECALL sin encabezado UVM. E04b L2652: evento UVM relacionado; el mensaje en L2652 señala PC 0x80000a08 y detención de comparación, source_file uvm_classic/subscribers/cpu_commit_scoreboard.sv:101.
Agregado A01 L2674–2694: UVM_WARNING=0, ERROR=0 y FATAL=0 en L2678–2680. Cierre L2696–2699, tiempo final 6545 ns y Warnings=1 del simulador.
Resultado local propuesto: INDETERMINADO para éxito funcional/arquitectónico; ejecución COMPLETA. El log respalda llegada a ECALL y cero errores UVM, pero aquí no se ha validado que cualquier ECALL implique aprobación del programa. Si se documenta ese criterio con fuentes del test y comprobaciones suficientes, revisar la etiqueta de forma trazable.
Relación E01–E02–E03a–E03b: carga del mismo archivo de memoria, respaldada por ruta y contexto; no demostrar que el warning afectó el resultado. E04a/E04b tienen relación de finalización con los mensajes posteriores, no prueba de que el warning lo causó.
El warning del simulador no contradice UVM_WARNING=0. PC es dato de ejecución; no etiquetarlo como ruta de señal.
Cómo anotarlo: no cortar la continuación L76; guardar ambas referencias (archivo de memoria y fuente del predictor). Mantener explícita la pregunta pendiente sobre el criterio de éxito.

9. Plantilla reutilizable y revisión final
Ficha de caso: case_id; run_id manual; origen y versión/hash; archivo local; test/seed con líneas; pregunta; criterio de resultado; resultado declarado; resultado local; estado de ejecución; limitaciones; autor/fecha/revisor/estado.
Ficha de evento: event_id; etapa; tipo; severidad original; message_id; intervalo inclusivo de líneas; fragmento; tiempo literal/unidad y evidencia de unidad; componente; archivo/línea fuente; otras referencias y su clase/origen; observación; interpretación separada.
Ficha de relación: relation_id; miembros; tipo; evidencia y líneas; observada/candidata/no determinada; alternativas; datos faltantes; causa raíz confirmada sí/no y sustento. No usar un porcentaje de confianza no calibrado.
Antes de cerrar, comprobar: cinco corridas distintas; evidencia para cada etiqueta; originales conservados; multilíneas completas; referencias de log y fuente separadas; ausencia de señales inventadas; resúmenes sin doble conteo; incertidumbres visibles; revisión pendiente claramente marcada.
Este material permite iniciar la anotación reproducible de desarrollo. Falta completar y revisar el inventario exhaustivo de eventos de cada corrida si se desea usarlo posteriormente como referencia de conteos o recuperación. Las fichas seleccionadas no representan una anotación exhaustiva del log RISC-V.
La guía permanecerá separada del archivo de contexto de semana 1 hasta que se solicite incorporarla.

10. Referencia de alcance
Ruta técnica vigente:
https://docs.google.com/document/d/11nr1JTTRA4npCvqcUrdVgrics5_8SSlhgF1YMALvUoI/edit
Conversaciones de contexto: “Conjunto de datos” y “Ruta técnica”.
Política pública definida por el estudiante: conservar procedencia y condiciones de cada fuente. Esta edición se entrega localmente en la carpeta del proyecto; el documento previo de Drive conserva su versión anterior.
11. Formato elegido: un archivo JSON por caso
JSON es el formato de almacenamiento de las fichas. Una ficha de caso contiene dentro sus eventos, agregados y relaciones; no se crea un archivo por evento. Se eligió porque representa listas y objetos anidados, conserva números y ausencias, permite revisión textual y Python puede leerlo con su biblioteca estándar. No se necesita una base de datos, Word, Excel ni una conexión a Drive para usar estas fichas.
La guía se entrega en Markdown (.md) para leerla cómodamente y también en JSON (.json) con su texto organizado por secciones. Las cinco fichas se entregan en JSON. Ambos formatos de la guía contienen el mismo contenido; no son fuentes independientes que deban editarse de manera divergente.
Esta estructura es una convención de anotación de semana 1, no la API del agente ni el esquema definitivo de ingestión de semana 2. Los R01–R05 son identificadores manuales y los E01, E03a, etc. son únicos dentro de su caso. La clave completa de un evento es (case_id, event_id).

12. Organización de archivos y referencias a los logs
Carpeta raíz: C:/Users/hecto/Downloads/proyecto_residencia/.
La entrega actual se organiza así:
semana_1/guia_etiquetado_actualizada.md — guía legible.
semana_1/guia_etiquetado_actualizada.json — la misma guía por secciones.
semana_1/etiquetas/C01_simple_test.json — 4 eventos seleccionados.
semana_1/etiquetas/C02_scoreboard.json — 4 eventos seleccionados.
semana_1/etiquetas/C03_axi4_fail.json — 7 eventos seleccionados.
semana_1/etiquetas/C04_axi4_pass.json — 3 eventos seleccionados.
semana_1/etiquetas/C05_riscv.json — 6 eventos seleccionados.
semana_1/verificacion_fichas.json — informe de integridad de la entrega.
Los logs originales permanecen en fuentes_logs_revision/muestras/ y semana_1/fuentes/. No se duplican dentro de cada ficha. fuente.log_file se interpreta desde el directorio etiquetas/, no desde donde se abra Python. Por eso C01 utiliza ../../fuentes_logs_revision/muestras/uvm_test_run_test.log y C03 utiliza ../fuentes/burst_read_test_seed1_questa_FAIL.log.
Conservar esta estructura completa al trasladar el proyecto. Si se mueve una ficha sola, su ruta relativa deja de apuntar correctamente. Un enlace público puede cambiar, pero el SHA-256 local permite comprobar la instantánea exacta a la que corresponden las líneas.
No modificar ni limpiar los logs etiquetados. Una modificación de bytes cambia el hash, incluso si sólo altera finales de línea. Si se necesita otra extracción, conservarla como otra instantánea y revisar sus referencias.

13. Estructura común de cada ficha y significado de los campos
annotation_version: versión de la convención de anotación (1.2). Cambiarla sólo si cambia la estructura o el significado de los campos; fecha identifica esta edición.
case_id y run_id_manual: identidad del caso y de su corrida. titulo y pregunta_del_caso indican el propósito.
politicas: reglas locales de resultado y referencias usadas. revision identifica autor y estado propuesto; revisor y fecha de revisión son null hasta que exista revisión independiente real.
fuente: ruta relativa, base de ruta, número de líneas, SHA-256 local, URL, SHA del objeto Git y método de obtención. En sv-tests el objeto Git es el HTML original; su SHA no es el hash del .log extraído. En AXI4/RISC-V identifica el archivo publicado, no la revisión ejecutada de RTL.
metadatos: test, seed, simulador y UVM, con líneas de respaldo. Un dato externo o inferido no se presenta como observado. En C02 no se conoce el nombre concreto del test; en C05 no se deduce la seed del nombre del programa.
resultado: clasificación local PASS/FAIL/INDETERMINADO, declaración del testbench, estado de ejecución, criterio, líneas de respaldo y causa raíz. Conservar la declaración y la interpretación local por separado.
cobertura_anotacion: declara el alcance parcial, si existe inventario exhaustivo, las categorías completas certificadas y si la ficha puede usarse para validar totales. Todas las fichas actuales tienen inventario_exhaustivo=false y habilitada_para_validar_totales=false.
eventos: lista de registros individuales seleccionados. Cada evento incluye ID, etapa, tipo, severidad y dominio, message_id, líneas inicial/final inclusivas, texto original, tiempo, componente emisor, archivo/línea fuente, estado de señal, otras referencias, campos observados, hecho e interpretación.
agregados: resúmenes UVM con cuentas declaradas y su texto. A01 no es un evento de error ni se suma a los eventos. Los resúmenes del scoreboard E05 de C03 y E01 de C04 sí son mensajes UVM_INFO individuales con un cuerpo de estadísticas: sus cifras de beats no son cantidades de UVM_ERROR.
relaciones: vínculos entre IDs del mismo caso, tipo, calificación candidata, evidencia, límite, alternativas y causalidad_demostrada=false. Un vínculo posible no certifica una causa.
vinculos_entre_casos: referencias C03/C04 con incidente candidato I01, test y seed compartidos, líneas de cada caso y limitaciones de comparabilidad. No constituye una comparación automática de corridas.
conteos_anotados: cantidad de registros seleccionados y desglose UVM sólo de esa selección. Se excluyen los agregados de UVM Report Summary. Un warning del simulador no pertenece al conteo UVM_WARNING. limitaciones enumera vacíos de evidencia y revisión.

Convenciones de ausencia y sintaxis:
- null es un valor ausente/no determinado, nunca cero ni la cadena "null". El campo estado o una nota precisa el motivo. signal_path=null con estado_signal_path=no_observado indica que no se observó una señal; una lista vacía de relaciones sólo indica que no se registró ninguna, no que se haya demostrado ausencia total de relaciones.
- Las líneas físicas se guardan como enteros desde 1, incluyendo vacías. Los arrays evidencia_lineas y lineas_log enumeran líneas concretas. Los arrays cierre_lineas contienen los dos extremos de un intervalo inclusivo. log_line_start/end delimitan el evento o agregado completo seleccionado; no se deben confundir con source_line.
- texto_original contiene exactamente las líneas seleccionadas, con prefijos # y espacios, unidas por saltos representados como \n dentro del JSON. No reformular ese campo; el hecho se escribe por separado.
- tiempo.valor_literal es texto para no alterar la representación. unidad=null no significa ns. C05 E02 conserva ps porque lo declara L77; los encabezados sin unidad permanecen sin resolver.
- Las direcciones y valores hexadecimales son cadenas; byte y cantidades son enteros. No cambiar mayúsculas o rutas para uniformar nombres. No copiar component_path, PC ni address a signal_path.
- JSON utiliza comillas dobles, true/false y null; no admite comentarios, comas finales ni claves duplicadas. Se guarda en UTF-8, con sangría de dos espacios, para conservar acentos y facilitar revisión. Una ruta Windows escrita directamente en JSON debe escapar sus barras invertidas; las rutas relativas entregadas usan /.

14. Procedimiento de almacenamiento, paso a paso
1) Elegir la corrida y confirmar el archivo original. Abrir el log con números de línea visibles y verificar su identidad mediante la ruta y SHA-256. No usar líneas copiadas de una página con otra numeración.
2) Crear o abrir el JSON del caso en un editor de texto, por ejemplo el editor que ya se utilice para el proyecto. Mantener una ficha por corrida; no pegar dos objetos JSON completos consecutivos en el mismo archivo.
3) Completar primero identidad, procedencia, pregunta y metadatos con evidencia. No inventar seed, test o revisión. Registrar las políticas aplicadas y el estado propuesto.
4) Por cada evento seleccionado, copiar su intervalo literal y completar tipo, severidad, tiempo, emisor y referencias. Añadir un objeto nuevo dentro de eventos, separado del anterior por una coma. Mantener un ID estable; no renumerar eventos anteriores para insertar uno omitido. Puede añadirse E08 o E03c y conservar el orden de lectura mediante las líneas.
5) Guardar los resúmenes UVM en agregados y sus cuentas en conteos_declarados. Completar los conteos de eventos seleccionados de forma separada. Aunque una cuenta coincida con el resumen, no atribuir exhaustividad sin revisar la categoría completa.
6) Registrar relaciones con IDs existentes y evidencia concreta; separar hechos e interpretación. Para AXI4 mantener C03 y C04 separados y registrar el vínculo candidato en ambos.
7) Aplicar la regla local de resultado y documentar el criterio. Completar limitaciones y cobertura_anotacion. En esta entrega se mantiene modo=seleccion_de_eventos y la validación de totales deshabilitada.
8) Guardar como .json real, en UTF-8, dentro de etiquetas/. Comprobar que el editor no añadió .txt al nombre. Abrir de nuevo y comprobar acentos, comillas y estructura. No guardar la ficha sobre el .log.
9) Validar que el JSON abre, que las rutas resuelven, que el hash coincide, que cada intervalo reproduce texto_original y que todos los IDs de relaciones existen. El informe verificacion_fichas.json registra esas comprobaciones para esta entrega; no certifica causalidad ni exhaustividad. Un JSON sintácticamente válido puede contener una interpretación equivocada y requiere lectura humana.
10) Conservar una copia de la revisión previa antes de cambios importantes, fuera de la carpeta activa o con un sufijo claro de versión; evitar que se tome como otro caso. Registrar fecha y motivo del cambio. Revisor independiente y fecha_revision sólo se completan cuando esa revisión ocurra.
Los auxiliares preparar_fichas.py y actualizar_guia_local.py materializan esta entrega desde selecciones explícitas. No son herramientas de ingestión del agente. No volver a ejecutarlos después de editar manualmente las fichas o la guía sin respaldar los cambios: regeneran los archivos y podrían sustituir el trabajo posterior.

15. Conteos: selección, total declarado y referencia exhaustiva
Estos tres conceptos se mantienen separados:
a) Conteo anotado: mensajes presentes en eventos de esta ficha, calculable desde esa selección.
b) Total declarado: lo que imprime UVM Report Summary; se conserva como evidencia del log, no como prueba independiente de extracción exhaustiva.
c) Referencia exhaustiva: inventario revisado de todos los mensajes de una categoría y etapa, sobre toda la corrida, con sus líneas o confirmación documentada de ausencia.
Ejemplo C03: hay cinco UVM_ERROR seleccionados (E01–E04 y E06); A01 declara cinco y el scoreboard declara un beat incorrecto. No sumar 5+5 ni interpretar cinco causas raíz. Esta coincidencia permite una comprobación preliminar, pero la ficha permanece parcial para otras categorías y sin certificación de exhaustividad independiente.
Ejemplo C01: eventos incluye dos UVM_WARNING y dos UVM_INFO, mientras A01 declara cuatro INFO. Esa diferencia no indica que la ficha esté mal: seleccionó sólo algunos INFO. No usar el total de la lista como total de la corrida.
Ejemplo C04: que no haya UVM_ERROR en la lista no demuestra por sí solo ausencia global. Un resultado cero necesita revisar toda la categoría y el intervalo; no se valida sólo con una lista vacía.
Para preparar una categoría para conteos futuros: definir severidad/tipo, etapa y rango completo; recorrer todo el log; añadir cada mensaje faltante con un ID y sus líneas; distinguir eventos multilínea de sus continuaciones; excluir filas agregadas; contrastar el resumen; resolver diferencias y obtener revisión independiente. Sólo después registrar en categorias_completas_certificadas el filtro, intervalo revisado, total de referencia, IDs y autor/fecha de revisión, y habilitar validación únicamente para ese filtro. El permiso nunca se interpreta como validación de todas las categorías. El inventario global puede seguir siendo parcial.
No hace falta etiquetar todos los INFO para validar sólo UVM_ERROR. Pero las afirmaciones sobre ausencia de otro tipo de fallo o sobre resultado funcional pueden requerir evidencia adicional fuera de ese filtro. Esta entrega no implementa aún evaluación del agente.

16. Estado de las cinco fichas entregadas
C01: cuatro eventos; PASS acotado a simple_test, dos relaciones candidatas y un resumen UVM separado.
C02: cuatro eventos; INDETERMINADO funcional por falta de marcador explícito de éxito global o excepción validada; relación candidata de estímulo/comparación que no acredita transporte monitor → scoreboard; test y seed no observados.
C03: siete eventos, incluidos cinco UVM_ERROR; FAIL, agrupamiento candidato de discrepancias, sin causa raíz demostrada.
C04: tres eventos; PASS de AXI4, vínculo candidato con C03, sin prueba de qué cambio produjo la mejora.
C05: seis eventos; warning de simulador completo en tres líneas, dos reportes ECALL separados, resultado funcional INDETERMINADO y ejecución COMPLETA.
Los 24 registros de eventos no constituyen 24 fallos ni todos los eventos de las cinco corridas. Cada ficha tiene además A01 como registro agregado; no se incluye en esos 24.
Las fichas están elaboradas y verificadas contra sus fragmentos y fuentes, en estado propuesto y pendientes de revisión humana independiente. No se declara cerrada toda la semana 1 ni se realizan actividades de semanas posteriores a la segunda.
La guía local actualizada es la referencia para los JSON entregados. El respaldo anterior y el documento anterior de Google Drive se conservan como antecedentes; el contenido de esta tarea sigue separado de contexto_semana_1.txt, conforme a la decisión previa.


17. Adecuación vigente: correlación y prioridad de fuentes (versión 1.2)
Esta sección rige la interpretación actual de las fichas. Conservamos los 24 eventos seleccionados y sus originales. Se actualiza documentación y anotación de semana 1, sin implementar el correlacionador de semana 5.
Pregunta RCA incorporada: «¿Qué transacciones publicadas por el monitor llegaron al scoreboard, cuáles faltan o difieren y qué evidencia permite comprobarlo?». Forma parte de la segunda pregunta de relaciones, no sustituye la investigación causal ni agrega una cuarta pregunta obligatoria.
La observabilidad se registra en observabilidad_monitor_scoreboard. Las cinco muestras quedan NOT_OBSERVABLE para transporte: los eventos seleccionados no proporcionan pares identificados de publicación en monitor y recepción/consumo correspondiente en scoreboard. Su existencia nominal en un testbench no basta. Una comparación del scoreboard o un resumen no demuestra ese recorrido. No declarar LOSS ni MATCH por ausencia de mensajes, ni confundir conteos iguales con contenido íntegro.
Los campos monitor_publicaciones_identificadas, scoreboard_recepciones_por_transaccion_identificadas y pares_confirmados son listas vacías de evidencia identificada, no prueba de ausencia de transacciones. cantidad_pares_confirmados=null indica que el total no puede establecerse. Los event_id de evidencia contextual del scoreboard no se consideran recepciones comprobadas.
Separar resultado.funcional de aceptación cuando la correlación es obligatoria. resultado.local se mantiene como alias del funcional para continuidad; no se debe leer como aceptación integral. No se ha documentado para estas muestras una exigencia original de correlación, por lo que obligatoria_para_aceptacion_del_test=no_documentado. El campo aceptacion_con_correlacion_obligatoria expresa la decisión condicional si se exige: C03 sigue FAIL; las otras quedan INDETERMINADO. No asignar silenciosamente una obligación histórica nueva al test.
Política LOCAL-PF-1.1: FAIL inequívoco no esperado prevalece aun con log incompleto. PASS funcional requiere cierre, marcador explícito de éxito, ausencia de fallo y de contradicciones sin resolver. Una excepción de prueba mínima necesita criterio documentado y validado, no inferido de un match aislado. Falta de cierre/resultado, truncamiento o evidencia irresoluble producen INDETERMINADO si no hay FAIL concluyente. Si el transporte es obligatorio, correlación no observable o ambigua impide aceptación PASS; una pérdida/alteración sólo produce FAIL cuando está confirmada con expectativas y observabilidad suficientes. Warnings se conservan como pistas, nunca disparadores automáticos de FAIL. Pruebas negativas requieren expectativas documentadas; no ocultar sus errores.
C01 mantiene PASS funcional por SUCCESS y cierre; C02 cambia a INDETERMINADO por falta de marcador explícito de éxito global o excepción validada. C03 mantiene FAIL. C04 conserva PASS funcional explícito, con aceptación INDETERMINADO si se exige correlación. C05 conserva INDETERMINADO funcional. Todos conservan ejecución COMPLETA según la evidencia de cierre.
Metadatos: identificacion_test guarda por separado todas las apariciones observadas de +UVM_TESTNAME y RNTST, con línea y texto original. test_name sólo se consolida si hay un nombre único; cualquier discrepancia mantiene las dos evidencias y no se resuelve eligiendo silenciosamente una. El marcador no es una severidad ni criterio de fallo. En C02 RNTST no proporciona nombre concreto. Se mantiene seed ausente cuando no está observado.
Warnings: cada aviso seleccionado incluye pista_rca con contexto cercano, relevancia y límite de causalidad. La selección de eventos a cinco líneas ayuda a navegar y no certifica relaciones. Los avisos de DPI siguen siendo de entorno. El warning del simulador en C05 permanece separado de UVM_WARNING; no cambiar su severidad original.
Nomenclatura LOCAL-REF-1.1: además de señales/componentes, distinguir interfaz, canal, sentido, transaction_id, beat_id, ocurrencia y segmento de reset/flush. Usar direccion_memoria para dirección de memoria, evitando confundirla con sentido de flujo. Conservar el nombre original TID como dato de origen y no asumir que es único durante toda la corrida. Comparar campos definidos por protocolo y transformaciones esperadas; no exigir igualdad textual de mensajes. Mantener ambiguo un emparejamiento sin clave suficiente.
Contrato manual mínimo de correlación pendiente: identidad de corrida, test y seed cuando existan; interfaz/canal/sentido; ID y ocurrencia/segmento de reset, y beat si aplica; datos/control comparables; evento/líneas de ambos extremos y regla aplicada. Acordar reordenamiento, reintentos, duplicados, relaciones 1:N, reset y flush antes de concluir pérdidas. Estos campos se proponen para las próximas muestras; no se rellenan con valores inventados en las actuales.
Prioridad de adquisición: primero CVFPU-UVM, después OpenTitan UART; Ibex y CORE-V-VERIF quedan para ampliación posterior. Conservar sv-tests, AXI4 y RISC-V para extracción, referencias y anotación parcial. CV32E40P y common_verification son apoyos, no corpus independientes equivalentes. Referencia local: revision_fuentes_2026-10-30/prioridades.md.
Para adquirir un caso útil de CVFPU, solicitar una corrida breve con test, seed, revisiones, configuración y UVM_HIGH que conserve FPU_MONITOR_REQ/RSP y FPU_SB_REQ/RSP; validar IDs, campos y ambos extremos en el log real. Para UART también se requiere verbosidad y contexto de TX/RX/reset. Son requisitos de adquisición derivados de la revisión de fuentes, no evidencia de logs ya recibidos o simulaciones ejecutadas.
La obtención inicial está cubierta para consultas básicas, pero pendiente para la nueva correlación. El cierre de semana 1 exige acordar campos, política y mínimo de observabilidad, y registrar los vacíos. No certificar la evaluación de correlación hasta contar con muestras de ambos lados. Los reportes parciales de CI no sustituyen un log completo para medir conteos o pérdidas.
Se conservan cobertura_anotacion parcial y habilitada_para_validar_totales=false. La actualización de prioridad no modifica conteos ni convierte anotaciones seleccionadas en referencia exhaustiva. Faltan revisión humana independiente y acuerdos del asesor sobre campos, obligatoriedad y manejo de casos especiales. El usuario autorizó estas adecuaciones; no se registra una aprobación del asesor inexistente.
La versión local 1.2 es la referencia vigente. Los respaldos anteriores son históricos. El documento previo de Google Drive no se modifica con esta entrega local.
