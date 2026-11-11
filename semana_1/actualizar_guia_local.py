"""Genera las dos representaciones locales de la guía a partir del respaldo."""
from pathlib import Path
import json
import re
from adecuaciones_semana_1 import adecuar_guia

HERE=Path(__file__).resolve().parent
original=(HERE/'guia_etiquetado_respaldo.md').read_text(encoding='utf-8-sig').strip()
original=original.replace('Guía de trabajo con evidencia verificable · 26 de octubre de 2026',
    'Guía de trabajo con evidencia verificable · Actualización del 30 de octubre de 2026 · Versión 1.1')
original=original.replace('Este documento se crea en Drive sin cambiar sus permisos de uso compartido.',
    'Esta edición se entrega localmente en la carpeta del proyecto; el documento previo de Drive conserva su versión anterior.')
extra='''

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
annotation_version: versión de la convención de anotación (1.1). Cambiarla sólo si cambia la estructura o el significado de los campos; fecha identifica esta edición.
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
- texto_original contiene exactamente las líneas seleccionadas, con prefijos # y espacios, unidas por saltos representados como \\n dentro del JSON. No reformular ese campo; el hecho se escribe por separado.
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
C02: cuatro eventos; PASS acotado a estímulo/comparación, una relación candidata, nombre de test y seed no observados.
C03: siete eventos, incluidos cinco UVM_ERROR; FAIL, agrupamiento candidato de discrepancias, sin causa raíz demostrada.
C04: tres eventos; PASS de AXI4, vínculo candidato con C03, sin prueba de qué cambio produjo la mejora.
C05: seis eventos; warning de simulador completo en tres líneas, dos reportes ECALL separados, resultado funcional INDETERMINADO y ejecución COMPLETA.
Los 24 registros de eventos no constituyen 24 fallos ni todos los eventos de las cinco corridas. Cada ficha tiene además A01 como registro agregado; no se incluye en esos 24.
Las fichas están elaboradas y verificadas contra sus fragmentos y fuentes, en estado propuesto y pendientes de revisión humana independiente. No se declara cerrada toda la semana 1 ni se realizan actividades de semanas posteriores a la segunda.
La guía local actualizada es la referencia para los JSON entregados. El respaldo anterior y el documento anterior de Google Drive se conservan como antecedentes; el contenido de esta tarea sigue separado de contexto_semana_1.txt, conforme a la decisión previa.
'''
text=adecuar_guia(original+'\n'+extra.strip()+'\n')
(HERE/'guia_etiquetado_actualizada.md').write_text(text,encoding='utf-8')
sections=[]
for part in re.split(r'(?=^\d+\. )',text,flags=re.M):
    if not part.strip(): continue
    title,_,body=part.strip().partition('\n')
    sections.append({'titulo':title,'contenido':body})
payload={'guide_version':'1.2','fecha':'2026-10-30','titulo':'Guía paso a paso para almacenar y elaborar cinco fichas UVM',
         'representacion_legible':'guia_etiquetado_actualizada.md','ambito':'Semana 1; anotaciones seleccionadas, no contrato API del agente.',
         'secciones':sections,
         'fichas':['etiquetas/'+n for n in ['C01_simple_test.json','C02_scoreboard.json','C03_axi4_fail.json','C04_axi4_pass.json','C05_riscv.json']]}
(HERE/'guia_etiquetado_actualizada.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert len(sections)==18
assert all((HERE/p).exists() for p in payload['fichas'])
print('Guía actualizada en Markdown y JSON; versión 1.2, 17 secciones más título e introducción.')
