import subprocess
import sys

from nexgent.cli import _build_parser


def test_tui_flag_is_available_and_opt_in():
    parser = _build_parser()
    assert parser.parse_args([]).tui is False
    assert parser.parse_args(["--tui"]).tui is True


def test_cli_module_does_not_eagerly_import_qt():
    code = "import sys; import nexgent.cli; print('PyQt6.QtWidgets' in sys.modules)"
    completed = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert completed.stdout.strip() == "False"
