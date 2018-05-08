from test.example_source import with_test_examples_source

basename = "test_items_table_directive"
html_filename = basename + ".html"


@with_test_examples_source
def test_base_name_in_html(app, status, warning):
    app.build()
    html = (app.outdir / html_filename).read_text()
    assert basename in html


@with_test_examples_source
def test_format_literal_integer_html_contains_value(app, status, warning):
    app.build()
    html = (app.outdir / html_filename).read_text()
    assert "The value of pi to three decimal places is 3.142." in html
