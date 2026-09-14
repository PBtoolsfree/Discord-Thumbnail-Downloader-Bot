from app.security.ssrf import is_safe_url

def test_ssrf_safe_urls():
    assert is_safe_url("https://www.google.com") is True
    assert is_safe_url("http://example.com") is True

def test_ssrf_blocked_urls():
    # Private IPs and localhost
    assert is_safe_url("http://localhost:8080") is False
    assert is_safe_url("http://127.0.0.1") is False
    assert is_safe_url("https://192.168.1.1") is False
    assert is_safe_url("http://10.0.0.1") is False
    # Link local / metadata
    assert is_safe_url("http://169.254.169.254/latest/meta-data/") is False
    # Bad schemes
    assert is_safe_url("ftp://example.com/file") is False
    assert is_safe_url("file:///etc/passwd") is False
