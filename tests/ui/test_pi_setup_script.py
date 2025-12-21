import os
import stat


def test_pi_setup_script_exists_and_is_executable():
    script_path = "scripts/pi-setup.sh"

    assert os.path.exists(script_path)

    mode = os.stat(script_path).st_mode
    assert mode & stat.S_IXUSR  # user executable bit


def test_pi_setup_script_contains_expected_commands():
    script_path = "scripts/pi-setup.sh"

    with open(script_path) as f:
        content = f.read()

    assert "apt-get" in content
    assert "systemctl" in content
    assert "python3" in content
