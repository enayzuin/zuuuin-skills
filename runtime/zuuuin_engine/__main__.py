"""Explicit local JSON CLI. No automatic account access or runtime installation."""
import argparse
import importlib
import json
from pathlib import Path
import sys
from .state import ExecutionStore, ControlError, atomic_json
from .util import contained

OPERATIONS = {"project-map":"project_map","catalog":"catalog","compare":"compare","evaluate":"evaluate","author":"author","audit":"audit","publish":"publish","router":"router"}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("operation",choices=OPERATIONS)
    parser.add_argument("--request",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--private-root",required=True)
    args=parser.parse_args()
    try:
        private=Path(args.private_root).absolute();store=ExecutionStore(private)
        state=store.read();store.verify_checkpoint_evidence()
        policy=json.loads((private/"policies/bootstrap.json").read_text())
        roots=state["roots"]
        reads=[roots["private"],roots["source"],roots["test"],*policy.get("skill_roots",[])]
        request_path,output=Path(args.request).absolute(),Path(args.output).absolute()
        if request_path.is_symlink() or not any(contained(request_path,Path(p)) for p in reads):raise ControlError("Request outside authorized read scope")
        if output.exists() or output.is_symlink() or not any(contained(output,Path(p)) for p in (roots["private"],roots["test"])):raise ControlError("Output must be new and inside private/test scope")
        output.parent.mkdir(parents=True,exist_ok=True)
        authorization_file=private/"policies/authorizations.json"
        auth=json.loads(authorization_file.read_text()).get("authorizations",{})
        ctx={"allowed_read_roots":reads,"policy":policy,"phase":state["phase"],"authorizations":auth,"publication_approval":state.get("publication_approval",{}),"receipt_root":str(private/"publication/receipts"),"provider_mode":"synthetic","available_tools":[],"seen_events":set()}
        module=importlib.import_module("zuuuin_engine."+OPERATIONS[args.operation])
        result=module.run(json.loads(request_path.read_text()),ctx)
        atomic_json(output,result)
        print(json.dumps({"status":result["status"],"output":str(output)},ensure_ascii=False))
        return 0
    except (ControlError,OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({"error_type":type(exc).__name__,"error":"Operation refused or invalid input; inspect the authorized local request and contracts"}),file=sys.stderr)
        return 2


if __name__=="__main__":raise SystemExit(main())
