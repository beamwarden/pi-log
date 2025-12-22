def test_service_file_exists(host):
    svc = host.file("/etc/systemd/system/pi-log.service")
    assert svc.exists
    assert svc.user == "root"
    assert svc.group == "root"


def test_service_running_and_enabled(host):
    service = host.service("pi-log")
    assert service.is_enabled
    assert service.is_running
