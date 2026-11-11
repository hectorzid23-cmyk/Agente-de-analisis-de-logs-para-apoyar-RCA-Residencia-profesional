"""Materializa anotaciones seleccionadas explícitamente; no es el parser del agente."""
from pathlib import Path
import hashlib
import json
import re
from adecuaciones_semana_1 import adecuar_ficha

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'semana_1' / 'etiquetas'
OUT.mkdir(exist_ok=True)
DATE = '2026-10-30'

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

old_sources = json.loads((ROOT/'fuentes_logs_revision/procedencia.json').read_text(encoding='utf-8-sig'))['archivos']
new_sources = json.loads((ROOT/'semana_1/fuentes/procedencia.json').read_text(encoding='utf-8-sig'))

def base(case, filename, relative, test, test_lines, seed, seed_lines, result, reason, result_lines, close, summary, counts, simulator, simulator_lines, uvm, uvm_lines):
    path = ROOT / relative
    lines = path.read_text(encoding='utf-8-sig').splitlines()
    source = next((x for x in old_sources + new_sources if Path(x['archivo']).name == path.name), None)
    assert source
    obj = {
        'annotation_version': '1.1', 'case_id': case, 'run_id_manual': 'R'+case[1:],
        'titulo': filename, 'fecha': DATE,
        'politicas': ['LOCAL-PF-1.0', 'LOCAL-REF-1.0'],
        'revision': {'autor': 'Asistente, a solicitud del estudiante', 'estado': 'propuesto', 'revisor_independiente': None, 'fecha_revision': None},
        'fuente': {'log_file': __import__('os').path.relpath(path, OUT).replace('\\','/'),
                   'base_ruta': 'directorio_de_esta_ficha', 'sha256_local': hashlib.sha256(path.read_bytes()).hexdigest(),
                   'cantidad_lineas': len(lines), 'url': source.get('url', source.get('fuente')),
                   'git_blob_sha': source['git_blob_sha'],
                   'objeto_git_corresponde_a': 'HTML original' if source in old_sources else 'contenido del log publicado',
                   'metodo': source['metodo'], 'simulacion_ejecutada_localmente': False},
        'metadatos': {'test': {'valor': test, 'lineas_log': test_lines, 'estado': 'observado' if test else 'no_observado'},
                      'seed': {'valor': seed, 'lineas_log': seed_lines, 'estado': 'observado' if seed is not None else 'no_observado'},
                      'simulador': {'valor': simulator, 'lineas_log': simulator_lines},
                      'uvm': {'valor': uvm, 'lineas_log': uvm_lines},
                      'revision_rtl_testbench': None},
        'pregunta_del_caso': reason,
        'resultado': {'local': result, 'declarado': None, 'estado_ejecucion': 'COMPLETA',
                      'criterio': reason, 'evidencia_lineas': result_lines, 'cierre_lineas': close,
                      'causa_raiz': {'estado': 'no_determinada', 'valor': None}},
        'cobertura_anotacion': {'modo': 'seleccion_de_eventos', 'inventario_exhaustivo': False,
              'categorias_completas_certificadas': [], 'habilitada_para_validar_totales': False,
              'alcance_actual': 'Eventos seleccionados, sus referencias y relaciones candidatas; los resúmenes se conservan aparte.',
              'pendiente_para_totales': 'Elegir categoría y etapa, revisar todo el intervalo de la corrida, completar sus eventos o confirmar ausencia, contrastar resumen y obtener revisión independiente.'},
        'eventos': [],
        'agregados': [{'aggregate_id': 'A01', 'tipo': 'UVM_REPORT_SUMMARY', 'log_line_start': summary[0], 'log_line_end': summary[1],
                       'texto_original': '\n'.join(lines[summary[0]-1:summary[1]]),
                       'conteos_declarados': counts, 'es_evento_individual': False,
                       'regla': 'No sumar estas filas a los mensajes individuales; INFO puede excluir el anuncio del propio resumen.'}],
        'relaciones': [], 'vinculos_entre_casos': [],
        'limitaciones': ['La ficha no certifica un inventario exhaustivo de todas las categorías.',
                         'No se han observado rutas de señales RTL en los eventos seleccionados; no confundir componentes o PC con señales.',
                         'No existe revisión humana independiente registrada.']}
    return obj, lines

def event(pair, eid, start, end, kind, fact, fields=None, note=None):
    obj, lines = pair
    raw = '\n'.join(lines[start-1:end])
    first = lines[start-1]
    header = re.search(r'(UVM_INFO|UVM_WARNING|UVM_ERROR|UVM_FATAL)\s+(.*?)\s*@\s*(\d+):\s*(.*?)\s+\[([^\]]+)\]', first)
    source = re.search(r'([^\s]+\.(?:sv|svh))\((\d+)\)', raw)
    tm = re.search(r'Time:\s*(\d+)\s*(ps|ns|us|ms|s)\b', raw) if not header else None
    e = {'event_id': eid, 'etapa': 'simulacion', 'tipo': kind,
         'severidad_original': header.group(1) if header else ('Warning' if 'Warning:' in raw else None),
         'dominio_severidad': 'UVM' if header else ('simulador' if 'Warning:' in raw else 'texto_sin_severidad'),
         'message_id': header.group(5) if header else ('vsim-PLI-8707' if 'vsim-PLI-8707' in raw else None),
         'log_line_start': start, 'log_line_end': end, 'texto_original': raw,
         'tiempo': {'valor_literal': header.group(3) if header else (tm.group(1) if tm else None),
                    'unidad': tm.group(2) if tm else None, 'origen': 'explicito_log' if (header or tm) else 'no_observado',
                    'nota': None if tm else 'La unidad del encabezado no se ha resuelto; no convertir numéricamente.'},
         'component_path': header.group(4) if header else None,
         'source_file': source.group(1) if source else None, 'source_line': int(source.group(2)) if source else None,
         'origen_source': 'explicito_log' if source else 'no_observado',
         'signal_path': None, 'estado_signal_path': 'no_observado',
         'otras_referencias': [], 'campos_observados': fields or {},
         'hecho': fact, 'interpretacion': note, 'es_mensaje_individual': True}
    obj['eventos'].append(e)
    return e

def relation(pair, rid, ids, kind, support, limit):
    pair[0]['relaciones'].append({'relation_id': rid, 'miembros': ids, 'tipo': kind,
        'calificacion': 'candidata', 'evidencia': support, 'limite': limit,
        'causalidad_demostrada': False, 'alternativas': ['Coincidencia de contexto sin causa común demostrada.']})

c1 = base('C01','Inicio y éxito explícito de simple_test','fuentes_logs_revision/muestras/uvm_test_run_test.log',
          'simple_test',[144],None,[],'PASS','Inicio de simple_test, marcador SUCCESS de su propósito mínimo, resumen sin ERROR/FATAL y cierre normal.',
          [144,147,154,155],[164,167],[149,162],{'UVM_INFO':4,'UVM_WARNING':2,'UVM_ERROR':0,'UVM_FATAL':0},'Verilator 5.053 devel',[165],'Accellera UVM 2020.3.1',[135])
event(c1,'E01',143,143,'warning_entorno','Se advierte sobre soporte de UVM_NO_DPI.')
event(c1,'E02',144,144,'inicio_test','Se anuncia la ejecución de simple_test.')
event(c1,'E03',146,146,'warning_entorno','No se comprobarán restricciones de nombres de componentes sin DPI.')
event(c1,'E04',147,147,'resultado_test','Se informa SUCCESS de la llamada a simple_test.')
c1[0]['resultado']['declarado'] = {'valor':'SUCCESS, simple_test called','lineas_log':[147]}
relation(c1,'G01',['E01','E03'],'entorno_DPI','L143 y L146 identifican limitaciones de DPI.','No son evidencia de defecto RTL.')
relation(c1,'G02',['E02','E04'],'mismo_test','L144 y L147 nombran simple_test.','El éxito sólo cubre el propósito de esta muestra mínima.')

c2 = base('C02','Estímulo y comparación coincidente','fuentes_logs_revision/muestras/uvm_scoreboard_monitor_agent_env.log',
          None,[],None,[],'PASS','Muestra mínima: escritura de 2, comparación coincidente, cero ERROR/FATAL y cierre; PASS acotado a esa comprobación.',
          [227,228,235,236],[245,248],[230,243],{'UVM_INFO':5,'UVM_WARNING':2,'UVM_ERROR':0,'UVM_FATAL':0},'Verilator 5.053 devel',[246],'Accellera UVM 2020.3.1',[215])
event(c2,'E01',223,223,'warning_entorno','Soporte de UVM_NO_DPI advertido.')
event(c2,'E02',226,226,'warning_entorno','No se comprobarán restricciones de nombres de componentes.')
event(c2,'E03',227,227,'estimulo','Se informa escritura del valor 2 a la interfaz de entrada.',{'valor':2})
event(c2,'E04',228,228,'comparacion_coincidente','El comparador informa coincidencia de 2 y 2.',{'operando_izquierdo':2,'operando_derecho':2})
c2[0]['resultado']['declarado']={'valor':'Comparator match','lineas_log':[228],'nota':'No es un marcador universal TEST PASSED.'}
c2[0]['limitaciones'].append('L224 contiene Running test ... sin nombre concreto; el nombre del archivo no se usa como test observado.')
relation(c2,'G01',['E03','E04'],'estimulo_comprobacion','L227 y L228: orden observado y valor 2 compartido.','Sin transaction_id ni señal explícita; no prueba conectividad o causalidad.')

c3 = base('C03','Fallo AXI4 con varios mensajes','semana_1/fuentes/burst_read_test_seed1_questa_FAIL.log',
          'burst_read_test',[1,146],1,[1],'FAIL','Cinco mensajes UVM_ERROR, un beat incorrecto declarado, TEST FAILED y cierre; vsim Errors:0 pertenece al simulador.',
          [147,148,149,150,167,169,170,171,178,179,198],[189,200],[173,187],{'UVM_INFO':8,'UVM_WARNING':0,'UVM_ERROR':5,'UVM_FATAL':0},'QuestaSim 2025.2',[2],'UVM 1.2',[1])
for i,(addr,exp,act) in enumerate([('0x00000100','0xb5','0xf1'),('0x00000101','0xf9','0x43'),('0x00000102','0x57','0xdd'),('0x00000103','0x82','0x34')]):
    event(c3,f'E0{i+1}',147+i,147+i,'discrepancia_byte',f'Byte {i} discrepante en {addr}.',{'address':addr,'byte':i,'esperado':exp,'observado':act})
event(c3,'E05',160,168,'resumen_scoreboard','El scoreboard declara 29 beats coincidentes y 1 incorrecto.',{'matching_beats':29,'mismatched_beats':1,'write_transactions':2,'read_transactions':5})
event(c3,'E06',169,169,'fallo_scoreboard','Se reporta FAIL por un beat incorrecto.',{'mismatched_beats':1})
event(c3,'E07',170,171,'resultado_test','El cuerpo de un UVM_INFO declara TEST FAILED.')
c3[0]['resultado']['declarado']={'valor':'TEST FAILED','lineas_log':[170,171]}
relation(c3,'G01',['E01','E02','E03','E04','E05','E06'],'incidente_scoreboard','Mismo tiempo de los cuatro bytes, componente y origen; direcciones contiguas; E05/E06 declaran un beat incorrecto.','No hay identificador explícito por beat; cinco mensajes no equivalen a cinco causas raíz.')
c3[0]['limitaciones'].append('Los cinco UVM_ERROR seleccionados coinciden con el total declarado; ello no certifica exhaustividad independiente ni otras categorías.')

c4 = base('C04','Corrida AXI4 exitosa asociable','semana_1/fuentes/burst_read_test_seed1_questa.log',
          'burst_read_test',[1,146],1,[1],'PASS','30 beats coincidentes, cero incorrectos, TEST PASSED, resumen 0 ERROR/FATAL y cierre.',
          [162,163,165,166,167,174,175],[185,196],[169,183],{'UVM_INFO':9,'UVM_WARNING':0,'UVM_ERROR':0,'UVM_FATAL':0},'QuestaSim 2025.2',[2],'UVM 1.2',[1])
event(c4,'E01',156,164,'resumen_scoreboard','El scoreboard declara 30 beats coincidentes y 0 incorrectos.',{'matching_beats':30,'mismatched_beats':0,'write_transactions':2,'read_transactions':5})
event(c4,'E02',165,165,'comprobacion_exitosa','Se informa conformidad con shadow memory.')
event(c4,'E03',166,167,'resultado_test','Se declara TEST PASSED.')
c4[0]['resultado']['declarado']={'valor':'TEST PASSED','lineas_log':[166,167]}
relation(c4,'G01',['E01','E02','E03'],'resumen_y_resultado','L156–167: estadísticas y mensajes de éxito al mismo tiempo literal.','PASS de esa prueba; no certifica cobertura total del diseño.')
for pair,other,lines_here,lines_other in [(c3,'C04',[1,166,167,171],[1,162,163,167]),(c4,'C03',[1,162,163,167],[1,166,167,171])]:
    pair[0]['vinculos_entre_casos']=[{'incident_id_candidato':'I01','otro_case_id':other,'tipo':'mismo_test_seed',
        'estado':'candidato','evidencia_local_lineas':lines_here,'evidencia_otro_caso_lineas':lines_other,
        'observacion':'burst_read_test y seed 1 en ambas corridas; cambia el resultado y el número de beats incorrectos.',
        'limite':'Faltan revisiones y configuración completas; no se demuestra una corrección causal específica.'}]

c5 = base('C05','Warning multilínea y límites del resultado','semana_1/fuentes/riscv_uvm_run.log',
          'riscv_base_test',[5,59],None,[],'INDETERMINADO','Se observa ECALL y finalización con cero errores UVM, pero no se ha validado que ese criterio certifique éxito arquitectónico.',
          [2651,2652,2679,2680],[2696,2699],[2674,2694],{'UVM_INFO':1971,'UVM_WARNING':0,'UVM_ERROR':0,'UVM_FATAL':0},'Questa Intel Starter FPGA Edition 2024.3',[9,10],'UVM 1.2',[36])
memory='out_2025-06-29/asm_test/riscv_arithmetic_basic_test_17216.o.mem'
event(c5,'E01',74,74,'carga_memoria','El predictor carga el archivo de memoria indicado.',{'memory_file':memory})
e=event(c5,'E02',75,77,'warning_simulador','No se especifica dirección en la línea 1 del archivo de memoria al cargar un array asociativo.',{'memory_file':memory,'linea_archivo_memoria':1})
e['otras_referencias']=[{'clase':'region_ejecucion','valor':'/uvm_pkg::uvm_task_phase::execute','origen':'explicito_log','lineas_log':[77]}]
event(c5,'E03a',78,78,'carga_memoria','La secuencia anuncia carga del mismo archivo.',{'memory_file':memory})
event(c5,'E03b',79,79,'inventario_instrucciones','La secuencia declara 810 instrucciones.',{'cantidad_instrucciones':810})
event(c5,'E04a',2651,2651,'deteccion_ecall','Aviso sin severidad de ECALL y finalización vía UVM.',{'pc':'0x80000a08'})
event(c5,'E04b',2652,2652,'deteccion_ecall','El scoreboard detiene comparación al detectar ECALL.',{'pc':'0x80000a08'})
c5[0]['resultado']['declarado']={'valor':'ECALL detectado y cierre UVM','lineas_log':[2651,2652,2672,2696,2697],'nota':'No equivale a TEST PASSED verificado.'}
relation(c5,'G01',['E01','E02','E03a','E03b'],'carga_mismo_archivo','L74–79: mismo archivo de memoria y contexto de carga de secuencia.','El warning no demuestra defecto del DUT ni impacto en el resultado.')
relation(c5,'G02',['E04a','E04b'],'misma_observacion_ecall','L2651 y L2652 citan PC 0x80000a08 y finalización/detención.','Dos reportes de contexto compartido, sin causa raíz demostrada.')
c5[0]['limitaciones'] += ['17216 forma parte de un nombre de programa; no se usa como seed.',
    'El emisor con @@memory_seq se conserva literal; es una referencia de secuencia, no una señal RTL.',
    'Un warning del simulador (L75–77, cierre L2699) puede coexistir con UVM_WARNING=0; son dominios distintos.']

names=['C01_simple_test.json','C02_scoreboard.json','C03_axi4_fail.json','C04_axi4_pass.json','C05_riscv.json']
for pair,name in zip([c1,c2,c3,c4,c5],names):
    obj,lines=pair
    obj['pregunta_del_caso'] = {
        'C01':'¿Se ejecutó simple_test y qué evidencia respalda su éxito pese a los warnings de DPI?',
        'C02':'¿Qué estímulo y comparación se observaron y hasta dónde permiten sostener el resultado?',
        'C03':'¿Por qué falla la verificación AXI4 si vsim informa cero errores y cómo se relacionan sus cinco UVM_ERROR?',
        'C04':'¿Qué respalda el PASS de esta corrida y qué limita su asociación con C03?',
        'C05':'¿Qué significa el warning de carga y basta el cierre con ECALL para certificar éxito funcional?'
    }[obj['case_id']]
    for e in obj['eventos']:
        for key,kind in [('memory_file','archivo_memoria'),('address','direccion_transaccion'),('pc','contador_programa')]:
            if key in e['campos_observados']:
                e['otras_referencias'].append({'clase':kind,'valor':e['campos_observados'][key],
                    'origen':'explicito_log','lineas_log':list(range(e['log_line_start'],e['log_line_end']+1))})
        if e['component_path'] and '@@' in e['component_path']:
            e['otras_referencias'].append({'clase':'referencia_secuencia','valor':e['component_path'],
                'origen':'explicito_log','nota':'Ruta del emisor conservada literal; no es signal_path.'})
    observed={sev:sum(e['severidad_original']==sev for e in obj['eventos']) for sev in ['UVM_INFO','UVM_WARNING','UVM_ERROR','UVM_FATAL']}
    obj['conteos_anotados']={'dominio':'Sólo mensajes individuales seleccionados, incluidos resúmenes de scoreboard con encabezado UVM; excluye el agregado UVM Report Summary.',
         'por_severidad_uvm':observed,'cantidad_registros_evento':len(obj['eventos']),
         'no_representan_totales_de_corrida':True}
    save(OUT/name,adecuar_ficha(obj))

# Verificación de entrega, no evaluación del agente ni parser general.
checks=[]
for name in names:
    obj=json.loads((OUT/name).read_text(encoding='utf-8'))
    path=(OUT/obj['fuente']['log_file']).resolve()
    assert path.is_relative_to(ROOT)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==obj['fuente']['sha256_local']
    lines=path.read_text(encoding='utf-8-sig').splitlines()
    ids=[e['event_id'] for e in obj['eventos']]
    assert len(ids)==len(set(ids))
    for e in obj['eventos']+obj['agregados']:
        a,b=e['log_line_start'],e['log_line_end']
        assert 1<=a<=b<=len(lines)
        assert e['texto_original']=='\n'.join(lines[a-1:b])
    for r in obj['relaciones']:
        assert set(r['miembros']).issubset(ids)
    assert obj['cobertura_anotacion']['habilitada_para_validar_totales'] is False
    checks.append({'archivo':name,'eventos':len(ids),'fragmentos_y_hash':'verificados','json':'valido'})
save(ROOT/'semana_1/verificacion_fichas.json',{'fecha':DATE,'alcance':'Integridad de JSON, fuentes, fragmentos, intervalos e identificadores. No certifica verdad causal, revisión independiente o exhaustividad.', 'resultados':checks})
print(json.dumps(checks,ensure_ascii=False,indent=2))
