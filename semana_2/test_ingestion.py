import hashlib
import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from jsonschema import Draft202012Validator
from semana_2.ingestion import ingest_log

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validator(name):
    schema = load(HERE / "esquemas" / (name + ".schema.json"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


class IngestionTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.storage = Path(tmp.name)
        self.response = validator("ingestion")
        self.line = validator("linea")

    def check_case(self, folder, case):
        source = folder / case["archivo"]
        raw = source.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), case["sha256"])
        self.assertEqual(len(raw), case["bytes"])
        enc = case.get("codificacion_conocida", case.get("codificacion"))
        cut = case.get("prefijo_truncado", False)
        bad = case.get("error_decodificacion_estricta", False)
        out = ingest_log(source, allowed_root=folder, storage=self.storage,
                         metadata={"encoding": enc, "known_truncated": cut})
        self.response.validate(out)
        run = self.storage / out["run_id"]
        self.assertEqual(load(run / "manifest.json"), out)
        p = out["provenance"][0]
        self.assertEqual((run / p["snapshot"]).read_bytes(), raw)
        self.assertEqual(p["sha256"], case["sha256"])
        self.assertEqual(p["log_file"], case["archivo"])
        codes = {w["code"] for w in out["warnings"]}
        self.assertEqual("decode_error" in codes, bad)
        self.assertEqual("known_truncated" in codes, cut)
        self.assertEqual(out["status"], "partial" if bad or cut or "test_name_conflict" in codes else "ok")
        if bad:
            self.assertIsNone(p["records"])
            self.assertEqual(p["line_count"], 0)
            self.assertFalse(list(run.glob("*.jsonl")))
            return None
        codec = "utf-16" if (enc or "").startswith("utf-16") else enc or "utf-8"
        expected = list(io.StringIO(raw.decode(codec), newline=""))
        records = [json.loads(line) for line in (run / p["records"]).read_text(encoding="utf-8").split("\n") if line]
        self.assertEqual(p["line_count"], len(expected))
        self.assertEqual(out["data"]["lines"], len(expected))
        self.assertEqual(p["final_newline"], expected[-1].endswith(("\n", "\r")) if expected else None)
        if "salto_final" in case:
            self.assertEqual(bool(p["final_newline"]), case["salto_final"])
        self.assertEqual(len(records), len(expected))
        for number, (row, original) in enumerate(zip(records, expected), 1):
            self.line.validate(row)
            self.assertEqual((row["log_line_start"], row["log_line_end"]), (number, number))
            self.assertEqual(row["texto_original"] + row["terminador"], original)
            self.assertEqual(row["event_id"], f'{out["run_id"]}:{p["file_id"]}:{number}')
        for observation in out["data"]["test_name_observations"]:
            self.assertIn("+UVM_TESTNAME=", expected[observation["line"]-1])
            self.assertEqual(observation["event_id"], records[observation["line"]-1]["event_id"])
        for evidence in case.get("evidencia", []):
            for mention in evidence["apariciones"]:
                self.assertEqual(records[mention["linea"]-1]["texto_original"], mention["texto"])
        return expected

    def test_43_robustez(self):
        folder = ROOT / "pruebas_robustez_logs"
        cases = load(folder / "manifest.json")["casos"]
        self.assertEqual(len(cases), 43)
        groups = {}
        for case in cases:
            with self.subTest(case=case["archivo"]):
                lines = self.check_case(folder, case)
                group = case["grupo_texto_equivalente"]
                if group:
                    self.assertEqual(lines, groups.setdefault(group, lines))

    def test_8_funcionales_y_2_controles_solo_lectura(self):
        folder = ROOT / "pruebas_funcionales_logs"
        cases = load(folder / "manifest.json")["casos"]
        self.assertEqual(len(cases), 10)
        for case in cases:
            with self.subTest(case=case["archivo"]):
                self.assertEqual(case["esperado"]["lectura"], "OK")
                self.assertIsNotNone(self.check_case(folder, case))

    def test_fichas_semana_1(self):
        directory = ROOT / "semana_1" / "etiquetas"
        cases = sorted(directory.glob("C*.json"))
        self.assertEqual(len(cases), 5)
        total = 0
        for path in cases:
            with self.subTest(case=path.name):
                case = load(path)
                source = (directory / case["fuente"]["log_file"]).resolve()
                out = ingest_log(source, allowed_root=ROOT, storage=self.storage)
                self.response.validate(out)
                p = out["provenance"][0]
                self.assertEqual(p["sha256"], case["fuente"]["sha256_local"])
                rows = [json.loads(s) for s in (self.storage / out["run_id"] / p["records"]).read_text(encoding="utf-8").split("\n") if s]
                for event in case["eventos"]:
                    start, end = event["log_line_start"], event["log_line_end"]
                    self.assertEqual("\n".join(row["texto_original"] for row in rows[start-1:end]),
                                     event["texto_original"])
                    total += 1
        self.assertEqual(total, 24)

    def test_autorizacion_y_publicacion(self):
        root = self.storage / "entrada"
        root.mkdir()
        outdir = self.storage / "salida"
        outside = self.storage / "externo.log"
        outside.write_text("externo", encoding="utf-8")
        denied = ingest_log("../externo.log", allowed_root=root, storage=outdir)
        self.response.validate(denied)
        self.assertEqual(denied["status"], "invalid_input")
        self.assertFalse(outdir.exists())
        for i in (1, 2):
            (root / f"{i}.log").write_text(f'+UVM_TESTNAME="test_{i}"', encoding="utf-8")
        kwargs = dict(allowed_root=root, storage=outdir)
        a = ingest_log(["1.log", "2.log"], **kwargs)
        b = ingest_log(["1.log", "2.log"], **kwargs)
        self.response.validate(a)
        self.assertNotEqual(a["run_id"], b["run_id"])
        self.assertIsNone(a["test_name"])
        self.assertEqual(a["status"], "partial")
        self.assertEqual({x["value"] for x in a["data"]["test_name_observations"]}, {"test_1", "test_2"})
        self.assertNotIn("known_truncated", {w["code"] for w in a["warnings"]})
        self.assertEqual(ingest_log("1.log", **kwargs)["test_name"], "test_1")

    def test_bom_automatico_y_terminadores_mixtos(self):
        root = self.storage / "entrada"
        root.mkdir()
        source = root / "mixto.log"
        source.write_bytes("señal\r\n\rtexto\nfin".encode("utf-16"))
        out = ingest_log(source, allowed_root=root, storage=self.storage / "salida")
        self.response.validate(out)
        p = out["provenance"][0]
        self.assertEqual(out["status"], "ok")
        self.assertIn(p["encoding"], {"utf-16-le", "utf-16-be"})
        self.assertIs(p["final_newline"], False)
        rows = [json.loads(s) for s in (self.storage / "salida" / out["run_id"] / p["records"]).read_text(encoding="utf-8").split("\n") if s]
        self.assertEqual([(x["texto_original"], x["terminador"]) for x in rows],
                         [("señal", "\r\n"), ("", "\r"), ("texto", "\n"), ("fin", "")])


if __name__ == "__main__":
    unittest.main()
