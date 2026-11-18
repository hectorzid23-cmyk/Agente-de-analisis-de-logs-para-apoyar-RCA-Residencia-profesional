"""Captura local de logs. Cada registro provisional representa una línea física."""
import codecs
import hashlib
import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4
from semana_2.patrones_ingestion import scan, verbosity

SCHEMA_VERSION = "1.1"
INVALID_UTF8 = re.compile(r"[\udc80-\udcff]+")
ENCODINGS = {"utf-8", "utf-8-sig", "utf-16-le", "utf-16-be", "cp1252"}



def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ingest_log(paths, *, allowed_root, storage, metadata=None):
    """Ingiere archivos locales bajo una raíz autorizada; un llamado registra una corrida."""
    result = dict(schema_version=SCHEMA_VERSION, status="invalid_input", run_id=None,
                  test_name=None, query={"operation": "ingest_log"}, data=None,
                  warnings=[], provenance=[])
    try:
        root = Path(allowed_root).resolve(strict=True)
        if isinstance(paths, (str, Path)):
            paths = [paths]
        paths = list(paths)
        metadata = {} if metadata is None else metadata
        if not isinstance(metadata, dict) or set(metadata) - {"encoding", "known_truncated"}:
            raise ValueError("Metadatos permitidos: encoding y known_truncated")
        encoding = metadata.get("encoding")
        truncated = metadata.get("known_truncated", False)
        if encoding is not None and encoding not in ENCODINGS:
            raise ValueError("Codificación no admitida")
        if type(truncated) is not bool or not paths or not root.is_dir():
            raise ValueError("Se requiere una raíz, archivos y un indicador booleano válido")
        sources = []
        for name in paths:
            source = (root / name).resolve(strict=True)
            if not source.is_relative_to(root) or not source.is_file():
                raise ValueError("Entrada fuera de la raíz autorizada o no es archivo")
            sources.append(source)
        if len(set(sources)) != len(sources):
            raise ValueError("Ruta duplicada")
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        result["warnings"].append({"code": "invalid_input", "message": str(exc)})
        return result

    run = "R-" + uuid4().hex
    base = Path(storage).resolve()
    base.mkdir(parents=True, exist_ok=True)
    observations, levels, finishes, successes, failures = [], [], [], [], []
    with TemporaryDirectory(dir=base) as temp:
        stage = Path(temp) / run
        stage.mkdir()
        for i, source in enumerate(sources, 1):
            file_id = f"F{i:04}"
            snapshot = f"{file_id}.log"
            records = f"{file_id}.jsonl"
            rel = source.relative_to(root).as_posix()
            digest = hashlib.sha256()
            size = 0
            with source.open("rb") as src, (stage / snapshot).open("xb") as dst:
                for chunk in iter(lambda: src.read(1024 * 1024), b""):
                    digest.update(chunk)
                    size += len(chunk)
                    dst.write(chunk)
            with (stage / snapshot).open("rb") as src:
                prefix = src.read(4)
            bom_encoding = next((enc for bom, enc in (
                (codecs.BOM_UTF8, "utf-8-sig"),
                (codecs.BOM_UTF16_LE, "utf-16-le"),
                (codecs.BOM_UTF16_BE, "utf-16-be"),
            ) if prefix.startswith(bom)), None)
            enc = encoding or bom_encoding or "utf-8"
            count, final, nonblank = 0, None, False
            spans = None

            def warn(code, message, **location):
                result["warnings"].append(dict(code=code, message=message, file_id=file_id, **location))

            if truncated:
                warn("known_truncated", "Recorte declarado por el llamador; no inferido del salto final.")
            try:
                if bom_encoding and encoding and encoding != bom_encoding and not (
                    bom_encoding == "utf-8-sig" and encoding == "utf-8"
                ):
                    raise UnicodeError("BOM incompatible con codificación indicada")
                if bom_encoding == "utf-8-sig":
                    enc = "utf-8-sig"
                # Preserve invalid bytes temporarily to report offsets in the snapshot.
                tolerant = encoding is None and bom_encoding is None
                byte_offset = 0
                with (stage / snapshot).open(encoding=enc, errors="surrogateescape" if tolerant else "strict",
                                             newline="") as src, (
                    stage / records
                ).open("x", encoding="utf-8", newline="\n") as out:
                    for count, line in enumerate(src, 1):
                        if count == 1 and bom_encoding in {"utf-16-le", "utf-16-be"}:
                            line = line.removeprefix("\ufeff")
                            if not line:
                                count = 0
                                continue
                        body = line.rstrip("\r\n")
                        if "\x00" in body:
                            raise UnicodeError("NUL en texto: codificación desconocida o archivo no textual")
                        final = bool(line[len(body):])
                        nonblank |= bool(body.strip())
                        event_id = f"{run}:{file_id}:{count}"
                        record = dict(schema_version=SCHEMA_VERSION, kind="raw_line", run_id=run,
                                      event_id=event_id, file_id=file_id, log_file=rel,
                                      log_line_start=count, log_line_end=count, texto_original=body,
                                      terminador=line[len(body):])
                        if tolerant:
                            previous = 0
                            offset = byte_offset
                            for bad in INVALID_UTF8.finditer(body):
                                offset += len(body[previous:bad.start()].encode("utf-8"))
                                length = bad.end() - bad.start()
                                warn("decode_replacement", "Bytes inválidos en UTF-8; la línea se conserva con sustitución.",
                                     line=count, byte_offset=offset, byte_length=length)
                                offset += length
                                previous = bad.end()
                            byte_offset += len(line.encode("utf-8", errors="surrogateescape"))
                            if previous:
                                record["decoding_lossy"] = True
                                record["texto_original"] = INVALID_UTF8.sub("\ufffd", body)
                        out.write(json.dumps(record, ensure_ascii=False) + "\n")
            except UnicodeError as exc:
                (stage / records).unlink(missing_ok=True)
                records, count, final = None, 0, None
                warn("decode_error", str(exc))
            else:
                if not nonblank:
                    warn("empty_content", "No hay texto significativo; se conservan las líneas físicas.")
                if final is False:
                    warn("no_final_newline", "Última línea sin terminador; no prueba truncamiento.")
                spans = f"{file_id}.multiline.jsonl"
                for dst, found in zip((observations, levels, finishes, successes, failures),
                                      scan(stage / records, stage / spans)):
                    dst.extend(found)
            result["provenance"].append(dict(file_id=file_id, log_file=rel, snapshot=snapshot,
                records=records, multiline_records=spans, sha256=digest.hexdigest(), bytes=size, encoding=enc,
                line_count=count, final_newline=final, known_truncated=truncated))
        preferred = [x for x in observations if x["source"] == "RNTST"] or observations
        values = {x["value"] for x in preferred}
        if len({x["value"] for x in observations}) > 1:
            result["warnings"].append(dict(code="test_name_conflict",
                                           message="Se conservan todos los nombres discrepantes."))
        incomplete = any(w["code"] in {"decode_error", "decode_replacement", "known_truncated", "test_name_conflict", "empty_content"}
                         for w in result["warnings"])
        # Sin un único archivo no se presupone que las evidencias correspondan al mismo test.
        functional = "FAIL" if failures else "PASS" if len(sources)==1 and any(a['line'] < b['line'] for a in successes for b in finishes) and not incomplete else "INDETERMINADO"
        result.update(run_id=run, test_name=next(iter(values)) if len(values)==1 else None,
                      status="partial" if any(w["code"] in {"decode_error", "decode_replacement", "known_truncated", "test_name_conflict"}
                                              for w in result["warnings"]) else "ok",
                      data=dict(files_processed=len(sources),
                                lines=sum(x["line_count"] for x in result["provenance"]),
                                test_name_observations=observations,
                                verbosity=verbosity(levels),
                                finish=dict(count=len(finishes), evidence=finishes),
                                functional_evidence=dict(result=functional, success=successes, failures=failures),
                                format_hint="uvm" if observations else "unknown"))
        write_json(stage / "manifest.json", result)
        stage.rename(base / run)
    return result
