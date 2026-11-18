Semana 1 — Etiquetado manual de cinco casos UVM
Guía de trabajo con evidencia verificable · 26 de octubre de 2026

1. Objetivo y límites
Etiquetar manualmente significa leer una corrida, seleccionar hechos y registrar dónde aparecen, qué referencias contienen y qué relaciones se pueden sostener. El resultado sirve como referencia humana para desarrollar y comprobar después el agente. No equivale a conocer la causa raíz.
Esta guía desarrolla la tarea 4 de la semana 1. Incluye un procedimiento y cinco fichas de ejemplo basadas en archivos realmente consultados, sin ejecutar simulaciones ni implementar parsers, agrupadores o comparación automática. Las anotaciones son propuestas revisadas contra el texto; queda pendiente una revisión humana independiente.
Un caso será una corrida completa con uno o varios eventos de interés. Usamos cinco corridas, no cinco líneas de un mismo archivo. Los dos casos AXI4 pueden compartir un identificador de incidente candidato, pero mantienen sus identidades de corrida.
Se siguen las políticas LOCAL-PF-1.0 y LOCAL-REF-1.0 del archivo contexto_semana_1.txt: distinguir resultado funcional y ejecución; conservar referencias literales; no inventar señales; no confundir relaciones con causas.

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
Resultado propuesto: PASS para el propósito acotado de ejecutar simple_test y obtener su marcador de éxito; ejecución COMPLETA. No certificar un DUT industrial.
Relación: E01 y E03 tienen asociación de entorno respaldada por los mensajes sobre DPI; no son dos defectos del circuito. E02 y E04 son hitos del mismo test.
signal_path: no observado. uvm_test_top es componente UVM.
Cómo anotarlo: copiar cada fragmento, comprobar ambas coordenadas, justificar PASS con L144, L147, L154–155 y L164–166. Si se omite el cierre, la ficha queda incompleta.

5. Caso C02 — Estímulo y comparación coincidente
Archivo: uvm_scoreboard_monitor_agent_env.log. Corrida R02. El marcador L224 dice “Running test ...” y no proporciona nombre concreto; no inventarlo a partir del nombre del archivo.
E01 L223: NO_DPI_USED; E02 L226: NO_VISIT_CHECK. E03 L227: escritura del valor 2 a la interfaz de entrada, componente env, archivo tests/testbenches/uvm_scoreboard_monitor_agent_env.sv:184, tiempo literal 0.
E04 L228: comparación coincidente de 2 y 2, componente env.comp, mismo archivo fuente:144, tiempo literal 15.
Agregado A01 L230–243: ERROR=0 en L235 y FATAL=0 en L236. Cierre L245–248; el cierre informa 15 ps, pero no atribuir automáticamente esa unidad a cada encabezado sin validar su formato.
Resultado propuesto: PASS bajo el criterio local de esta muestra mínima (estímulo y comparación coincidente, sin errores y con cierre); ejecución COMPLETA.
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
Resultado: PASS para esa prueba; ejecución COMPLETA. Cobertura registrada no implica que se haya cumplido una meta no acordada.
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
Política pública definida por el estudiante: conservar procedencia y condiciones de cada fuente. Este documento se crea en Drive sin cambiar sus permisos de uso compartido.

