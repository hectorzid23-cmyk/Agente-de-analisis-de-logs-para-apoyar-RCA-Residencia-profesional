# Muestras UVM verificadas

Consulta: 22 de octubre de 2026.

Estas muestras proceden de los resultados públicos de CHIPS Alliance sv-tests. No se ejecutaron simulaciones localmente. Los HTML originales se conservaron en `originales/`; los archivos de `muestras/` contienen el texto de los bloques `<pre>` de la sección del log, en su orden original, sin las etiquetas y con las entidades HTML decodificadas. Incluyen compilación y simulación.

## Archivos

| Archivo | Utilidad | Conteos del resumen UVM (INFO / WARNING / ERROR / FATAL) |
| --- | --- | --- |
| uvm_test_run_test.log | Inicio de test, mensajes multilínea, advertencias y cierre | 4 / 2 / 0 / 0 |
| uvm_scoreboard_monitor_agent_env.log | Comparación del scoreboard, tiempo, componente y archivo/línea | 5 / 2 / 0 / 0 |

Ambas ejecuciones figuran como exitosas en la fuente. Son casos básicos; no constituyen un corpus suficiente para investigar causas raíz ni evaluar detección de fallos. El resumen UVM y el número de líneas que contienen un prefijo no tienen por qué coincidir: el mensaje que anuncia el propio resumen también aparece como UVM_INFO. No contar las filas del resumen como eventos nuevos.

La corrida del scoreboard se completó el 21 de octubre de 2026 según la página fuente. Su salida identifica Verilator 5.053 de desarrollo y Accellera UVM 2020.3.1. Las dos advertencias UVM corresponden a DPI deshabilitado. Conservarlas como evidencia del entorno; no etiquetarlas automáticamente como defectos del circuito.

## Procedencia y límites

`procedencia.json` registra la URL y el SHA del objeto Git de cada HTML leído. `verificacion.json` registra hashes de las muestras y conteos del resumen revisados. La extracción conserva la secuencia textual publicada, pero no garantiza identidad de bytes con el stdout original del proceso.

## Resultado de la revisión de fuentes

- OpenCores: acceso parcial a fichas y contenido indexado. La conexión directa a la descarga y al SVN de LPFFIR no se completó desde este entorno. No se descargó su sim.log completo.
- LPFFIR / rca_uvm: el índice público muestra un sim.log VCS/UVM con resumen sin errores ni fatales, y fuentes del testbench. Es un candidato básico pendiente de recuperar y validar íntegramente. RCA en ese proyecto significa Ripple Carry Adder.
- openHMC: se pudieron leer fuentes UVM del repositorio de sus autores, `unihd-cag/openhmc`, como alternativa al acceso a OpenCores. Contiene scoreboard, inyección de errores y tests de errores de bits; su script utiliza irun de Cadence. No se ejecutó ni se verificó compatibilidad con un simulador instalado.
- chipsalliance/sv-tests: útil para comenzar con casos UVM pequeños y para ampliar formatos. Sus resultados mezclan parsing, elaboración y simulación: seleccionar explícitamente el modo simulation.
- openhwfoundation/core-v-verif: entorno UVM completo apropiado para un corpus posterior de regresiones e investigación de fallos. Los logs se generan al ejecutar; no se identificaron archivos .log ni transcript versionados en el árbol master inspeccionado. Necesita preparación de simulador, dependencias y toolchain.
- ben-marshall/awesome-open-hardware-verification: catálogo para descubrir herramientas y proyectos; no es un dataset ni un testbench ejecutable por sí mismo.

## Requisitos derivados del nuevo alcance

Conservar texto original, posición de cada evento, tiempo y unidad, severidad, identificador, componente, archivo y línea cuando estén presentes. Asociar cada corrida con test, seed, simulador/versiones, configuración, revisiones de RTL/testbench y resultado esperado. Para evaluar relaciones entre errores se necesitan fallos de causa conocida y, preferentemente, corridas antes/después de la corrección. Una jerarquía de componente UVM no equivale a una ruta de señal RTL. Los logs no contienen necesariamente toda la conectividad ni todos los valores de señales; puede ser necesaria instrumentación o consulta de otros artefactos.

La evaluación del agente debe distinguir hechos respaldados por líneas concretas de hipótesis sobre errores relacionados. Los dos logs aquí incluidos sirven para extracción y consultas básicas, no como etiquetas de causas raíz.
