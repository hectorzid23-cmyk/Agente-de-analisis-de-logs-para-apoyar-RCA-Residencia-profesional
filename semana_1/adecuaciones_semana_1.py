"""Alineación documental de semana 1; no ejecuta correlación ni simulaciones."""
from pathlib import Path
import json
import re
import hashlib
import shutil

HERE = Path(__file__).resolve().parent

def adecuar_ficha(obj):
    obj['annotation_version'] = '1.2'
    obj['politicas'] = ['LOCAL-PF-1.1', 'LOCAL-REF-1.1']
    path = HERE/'etiquetas'/obj['fuente']['log_file']
    lines = path.read_text(encoding='utf-8-sig').splitlines()
    commands=[]
    starts=[]
    for n,line in enumerate(lines,1):
        for m in re.finditer(r'\+UVM_TESTNAME=([^\s\"\x27]+)',line):
            commands.append({'valor':m.group(1),'linea_log':n,'texto_original':line})
        m=re.search(r'\[RNTST\] Running test (.*?)\.\.\.',line)
        if m:
            starts.append({'valor':m.group(1) or None,'linea_log':n,'texto_original':line})
    names={r['valor'] for r in commands+starts if r['valor']}
    obj['metadatos']['identificacion_test']={
        'uvm_testname_comando':commands,'rntst':starts,
        'test_name':next(iter(names)) if len(names)==1 else None,
        'estado':'discrepancia' if len(names)>1 else ('concordante' if commands and any(x['valor'] for x in starts) else 'una_fuente' if names else 'no_observado'),
        'es_criterio_fail':False,
        'regla':'Conservar ambos orígenes; si difieren no elegir uno silenciosamente. UVM_TESTNAME no es severidad.'}
    obj['metadatos']['test']['valor']=obj['metadatos']['identificacion_test']['test_name']
    obj['metadatos']['test']['lineas_log']=sorted({r['linea_log'] for r in commands+starts if r['valor']})
    obj['metadatos']['test']['estado']='no_determinado' if len(names)>1 else 'observado' if names else 'no_observado'
    ev=obj['eventos']
    board=[e['event_id'] for e in ev if e['tipo'] in ['resumen_scoreboard','fallo_scoreboard','discrepancia_byte','comparacion_coincidente','comprobacion_exitosa','deteccion_ecall'] and e['component_path']]
    obj['observabilidad_monitor_scoreboard']={
        'estado_global':'NOT_OBSERVABLE',
        'alcance_revision':'Eventos seleccionados y contexto de la muestra; no inventario exhaustivo de publicaciones TLM.',
        'monitor_publicaciones_identificadas':[],
        'scoreboard_recepciones_por_transaccion_identificadas':[],
        'evidencia_contextual_scoreboard_event_ids':board,
        'pares_confirmados':[], 'cantidad_pares_confirmados':None,
        'obligatoria_para_aceptacion_del_test':'no_documentado',
        'motivo':'No se dispone de mensajes identificados en ambos extremos para demostrar publicación y recepción de una misma transacción. Un match o resumen del scoreboard no demuestra ese transporte.',
        'datos_faltantes':['Registro de publicación del monitor y recepción/consumo correspondiente en scoreboard.',
                          'Clave de identidad, canal, campos comparables y reglas de reset, reordenamiento, flush y reutilización de IDs.',
                          'Verbosidad y configuración completas de la corrida.'],
        'clave_propuesta':{'comunes':['run_id','test_name','seed','interfaz','canal','sentido','transaction_id','ocurrencia','segmento_reset_flush'],
                          'opcionales':['beat_id','direccion_memoria'],
                          'nota':'No todos son obligatorios para todo protocolo. TID o datos iguales no garantizan identidad única.'},
        'campos_comparables_propuestos':['datos o huella verificable','campos de control pertinentes al protocolo'],
        'reglas_pendientes':['Fijar qué campos se conservan y qué transformaciones son válidas.',
                            'Acordar correspondencia 1:1 o 1:N, reordenamiento, reintentos y descartes esperados.',
                            'Documentar por test si la correlación es obligatoria para aceptación.'],
        'regla_ausencias':'No clasificar pérdidas ni campos distintos cuando falta observabilidad suficiente; cero pares anotados no demuestra cero transacciones.'}
    for e in ev:
        if e['severidad_original'] in ['UVM_WARNING','Warning']:
            e['pista_rca']={'conservar':True,'disparador_automatico_fail':False,
                'eventos_contexto':[other['event_id'] for other in ev if other is not e and abs(other['log_line_start']-e['log_line_start'])<=5],
                'criterio_contexto':'Proximidad de hasta cinco líneas físicas; ayuda a navegar, no demuestra relación causal.',
                'relevancia':'entorno_DPI' if e['dominio_severidad']=='UVM' else 'carga_memoria',
                'relacion_con_fallo':'no_demostrada','causa_raiz_confirmada':False}
    if obj['case_id']=='C02':
        obj['resultado']['local']='INDETERMINADO'
        obj['resultado']['criterio']='La comparación 2 == 2 y el cierre son hechos, pero no hay marcador explícito de éxito global ni excepción del test documentada. La correlación de transporte tampoco es observable.'
        obj['resultado']['evidencia_lineas']=[224,227,228,235,236,245,247]
        obj['pregunta_del_caso']='¿Qué demuestra la comparación coincidente y qué falta para aceptar el test y comprobar el transporte monitor → scoreboard?'
        for r in obj['relaciones']:
            r['limite']='Relación candidata de estímulo/comprobación; no demuestra publicación del monitor y recepción de la misma transacción en scoreboard ni permite declarar PASS global.'
    functional=obj['resultado']['local']
    obj['resultado']['funcional']=functional
    obj['resultado']['local']=functional
    obj['resultado']['alcance_local']='Resultado funcional según la evidencia del test; no acredita correlación de transporte.'
    obj['resultado']['aceptacion_con_correlacion_obligatoria']='FAIL' if functional=='FAIL' else 'INDETERMINADO'
    obj['resultado']['razon_aceptacion']='FAIL funcional concluyente prevalece.' if functional=='FAIL' else 'Si se exige correlación para aceptar el test, NOT_OBSERVABLE impide declarar PASS de aceptación.'
    obj['resultado']['dato_faltante_para_resolver']='Marcador explícito de éxito o excepción de test documentada; mensajes de ambos extremos para correlación.' if obj['case_id']=='C02' else 'Criterio de éxito arquitectónico documentado y evidencia de ambos extremos.' if obj['case_id']=='C05' else 'Mensajes correlacionables de ambos extremos y política de aceptación por test.'
    obj['pregunta_rca_correlacion']='¿Qué transacciones publicadas por el monitor llegaron al scoreboard, cuáles faltan o difieren y qué evidencia permite comprobarlo?'
    obj['historial_adecuacion']={'version':'1.2','fecha':'2026-10-30','motivo':'Ruta técnica vigente y prioridad de fuentes; aprobación del estudiante en esta conversación.',
        'cambios':['Observabilidad y aceptación separadas del resultado funcional.','UVM_TESTNAME/RNTST con procedencia.','Warnings como pistas; selección parcial conservada.']}
    return obj

ADENDA='''

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
'''

def adecuar_guia(text):
    text=text.split('\n17. Adecuación vigente:')[0]
    text=text.replace('Versión 1.1','Versión 1.2').replace('LOCAL-PF-1.0','LOCAL-PF-1.1').replace('LOCAL-REF-1.0','LOCAL-REF-1.1')
    text=text.replace('Resultado propuesto: PASS bajo el criterio local de esta muestra mínima (estímulo y comparación coincidente, sin errores y con cierre); ejecución COMPLETA.',
        'Resultado funcional vigente: INDETERMINADO. Estímulo y comparación coincidente son hechos, pero falta marcador explícito de éxito global o excepción documentada; ejecución COMPLETA. Correlación monitor → scoreboard: NOT_OBSERVABLE.')
    text=text.replace('C02: cuatro eventos; PASS acotado a estímulo/comparación, una relación candidata, nombre de test y seed no observados.',
        'C02: cuatro eventos; INDETERMINADO funcional por falta de marcador explícito de éxito global o excepción validada; relación candidata de estímulo/comparación que no acredita transporte monitor → scoreboard; test y seed no observados.')
    text=text.replace('Resultado propuesto: PASS para el propósito acotado de ejecutar simple_test y obtener su marcador de éxito; ejecución COMPLETA.',
        'Resultado funcional: PASS por el marcador SUCCESS y cierre; ejecución COMPLETA. No acredita correlación de transporte; si se exige para aceptación, ésta es INDETERMINADA.')
    text=text.replace('Resultado: PASS para esa prueba; ejecución COMPLETA.',
        'Resultado funcional: PASS para esa prueba; ejecución COMPLETA. La aceptación es INDETERMINADA si se exige correlación monitor → scoreboard no observable.')
    text=text.replace('annotation_version: versión de la convención de anotación (1.1).','annotation_version: versión de la convención de anotación (1.2).')
    return text.rstrip()+'\n'+ADENDA

def guardar_guia(text):
    (HERE/'guia_etiquetado_actualizada.md').write_text(text,encoding='utf-8')
    sections=[]
    for part in re.split(r'(?=^\d+\. )',text,flags=re.M):
        if part.strip():
            title,_,body=part.strip().partition('\n')
            sections.append({'titulo':title,'contenido':body})
    obj={'guide_version':'1.2','fecha':'2026-10-30','titulo':'Guía paso a paso para almacenar y elaborar cinco fichas UVM',
         'representacion_legible':'guia_etiquetado_actualizada.md','ambito':'Semana 1: anotación manual, observabilidad y política; sin implementación de correlación.',
         'secciones':sections,'fichas':['etiquetas/'+p.name for p in sorted((HERE/'etiquetas').glob('C*.json'))]}
    (HERE/'guia_etiquetado_actualizada.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    backup=HERE/'historial'/'antes_adecuacion_1_2'
    backup.mkdir(parents=True,exist_ok=True)
    paths=list((HERE/'etiquetas').glob('C*.json'))+[HERE/'guia_etiquetado_actualizada.md',HERE/'guia_etiquetado_actualizada.json',HERE/'contexto_semana_1.txt',HERE/'verificacion_fichas.json']
    for p in paths:
        dest=backup/p.relative_to(HERE)
        if p.exists() and not dest.exists():
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(p,dest)
    for p in sorted((HERE/'etiquetas').glob('C*.json')):
        obj=adecuar_ficha(json.loads(p.read_text(encoding='utf-8')))
        p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    guardar_guia(adecuar_guia((HERE/'guia_etiquetado_actualizada.md').read_text(encoding='utf-8')))
    context=HERE/'contexto_semana_1.txt'
    text=context.read_text(encoding='utf-8-sig')
    text=text.split('\n6. ADECUACIÓN VIGENTE DEL 30-10-2026')[0]
    text=text.replace('Versión: 1.0.','Versión: 1.1; actualización del 30 de octubre de 2026.').replace('LOCAL-PF-1.0','LOCAL-PF-1.1').replace('LOCAL-REF-1.0','LOCAL-REF-1.1')
    text=text.replace('c) Ausencia de fallos no esperados', 'c) Ausencia de fallos no esperados')
    text=text.replace('Para scoreboard sv-tests: estímulo observado + comparación coincidente que define el propósito de esa muestra + resumen 0/0 + cierre.',
        'Para scoreboard sv-tests: la comparación aislada y resumen 0/0 no bastan para PASS sin marcador explícito global o excepción documentada; C02 queda INDETERMINADO.')
    # La frase previa tiene otra capitalización en algunas ediciones.
    text=text.replace('Para sv-tests simple_test: SUCCESS de llamada al test + resumen 0/0 + cierre. Para scoreboard sv-tests: estímulo observado + comparación coincidente que define el propósito de esa muestra + resumen 0/0 + cierre.',
        'Para sv-tests simple_test: SUCCESS de llamada al test + resumen 0/0 + cierre. Para scoreboard sv-tests C02: comparación coincidente y cierre no bastan sin marcador explícito global o excepción validada; resultado INDETERMINADO.')
    text+='\n6. ADECUACIÓN VIGENTE DEL 30-10-2026\nEsta sección prevalece sobre formulaciones previas del contexto.\n'+ADENDA.split('\n17. Adecuación vigente: correlación y prioridad de fuentes (versión 1.2)\n',1)[1]
    text+='\nP2 actualizada: «Tomando el evento seleccionado, ¿qué otros eventos podrían pertenecer al mismo incidente y qué evidencia permite relacionarlos o separarlos? En particular, ¿qué transacciones publicadas por el monitor llegaron al scoreboard, cuáles faltan o difieren y qué evidencia de ambos extremos permite comprobarlo? Distinguir asociación candidata, transporte comprobado y causa raíz; indicar ambigüedades y datos faltantes».\n'
    context.write_text(text,encoding='utf-8')
    checks=[]
    for p in sorted((HERE/'etiquetas').glob('C*.json')):
        o=json.loads(p.read_text(encoding='utf-8')); src=(p.parent/o['fuente']['log_file']).resolve()
        assert hashlib.sha256(src.read_bytes()).hexdigest()==o['fuente']['sha256_local']
        lines=src.read_text(encoding='utf-8-sig').splitlines(); ids={e['event_id'] for e in o['eventos']}
        assert len(ids)==len(o['eventos'])
        for e in o['eventos']+o['agregados']:
            a,b=e['log_line_start'],e['log_line_end']; assert 1<=a<=b<=len(lines)
            assert e['texto_original']=='\n'.join(lines[a-1:b])
        for r in o['relaciones']: assert set(r['miembros'])<=ids
        for entries in [o['metadatos']['identificacion_test']['uvm_testname_comando'],o['metadatos']['identificacion_test']['rntst']]:
            for e in entries: assert e['texto_original']==lines[e['linea_log']-1]
        assert o['observabilidad_monitor_scoreboard']['estado_global']=='NOT_OBSERVABLE'
        assert not o['cobertura_anotacion']['habilitada_para_validar_totales']
        checks.append({'archivo':p.name,'eventos':len(ids),'funcional':o['resultado']['funcional'],
                       'correlacion':'NOT_OBSERVABLE','aceptacion_si_obligatoria':o['resultado']['aceptacion_con_correlacion_obligatoria'],
                       'hash_fragmentos_identificadores_metadatos':'verificados'})
    report={'fecha':'2026-10-30','version':'1.2','alcance':'Integridad documental; no certifica exhaustividad, causalidad ni revisión humana independiente.','resultados':checks}
    (HERE/'verificacion_fichas.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(checks,ensure_ascii=False,indent=2))
