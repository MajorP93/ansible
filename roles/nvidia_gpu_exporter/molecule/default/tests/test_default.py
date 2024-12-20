from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from testinfra_helpers import get_target_hosts

testinfra_hosts = get_target_hosts()


def test_files(host):
    files = [
        "/etc/systemd/system/nvidia_gpu_exporter.service",
        "/usr/local/bin/nvidia_gpu_exporter"
    ]
    for file in files:
        f = host.file(file)
        assert f.exists
        assert f.is_file


def test_permissions_didnt_change(host):
    dirs = [
        "/etc",
        "/root",
        "/usr",
        "/var"
    ]
    for file in dirs:
        f = host.file(file)
        assert f.exists
        assert f.is_directory
        assert f.user == "root"
        assert f.group == "root"


def test_user(host):
    assert host.group("nvidia-gpu-exp").exists
    assert "nvidia-gpu-exp" in host.user("nvidia-gpu-exp").groups
    assert host.user("nvidia-gpu-exp").shell == "/usr/sbin/nologin"


def test_service(host):
    s = host.service("nvidia_gpu_exporter")
    try:
        assert s.is_running
    except AssertionError:
        # Capture service logs
        journal_output = host.run('journalctl -u nvidia_gpu_exporter --since "1 hour ago"')
        print("\n==== journalctl -u nvidia_gpu_exporter Output ====\n")
        print(journal_output)
        print("\n============================================\n")
        raise  # Re-raise the original assertion error


def test_protecthome_property(host):
    s = host.service("nvidia_gpu_exporter")
    p = s.systemd_properties
    assert p.get("ProtectHome") == "yes"


def test_socket(host):
    sockets = [
        "tcp://127.0.0.1:9835"
    ]
    for socket in sockets:
        s = host.socket(socket)
        assert s.is_listening
