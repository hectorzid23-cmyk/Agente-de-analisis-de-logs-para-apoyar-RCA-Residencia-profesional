"""Produce fixtures de ingestión; no simula hardware ni implementa el parser."""
import base64
import codecs
import hashlib
import json
import re
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
WORK = BASE.parent
CASES = []
SOURCES = []

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def put(path, data):
    target = BASE / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_bytes() != data:
        raise RuntimeError(f'Existe un archivo diferente; no se sobrescribe: {target}')
    target.write_bytes(data)

def add_case(name, data, source, operation, encoding=None, same_text=None,
             incomplete=False, malformed=False):
    path = 'casos/' + name
    put(path, data)
    CASES.append(dict(archivo=path, bytes=len(data), sha256=sha256(data),
                      fuente_id=source, transformacion=operation,
                      codificacion_conocida=encoding, grupo_texto_equivalente=same_text,
                      prefijo_truncado=incomplete, error_decodificacion_estricta=malformed))

downloads = json.loads((BASE / 'descargas_base64.json').read_text('utf-8'))
names = dict(axiPass='axi4_pass_original.log', axiFail='axi4_fail_original.log',
             riscBefore='riscv_before_fix_original.log', riscAfter='riscv_after_fix_original.log',
             vlEmpty='verilator_empty.mem.out', vlRuntime='verilator_assertions_original.out',
             vlEmptyDriver='verilator_readmem_driver.py')
published = {}
for item in downloads:
    data = base64.b64decode(item['content'])
    git_sha = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if git_sha != item['sha']:
        raise RuntimeError('SHA Git diferente en ' + item['key'])
    key = item['key']
    path = 'originales_publicados/' + names[key]
    put(path, data)
    published[key] = data
    SOURCES.append(dict(id=key, archivo=path, fuente=item['display_url'],
                        git_blob_sha=item['sha'], sha256=sha256(data), bytes=len(data),
                        salto_final=data.endswith((b'\n', b'\r')),
                        naturaleza='bytes publicados, sin recodificar ni normalizar'))

sv_info = json.loads((WORK/'fuentes_logs_revision/procedencia.json').read_text('utf-8'))
sv = next(x for x in sv_info['archivos'] if 'scoreboard' in x['archivo'])
risc_info = json.loads((WORK/'semana_1/fuentes/procedencia.json').read_text('utf-8'))
risc = next(x for x in risc_info if x['archivo'] == 'riscv_uvm_run.log')
selected = [('axi4_fail', published['axiFail'], 'axiFail')]
for key, path, info in [
    ('sv_scoreboard', WORK/'fuentes_logs_revision/muestras/uvm_scoreboard_monitor_agent_env.log', sv),
    ('riscv_uvm', WORK/'semana_1/fuentes/riscv_uvm_run.log', risc),
]:
    data = path.read_bytes()
    rel = 'bases_locales/' + key + '.log'
    put(rel, data)
    SOURCES.append(dict(id=key, archivo=rel, fuente=info.get('fuente', info.get('url')),
                        git_blob_sha=info['git_blob_sha'], sha256=sha256(data), bytes=len(data),
                        naturaleza='copia local previa; ver procedencia; no equivale a bytes stdout originales',
                        procedencia_previa=info))
    selected.append((key, data, key))

marker = '# FIXTURE SINTETICO DE CODIFICACION: simulación, señal, áéíóúñü, €\n'
for key, data, source_id in selected:
    text = data.decode('utf-8-sig', errors='strict').replace('\r\n', '\n').replace('\r', '\n')
    control = text.rstrip('\n') + '\n'
    raw = control.encode('utf-8')
    group = key + '_texto_base'
    def emit(suffix, content, operation, enc='utf-8', **kw):
        add_case(key + '/' + suffix + '.log', content, source_id, operation, enc, **kw)
    emit('control_utf8_lf', raw, 'Normalización explícita LF y un salto final', same_text=group)
    emit('sin_salto_final', raw[:-1], 'Eliminar sólo el último byte LF del control')
    emit('control_utf8_crlf', control.replace('\n', '\r\n').encode(), 'Convertir LF a CRLF')
    encoded_text = marker + control
    egroup = key + '_con_marcador_sintetico'
    for label, enc in [('utf8_acentos', 'utf-8'), ('utf8_bom', 'utf-8-sig'),
                       ('utf16le_bom', 'utf-16-le'), ('utf16be_bom', 'utf-16-be'),
                       ('windows1252', 'cp1252')]:
        encoded = encoded_text.encode(enc, errors='strict')
        if enc == 'utf-16-le': encoded = codecs.BOM_UTF16_LE + encoded
        if enc == 'utf-16-be': encoded = codecs.BOM_UTF16_BE + encoded
        emit(label, encoded, 'Añadir comentario sintético idéntico con caracteres no ASCII y recodificar',
             enc, same_text=egroup)
    summary = control.find('--- UVM Report Summary ---')
    if summary < 0:
        raise RuntimeError('No hay resumen UVM en ' + key)
    emit('truncado_antes_resumen', control[:summary].encode(),
         'Conservar prefijo exacto del control hasta antes de los conteos del resumen', incomplete=True)
    events = list(re.finditer(r'(?m)^(?:#\s*)?UVM_(?:INFO|WARNING|ERROR|FATAL)\b[^\n]*', control))
    event = next((m for m in events if re.match(r'^(?:#\s*)?UVM_ERROR\b', m.group())), events[0])
    cut = event.start() + max(1, len(event.group()) // 2)
    emit('truncado_mitad_mensaje', control[:cut].encode(),
         'Cortar por caracteres dentro de una línea UVM (preferir primer ERROR si existe)', incomplete=True)
    emit('truncado_despues_evento', control[:event.end()].encode() + b'\n',
         'Conservar primer ERROR completo si existe; en otro caso primer evento UVM completo', incomplete=True)
    bad = bytearray(raw)
    bad[len(bad)//2] = 0xff
    emit('utf8_byte_invalido', bytes(bad), 'Sustituir un byte interior por FF', malformed=True)
    odd = codecs.BOM_UTF16_LE + encoded_text.encode('utf-16-le')
    emit('utf16le_truncado_un_byte', odd[:-1], 'Eliminar último byte de UTF-16LE, dejando unidad incompleta',
         'utf-16-le', incomplete=True, malformed=True)

add_case('especiales/vacio.log', b'', None, 'Archivo sintético de cero bytes')
add_case('especiales/solo_bom_utf8.log', codecs.BOM_UTF8, None, 'BOM sin contenido; no es cero bytes', 'utf-8-sig')
add_case('especiales/solo_espacios.log', b' \t\r\n\n', None, 'Sólo espacios y saltos', 'utf-8')
prefix = '# FIXTURE SINTETICO: señal'.encode('utf-8')
pos = prefix.index('ñ'.encode('utf-8'))
add_case('especiales/utf8_truncado_multibyte.log', prefix[:pos+1], None,
         'Corte sintético dentro de la secuencia UTF-8 de ñ', 'utf-8', incomplete=True, malformed=True)

manifest = dict(fecha='2026-11-04', version=1, fuentes=SOURCES, casos=CASES,
                nota='No son nuevas corridas. Derivados controlados para ingestión y límites de evidencia; no se ejecutó parser.')
put('manifest.json', (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode())

# Verificación independiente de lectura, contenido, equivalencia y límites.
groups = {}
for case in CASES:
    b = (BASE/case['archivo']).read_bytes()
    assert sha256(b) == case['sha256'] and len(b) == case['bytes']
    enc = case['codificacion_conocida']
    if enc:
        codec = 'utf-16' if enc.startswith('utf-16') else enc
        try:
            decoded = b.decode(codec, errors='strict')
        except UnicodeDecodeError:
            assert case['error_decodificacion_estricta'], case['archivo']
        else:
            assert not case['error_decodificacion_estricta'], case['archivo']
            if case['grupo_texto_equivalente']:
                groups.setdefault(case['grupo_texto_equivalente'], []).append(decoded)
    if case['archivo'].endswith('/sin_salto_final.log'):
        assert not b.endswith((b'\r', b'\n'))
    if case['archivo'].endswith('/truncado_antes_resumen.log'):
        assert b'--- UVM Report Summary ---' not in b
    if case['archivo'].endswith('/control_utf8_crlf.log'):
        assert b'\n' not in b.replace(b'\r\n', b'')
for values in groups.values():
    assert all(v == values[0] for v in values)
assert (BASE/'casos/especiales/vacio.log').stat().st_size == 0
qa = dict(casos=len(CASES), fuentes=len(SOURCES), grupos_equivalencia=len(groups),
          verificacion='OK', alcance='Bytes, hashes, decodificación estricta y equivalencia. No evalúa el parser.',
          casos_invalidos=sum(c['error_decodificacion_estricta'] for c in CASES))
put('verificacion.json', (json.dumps(qa, ensure_ascii=False, indent=2)+'\n').encode())

archive = BASE / 'casos_robustez_logs.zip'
paths = sorted([p for p in BASE.rglob('*') if p.is_file() and p.suffix != '.zip'])
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in paths:
        z.write(path, path.relative_to(BASE))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for case in CASES:
        assert sha256(z.read(case['archivo'])) == case['sha256']
print(json.dumps(qa, ensure_ascii=False))
