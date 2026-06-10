"""CLI behavior: stdout purity, stderr diagnostics, exit codes."""

from url2md4ai._cli import main


def test_converts_to_stdout(serve_fixture, capsys):
    url = serve_fixture("article.html")
    assert main([url]) == 0
    out, err = capsys.readouterr()
    assert "Idempotency first" in out
    assert err == ""


def test_error_goes_to_stderr_with_exit_1(serve, capsys):
    serve({})
    assert main(["https://test.example/missing"]) == 1
    out, err = capsys.readouterr()
    assert out == ""
    assert "error" in err


def test_verbose_prints_strategy(serve_fixture, capsys):
    assert main(["-v", serve_fixture("article.html")]) == 0
    _, err = capsys.readouterr()
    assert "strategy:" in err


def test_no_frontmatter_flag(serve_fixture, capsys):
    assert main(["--no-frontmatter", serve_fixture("article.html")]) == 0
    out, _ = capsys.readouterr()
    assert not out.startswith("---")


def test_raw_flag(serve_fixture, capsys):
    assert main(["--raw", serve_fixture("article.html")]) == 0
    out, _ = capsys.readouterr()
    assert not out.startswith("---")
    assert "Idempotency first" in out
