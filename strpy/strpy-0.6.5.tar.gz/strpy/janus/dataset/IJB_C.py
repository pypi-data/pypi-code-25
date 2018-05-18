import os
import strpy.janus.environ
from strpy.bobo.util import remkdir, isstring, filebase, quietprint, tolist, islist, is_hiddenfile, readcsv
from strpy.bobo.image import ImageDetection
from strpy.bobo.video import VideoDetection
from strpy.janus.template import GalleryTemplate
from strpy.bobo.geometry import BoundingBox
from itertools import product, groupby
from collections import OrderedDict


def uniq_ijbc_id(im):
    return '%s_%s' % (im.attributes['SIGHTING_ID'], os.path.basename(im.filename()).split('.')[0])

class IJBC(object):
    def __init__(self, ijbcdir):
        self.datadir = ijbcdir  # this dir contains protocols/
        if not os.path.isdir(self.datadir):
            raise ValueError('Download Janus IJB-C dataset manually to "%s" ' % self.datadir)

    def __repr__(self):
        return str('<janus.dataset.ijbc: %s>' % self.datadir)

    def _parse_csv(self, csvfile):
        """ [generic ijbc metadata csv]"""
        fields = 'TEMPLATE_ID,SUBJECT_ID,FILENAME,SIGHTING_ID,FACE_X,FACE_Y,FACE_WIDTH,FACE_HEIGHT,FRAME_NUM,FACIAL_HAIR,AGE,INDOOR_OUTDOOR,SKINTONE,GENDER,YAW,ROLL,OCC1,OCC2,OCC3,OCC4,OCC5,OCC6,OCC7,OCC8,OCC9,OCC10,OCC11,OCC12,OCC13,OCC14,OCC15,OCC16,OCC17,OCC18'
        schema = fields.split(',')

        csv = readcsv(csvfile)
        imdet = [ImageDetection(filename=os.path.join(self.datadir, x[2]), category='%04d' % int(x[1]),
                             xmin=float(x[4]) if len(x[4]) > 0 else float('nan'),
                             ymin=float(x[5]) if len(x[5]) > 0 else float('nan'),
                             xmax=float(x[4])+float(x[6]) if ((len(x[4])>0) and (len(x[6])>0)) else float('nan'),
                             ymax=float(x[5])+float(x[7]) if ((len(x[5])>0) and (len(x[7])>0)) else float('nan'),
                             attributes={k:v for (k,v) in zip(schema,x)}) for x in csv[1:]]
        return imdet

    def _ijbc_11_covariate_probe_reference(self):
        imdet = self._parse_csv(os.path.join(self.datadir, 'protocols', 'ijbc_11_covariate_probe_reference.csv'))
        imtmpl = [list(x) for (k,x) in groupby(imdet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # list of sightings for each template
        return [GalleryTemplate(media=t) for t in imtmpl]


    def _ijbc_11_S1_S2_matches(self):
        return readcsv(os.path.join(self.datadir, 'protocols', 'ijbc_11_G1_G2_matches.csv'))

    def _ijbc_11_covariate_matches(self):
        return readcsv(os.path.join(self.datadir, 'protocols', 'ijbc_11_covariate_matches.csv'))

    def _ijbc_1N_gallery_S1(self):
        imdet = self._parse_csv(os.path.join(self.datadir, 'protocols', 'ijbc_1N_gallery_G1.csv'))
        imtmpl = [list(x) for (k,x) in groupby(imdet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # list of sightings for each template
        return [GalleryTemplate(media=t) for t in imtmpl]

    def _ijbc_1N_gallery_S2(self):
        imdet = self._parse_csv(os.path.join(self.datadir, 'protocols', 'ijbc_1N_gallery_G2.csv'))
        imtmpl = [list(x) for (k,x) in groupby(imdet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # list of sightings for each template
        return [GalleryTemplate(media=t) for t in imtmpl]

    def _ijbc_1N_probe_mixed(self):
        imdet = self._parse_csv(os.path.join(self.datadir, 'protocols', 'ijbc_1N_probe_mixed.csv'))
        immedia = [list(x) for (k,x) in groupby(imdet, key=lambda im: ('%s_%s' % (im.attributes['TEMPLATE_ID'], im.attributes['SIGHTING_ID'])))]  # list of media
        imviddet = [VideoDetection(frames=x) if len(x)>1 else x[0] for x in immedia]  # media to video
        imtmpl = [list(x) for (k,x) in groupby(imviddet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # video and image to template
        return [GalleryTemplate(media=t) for t in imtmpl]

    def _ijbc_face_detection(self):
        return self._parse_csv_5(os.path.join(self.datadir, 'protocols', 'ijbc_face_detection.csv'))

    def ijbc_11(self):
        """Returns (tuples of template IDs for verification, dictionary mapping template IDs to index into template list, template list)"""
        tmpl = self._ijbc_1N_gallery_S1() + self._ijbc_1N_gallery_S2() + self._ijbc_1N_probe_mixed()
        id_to_index = {str(t.templateid()):k for (k,t) in enumerate(tmpl)}
        id_pairs = self._ijbc_11_S1_S2_matches()
        return (id_pairs, id_to_index, tmpl)


    def ijbc_11_covariate(self):
        """Returns (tuples of template IDs for verification, dictionary mapping template IDs to index into template list, template list)"""
        tmpl = self._ijbc_11_covariate_probe_reference()
        dict_id_to_index = {str(t.templateid()):k for (k,t) in enumerate(tmpl)}
        id_pairs = self._ijbc_11_covariate_matches()
        return (id_pairs, dict_id_to_index, tmpl)

    def ijbc_1N_probe_mixed_gallery_S1(self):
        """Returns (probe templates, gallery templates)"""
        return (self._ijbc_1N_probe_mixed(), self._ijbc_1N_gallery_S1())

    def ijbc_1N_probe_mixed_gallery_S2(self):
        """Returns (probe templates, gallery templates)"""
        return (self._ijbc_1N_probe_mixed(), self._ijbc_1N_gallery_S2())

    def ijbc_detection(self):
        return self._ijbc_face_detection()

    def all_sightings(self,P=None):
        if (P==None):
            P = [self._ijbc_11_covariate_probe_reference(), self._ijbc_1N_gallery_S2() + self._ijbc_1N_gallery_S1(),
                 self._ijbc_1N_probe_mixed()]
        D = {}
        for (k,p) in enumerate(P):  # every protocol
            for t in p:  # every template in every protocol
                for v in t:  # every video or image
                    for im in v:  # every frame or image
                        key = uniq_ijbc_id(im)
                        if key not in D:
                            D[key] = im
                        elif D[key].boundingbox().overlap(im.boundingbox()) < 0.99:
                            print D[key], ' versus ', im

                        # So far, after the latest update, there are no duplicates according to
                        # this hashing function in uniq_ijbc_id = (fileID_sightingID).
                        # Uncomment the lines above to calculate the
                        # bb overlap to see if a labeling error/ duplicate exists.
                        # ijbc should have 68919 sids according to uniq_ijbc_id

                        # The hash function fpath_bboxRepr is way slow, albeit it should guarantee uniqueness.
                        # However, due to some bbox labeling errors
                        # (different subject id, different sighting id, same filename, same bbox)
                        # 250ish sightings are not included
                        # under this hash ijbc has 68666 sightings
                        # key = im.filename() + str(im.boundingbox()) labeling errors
                        # if key not in D.keys():
                        #     D[key] = im  # not seen this one yet
        return D.values()

    def ijbc_clustering_protocol7(self):
        csv = ['ijbc_clustering_32_hint_100.csv', 'ijbc_clustering_64_hint_100.csv', 'ijbc_clustering_128_hint_1000.csv', 'ijbc_clustering_256_hint_1000.csv', 'ijbc_clustering_512_hint_1000.csv', 'ijbc_clustering_1024_hint_10000.csv', 'ijbc_clustering_1870_hint_10000.csv']
        return [self._parse_csv_12(os.path.join(self.datadir, 'clustering_protocols', 'test7_clustering', c)) for c in csv]


