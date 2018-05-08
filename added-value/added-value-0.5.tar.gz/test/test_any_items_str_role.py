from test.example_source import with_test_examples_source

basename = "test_any_items_str_role"
html_filename = basename + ".html"


@with_test_examples_source
def test_base_name_in_html(app, status, warning):
    app.build()
    html = (app.outdir / html_filename).read_text()
    assert basename in html


@with_test_examples_source
def test_any_items_str_items_html_contains_value(app, status, warning):
    app.build()
    html = (app.outdir / html_filename).read_text()
    assert "I would choose any of cherry, chocolate, or pear." in html
