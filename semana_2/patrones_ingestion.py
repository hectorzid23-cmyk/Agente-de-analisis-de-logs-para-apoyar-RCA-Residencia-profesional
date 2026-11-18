"""Patrones y evidencias de las correcciones de semana 2."""
import json
import re

TEST = re.compile(r"""\bUVM_TESTNAME=("[^"]+"|'[^']+'|[^\s"']+)""")
RNTST = re.compile(r"\bUVM_INFO\b.*?\[RNTST\]\s+Running test\s+(\S+?)\s*\.{3}\s*$")
VERB = re.compile(r"\bUVM_VERBOSITY=(UVM_\w+|\d+)\b", re.I)
OVERRIDE = re.compile(r"\+uvm_set_verbosity=([^,\s]+),([^,\s]+),(UVM_\w+|\d+),([^\s\"']+)", re.I)
HEADER = re.compile(r"^(?:# ?)?\s*(UVM_INFO\b(?!\s*:)|DISPLAY:|\[DISPLAY\])", re.I)
CONT = re.compile(r"^(?:# ?)?[ \t]+(?![ \t])\S")
BOUNDARY = re.compile(r"^(?:#\s*)?(?:UVM_|---|\[|End time:|Errors:|\*\* |%Error|[-] )", re.I)
FINISH = re.compile(r"^(?:#\s*)?(?:(?:\*\*\s*Note:\s*)?(?:\$finish\b|Finish\s*(?::|$))|-\s*[^$]*\b(?:Verilog\s+)?\$finish\b)", re.I)
SUCCESS = re.compile(r"(?:^|:\s*|\]\s*)TEST PASSED\s*$|\[RESULT\]\s+SUCCESS\b", re.I)
FAILURE = re.compile(r"\bTEST FAILED\b|^(?:#\s*)?UVM_(?:ERROR|FATAL)\s+(?!\s*:)|^(?:#\s*)?UVM_(?:ERROR|FATAL)\s*:\s*[1-9]\d*\b|^(?:#\s*)?(?:\*\*\s*)?(?:Error|Fatal):|^(?:#\s*)?%Error\b|^(?:#\s*)?Errors:\s*[1-9]\d*\b|\bAssertion failed\b", re.I)
LEVELS = dict(zip(("UVM_NONE","UVM_LOW","UVM_MEDIUM","UVM_HIGH","UVM_FULL","UVM_DEBUG"),range(0,600,100)))
REQUIRED = {"monitor":300,"scoreboard":100}


def scan(records, spans):
    names, levels, finishes, successes, failures = [], [], [], [], []
    pending = None
    with records.open(encoding="utf-8") as src, spans.open("x",encoding="utf-8",newline="\n") as out:
        def flush():
            if pending and len(pending["lines"]) > 1:
                out.write(json.dumps(pending,ensure_ascii=False)+"\n")

        for line in src:
            row=json.loads(line)
            # Keep damaged lines queryable without treating them as evidence.
            if row.get("decoding_lossy"):
                flush()
                pending = None
                continue
            body=row["texto_original"]
            ref=dict(file_id=row["file_id"],event_id=row["event_id"],line=row["log_line_start"])
            if m:=RNTST.search(body):
                names.append(dict(ref,value=m[1],source="RNTST"))
            for m in TEST.finditer(body):
                names.append(dict(ref,value=m[1].strip("'\""),source="UVM_TESTNAME"))
            for m in VERB.finditer(body):
                levels.append(dict(ref,level=m[1].upper(),scope="global"))
            for m in OVERRIDE.finditer(body):
                levels.append(dict(ref,level=m[3].upper(),scope="component",component=m[1],message_id=m[2],phase_time=m[4]))
            if FINISH.search(body):
                finishes.append(ref)
            if SUCCESS.search(body):
                successes.append(ref)
            if FAILURE.search(body):
                failures.append(ref)
            header=HEADER.match(body)
            if pending and not header and not BOUNDARY.match(body) and not FINISH.match(body) and CONT.match(body):
                pending["lines"].append(body)
                pending["log_line_end"]=ref["line"]
                continue
            flush()
            pending=dict(ref,kind="uvm_info" if header[1].upper()=="UVM_INFO" else "display",
                         log_line_start=ref["line"],log_line_end=ref["line"],lines=[body]) if header else None
        flush()
    return names,levels,finishes,successes,failures


def number(level):
    return int(level) if level and level.isdecimal() else LEVELS.get(level)


def verbosity(observations):
    declared={number(x["level"]) for x in observations if x["scope"]=="global"}
    level=next(iter(declared)) if len(declared)==1 else None
    overrides=[x for x in observations if x["scope"]=="component"]
    roles={}
    for role,needed in REQUIRED.items():
        # Un patrón de componente no se puede resolver sin topología; no inventar un nivel efectivo.
        estimate=level if not overrides else None
        roles[role]=dict(required=needed,estimated=estimate,
                         status="unknown" if estimate is None else "low" if estimate<needed else "sufficient")
    need=any(r["status"]!="sufficient" for r in roles.values())
    return dict(global_declared=level,observations=observations,roles=roles,adjustment_applied=False,
                recommendation="Solicitar una nueva corrida con monitor UVM_HIGH y scoreboard al menos UVM_LOW; comprobar filtros, fase e ID." if need else None)

