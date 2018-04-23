# coding: utf-8

import os

import zipfile

from flask import abort
from flask import send_file
from flask_restful import reqparse
from flask_restful import Resource
from flask_restful.inputs import boolean

from mlang.res.corpus import Corpus

from mlang.model.seq2seq import Seq2Seq
from mlang.model.seq2seq import load_s2s_model
from mlang.model.seq2seq import train_s2s_model

from mlang.utils import get_cache
from mlang.utils import put_cache

from mlang.config import SERVICE_S2S_DIR

from mlang_server.service.corpus import get_corpus


def init(api, furl):
    api.add_resource(S2S, furl('/s2s/<s2sid>'))
    api.add_resource(S2SPredict, furl('/s2s/predict'))
    api.add_resource(S2SMetaData, furl('/s2s_info/<s2sid>'))
    api.add_resource(S2SMetaDataList, furl('/s2s_list'))


def s2s_exists(s2sid):
    s2sdir = s2s_dir(s2sid)
    return os.path.exists(s2sdir) and not os.path.isfile(s2sdir)


def s2s_dir(s2sid):
    return os.path.join(SERVICE_S2S_DIR, s2sid)


def get_s2s(s2sid, update_cache):
    """
    :param s2sid:
    :param update_cache:
    :return:
    :rtype: Seq2Seq
    """
    s2s = get_cache(s2sid)

    if update_cache:
        s2s = None

    if s2s is None:
        model_path = os.path.join(s2s_dir(s2sid), 'seq2seq.model')
        kmodel_path = os.path.join(s2s_dir(s2sid), 'seq2seq.kmodel.h5')
        s2s = load_s2s_model(model_path, kmodel_path)
        put_cache(s2sid, s2s)

    return s2s


class S2S(Resource):
    """
    语言模型
    """

    def __init__(self):
        self.rqp = reqparse.RequestParser()
        self.rqp.add_argument('corpusid', type=str, required=True, help='corpusid')
        self.rqp.add_argument('epochs', type=int, required=False, default=100, help='epochs')
        self.rqp.add_argument('batch_size', type=int, required=False, default=128, help='batch_size')
        self.rqp.add_argument('min_freq', type=int, required=False, default=5, help='min_freq')
        self.rqp.add_argument('max_length', type=int, required=False, default=50, help='max_length')
        self.rqp.add_argument('hidden_size', type=int, required=False, default=128, help='hidden_size')
        self.rqp.add_argument('layers', type=int, required=False, default=3, help='layers')

    def post(self, s2sid):
        args = self.rqp.parse_args()
        corpusid = args['corpusid']

        corpus = get_corpus(corpusid)

        def x_record_reader(line, **kwargs):
            return line.split('\t')[0].split()

        def y_record_reader(line, **kwargs):
            return line.split('\t')[1].split()

        X_corpus = Corpus(corpus, record_reader=x_record_reader)
        y_corpus = Corpus(corpus, record_reader=y_record_reader)

        s2sdir = s2s_dir(s2sid)
        if not s2s_exists(s2sid):
            os.mkdir(s2sdir)

        epochs = args['epochs']
        batch_size = args['batch_size']
        min_freq = args['min_freq']
        max_length = args['max_length']
        hidden_size = args['hidden_size']
        layers = args['layers']

        train_s2s_model(s2sdir, X_corpus, y_corpus, epoch=epochs, batch_size=batch_size, min_freq=min_freq,
                        max_length=max_length, hidden_size=hidden_size, layers=layers)
        return 'success'

    def delete(self, s2sid):
        if s2s_exists(s2sid):
            os.removedirs(s2s_dir(s2sid))
        return 'success'

    def get(self, s2sid):
        if s2s_exists(s2sid):
            '''
            打包模型文件夹内的文件，发送给客户端
            '''
            zip_file_path = '%s.zip' % s2sid
            zip_file = zipfile.ZipFile(zip_file_path, mode='w', compression=zipfile.ZIP_DEFLATED)

            s2sdir = s2s_dir(s2sid)
            for f in os.listdir(s2sdir):
                file_path = os.path.join(s2sdir, f)
                if os.path.isfile(file_path):
                    zip_file.write(file_path)

            zip_file.close()

            # @after_this_request
            # def clean(response):
            #     os.remove(zip_file_path)

            return send_file(zip_file_path)
        else:
            abort(404)


class S2SPredict(Resource):

    def __init__(self):
        self.rqp = reqparse.RequestParser()
        self.rqp.add_argument('s2sid', type=str, required=True, help='s2sid')
        self.rqp.add_argument('seqs', type=str, required=True, help='seqs')
        self.rqp.add_argument('update_cache', type=boolean, required=False, default=False, help='update_cache')

    def post(self):
        args = self.rqp.parse_args()

        s2sid = args['s2sid']
        seqs = args['seqs']
        update_cache = args['update_cache']

        s2s = get_s2s(s2sid, update_cache)

        raw_seqs = seqs.split()
        print(raw_seqs)
        target_seqs = s2s.predict(raw_seqs)
        return ' '.join([t.word for t in target_seqs])


class S2SMetaData(Resource):
    """
    Seq2Seq模型文件信息
    """

    def get(self, s2sid):
        if s2s_exists(s2sid):
            s2sdir = s2s_dir(s2sid)

            files = []
            for d in os.listdir(s2sdir):
                file_path = os.path.join(s2sdir, d)
                if os.path.isfile(file_path):
                    files.append({
                        'name': d,
                        'size': int(os.path.getsize(file_path)),
                        'atime': int(os.path.getatime(file_path)),
                        'ctime': int(os.path.getctime(file_path)),
                        'mtime': int(os.path.getmtime(file_path))
                    })

            return files
        else:
            return {}


class S2SMetaDataList(Resource):
    """
    Seq2Seq模型文件信息
    """

    def get(self):
        files = []

        for d in os.listdir(SERVICE_S2S_DIR):
            s2sdir = os.path.join(SERVICE_S2S_DIR, d)
            if os.path.isfile(s2sdir):
                continue

            files2 = []
            for d2 in os.listdir(s2sdir):
                file_path = os.path.join(s2sdir, d2)
                if os.path.isfile(file_path):
                    files2.append({
                        'name': d2,
                        'size': int(os.path.getsize(file_path)),
                        'atime': int(os.path.getatime(file_path)),
                        'ctime': int(os.path.getctime(file_path)),
                        'mtime': int(os.path.getmtime(file_path))
                    })

            files.append({
                's2sid': d,
                'files': files2
            })

        return files
