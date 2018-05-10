import abjad
import abjadext.book
import docutils
import os
import posixpath
import pytest
import shutil
import types
from uqbar.strings import normalize
from sphinx.util import FilenameUniqDict


@pytest.fixture
def app():
    app = types.SimpleNamespace()
    app.config = types.SimpleNamespace()
    app.config.abjadbook_ignored_documents = ()
    app.builder = types.SimpleNamespace()
    app.builder.warn = print
    app.builder.current_docname = 'test'
    app.builder.status_iterator = lambda iterable, x, y, z: iter(iterable)
    app.builder.thumbnails = FilenameUniqDict()
    app.builder.outdir = os.path.dirname(os.path.abspath(__file__))
    app.builder.imagedir = '_images'
    app.builder.imgpath = posixpath.join('..', '_images')
    app.builder.srcdir = os.path.join(
        abjad.__path__[0],
        'docs',
        'source',
        )
    app.body = []
    return app


@pytest.fixture
def paths(app):
    paths = types.SimpleNamespace()
    paths.images_directory = os.path.join(
        app.builder.outdir,
        app.builder.imagedir,
        )
    paths.abjadbook_images_directory = os.path.join(
        paths.images_directory,
        'abjadbook',
        )
    if os.path.exists(paths.images_directory):
        shutil.rmtree(paths.images_directory)
    yield paths
    if os.path.exists(paths.images_directory):
        shutil.rmtree(paths.images_directory)


def test_01(app, paths):
    source = r'''
    ..  abjad::
        :hide:
        :no-stylesheet:

        abjad.show(Staff("c'4 d'4 e'4 f'4"))
    '''
    source = normalize(source)
    handler = abjadext.book.SphinxDocumentHandler()
    document = handler.parse_rst(source)
    handler.on_doctree_read(app, document)
    node = document[0]
    try:
        abjadext.book.SphinxDocumentHandler.visit_abjad_output_block_html(
            app, node)
    except docutils.nodes.SkipNode:
        pass
    handler.on_build_finished(app, None)
    actual = '\n'.join(app.body)
    expected = normalize(r'''
        <a href="../_images/abjadbook/lilypond-57112712fcf935879acedf8575a6db82128a1b69.ly" title="" class="abjadbook">
            <img src="../_images/abjadbook/lilypond-57112712fcf935879acedf8575a6db82128a1b69.png" alt=""/>
        </a>
        ''')
    assert actual == expected
    assert len(os.listdir(paths.abjadbook_images_directory)) == 2
    for name in (
        'lilypond-57112712fcf935879acedf8575a6db82128a1b69.ly',
        'lilypond-57112712fcf935879acedf8575a6db82128a1b69.png',
    ):
        path = os.path.join(paths.images_directory, 'abjadbook', name)
        assert os.path.exists(path)


def test_02(app, paths):
    source = r'''
    ..  abjad::
        :hide:
        :no-stylesheet:
        :no-trim:

        abjad.show(Staff("c'4 d'4 e'4 f'4"))
    '''
    source = normalize(source)
    handler = abjadext.book.SphinxDocumentHandler()
    document = handler.parse_rst(source)
    handler.on_doctree_read(app, document)
    node = document[0]
    try:
        abjadext.book.SphinxDocumentHandler.visit_abjad_output_block_html(
            app, node)
    except docutils.nodes.SkipNode:
        pass
    handler.on_build_finished(app, None)
    actual = '\n'.join(app.body)
    expected = normalize(r'''
        <a href="../_images/abjadbook/lilypond-df50a78c470bffbfde206fddd1ede73e9712bd48.ly" title="" class="abjadbook">
            <img src="../_images/abjadbook/lilypond-df50a78c470bffbfde206fddd1ede73e9712bd48.png" alt=""/>
        </a>
        ''')
    assert actual == expected
    assert actual == expected
    assert len(os.listdir(paths.abjadbook_images_directory)) == 2
    for name in (
        'lilypond-df50a78c470bffbfde206fddd1ede73e9712bd48.ly',
        'lilypond-df50a78c470bffbfde206fddd1ede73e9712bd48.png',
    ):
        path = os.path.join(paths.images_directory, 'abjadbook', name)
        assert os.path.exists(path)


def test_03(app, paths):
    source = r'''
    ..  abjad::
        :hide:
        :no-resize:
        :no-stylesheet:
        :no-trim:

        abjad.show(Staff("c'4 d'4 e'4 f'4"))
    '''
    source = normalize(source)
    handler = abjadext.book.SphinxDocumentHandler()
    document = handler.parse_rst(source)
    handler.on_doctree_read(app, document)
    node = document[0]
    try:
        abjadext.book.SphinxDocumentHandler.visit_abjad_output_block_html(
            app, node)
    except docutils.nodes.SkipNode:
        pass
    handler.on_build_finished(app, None)
    actual = '\n'.join(app.body)
    expected = normalize(r'''
        <a href="../_images/abjadbook/lilypond-d103b3a4d88e2c214963dd3da9f06c2302318b81.ly" title="" class="abjadbook">
            <img src="../_images/abjadbook/lilypond-d103b3a4d88e2c214963dd3da9f06c2302318b81.png" alt=""/>
        </a>
        ''')
    assert actual == expected
    assert len(os.listdir(paths.abjadbook_images_directory)) == 2
    for name in (
        'lilypond-d103b3a4d88e2c214963dd3da9f06c2302318b81.ly',
        'lilypond-d103b3a4d88e2c214963dd3da9f06c2302318b81.png',
    ):
        path = os.path.join(paths.images_directory, 'abjadbook', name)
        assert os.path.exists(path)


def test_04(app, paths):
    source = r'''
    ..  abjad::
        :hide:
        :no-resize:
        :no-stylesheet:
        :no-trim:
        :with-thumbnail:

        abjad.show(Staff("c'4 d'4 e'4 f'4"))
    '''
    source = normalize(source)
    handler = abjadext.book.SphinxDocumentHandler()
    document = handler.parse_rst(source)
    handler.on_doctree_read(app, document)
    node = document[0]
    try:
        abjadext.book.SphinxDocumentHandler.visit_abjad_output_block_html(
            app, node)
    except docutils.nodes.SkipNode:
        pass
    handler.on_build_finished(app, None)
    assert len(app.builder.thumbnails) == 1
    assert '../_images/abjadbook/lilypond-d103b3a4d88e2c214963dd3da9f06c2302318b81.png' in app.builder.thumbnails
    actual = '\n'.join(app.body)
    expected = normalize(r'''
        <a data-lightbox="group-lilypond-d103b3a4d88e2c214963dd3da9f06c2302318b81.ly" href="../_images/abjadbook/lilypond-d103b3a4d88e2c214963dd3da9f06c2302318b81.png" title="" data-title="" class="abjadbook thumbnail">
            <img src="../_images/abjadbook/lilypond-d103b3a4d88e2c214963dd3da9f06c2302318b81-thumbnail.png" alt=""/>
        </a>
        ''')
    assert actual == expected
    assert len(os.listdir(paths.abjadbook_images_directory)) == 3
    for name in (
        'lilypond-d103b3a4d88e2c214963dd3da9f06c2302318b81.ly',
        'lilypond-d103b3a4d88e2c214963dd3da9f06c2302318b81.png',
        'lilypond-d103b3a4d88e2c214963dd3da9f06c2302318b81-thumbnail.png',
    ):
        path = os.path.join(paths.images_directory, 'abjadbook', name)
        assert os.path.exists(path)


def test_05(app, paths):
    source = r'''
    ..  abjad::
        :hide:
        :stylesheet: default.ily
        :no-trim:

        abjad.show(Staff("c'4 d'4 e'4 f'4"))
    '''
    source = normalize(source)
    handler = abjadext.book.SphinxDocumentHandler()
    document = handler.parse_rst(source)
    handler.on_doctree_read(app, document)
    abjadext.book.SphinxDocumentHandler.on_builder_inited(app)
    node = document[0]
    try:
        abjadext.book.SphinxDocumentHandler.visit_abjad_output_block_html(
            app, node)
    except docutils.nodes.SkipNode:
        pass
    handler.on_build_finished(app, None)
    actual = '\n'.join(app.body)
    expected = normalize(r'''
        <a href="../_images/abjadbook/lilypond-e012f949124c2146b2ca2cc863a420702cde98e3.ly" title="" class="abjadbook">
            <img src="../_images/abjadbook/lilypond-e012f949124c2146b2ca2cc863a420702cde98e3.png" alt=""/>
        </a>
        ''')
    assert actual == expected
    assert len(os.listdir(paths.abjadbook_images_directory)) == 8
    for name in (
        'default.ily',
        'external-settings-file-1.ily',
        'external-settings-file-2.ily',
        'lilypond-e012f949124c2146b2ca2cc863a420702cde98e3.ly',
        'lilypond-e012f949124c2146b2ca2cc863a420702cde98e3.png',
        'rhythm-maker-docs.ily',
        'text-spanner-id.ily',
    ):
        path = os.path.join(paths.images_directory, 'abjadbook', name)
        assert os.path.exists(path)


def test_06(app, paths):
    source = r'''
    ..  abjad::
        :hide:
        :no-stylesheet:

        staff = Staff("c'1 d'1 e'1 f'1 g'1")
        for note in staff[:-1]:
            attach(indicatortools.PageBreak(), note)

        abjad.show(staff)
    '''
    source = normalize(source)
    handler = abjadext.book.SphinxDocumentHandler()
    document = handler.parse_rst(source)
    handler.on_doctree_read(app, document)
    node = document[0]
    try:
        abjadext.book.SphinxDocumentHandler.visit_abjad_output_block_html(
            app, node)
    except docutils.nodes.SkipNode:
        pass
    handler.on_build_finished(app, None)
    actual = '\n'.join(app.body)
    expected = normalize(r'''
        <a href="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193.ly" title="" class="abjadbook">
            <img src="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page1.png" alt=""/>
        </a>
        <a href="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193.ly" title="" class="abjadbook">
            <img src="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page2.png" alt=""/>
        </a>
        <a href="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193.ly" title="" class="abjadbook">
            <img src="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page3.png" alt=""/>
        </a>
        <a href="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193.ly" title="" class="abjadbook">
            <img src="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page4.png" alt=""/>
        </a>
        <a href="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193.ly" title="" class="abjadbook">
            <img src="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page5.png" alt=""/>
        </a>
        ''')
    assert actual == expected
    assert len(os.listdir(paths.abjadbook_images_directory)) == 6
    for name in (
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193.ly',
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page1.png',
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page2.png',
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page3.png',
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page4.png',
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page5.png',
    ):
        path = os.path.join(paths.images_directory, 'abjadbook', name)
        assert os.path.exists(path)


def test_07(app, paths):
    source = r'''
    ..  abjad::
        :hide:
        :no-stylesheet:
        :pages: 2-4

        staff = Staff("c'1 d'1 e'1 f'1 g'1")
        for note in staff[:-1]:
            attach(indicatortools.PageBreak(), note)

        abjad.show(staff)
    '''
    source = normalize(source)
    handler = abjadext.book.SphinxDocumentHandler()
    document = handler.parse_rst(source)
    handler.on_doctree_read(app, document)
    node = document[0]
    try:
        abjadext.book.SphinxDocumentHandler.visit_abjad_output_block_html(
            app, node)
    except docutils.nodes.SkipNode:
        pass
    handler.on_build_finished(app, None)
    actual = '\n'.join(app.body)
    expected = normalize(r'''
        <a href="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193.ly" title="" class="abjadbook">
            <img src="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page2.png" alt=""/>
        </a>
        <a href="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193.ly" title="" class="abjadbook">
            <img src="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page3.png" alt=""/>
        </a>
        <a href="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193.ly" title="" class="abjadbook">
            <img src="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page4.png" alt=""/>
        </a>
        ''')
    assert actual == expected
    assert len(os.listdir(paths.abjadbook_images_directory)) == 6
    for name in (
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193.ly',
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page1.png',
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page2.png',
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page3.png',
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page4.png',
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page5.png',
    ):
        path = os.path.join(paths.images_directory, 'abjadbook', name)
        assert os.path.exists(path)


def test_08(app, paths):
    source = r'''
    ..  abjad::
        :hide:
        :no-stylesheet:
        :pages: 2-4
        :with-columns: 2

        staff = Staff("c'1 d'1 e'1 f'1 g'1")
        for note in staff[:-1]:
            attach(indicatortools.PageBreak(), note)

        abjad.show(staff)
    '''
    source = normalize(source)
    handler = abjadext.book.SphinxDocumentHandler()
    document = handler.parse_rst(source)
    handler.on_doctree_read(app, document)
    node = document[0]
    try:
        abjadext.book.SphinxDocumentHandler.visit_abjad_output_block_html(
            app, node)
    except docutils.nodes.SkipNode:
        pass
    handler.on_build_finished(app, None)
    actual = '\n'.join(app.body)
    expected = normalize(r'''
        <div class="table-row">
            <a href="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193.ly" title="" class="table-cell">
                <img src="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page2.png" alt=""/>
            </a>
            <a href="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193.ly" title="" class="table-cell">
                <img src="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page3.png" alt=""/>
            </a>
        </div>
        <div class="table-row">
            <a href="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193.ly" title="" class="table-cell">
                <img src="../_images/abjadbook/lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page4.png" alt=""/>
            </a>
        </div>
        ''')
    assert actual == expected
    assert len(os.listdir(paths.abjadbook_images_directory)) == 6
    for name in (
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193.ly',
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page1.png',
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page2.png',
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page3.png',
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page4.png',
        'lilypond-a6df2f81af35e45b1dbf9522e25649c6310a5193-page5.png',
    ):
        path = os.path.join(paths.images_directory, 'abjadbook', name)
        assert os.path.exists(path)


def test_09(app, paths):
    source = r'''
    ..  abjad::
        :hide:
        :no-stylesheet:
        :no-trim:
        :pages: 2-4
        :with-columns: 2

        staff = Staff("c'1 d'1 e'1 f'1 g'1")
        for note in staff[:-1]:
            attach(indicatortools.PageBreak(), note)

        abjad.show(staff)
    '''
    source = normalize(source)
    handler = abjadext.book.SphinxDocumentHandler()
    document = handler.parse_rst(source)
    handler.on_doctree_read(app, document)
    node = document[0]
    try:
        abjadext.book.SphinxDocumentHandler.visit_abjad_output_block_html(
            app, node)
    except docutils.nodes.SkipNode:
        pass
    handler.on_build_finished(app, None)
    actual = '\n'.join(app.body)
    expected = normalize(r'''
        <div class="table-row">
            <a href="../_images/abjadbook/lilypond-e67b0148a7c7f1e6770218e7cdb35be70331a20a.ly" title="" class="table-cell">
                <img src="../_images/abjadbook/lilypond-e67b0148a7c7f1e6770218e7cdb35be70331a20a-page2.png" alt=""/>
            </a>
            <a href="../_images/abjadbook/lilypond-e67b0148a7c7f1e6770218e7cdb35be70331a20a.ly" title="" class="table-cell">
                <img src="../_images/abjadbook/lilypond-e67b0148a7c7f1e6770218e7cdb35be70331a20a-page3.png" alt=""/>
            </a>
        </div>
        <div class="table-row">
            <a href="../_images/abjadbook/lilypond-e67b0148a7c7f1e6770218e7cdb35be70331a20a.ly" title="" class="table-cell">
                <img src="../_images/abjadbook/lilypond-e67b0148a7c7f1e6770218e7cdb35be70331a20a-page4.png" alt=""/>
            </a>
        </div>
        ''')
    assert actual == expected
    assert len(os.listdir(paths.abjadbook_images_directory)) == 6
    for name in (
        'lilypond-e67b0148a7c7f1e6770218e7cdb35be70331a20a.ly',
        'lilypond-e67b0148a7c7f1e6770218e7cdb35be70331a20a-page1.png',
        'lilypond-e67b0148a7c7f1e6770218e7cdb35be70331a20a-page2.png',
        'lilypond-e67b0148a7c7f1e6770218e7cdb35be70331a20a-page3.png',
        'lilypond-e67b0148a7c7f1e6770218e7cdb35be70331a20a-page4.png',
        'lilypond-e67b0148a7c7f1e6770218e7cdb35be70331a20a-page5.png',
    ):
        path = os.path.join(paths.images_directory, 'abjadbook', name)
        assert os.path.exists(path)


def test_10(app, paths):
    source = r'''
    ..  abjad::
        :hide:
        :no-resize:
        :no-stylesheet:
        :with-thumbnail:

        staff = Staff("c'1 d'1 e'1 f'1 g'1")
        for note in staff[:-1]:
            attach(indicatortools.PageBreak(), note)

        abjad.show(staff)
    '''
    source = normalize(source)
    handler = abjadext.book.SphinxDocumentHandler()
    document = handler.parse_rst(source)
    handler.on_doctree_read(app, document)
    node = document[0]
    try:
        abjadext.book.SphinxDocumentHandler.visit_abjad_output_block_html(
            app, node)
    except docutils.nodes.SkipNode:
        pass
    handler.on_build_finished(app, None)
    actual = '\n'.join(app.body)
    expected = normalize(r'''
        <a data-lightbox="group-lilypond-93a0247aa388d5a6e590646997957e868a61d5b6.ly" href="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page1.png" title="" data-title="" class="abjadbook thumbnail">
            <img src="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page1-thumbnail.png" alt=""/>
        </a>
        <a data-lightbox="group-lilypond-93a0247aa388d5a6e590646997957e868a61d5b6.ly" href="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page2.png" title="" data-title="" class="abjadbook thumbnail">
            <img src="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page2-thumbnail.png" alt=""/>
        </a>
        <a data-lightbox="group-lilypond-93a0247aa388d5a6e590646997957e868a61d5b6.ly" href="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page3.png" title="" data-title="" class="abjadbook thumbnail">
            <img src="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page3-thumbnail.png" alt=""/>
        </a>
        <a data-lightbox="group-lilypond-93a0247aa388d5a6e590646997957e868a61d5b6.ly" href="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page4.png" title="" data-title="" class="abjadbook thumbnail">
            <img src="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page4-thumbnail.png" alt=""/>
        </a>
        <a data-lightbox="group-lilypond-93a0247aa388d5a6e590646997957e868a61d5b6.ly" href="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page5.png" title="" data-title="" class="abjadbook thumbnail">
            <img src="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page5-thumbnail.png" alt=""/>
        </a>
        ''')
    assert actual == expected
    assert len(os.listdir(paths.abjadbook_images_directory)) == 11
    for name in (
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6.ly',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page1.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page1-thumbnail.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page2.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page2-thumbnail.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page3.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page3-thumbnail.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page4.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page4-thumbnail.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page5.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page5-thumbnail.png',
    ):
        path = os.path.join(paths.images_directory, 'abjadbook', name)
        assert os.path.exists(path)


def test_11(app, paths):
    source = r'''
    ..  abjad::
        :hide:
        :no-resize:
        :no-stylesheet:
        :with-columns: 2
        :with-thumbnail:

        staff = Staff("c'1 d'1 e'1 f'1 g'1")
        for note in staff[:-1]:
            attach(indicatortools.PageBreak(), note)

        abjad.show(staff)
    '''
    source = normalize(source)
    handler = abjadext.book.SphinxDocumentHandler()
    document = handler.parse_rst(source)
    handler.on_doctree_read(app, document)
    node = document[0]
    try:
        abjadext.book.SphinxDocumentHandler.visit_abjad_output_block_html(
            app, node)
    except docutils.nodes.SkipNode:
        pass
    handler.on_build_finished(app, None)
    actual = '\n'.join(app.body)
    expected = normalize(r'''
        <div class="table-row">
            <a data-lightbox="group-lilypond-93a0247aa388d5a6e590646997957e868a61d5b6.ly" href="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page1.png" title="" data-title="" class="table-cell thumbnail">
                <img src="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page1-thumbnail.png" alt=""/>
            </a>
            <a data-lightbox="group-lilypond-93a0247aa388d5a6e590646997957e868a61d5b6.ly" href="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page2.png" title="" data-title="" class="table-cell thumbnail">
                <img src="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page2-thumbnail.png" alt=""/>
            </a>
        </div>
        <div class="table-row">
            <a data-lightbox="group-lilypond-93a0247aa388d5a6e590646997957e868a61d5b6.ly" href="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page3.png" title="" data-title="" class="table-cell thumbnail">
                <img src="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page3-thumbnail.png" alt=""/>
            </a>
            <a data-lightbox="group-lilypond-93a0247aa388d5a6e590646997957e868a61d5b6.ly" href="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page4.png" title="" data-title="" class="table-cell thumbnail">
                <img src="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page4-thumbnail.png" alt=""/>
            </a>
        </div>
        <div class="table-row">
            <a data-lightbox="group-lilypond-93a0247aa388d5a6e590646997957e868a61d5b6.ly" href="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page5.png" title="" data-title="" class="table-cell thumbnail">
                <img src="../_images/abjadbook/lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page5-thumbnail.png" alt=""/>
            </a>
        </div>
        ''')
    assert actual == expected
    assert len(os.listdir(paths.abjadbook_images_directory)) == 11
    for name in (
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6.ly',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page1.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page1-thumbnail.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page2.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page2-thumbnail.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page3.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page3-thumbnail.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page4.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page4-thumbnail.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page5.png',
        'lilypond-93a0247aa388d5a6e590646997957e868a61d5b6-page5-thumbnail.png',
    ):
        path = os.path.join(paths.images_directory, 'abjadbook', name)
        assert os.path.exists(path)
