from test.example_source import with_test_examples_source

basename = "test_items_table_directive"
html_filename = basename + ".html"


@with_test_examples_source
def test_base_name_in_html(app, status, warning):
    app.build()
    html = (app.outdir / html_filename).read_text()
    assert basename in html
