"""Demostración de captura: las etiquetas son referencias del manifiesto, no predicciones."""
import argparse
import hashlib
import json
from pathlib import Path

from semana_2.ingestion import ingest_log

FILES = {
    "PASS": "N01_pass_limpio.log",
    "FAIL": "F01_error_scoreboard.log",
    "INDETERMINADO": "I01_error_herramienta.log",
}
EVIDENCE = {
    "PASS": ("TEST PASSED",),
    "FAIL": ("UVM_ERROR fixture_scoreboard", "TEST FAILED"),
    "INDETERMINADO": ("License checkout failed", "Simulation was not started"),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("caso", choices=FILES)
    label = parser.parse_args().caso
    root = Path(__file__).resolve().parent.parent
    corpus = root / "pruebas_funcionales_logs"
    storage = root / "semana_2" / "demostracion_manual" / label
    name = "casos/" + FILES[label]
    manifest = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
    case = next(c for c in manifest["casos"] if c["archivo"] == name)
    result = ingest_log(name, allowed_root=corpus, storage=storage,
                        metadata={"encoding": case["codificacion"]})
    if result["status"] != "ok":
        parser.exit(1, json.dumps(result, ensure_ascii=False) + "\n")
    p = result["provenance"][0]
    run = storage / result["run_id"]
    rows = [json.loads(line) for line in (run / p["records"]).read_text(encoding="utf-8").split("\n") if line]
    evidence = [
        {"event_id": row["event_id"], "linea": row["log_line_start"], "texto": row["texto_original"]}
        for row in rows if any(marker in row["texto_original"] for marker in EVIDENCE[label])
    ]
    digest = hashlib.sha256((run / p["snapshot"]).read_bytes()).hexdigest()
    summary = dict(
        resultado_funcional_de_referencia=case["esperado"]["resultado_funcional"],
        status_ingestion=result["status"], run_id=result["run_id"], test_name=result["test_name"],
        lineas=p["line_count"], hash_coincide=(digest == p["sha256"] == case["sha256"]),
        evidencia_capturada=evidence, warnings_ingestion=result["warnings"],
        carpeta_salida=str(run),
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["hash_coincide"] and evidence else 1


if __name__ == "__main__":
    raise SystemExit(main())
