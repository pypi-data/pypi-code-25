import unittest2 as unittest
from fontParts.base.deprecated import RemovedWarning


class TestDeprecated(unittest.TestCase):

    # ----
    # Font
    # ----

    def getFont_glyphs(self):
        font, _ = self.objectGenerator("font")
        for name in "ABCD":
            font.newGlyph(name)
        return font

    def test_font_removed_getParent(self):
        font, _ = self.objectGenerator("font")
        with self.assertRaises(RemovedWarning):
            font.getParent()

    def test_font_removed_generateGlyph(self):
        font, _ = self.objectGenerator("font")
        with self.assertRaises(RemovedWarning):
            font.generateGlyph()

    def test_font_removed_compileGlyph(self):
        font, _ = self.objectGenerator("font")
        with self.assertRaises(RemovedWarning):
            font.compileGlyph()

    def test_font_removed_getGlyphNameToFileNameFunc(self):
        font, _ = self.objectGenerator("font")
        with self.assertRaises(RemovedWarning):
            font.getGlyphNameToFileNameFunc()

    def test_font_deprecated_update(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        font, _ = self.objectGenerator("font")
        with self.assertWarnsRegex(DeprecationWarning, "Font.changed()"):
            font.update()

    def test_font_deprecated_setChanged(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        font, _ = self.objectGenerator("font")
        with self.assertWarnsRegex(DeprecationWarning, "Font.changed()"):
            font.setChanged()

    def test_font_removed_setParent(self):
        font, _ = self.objectGenerator("font")
        with self.assertRaises(RemovedWarning):
            font.setParent(font)

    def test_font_deprecated__fileName(self):
        font, _ = self.objectGenerator("font")
        with self.assertWarnsRegex(DeprecationWarning, "fileName"):
            font._get_fileName()
        self.assertEqual(font._get_fileName(), font.path)

    def test_font_deprecated_fileName(self):
        font, _ = self.objectGenerator("font")
        with self.assertWarnsRegex(DeprecationWarning, "fileName"):
            font.fileName
        self.assertEqual(font.fileName, font.path)

    def test_font_deprecated_getWidth(self):
        font, _ = self.objectGenerator("font")
        glyph = font.newGlyph("Test")
        glyph.width = 200
        with self.assertWarnsRegex(DeprecationWarning, "Font.getWidth()"):
            font.getWidth("Test")
        self.assertEqual(font.getWidth("Test"), font["Test"].width)

    def test_font_deprecated_getGlyph(self):
        font, _ = self.objectGenerator("font")
        font.newGlyph("Test")
        with self.assertWarnsRegex(DeprecationWarning, "Font.getGlyph()"):
            font.getGlyph("Test")
        self.assertEqual(font.getGlyph("Test"), font["Test"])

    def test_font_deprecated__get_selection(self):
        font = self.getFont_glyphs()
        try:
            font.defaultLayer.selected = False
        except NotImplementedError:
            return
        glyph1 = font["A"]
        glyph2 = font["B"]
        glyph1.selected = True
        glyph2.selected = True
        with self.assertWarnsRegex(DeprecationWarning, "Font.selectedGlyphNames"):
            font._get_selection()
        self.assertEqual(font._get_selection(), font.selectedGlyphNames)

    def test_font_deprecated__set_selection(self):
        font1 = self.getFont_glyphs()
        font2 = self.getFont_glyphs()
        with self.assertWarnsRegex(DeprecationWarning, "Font.selectedGlyphNames"):
            font1._set_selection(["A", "B"])
        font2.selectedGlyphNames = ["A", "B"]
        self.assertEqual(font1.selectedGlyphNames, font2.selectedGlyphNames)

    def test_font_deprecated_selection_set(self):
        font1 = self.getFont_glyphs()
        font2 = self.getFont_glyphs()
        with self.assertWarnsRegex(DeprecationWarning, "Font.selectedGlyphNames"):
            font1.selection = ["A", "B"]
        font2.selectedGlyphNames = ["A", "B"]
        self.assertEqual(font1.selectedGlyphNames, font2.selectedGlyphNames)

    def test_font_deprecated_selection_get(self):
        font = self.getFont_glyphs()
        try:
            font.defaultLayer.selected = False
        except NotImplementedError:
            return
        glyph1 = font["A"]
        glyph2 = font["B"]
        glyph1.selected = True
        glyph2.selected = True
        with self.assertWarnsRegex(DeprecationWarning, "Font.selectedGlyphNames"):
            font.selection
        self.assertEqual(font.selection, font.selectedGlyphNames)

    # ------
    # Anchor
    # ------

    def getAnchor(self):
        glyph, _ = self.objectGenerator("glyph")
        glyph.appendAnchor("anchor 0", (0, 0))
        return glyph

    def test_anchor_deprecated__generateIdentifer(self):
        anchor, _ = self.objectGenerator("anchor")
        with self.assertWarnsRegex(DeprecationWarning, "Anchor._generateIdentifier()"):
            anchor._generateIdentifier()
        self.assertEqual(
            anchor._generateIdentifier(),
            anchor._getIdentifier()
        )

    def test_anchor_deprecated_generateIdentifer(self):
        anchor, _ = self.objectGenerator("anchor")
        with self.assertWarnsRegex(DeprecationWarning, "Anchor.generateIdentifier()"):
            anchor.generateIdentifier()
        self.assertEqual(
            anchor.generateIdentifier(),
            anchor.getIdentifier()
        )

    def test_anchor_deprecated_getParent(self):
        glyph = self.getAnchor()
        anchor = glyph.anchors[0]
        with self.assertWarnsRegex(DeprecationWarning, "Anchor.getParent()"):
            anchor.getParent()
        self.assertEqual(
            anchor.getParent(),
            anchor.glyph
        )

    def test_anchor_deprecated_update(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        anchor, _ = self.objectGenerator("anchor")
        with self.assertWarnsRegex(DeprecationWarning, "Anchor.changed()"):
            anchor.update()

    def test_anchor_deprecated_setChanged(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        anchor, _ = self.objectGenerator("anchor")
        with self.assertWarnsRegex(DeprecationWarning, "Anchor.changed()"):
            anchor.setChanged()

    def test_anchor_removed_setParent(self):
        glyph = self.getAnchor()
        anchor = glyph.anchors[0]
        with self.assertRaises(RemovedWarning):
            anchor.setParent(glyph)

    def test_anchor_removed_draw(self):
        glyph = self.getAnchor()
        pen = glyph.getPen()
        anchor = glyph.anchors[0]
        with self.assertRaises(RemovedWarning):
            anchor.draw(pen)

    def test_anchor_removed_drawPoints(self):
        glyph = self.getAnchor()
        pen = glyph.getPen()
        anchor = glyph.anchors[0]
        with self.assertRaises(RemovedWarning):
            anchor.drawPoints(pen)

    # -----
    # Layer
    # -----

    def test_layer_deprecated_getParent(self):
        font, _ = self.objectGenerator("font")
        for name in "ABCD":
            font.newLayer("layer " + name)
        layer = font.layers[0]
        with self.assertWarnsRegex(DeprecationWarning, "Layer.font"):
            layer.getParent()
        self.assertEqual(layer.getParent(), layer.font)

    def test_layer_deprecated_update(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        layer, _ = self.objectGenerator("layer")
        with self.assertWarnsRegex(DeprecationWarning, "Layer.changed()"):
            layer.update()

    def test_layer_deprecated_setChanged(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        layer, _ = self.objectGenerator("layer")
        with self.assertWarnsRegex(DeprecationWarning, "Layer.changed()"):
            layer.setChanged()

    def test_layer_removed_setParent(self):
        font, _ = self.objectGenerator("font")
        for name in "ABCD":
            font.newLayer("layer " + name)
        layer = font.layers[0]
        with self.assertRaises(RemovedWarning):
            layer.setParent(font)

    # --------
    # Features
    # --------

    def test_features_deprecated_getParent(self):
        font, _ = self.objectGenerator("font")
        features = font.features
        features.text = "# Test"
        with self.assertWarnsRegex(DeprecationWarning, "Features.font"):
            features.getParent()
        self.assertEqual(features.getParent(), features.font)

    def test_features_deprecated_update(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        features, _ = self.objectGenerator("features")
        with self.assertWarnsRegex(DeprecationWarning, "Features.changed()"):
            features.update()

    def test_features_deprecated_setChanged(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        features, _ = self.objectGenerator("features")
        with self.assertWarnsRegex(DeprecationWarning, "Features.changed()"):
            features.setChanged()

    def test_feature_removed_setParent(self):
        font, _ = self.objectGenerator("font")
        features = font.features
        features.text = "# Test"
        with self.assertRaises(RemovedWarning):
            features.setParent(font)

    def test_feature_removed_round(self):
        feature, _ = self.objectGenerator("features")
        with self.assertRaises(RemovedWarning):
            feature.round()

    # -----
    # Image
    # -----

    def getImage_glyph(self):
        from fontParts.test.test_image import testImageData
        glyph, _ = self.objectGenerator("glyph")
        glyph.addImage(data=testImageData)
        image = glyph.image
        return image

    def test_image_deprecated_getParent(self):
        image = self.getImage_glyph()
        with self.assertWarnsRegex(DeprecationWarning, "Image.glyph"):
            image.getParent()
        self.assertEqual(image.getParent(), image.glyph)

    def test_image_deprecated_update(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        image, _ = self.objectGenerator("image")
        with self.assertWarnsRegex(DeprecationWarning, "Image.changed()"):
            image.update()

    def test_image_deprecated_setChanged(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        image, _ = self.objectGenerator("image")
        with self.assertWarnsRegex(DeprecationWarning, "Image.changed()"):
            image.setChanged()

    def test_image_removed_setParent(self):
        glyph, _ = self.objectGenerator("glyph")
        image = self.getImage_glyph()
        with self.assertRaises(RemovedWarning):
            image.setParent(glyph)

    # ----
    # Info
    # ----

    def test_info_deprecated_getParent(self):
        font, _ = self.objectGenerator("font")
        info = font.info
        info.unitsPerEm = 1000
        with self.assertWarnsRegex(DeprecationWarning, "Info.font"):
            info.getParent()
        self.assertEqual(info.getParent(), info.font)

    def test_info_deprecated_update(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        info, _ = self.objectGenerator("info")
        with self.assertWarnsRegex(DeprecationWarning, "Info.changed()"):
            info.update()

    def test_info_deprecated_setChanged(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        info, _ = self.objectGenerator("info")
        with self.assertWarnsRegex(DeprecationWarning, "Info.changed()"):
            info.setChanged()

    def test_info_removed_setParent(self):
        font, _ = self.objectGenerator("font")
        info, _ = self.objectGenerator("info")
        info.unitsPerEm = 1000
        with self.assertRaises(RemovedWarning):
            info.setParent(font)

    # -------
    # Kerning
    # -------

    def getKerning_generic(self):
        font, _ = self.objectGenerator("font")
        groups = font.groups
        groups["public.kern1.X"] = ["A", "B", "C"]
        groups["public.kern2.X"] = ["A", "B", "C"]
        kerning = font.kerning
        kerning.update({
            ("public.kern1.X", "public.kern2.X"): 100,
            ("B", "public.kern2.X"): 101,
            ("public.kern1.X", "B"): 102,
            ("A", "A"): 103,
        })
        return kerning

    def test_kerning_removed_setParent(self):
        font, _ = self.objectGenerator("font")
        kerning, _ = self.objectGenerator("kerning")
        with self.assertRaises(RemovedWarning):
            kerning.setParent(font)

    def test_kerning_removed_swapNames(self):
        kerning = self.getKerning_generic()
        swap = {"B": "C"}
        with self.assertRaises(RemovedWarning):
            kerning.swapNames(swap)

    def test_kerning_removed_getLeft(self):
        kerning = self.getKerning_generic()
        with self.assertRaises(RemovedWarning):
            kerning.getLeft("B")

    def test_kerning_removed_getRight(self):
        kerning = self.getKerning_generic()
        with self.assertRaises(RemovedWarning):
            kerning.getRight("B")

    def test_kerning_removed_getExtremes(self):
        kerning = self.getKerning_generic()
        with self.assertRaises(RemovedWarning):
            kerning.getExtremes()

    def test_kerning_removed_add(self):
        kerning = self.getKerning_generic()
        with self.assertRaises(RemovedWarning):
            kerning.add(10)

    def test_kerning_removed_minimize(self):
        kerning = self.getKerning_generic()
        with self.assertRaises(RemovedWarning):
            kerning.minimize()

    def test_kerning_removed_importAFM(self):
        kerning = self.getKerning_generic()
        with self.assertRaises(RemovedWarning):
            kerning.importAFM("fake/path")

    def test_kerning_removed_getAverage(self):
        kerning = self.getKerning_generic()
        with self.assertRaises(RemovedWarning):
            kerning.getAverage()

    def test_kerning_removed_combine(self):
        kerning = self.getKerning_generic()
        one = {("A", "v"): -10}
        two = {("v", "A"): -10}
        with self.assertRaises(RemovedWarning):
            kerning.combine([one, two])

    def test_kerning_removed_eliminate(self):
        kerning = self.getKerning_generic()
        with self.assertRaises(RemovedWarning):
            kerning.eliminate(leftGlyphsToEliminate=["A"])

    def test_kerning_removed_occurrenceCount(self):
        kerning = self.getKerning_generic()
        with self.assertRaises(RemovedWarning):
            kerning.occurrenceCount(["A"])

    def test_kerning_removed_implodeClasses(self):
        kerning = self.getKerning_generic()
        classes = {"group": ["a", "v"]}
        with self.assertRaises(RemovedWarning):
            kerning.implodeClasses(leftClassDict=classes)

    def test_kerning_removed_explodeClasses(self):
        kerning = self.getKerning_generic()
        classes = {"group": ["a", "v"]}
        with self.assertRaises(RemovedWarning):
            kerning.explodeClasses(leftClassDict=classes)

    def test_kerning_removed_setChanged(self):
        kerning = self.getKerning_generic()
        # As changed() is defined by the environment, only test if a Warning is issued.
        with self.assertWarnsRegex(DeprecationWarning, "Kerning.changed()"):
            kerning.setChanged()

    def test_kerning_removed_getParent(self):
        kerning = self.getKerning_generic()
        with self.assertWarnsRegex(DeprecationWarning, "Kerning.font"):
            kerning.getParent()
        self.assertEqual(kerning.getParent(), kerning.font)

    # ------
    # Groups
    # ------

    def test_groups_deprecated_getParent(self):
        font, _ = self.objectGenerator("font")
        groups = font.groups
        groups.update({
            "group 1": ["A", "B", "C"],
            "group 2": ["x", "y", "z"],
            "group 3": [],
            "group 4": ["A"]
        })
        with self.assertWarnsRegex(DeprecationWarning, "Groups.font"):
            groups.getParent()
        self.assertEqual(groups.getParent(), groups.font)

    def test_groups_deprecated_setChanged(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        groups, _ = self.objectGenerator("groups")
        with self.assertWarnsRegex(DeprecationWarning, "Groups.changed()"):
            groups.setChanged()

    def test_groups_removed_setParent(self):
        font, _ = self.objectGenerator("font")
        groups, _ = self.objectGenerator("groups")
        groups.update({
            "group 1": ["A", "B", "C"],
            "group 2": ["x", "y", "z"],
            "group 3": [],
            "group 4": ["A"]
        })
        with self.assertRaises(RemovedWarning):
            groups.setParent(font)

    # ---
    # Lib
    # ---

    def test_lib_deprecated_getParent_font(self):
        font, _ = self.objectGenerator("font")
        lib = font.lib
        lib.update({
            "key 1": ["A", "B", "C"],
            "key 2": "x",
            "key 3": [],
            "key 4": 20
        })
        with self.assertWarnsRegex(DeprecationWarning, "Lib.font"):
            lib.getParent()
        self.assertEqual(lib.getParent(), lib.font)

    def test_lib_deprecated_getParent_glyph(self):
        font, _ = self.objectGenerator("font")
        glyph = font.newGlyph("Test")
        lib = glyph.lib
        lib.update({
            "key 1": ["A", "B", "C"],
            "key 2": "x",
            "key 3": [],
            "key 4": 20
        })
        with self.assertWarnsRegex(DeprecationWarning, "Lib.glyph"):
            lib.getParent()
        self.assertEqual(lib.getParent(), lib.glyph)

    def test_lib_deprecated_setChanged(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        lib, _ = self.objectGenerator("lib")
        with self.assertWarnsRegex(DeprecationWarning, "Lib.changed()"):
            lib.setChanged()

    def test_lib_removed_setParent_font(self):
        font, _ = self.objectGenerator("font")
        lib, _ = self.objectGenerator("lib")
        lib.update({
            "key 1": ["A", "B", "C"],
            "key 2": "x",
            "key 3": [],
            "key 4": 20
        })
        with self.assertRaises(RemovedWarning):
            lib.setParent(font)

    def test_lib_removed_setParent_glyph(self):
        glyph, _ = self.objectGenerator("glyph")
        lib, _ = self.objectGenerator("lib")
        lib.update({
            "key 1": ["A", "B", "C"],
            "key 2": "x",
            "key 3": [],
            "key 4": 20
        })
        with self.assertRaises(RemovedWarning):
            lib.setParent(glyph)

    # ---------
    # Guideline
    # ---------

    def getGuideline_generic(self):
        guideline, _ = self.objectGenerator("guideline")
        guideline.x = 1
        guideline.y = 2
        guideline.angle = 90
        return guideline

    def getGuideline_transform(self):
        guideline = self.getGuideline_generic()
        guideline.angle = 45.0
        return guideline

    def test_guideline_deprecated__generateIdentifer(self):
        guideline = self.getGuideline_generic()
        with self.assertWarnsRegex(DeprecationWarning, "Guideline._getIdentifier()"):
            guideline._generateIdentifier()
        self.assertEqual(guideline._generateIdentifier(), guideline._getIdentifier())

    def test_guideline_deprecated_generateIdentifer(self):
        guideline = self.getGuideline_generic()
        with self.assertWarnsRegex(DeprecationWarning, "Guideline.getIdentifier()"):
            guideline.generateIdentifier()
        self.assertEqual(guideline.generateIdentifier(), guideline.getIdentifier())

    def test_guideline_deprecated_getParent_glyph(self):
        glyph, _ = self.objectGenerator("glyph")
        guideline = self.getGuideline_generic()
        guideline.glyph = glyph
        with self.assertWarnsRegex(DeprecationWarning, "Guideline.glyph"):
            guideline.getParent()
        self.assertEqual(guideline.getParent(), guideline.glyph)

    def test_guideline_deprecated_getParent_font(self):
        font, _ = self.objectGenerator("font")
        guideline = self.getGuideline_generic()
        guideline.font = font
        with self.assertWarnsRegex(DeprecationWarning, "Guideline.font"):
            guideline.getParent()
        self.assertEqual(guideline.getParent(), guideline.font)

    def test_guideline_deprecated_update(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        guideline, _ = self.objectGenerator("guideline")
        with self.assertWarnsRegex(DeprecationWarning, "Guideline.changed()"):
            guideline.update()

    def test_guideline_deprecated_setChanged(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        guideline, _ = self.objectGenerator("guideline")
        with self.assertWarnsRegex(DeprecationWarning, "Guideline.changed()"):
            guideline.setChanged()

    def test_guideline_removed_setParent(self):
        font, _ = self.objectGenerator("font")
        guideline = self.getGuideline_generic()
        with self.assertRaises(RemovedWarning):
            guideline.setParent(font)

    def test_guideline_deprecated_move(self):
        guideline1, _ = self.objectGenerator("guideline")
        guideline2, _ = self.objectGenerator("guideline")
        with self.assertWarnsRegex(DeprecationWarning, "Guideline.move()"):
            guideline1.move((0, 20))
        guideline2.moveBy((0, 20))
        self.assertEqual(guideline1.y, guideline2.y)

    def test_guideline_deprecated_translate(self):
        guideline1, _ = self.objectGenerator("guideline")
        guideline2, _ = self.objectGenerator("guideline")
        with self.assertWarnsRegex(DeprecationWarning, "Guideline.translate()"):
            guideline1.translate((0, 20))
        guideline2.moveBy((0, 20))
        self.assertEqual(guideline1.y, guideline2.y)

    def test_guideline_deprecated_scale_no_center(self):
        guideline = self.getGuideline_transform()
        with self.assertWarnsRegex(DeprecationWarning, "Guideline.scale()"):
            guideline.scale((-2))
        self.assertEqual(guideline.x, -2)
        self.assertEqual(guideline.y, -4)
        self.assertAlmostEqual(guideline.angle, 225.000, places=3)

    def test_guideline_deprecated_scale_center(self):
        guideline = self.getGuideline_transform()
        with self.assertWarnsRegex(DeprecationWarning, "Guideline.scale()"):
            guideline.scale((-2, 3), center=(1, 2))
        self.assertEqual(guideline.x, 1)
        self.assertEqual(guideline.y, 2)
        self.assertAlmostEqual(guideline.angle, 123.690, places=3)

    def test_guideline_deprecated_rotate_no_offset(self):
        guideline = self.getGuideline_transform()
        with self.assertWarnsRegex(DeprecationWarning, "Guideline.rotate()"):
            guideline.rotate(45)
        self.assertAlmostEqual(guideline.x, -0.707, places=3)
        self.assertAlmostEqual(guideline.y, 2.121, places=3)
        self.assertAlmostEqual(guideline.angle, 0.000, places=3)

    def test_guideline_deprecated_rotate_offset(self):
        guideline = self.getGuideline_transform()
        with self.assertWarnsRegex(DeprecationWarning, "Guideline.rotate()"):
            guideline.rotate(45, offset=(1, 2))
        self.assertAlmostEqual(guideline.x, 1)
        self.assertAlmostEqual(guideline.y, 2)
        self.assertAlmostEqual(guideline.angle, 0.000, places=3)

    def test_guideline_deprecated_transform(self):
        guideline = self.getGuideline_transform()
        with self.assertWarnsRegex(DeprecationWarning, "Guideline.transform()"):
            guideline.transform((2, 0, 0, 3, -3, 2))
        self.assertEqual(guideline.x, -1)
        self.assertEqual(guideline.y, 8)
        self.assertAlmostEqual(guideline.angle, 56.310, places=3)

    def test_guideline_deprecated_skew_no_offset_one_value(self):
        guideline = self.getGuideline_transform()
        with self.assertWarnsRegex(DeprecationWarning, "Guideline.skew()"):
            guideline.skew(100)
        self.assertAlmostEqual(guideline.x, -10.343, places=3)
        self.assertEqual(guideline.y, 2.0)
        self.assertAlmostEqual(guideline.angle, 8.525, places=3)

    def test_guideline_deprecated_skew_no_offset_two_values(self):
        guideline = self.getGuideline_transform()
        with self.assertWarnsRegex(DeprecationWarning, "Guideline.skew()"):
            guideline.skew((100, 200))
        self.assertAlmostEqual(guideline.x, -10.343, places=3)
        self.assertAlmostEqual(guideline.y, 2.364, places=3)
        self.assertAlmostEqual(guideline.angle, 5.446, places=3)

    def test_guideline_deprecated_skew_offset_one_value(self):
        guideline = self.getGuideline_transform()
        with self.assertWarnsRegex(DeprecationWarning, "Guideline.skew()"):
            guideline.skew(100, offset=(1, 2))
        self.assertEqual(guideline.x, 1)
        self.assertEqual(guideline.y, 2)
        self.assertAlmostEqual(guideline.angle, 8.525, places=3)

    def test_guideline_deprecated_skew_offset_two_values(self):
        guideline = self.getGuideline_transform()
        with self.assertWarnsRegex(DeprecationWarning, "Guideline.skew()"):
            guideline.skew((100, 200), offset=(1, 2))
        self.assertEqual(guideline.x, 1)
        self.assertEqual(guideline.y, 2)
        self.assertAlmostEqual(guideline.angle, 5.446, places=3)

    # -----
    # Glyph
    # -----

    def getGlyph_generic(self):
        glyph, _ = self.objectGenerator("glyph")
        glyph.name = "Test Glyph 1"
        glyph.unicode = int(ord("X"))
        glyph.width = 250
        glyph.height = 750
        pen = glyph.getPen()
        pen.moveTo((100, -10))
        pen.lineTo((100, 100))
        pen.lineTo((200, 100))
        pen.lineTo((200, 0))
        pen.closePath()
        pen.moveTo((110, 10))
        pen.lineTo((110, 90))
        pen.lineTo((190, 90))
        pen.lineTo((190, 10))
        pen.closePath()
        glyph.appendAnchor("Test Anchor 1", (1, 2))
        glyph.appendAnchor("Test Anchor 2", (3, 4))
        glyph.appendGuideline((1, 2), 0, "Test Guideline 1")
        glyph.appendGuideline((3, 4), 90, "Test Guideline 2")
        return glyph

    def test_glyph_removed_center(self):
        glyph = self.getGlyph_generic()
        with self.assertRaisesRegex(RemovedWarning, "center()"):
            glyph.center()

    def test_glyph_removed_clearVGuides(self):
        glyph = self.getGlyph_generic()
        with self.assertRaisesRegex(RemovedWarning, "clearGuidelines()"):
            glyph.clearVGuides()

    def test_glyph_removed_clearHGuides(self):
        glyph = self.getGlyph_generic()
        with self.assertRaisesRegex(RemovedWarning, "clearGuidelines()"):
            glyph.clearHGuides()

    def test_glyph_removed_setParent(self):
        font, _ = self.objectGenerator("font")
        glyph = self.getGlyph_generic()
        with self.assertRaisesRegex(RemovedWarning, "setParent()"):
            glyph.setParent(font)

    def test_glyph_deprecated_get_mark(self):
        glyph = self.getGlyph_generic()
        glyph.markColor = (1, 0, 0, 1)
        with self.assertWarnsRegex(DeprecationWarning, "Glyph.markColor"):
            glyph._get_mark()
        self.assertEqual(glyph._get_mark(), glyph.markColor)

    def test_glyph_deprecated_set_mark(self):
        glyph = self.getGlyph_generic()
        with self.assertWarnsRegex(DeprecationWarning, "Glyph.markColor"):
            glyph._set_mark((1, 0, 0, 1))
        self.assertEqual((1, 0, 0, 1), glyph.markColor)

    def test_glyph_deprecated_mark(self):
        glyph = self.getGlyph_generic()
        with self.assertWarnsRegex(DeprecationWarning, "Glyph.markColor"):
            glyph.mark = (1, 0, 0, 1)
        with self.assertWarnsRegex(DeprecationWarning, "Glyph.markColor"):
            glyph.mark
        self.assertEqual((1, 0, 0, 1), glyph.markColor)
