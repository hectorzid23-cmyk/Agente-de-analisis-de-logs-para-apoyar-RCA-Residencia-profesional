"""Prepara datos de prueba funcionales; no ejecuta simulaciones ni el parser."""
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent
CASES = []

def sha(data):
    return hashlib.sha256(data).hexdigest()

def write(path, data):
    dest = ROOT/path
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.read_bytes() != data:
        raise RuntimeError(f'No sobrescribir archivo diferente: {dest}')
    dest.write_bytes(data)

def summary(info, warning=0, error=0, fatal=0):
    return f'''# --- UVM Report Summary ---
# ** Report counts by severity
# UVM_INFO : {info}
# UVM_WARNING : {warning}
# UVM_ERROR : {error}
# UVM_FATAL : {fatal}
'''

def add(key, title, body, result, counts, correlation, purpose, evidence_ids,
        ending='complete', pairs=None, failures=None):
    text = '# FIXTURE SINTETICO: no procede de una simulacion ni de un repositorio externo.\n'
    text += '# Referencias fixture_*.sv ficticias; unidad de tiempo de este escenario: ns.\n'
    text += f'# +UVM_TESTNAME={key} -sv_seed 1\n' + body
    path = f'casos/{key}.log'
    write(path, text.encode('utf-8'))
    lines = text.splitlines()
    records = []
    for token in evidence_ids:
        hits = [dict(linea=i, texto=line) for i,line in enumerate(lines,1) if token in line]
        if not hits:
            raise RuntimeError(f'Evidencia ausente {key}: {token}')
        records.append(dict(identificador=token, apariciones=hits))
    CASES.append(dict(case_id=key,titulo=title,archivo=path,naturaleza='sintetico_controlado',
                      objetivo=purpose, sha256=sha(text.encode()),bytes=len(text.encode()),
                      codificacion='utf-8',salto_final=True,referencias_fuente='nombres ficticios, no archivos reales',
                      esperado=dict(lectura='OK',resultado_funcional=result,
                                    estado_ejecucion=ending,conteos_eventos_uvm=counts,
                                    correlacion_monitor_scoreboard=correlation,
                                    pares=pairs,incidentes=failures,
                                    aceptacion_si_correlacion_es_obligatoria=(result if correlation in ('MATCH','DIVERGENCE') or result=='FAIL' else 'INDETERMINADO')),
                      evidencia=records))

add('N01_pass_limpio','Prueba completa exitosa sin warnings',
'''# UVM_INFO fixture_test.sv(10) @ 0: uvm_test_top [RNTST] Running test N01_pass_limpio...
# UVM_INFO fixture_checker.sv(20) @ 20: uvm_test_top.env.checker [CHECK_OK] expected=0x2a observed=0x2a
# UVM_INFO fixture_test.sv(30) @ 30: uvm_test_top [TEST_RESULT] TEST PASSED
'''+summary(3)+'''# ** Note: $finish
# End time: 00:00:01; fixture run closed
''','PASS',dict(INFO=3,WARNING=0,ERROR=0,FATAL=0),'NOT_OBSERVABLE',
'Exigir evidencia positiva y cierre; no inferir correlacion de un CHECK_OK.',
['[CHECK_OK]','[TEST_RESULT]'])

add('N02_pass_con_warning','Prueba exitosa con una advertencia',
'''# UVM_INFO fixture_test.sv(10) @ 0: uvm_test_top [RNTST] Running test N02_pass_con_warning...
# UVM_WARNING fixture_monitor.sv(12) @ 5: uvm_test_top.env.monitor [WARMUP] First sample ignored during documented warmup
# UVM_INFO fixture_checker.sv(20) @ 20: uvm_test_top.env.checker [CHECK_OK] expected=0x11 observed=0x11
# UVM_INFO fixture_test.sv(30) @ 30: uvm_test_top [TEST_RESULT] TEST PASSED
'''+summary(3,warning=1)+'''# ** Note: $finish
# End time: 00:00:01; fixture run closed
''','PASS',dict(INFO=3,WARNING=1,ERROR=0,FATAL=0),'NOT_OBSERVABLE',
'Conservar warning como evidencia sin convertir automaticamente la prueba en FAIL.',
['[WARMUP]','[CHECK_OK]','[TEST_RESULT]'])

add('N03_pass_transporte_match','Monitor y scoreboard con dos transacciones coincidentes',
'''# UVM_INFO fixture_test.sv(10) @ 0: uvm_test_top [RNTST] Running test N03_pass_transporte_match...
# UVM_INFO fixture_monitor.sv(40) @ 10: uvm_test_top.env.monitor [MON_PUBLISH] channel=req direction=write tid=17 occurrence=1 segment=0 data=0x2a
# UVM_INFO fixture_scoreboard.sv(50) @ 11: uvm_test_top.env.scoreboard [SCB_RECEIVE] channel=req direction=write tid=17 occurrence=1 segment=0 data=0x2a
# UVM_INFO fixture_monitor.sv(40) @ 20: uvm_test_top.env.monitor [MON_PUBLISH] channel=req direction=write tid=18 occurrence=1 segment=0 data=0x7f
# UVM_INFO fixture_scoreboard.sv(50) @ 21: uvm_test_top.env.scoreboard [SCB_RECEIVE] channel=req direction=write tid=18 occurrence=1 segment=0 data=0x7f
# UVM_INFO fixture_test.sv(60) @ 30: uvm_test_top [TRANSPORT_CLOSED] All publication and reception records emitted; no reset, flush or reordering
# UVM_INFO fixture_test.sv(70) @ 31: uvm_test_top [TEST_RESULT] TEST PASSED
'''+summary(7)+'''# ** Note: $finish
# End time: 00:00:01; fixture run closed
''','PASS',dict(INFO=7,WARNING=0,ERROR=0,FATAL=0),'MATCH',
'Emparejar por canal, sentido, TID, ocurrencia y segmento; comparar data y devolver ambas lineas.',
['[MON_PUBLISH]','[SCB_RECEIVE]','[TRANSPORT_CLOSED]'],pairs=[
dict(tid=17,occurrence=1,segment=0,resultado='matched'),
dict(tid=18,occurrence=1,segment=0,resultado='matched')])

add('F01_error_scoreboard','Dos discrepancias de bytes de un mismo beat',
'''# UVM_INFO fixture_test.sv(10) @ 0: uvm_test_top [RNTST] Running test F01_error_scoreboard...
# UVM_ERROR fixture_scoreboard.sv(80) @ 40: uvm_test_top.env.scoreboard [MISMATCH] beat=4 byte=0 address=0x100 expected=0xaa observed=0x11
# UVM_ERROR fixture_scoreboard.sv(80) @ 40: uvm_test_top.env.scoreboard [MISMATCH] beat=4 byte=1 address=0x101 expected=0xbb observed=0x22
# UVM_INFO fixture_scoreboard.sv(90) @ 50: uvm_test_top.env.scoreboard [CHECK_SUMMARY] mismatched_beats=1
# UVM_INFO fixture_test.sv(100) @ 51: uvm_test_top [TEST_RESULT] TEST FAILED
'''+summary(3,error=2)+'''# ** Note: $finish
# Errors: 0, Warnings: 0
# End time: 00:00:01; fixture run closed
''','FAIL',dict(INFO=3,WARNING=0,ERROR=2,FATAL=0),'NOT_OBSERVABLE',
'Contar dos mensajes de error y un beat; no duplicar el resumen ni atribuir causa raiz al agrupamiento.',
['[MISMATCH]','[CHECK_SUMMARY]','[TEST_RESULT]'],failures=[
dict(agrupacion_candidata='mismo_beat_4',mensajes_error=2,beats_incorrectos=1,causa_raiz='no_determinada')])

add('F02_fatal_configuracion','Fatal UVM por interfaz no configurada',
'''# UVM_INFO fixture_test.sv(10) @ 0: uvm_test_top [RNTST] Running test F02_fatal_configuracion...
# UVM_FATAL fixture_env.sv(15) @ 0: uvm_test_top.env [NOVIF] Virtual interface vif not configured
# ** Note: $finish requested by fatal handler
# End time: 00:00:01; fixture run closed after fatal
''','FAIL',dict(INFO=1,WARNING=0,ERROR=0,FATAL=1),'NOT_OBSERVABLE',
'Detectar fatal sin resumen UVM. Atribuirlo al entorno de prueba, no demostrar defecto del DUT.',
['[NOVIF]'],ending='TERMINADA_POR_FATAL',failures=[dict(tipo='configuracion_testbench',causa_raiz_dut='no_demostrada')])

add('F03_assertion_fallida','Assertion con aviso nativo y reporte UVM del mismo fallo',
'''# UVM_INFO fixture_test.sv(10) @ 0: uvm_test_top [RNTST] Running test F03_assertion_fallida...
# ** Error: Assertion req_ack failed. Time: 40 ns. Instance: /fixture_top/dut. File: fixture_assertions.sv Line: 25
# UVM_ERROR fixture_assertions.sv(25) @ 40: uvm_test_top [ASSERT_FAILED] req_ack failed at /fixture_top/dut
# UVM_INFO fixture_test.sv(30) @ 41: uvm_test_top [TEST_RESULT] TEST FAILED
'''+summary(2,error=1)+'''# ** Note: $finish
# End time: 00:00:01; fixture run closed
''','FAIL',dict(INFO=2,WARNING=0,ERROR=1,FATAL=0),'NOT_OBSERVABLE',
'Conservar dos registros de dominios distintos sin convertirlos en dos assertions independientes.',
['Assertion req_ack failed','[ASSERT_FAILED]'],failures=[dict(assertion='req_ack',fallos_assertion=1,registros_evidencia=2)])

add('F04_transporte_dato_alterado','Misma transaccion recibida con un campo diferente',
'''# UVM_INFO fixture_test.sv(10) @ 0: uvm_test_top [RNTST] Running test F04_transporte_dato_alterado...
# UVM_INFO fixture_monitor.sv(40) @ 10: uvm_test_top.env.monitor [MON_PUBLISH] channel=req direction=write tid=17 occurrence=1 segment=0 data=0x2a
# UVM_INFO fixture_scoreboard.sv(50) @ 11: uvm_test_top.env.scoreboard [SCB_RECEIVE] channel=req direction=write tid=17 occurrence=1 segment=0 data=0x2b
# UVM_ERROR fixture_checker.sv(60) @ 12: uvm_test_top.env.transport_checker [TRANSPORT_MISMATCH] tid=17 field=data published=0x2a received=0x2b
# UVM_INFO fixture_test.sv(70) @ 20: uvm_test_top [TRANSPORT_CLOSED] All publication and reception records emitted; no reset, flush or reordering
# UVM_INFO fixture_test.sv(80) @ 21: uvm_test_top [TEST_RESULT] TEST FAILED
'''+summary(5,error=1)+'''# ** Note: $finish
# End time: 00:00:01; fixture run closed
''','FAIL',dict(INFO=5,WARNING=0,ERROR=1,FATAL=0),'DIVERGENCE',
'No aceptar igualdad de conteos como igualdad de contenido: una publicacion y una recepcion con data distinta.',
['[MON_PUBLISH]','[SCB_RECEIVE]','[TRANSPORT_MISMATCH]'],pairs=[
dict(tid=17,occurrence=1,segment=0,resultado='field_mismatch',campo='data',publicado='0x2a',recibido='0x2b')])

add('I01_error_herramienta','No se ejecuto simulacion por falta de licencia',
'''# simulator launch requested for fixture_top
# Error: License checkout failed; required simulation license unavailable
# Simulation was not started
# Process exited with code 1
''','INDETERMINADO',dict(INFO=0,WARNING=0,ERROR=0,FATAL=0),'NOT_OBSERVABLE',
'Separar ERROR_HERRAMIENTA de FAIL funcional; el archivo es legible y esta completo como reporte del lanzamiento.',
['License checkout failed','Simulation was not started'],ending='ERROR_HERRAMIENTA')

# Referencias reales ya disponibles: copias exactas, no nuevas simulaciones.
old_manifest = json.loads((WORK/'pruebas_robustez_logs/manifest.json').read_text('utf-8'))
for key, source_id, case_file in [('R01_axi4_pass','axiPass','C04_axi4_pass.json'),
                                  ('R02_axi4_fail','axiFail','C03_axi4_fail.json')]:
    source = next(s for s in old_manifest['fuentes'] if s['id']==source_id)
    data = (WORK/'pruebas_robustez_logs'/source['archivo']).read_bytes()
    assert sha(data)==source['sha256']
    annotation_path = WORK/'semana_1/etiquetas'/case_file
    annotation = json.loads(annotation_path.read_text('utf-8'))
    dest = f'referencias_reales/{key}.log'
    write(dest,data)
    # La copia conserva las anotaciones de semana_1 como contexto, no como inventario exhaustivo.
    write(f'referencias_reales/{key}_anotacion_previa.json',annotation_path.read_bytes())
    CASES.append(dict(case_id=key,archivo=dest,naturaleza='copia_exacta_de_log_publicado',
                      sha256=sha(data),bytes=len(data),fuente=source,
                      esperado=dict(lectura='OK',resultado_funcional=annotation['resultado']['funcional'],
                                    correlacion_monitor_scoreboard='NOT_OBSERVABLE',
                                    aceptacion_si_correlacion_es_obligatoria='INDETERMINADO' if source_id=='axiPass' else 'FAIL'),
                      anotacion_previa=f'referencias_reales/{key}_anotacion_previa.json',
                      nota='Las rutas relativas dentro de la anotacion previa son las originales de semana_1; no reinterpretarlas desde esta copia. La anotacion es propuesta y no exhaustiva.'))

manifest=dict(version=1,fecha_preparacion='2026-11-04',
              fecha_nota='Fecha del contexto de sesion; no fecha de las simulaciones originales.',
              casos=CASES,reglas=dict(
                  normales='Exito funcional observado; no implica necesariamente ausencia de advertencias.',
                  fallidos='Fallo de verificacion o del entorno expresado en el log; no acredita causa raiz del DUT.',
                  separacion='Lectura, estado de ejecucion, resultado funcional y correlacion son dimensiones diferentes.',
                  alcance='Fixtures para desarrollo; no benchmark independiente ni evidencia industrial nueva.'))
write('manifest.json',(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode())

checks=[]
for case in CASES:
    data=(ROOT/case['archivo']).read_bytes()
    assert sha(data)==case['sha256']
    if case['naturaleza']=='sintetico_controlado':
        text=data.decode('utf-8',errors='strict')
        actual={s:len(re.findall(r'^# UVM_'+s+r'\b(?!\s*:).*$',text,re.M)) for s in ['INFO','WARNING','ERROR','FATAL']}
        assert actual==case['esperado']['conteos_eventos_uvm'],(case['case_id'],actual)
        assert data.endswith(b'\n') and b'\xef\xbb\xbf' not in data[:3]
        if case['esperado']['correlacion_monitor_scoreboard'] in ('MATCH','DIVERGENCE'):
            pubs=re.findall(r'^# UVM_INFO .*\[MON_PUBLISH\] (.+)$',text,re.M)
            recvs=re.findall(r'^# UVM_INFO .*\[SCB_RECEIVE\] (.+)$',text,re.M)
            assert len(pubs)==len(recvs)>0
            if case['esperado']['correlacion_monitor_scoreboard']=='MATCH': assert pubs==recvs
            else: assert pubs!=recvs
    checks.append(dict(case_id=case['case_id'],sha256=case['sha256'],estado='OK'))
write('verificacion.json',(json.dumps(dict(estado='OK',casos=len(CASES),sinteticos=8,referencias_reales=2,
                                          alcance='Integridad y coherencia de fixtures; parser no ejecutado.',
                                          comprobaciones=checks),ensure_ascii=False,indent=2)+'\n').encode())
zpath=ROOT/'casos_funcionales_logs.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(ROOT.rglob('*')):
        if p.is_file() and p.suffix!='.zip': z.write(p,p.relative_to(ROOT))
with zipfile.ZipFile(zpath) as z:
    assert z.testzip() is None
    for case in CASES: assert sha(z.read(case['archivo']))==case['sha256']
print(json.dumps(dict(casos=len(CASES),sinteticos=8,referencias_reales=2,verificacion='OK')))
