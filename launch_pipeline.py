"""Pass MLflow parameters to Hydra without platform-specific shell expansion."""
import argparse
import json
import shlex
import sys
import runpy
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", default="all")
    parser.add_argument("--hydra-options", default="")
    args = parser.parse_args()
    sys.argv = ["main.py", f"main.steps={json.dumps(args.steps)}", *shlex.split(args.hydra_options)]
    runpy.run_path(str(Path(__file__).with_name("main.py")), run_name="__main__")


if __name__ == "__main__":
    main()
