# Prioridad de fuentes para el agente de logs de simulación
Revisión del 30 de octubre de 2026.

## Decisión
La prioridad estratégica para ampliar el corpus es: CVFPU-UVM, OpenTitan (UART), Ibex y CORE-V-VERIF. El corpus ya reunido de sv-tests, AXI4 y RISC-V conserva su papel como base de pruebas del parser/API. Esta lista prioriza el ajuste al objetivo, la observabilidad monitor → scoreboard, la reproducibilidad y el coste de integración; las estrellas no determinan el orden.

El contexto local actualizado incorpora correlación monitor → scoreboard y requiere devolver NOT_OBSERVABLE cuando faltan mensajes. La existencia de puertos TLM o de un scoreboard no basta: debe existir evidencia textual en ambos extremos y claves que permitan emparejarla.

## Lista de fuentes principales
| Prioridad | Fuente | Motivo y condición |
| --- | --- | --- |
| 1 | [openhwfoundation/cvfpu-uvm](https://github.com/openhwfoundation/cvfpu-uvm) | Mejor ajuste acotado a transacciones con TID, mensajes en monitor y scoreboard, modelo de referencia y scripts multisimulador. Requiere generar logs con verbosidad suficiente y preparar dependencias. |
| 2 | [lowRISC/opentitan — bloque UART](https://github.com/lowRISC/opentitan/tree/master/hw/ip/uart/dv) | Monitor y scoreboard imprimen items TX/RX; entorno conectado y testplan rico. Empezar por UART, no chip completo. Requiere revisar emparejamiento de bytes repetidos y resets. |
| 3 | [lowRISC/ibex](https://github.com/lowRISC/ibex/tree/master/dv/uvm/core_ibex) | UVM, cosimulación con Spike y reporte público reciente con fallos y evidencia contextual. Mayor complejidad de procesador; no confundir reporte parcial con log íntegro. |
| 4 | [openhwfoundation/core-v-verif](https://github.com/openhwfoundation/core-v-verif) | Entornos UVM completos y estructura de logs por test/corrida. Preparación más amplia; también dependencia de CVFPU-UVM. Seleccionar un núcleo y entorno concreto. |
| 5 | [chipsalliance/sv-tests](https://github.com/chipsalliance/sv-tests) | Casos UVM pequeños y resultados públicos; dos logs ya extraídos localmente. Bueno para formatos y consultas, limitado para incidentes complejos. Filtrar simulation. |
| 6 | [Tharunreddym/axi4-verification](https://github.com/Tharunreddym/axi4-verification) | Par FAIL/PASS ya reunido y depuración documentada. Mantener para evidencia y comparación; los logs actuales no registran cada envío del monitor. |
| 7 | [isbogdanov/riscv-core-dv-uvm](https://github.com/isbogdanov/riscv-core-dv-uvm) | Logs UVM existentes, jerarquías y scoreboard; útil para ampliar volumen y contexto. Proyecto comunitario; comprobar versiones y observabilidad por corrida. |
| 8 | [unihd-cag/openhmc](https://github.com/unihd-cag/openhmc) | Entorno UVM con inyección de errores y scoreboard revisado anteriormente. Flujo antiguo basado en irun; coste de actualización antes de generar corpus. |
| 9 | [verilator/verilator — test_regress](https://github.com/verilator/verilator/tree/master/test_regress) | Assertions y diversidad de diagnósticos. Muchas salidas son golden .out; distinguir simulación de compilación y fallo esperado del harness. |
| 10 | [NVlabs/verilog-eval](https://github.com/NVlabs/verilog-eval) | Base para generar otros casos funcionales de Verilog; menor ajuste a la prioridad inicial UVM. No es colección lista de transcripts UVM. |
| 11 | [OpenCores LPFFIR / rca_uvm](https://opencores.org/projects/lpffir) | Ejemplo UVM sencillo previamente identificado. Acceso integral pendiente; el log observado era sin errores. RCA aquí significa Ripple Carry Adder. |
| 12 | [OpenCores ethmac](https://opencores.org/projects/ethmac) | Testbench clásico para ampliar a formatos no UVM después. Sin ventaja inmediata frente a fuentes ya accesibles. |
| 13 | [Hugging Face: RTL_verilog_synthetic_o3_verified_to_simulate_FSM](https://huggingface.co/datasets/sonyashijin/RTL_verilog_synthetic_o3_verified_to_simulate_FSM) | Complemento para variedad de texto. Las contradicciones previamente observadas impiden tratar sus etiquetas como verdad sin revisión. |

Las fuentes 8–13 conservan la evaluación previa; esta revisión no reproduce sus simulaciones ni realiza una auditoría exhaustiva nueva de ellas. Se releen los README actuales de sv-tests, AXI4 y RISC-V para contrastar su función en el corpus.

## Fuentes de apoyo, fuera de la lista de corpus
- [openhwfoundation/cv32e40p](https://github.com/openhwfoundation/cv32e40p): su README remite la verificación completa a core-v-verif. Aporta RTL y manuales para interpretar evidencias, no una segunda fuente independiente equivalente de logs UVM. El pequeño testbench incluido es experimental.
- [pulp-platform/common_verification](https://github.com/pulp-platform/common_verification): generadores de reloj/reset, watchdogs y drivers. Útil para construir casos de timeout o inactividad; no es un entorno UVM completo ni una colección de logs.
- [ben-marshall/awesome-open-hardware-verification](https://github.com/ben-marshall/awesome-open-hardware-verification): catálogo de descubrimiento, no corpus.

## Evidencia de los seis repositorios propuestos
### CVFPU-UVM
El [monitor](https://github.com/openhwfoundation/cvfpu-uvm/blob/main/fpu_agent/fpu_monitor.svh) imprime solicitudes y respuestas con IDs FPU_MONITOR_REQ y FPU_MONITOR_RSP en UVM_HIGH antes de publicarlas. El [scoreboard](https://github.com/openhwfoundation/cvfpu-uvm/blob/main/env/fpu_sb.svh) imprime FPU_SB_REQ y FPU_SB_RSP en UVM_LOW después de retirarlas de sus FIFOs. El [paquete común](https://github.com/openhwfoundation/cvfpu-uvm/blob/main/fpu_common/fpu_common_pkg.sv) incluye TID y datos en las impresiones. El [entorno](https://github.com/openhwfoundation/cvfpu-uvm/blob/main/env/fpu_env.svh) conecta directamente estos puertos y FIFOs.

Esto permite proponer emparejamientos de solicitud-monitor contra solicitud-scoreboard y de respuesta-monitor contra respuesta-scoreboard. No confundir esa igualdad de transporte con la comprobación funcional que compara resultado del DUT y modelo C++. Se deben considerar reset, flush, reutilización de TID y ocurrencias sucesivas; TID no es una clave universalmente única para todo el log.

La [documentación](https://github.com/openhwfoundation/cvfpu-uvm/blob/main/README.md) describe Questa/Xcelium/VCS, Bender, GMP, MPFR y modelo C++ por DPI. La lista de regresión configura 10 entradas de 50 corridas; es configuración prevista, no evidencia de 500 logs existentes ni de que todos los tests se ejecuten sin adaptación. No se identificaron archivos .log/transcript en el árbol principal completo inspeccionado. El script scan_logs es una referencia de patrones, no sustituye la política local PASS/FAIL/INDETERMINADO: fin de proceso no equivale a éxito funcional.

### OpenTitan: UART
El [monitor UART](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/uart_agent/uart_monitor.sv) imprime el item antes de publicar por sus puertos de análisis. El [scoreboard](https://github.com/lowRISC/opentitan/blob/master/hw/ip/uart/dv/env/uart_scoreboard.sv) imprime el item después del get de sus FIFOs TX/RX. Ambos usan UVM_HIGH. El [entorno](https://github.com/lowRISC/opentitan/blob/master/hw/ip/uart/dv/env/uart_env.sv) conecta esos extremos cuando el scoreboard está habilitado.

Hay casos de FIFO, paridad, interrupciones y reset. La comparación necesita canal, orden, campos y contexto de reset; un byte idéntico repetido no es un ID único. El [agente UART también tiene logger](https://github.com/lowRISC/opentitan/blob/master/hw/dv/sv/uart_agent/uart_logger.sv) para texto recibido por UART, que no debe confundirse automáticamente con el registro de transporte monitor → scoreboard.

La [configuración del bloque](https://github.com/lowRISC/opentitan/blob/master/hw/ip/uart/dv/uart_sim_cfg.hjson) selecciona VCS para signoff y contiene uart_smoke. El [reporte público](https://reports.opentitan.org/hw/ip/uart/dv/latest/report.html) consultado es de 2025-02-08, revisión 9f20940d49, aunque la ruta diga latest: contiene extractos de fallos y ubicaciones de logs, no una descarga íntegra de todos ellos. No asociar números de línea históricos al master actual sin resolver la revisión.

La consulta recursiva del monorepo falló por transporte; se leyeron archivos y directorios concretos. No se afirma ausencia global de logs versionados en OpenTitan.

### Ibex
La [guía UVM](https://github.com/lowRISC/ibex/blob/master/dv/uvm/core_ibex/README.md) utiliza Xcelium, Spike específico de lowRISC y toolchain RISC-V. La documentación de verificación también contiene referencias a VCS: fijar herramienta y versión antes de ejecutar, en lugar de asumir equivalencia de cualquier flujo.

El [scoreboard de cosimulación](https://github.com/lowRISC/ibex/blob/master/dv/uvm/core_ibex/common/ibex_cosim_agent/ibex_cosim_scoreboard.sv) consume eventos de instrucciones y memoria y puede emitir un fatal por discrepancia con Spike. El [reporte público](https://ibex.reports.lowrisc.org/opentitan/latest/report.html) consultado corresponde al 2026-10-30, commit f451552, e incluye fallos con test, contexto, fichero y línea. Eso acredita material real de diagnóstico, no la disponibilidad pública del rtl_sim.log completo ni una causa raíz confirmada. Se deben adquirir corridas íntegras antes de medir exhaustividad o integridad de transacciones.

### CORE-V-VERIF y CV32E40P
El [README de CV32E40P](https://github.com/openhwfoundation/cv32e40p/blob/master/README.md) indica explícitamente que el entorno de verificación no se aloja allí. CORE-V-VERIF clona la versión del RTL requerida. Por tanto se usan juntos, sin contar el mismo caso como dos fuentes independientes.

La [estructura de resultados](https://github.com/openhwfoundation/core-v-verif/blob/master/cv32e40p/sim/uvmt/README.md) separa resultados por simulador, configuración, test y corrida, con logs y metadatos. El repositorio tiene scoreboards de RVFI y otros agentes; su existencia no garantiza que una corrida concreta imprima ambos extremos. Antes de elevar un log a prueba de correlación debe comprobarse qué mensajes contiene y su verbosidad.

### common_verification
El [README](https://github.com/pulp-platform/common_verification/blob/master/README.md) describe módulos y clases de apoyo, sin un flujo de corpus UVM. sim_timeout y stream_watchdog pueden emitir fatal por timeout/inactividad. Son componentes para preparar escenarios, no casos de fallo causal ya documentados.

## Aplicación práctica
1. Mantener el corpus y etiquetas existentes para la base determinista: no reemplazarlos ni relabelarlos por este ranking.
2. Obtener primero una corrida CVFPU breve, con seed y revisiones fijas, UVM_HIGH para observar ambos lados, y cantidad de transacciones reducida respecto al ejemplo de 10000. Comenzar sin flush y luego añadirlo como caso separado.
3. Verificar emparejamiento por canal, TID, datos, ocurrencia y segmento de reset/flush. Conservar el log original y devolver ambigüedad si el orden o la reutilización de ID impiden decidir.
4. Añadir una alteración controlada en una copia del entorno sólo en una tarea posterior autorizada, o adquirir un fallo documentado de la misma revisión. La presencia de archivos llamados bug no acredita una reproducción lista.
5. Usar UART de OpenTitan como segundo protocolo, y luego Ibex/CORE-V para generalización de consultas y relaciones candidatas.
6. Si no se dispone del simulador o dependencias, los casos existentes continúan primero en el trabajo diario; los puestos estratégicos 1–4 quedan como fuentes a conseguir del asesor o generar posteriormente.

## Límites de la revisión
Inspección estática de fuentes, árboles y documentación, sin instalar herramientas ni ejecutar simulaciones. Los cinco árboles completos de CVFPU, Ibex, CORE-V, CV32E40P y common_verification no mostraron .log/transcript con los patrones de búsqueda usados; esto no cubre submódulos ni artefactos de CI. La información de revisión, tamaños y archivos leídos se conserva en auditoria_repositorios.json.

