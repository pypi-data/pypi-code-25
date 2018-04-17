# coding: utf-8

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# pylint: disable=consider-iterating-dictionary

"""Text token embedding."""
from __future__ import absolute_import
from __future__ import print_function

__all__ = ['register', 'create', 'list_sources',
           'TokenEmbedding', 'GloVe', 'FastText']

import io
import logging
import os
import tarfile
import warnings
import zipfile

from mxnet import nd, registry
from mxnet.gluon.utils import download, check_sha1, _get_repo_file_url

from . import _constants as C


def register(embedding_cls):
    """Registers a new token embedding.


    Once an embedding is registered, we can create an instance of this embedding with
    :func:`~gluonnlp.embedding.create`.


    Examples
    --------
    >>> @gluonnlp.embedding.register
    ... class MyTextEmbed(gluonnlp.embedding.TokenEmbedding):
    ...     def __init__(self, source='my_pretrain_file'):
    ...         pass
    >>> embed = gluonnlp.embedding.create('MyTokenEmbed')
    >>> print(type(embed))
    <class '__main__.MyTokenEmbed'>
    """

    register_text_embedding = registry.get_register_func(TokenEmbedding, 'token embedding')
    return register_text_embedding(embedding_cls)


def create(embedding_name, **kwargs):
    """Creates an instance of token embedding.


    Creates a token embedding instance by loading embedding vectors from an externally hosted
    pre-trained token embedding file, such as those of GloVe and FastText. To get all the valid
    `embedding_name` and `source`, use :func:`gluonnlp.embedding.list_sources`.


    Parameters
    ----------
    embedding_name : str
        The token embedding name (case-insensitive).


    Returns
    -------
    An instance of :class:`gluonnlp.embedding.TokenEmbedding`:
        A token embedding instance that loads embedding vectors from an externally hosted
        pre-trained token embedding file.
    """

    create_text_embedding = registry.get_create_func(TokenEmbedding, 'token embedding')
    return create_text_embedding(embedding_name, **kwargs)


def list_sources(embedding_name=None):
    """Get valid token embedding names and their pre-trained file names.


    To load token embedding vectors from an externally hosted pre-trained token embedding file,
    such as those of GloVe and FastText, one should use
    `gluonnlp.embedding.create(embedding_name, source)`. This method returns all the
    valid names of `source` for the specified `embedding_name`. If `embedding_name` is set to
    None, this method returns all the valid names of `embedding_name` with their associated
    `source`.


    Parameters
    ----------
    embedding_name : str or None, default None
        The pre-trained token embedding name.


    Returns
    -------
    dict or list:
        A list of all the valid pre-trained token embedding file names (`source`) for the
        specified token embedding name (`embedding_name`). If the text embeding name is set to None,
        returns a dict mapping each valid token embedding name to a list of valid pre-trained files
        (`source`). They can be plugged into
        `gluonnlp.embedding.create(embedding_name, source)`.
    """

    text_embedding_reg = registry.get_registry(TokenEmbedding)

    if embedding_name:
        if embedding_name not in text_embedding_reg:
            raise KeyError('Cannot find `embedding_name` {}. Use '
                           '`list_sources(embedding_name=None).keys()` to get all the valid'
                           'embedding names.'.format(embedding_name))
        return list(text_embedding_reg[embedding_name].pretrained_file_name_sha1.keys())
    else:
        return {embedding_name: list(embedding_cls.pretrained_file_name_sha1.keys())
                for embedding_name, embedding_cls in registry.get_registry(TokenEmbedding).items()}


class TokenEmbedding(object):
    """Token embedding base class.


    To load token embedding from an externally hosted pre-trained token embedding file, such as
    those of GloVe and FastText, use :func:`gluonnlp.embedding.create`.
    To get all the available `embedding_name` and `source`, use
    :func:`gluonnlp.embedding.list_sources`.

    Alternatively, to load embedding vectors from a custom pre-trained token embedding file, use
    :func:`gluonnlp.embedding.from_file`.

    If `unknown_token` is None, looking up unknown tokens results in KeyError.
    Otherwise, for every unknown token, if its representation `self.unknown_token` is encountered
    in the pre-trained token embedding file, index 0 of `self.idx_to_vec` maps to the pre-trained
    token embedding vector loaded from the file; otherwise, index 0 of `self.idx_to_vec` maps to
    the token embedding vector initialized by `init_unknown_vec`.

    If a token is encountered multiple times in the pre-trained token embedding file, only the
    first-encountered token embedding vector will be loaded and the rest will be skipped.


    Parameters
    ----------
    unknown_token : hashable object or None, default '<unk>'
        The representation for any unknown token. In other words, any unknown token will be indexed
        as the same representation.


    Properties
    ----------
    idx_to_token : list of strs
        A list of indexed tokens where the list indices and the token indices are aligned.
    idx_to_vec : mxnet.ndarray.NDArray
        For all the indexed tokens in this embedding, this NDArray maps each token's index to an
        embedding vector.
    unknown_token : hashable object or None
        The representation for any unknown token. In other words, any unknown token will be indexed
        as the same representation.
    """

    def __init__(self, unknown_token='<unk>'):
        self._unknown_token = unknown_token
        self._idx_to_token = [unknown_token] if unknown_token else []
        self._token_to_idx = {token: idx for idx, token in enumerate(self._idx_to_token)}
        self._idx_to_vec = None

        if unknown_token:
            self._to_idx = lambda x: self._token_to_idx.get(x, C.UNK_IDX)
        else:
            self._to_idx = lambda x: self._token_to_idx[x]

    @classmethod
    def _get_download_file_name(cls, file_name):
        return file_name

    @classmethod
    def _get_pretrained_file_url(cls, pretrained_file_name):
        cls_name = cls.__name__.lower()

        namespace = 'gluon/embeddings/{}'.format(cls_name)
        return _get_repo_file_url(namespace, cls._get_download_file_name(pretrained_file_name))

    @classmethod
    def _get_pretrained_file(cls, embedding_root, pretrained_file_name):
        cls_name = cls.__name__.lower()
        embedding_root = os.path.expanduser(embedding_root)
        url = cls._get_pretrained_file_url(pretrained_file_name)

        embedding_dir = os.path.join(embedding_root, cls_name)
        pretrained_file_path = os.path.join(embedding_dir, pretrained_file_name)
        downloaded_file = os.path.basename(url)
        downloaded_file_path = os.path.join(embedding_dir, downloaded_file)

        expected_file_hash = cls.pretrained_file_name_sha1[pretrained_file_name]

        if hasattr(cls, 'pretrained_archive_name_sha1'):
            expected_downloaded_hash = \
                cls.pretrained_archive_name_sha1[downloaded_file]
        else:
            expected_downloaded_hash = expected_file_hash

        if not os.path.exists(pretrained_file_path) \
           or not check_sha1(pretrained_file_path, expected_file_hash):
            download(url, downloaded_file_path, sha1_hash=expected_downloaded_hash)

            ext = os.path.splitext(downloaded_file)[1]
            if ext == '.zip':
                with zipfile.ZipFile(downloaded_file_path, 'r') as zf:
                    zf.extractall(embedding_dir)
            elif ext == '.gz':
                with tarfile.open(downloaded_file_path, 'r:gz') as tar:
                    tar.extractall(path=embedding_dir)
        return pretrained_file_path

    def _load_embedding(self, pretrained_file_path, elem_delim, init_unknown_vec, encoding='utf8'):
        """Load embedding vectors from a pre-trained token embedding file.


        For every unknown token, if its representation `self.unknown_token` is encountered in the
        pre-trained token embedding file, index 0 of `self.idx_to_vec` maps to the pre-trained token
        embedding vector loaded from the file; otherwise, index 0 of `self.idx_to_vec` maps to the
        text embedding vector initialized by `init_unknown_vec`.

        If a token is encountered multiple times in the pre-trained text embedding file, only the
        first-encountered token embedding vector will be loaded and the rest will be skipped.
        """

        pretrained_file_path = os.path.expanduser(pretrained_file_path)

        if not os.path.isfile(pretrained_file_path):
            raise ValueError('`pretrained_file_path` must be a valid path to the pre-trained '
                             'token embedding file.')

        logging.info('Loading pre-trained token embedding vectors from %s', pretrained_file_path)
        vec_len = None
        all_elems = []
        tokens = set()
        loaded_unknown_vec = None
        with io.open(pretrained_file_path, 'r', encoding=encoding) as f:
            for line_num, line in enumerate(f):
                elems = line.rstrip().split(elem_delim)

                assert len(elems) > 1, 'line {} in {}: unexpected data format.'.format(
                    line_num, pretrained_file_path)

                token, elems = elems[0], [float(i) for i in elems[1:]]

                if token == self.unknown_token and loaded_unknown_vec is None:
                    loaded_unknown_vec = elems
                    tokens.add(self.unknown_token)
                elif token in tokens:
                    warnings.warn('line {} in {}: duplicate embedding found for '
                                  'token "{}". Skipped.'.format(line_num, pretrained_file_path,
                                                                token))
                elif len(elems) == 1 and line_num == 0:
                    warnings.warn('line {} in {}: skipped likely header line.'
                                  .format(line_num, pretrained_file_path))
                else:
                    if not vec_len:
                        vec_len = len(elems)
                        if self.unknown_token:
                            # Reserve a vector slot for the unknown token at the very beggining
                            # because the unknown token index is 0.
                            all_elems.extend([0] * vec_len)
                    else:
                        assert len(elems) == vec_len, \
                            'line {} in {}: found vector of inconsistent dimension for token ' \
                            '"{}". expected dim: {}, found: {}'.format(line_num,
                                                                       pretrained_file_path,
                                                                       token, vec_len, len(elems))
                    all_elems.extend(elems)
                    self._idx_to_token.append(token)
                    self._token_to_idx[token] = len(self._idx_to_token) - 1
                    tokens.add(token)

        self._idx_to_vec = nd.array(all_elems).reshape((-1, vec_len))

        if self.unknown_token:
            if loaded_unknown_vec is None:
                self._idx_to_vec[C.UNK_IDX] = init_unknown_vec(shape=vec_len)
            else:
                self._idx_to_vec[C.UNK_IDX] = nd.array(loaded_unknown_vec)

    @property
    def idx_to_token(self):
        return self._idx_to_token

    @property
    def idx_to_vec(self):
        return self._idx_to_vec

    @property
    def unknown_token(self):
        return self._unknown_token

    def __contains__(self, x):
        return x in self._token_to_idx

    def __getitem__(self, tokens):
        """Looks up embedding vectors of text tokens.


        Parameters
        ----------
        tokens : str or list of strs
            A token or a list of tokens.


        Returns
        -------
        mxnet.ndarray.NDArray:
            The embedding vector(s) of the token(s). According to numpy conventions, if `tokens` is
            a string, returns a 1-D NDArray (vector); if `tokens` is a list of
            strings, returns a 2-D NDArray (matrix) of shape=(len(tokens), vec_len).
        """

        to_reduce = not isinstance(tokens, (list, tuple))
        if to_reduce:
            tokens = [tokens]

        indices = [self._to_idx(token) for token in tokens]

        vecs = nd.Embedding(nd.array(indices), self.idx_to_vec, self.idx_to_vec.shape[0],
                            self.idx_to_vec.shape[1])

        return vecs[0] if to_reduce else vecs

    def __setitem__(self, tokens, new_embedding):
        """Updates embedding vectors for tokens.


        Parameters
        ----------
        tokens : hashable object or a list or tuple of hashable objects
            A token or a list of tokens whose embedding vector are to be updated.
        new_embedding : mxnet.ndarray.NDArray
            An NDArray to be assigned to the embedding vectors of `tokens`. Its length must be equal
            to the number of `tokens` and its width must be equal to the dimension of embedding of
            the glossary. If `tokens` is a singleton, it must be 1-D or 2-D. If `tokens` is a list
            of multiple strings, it must be 2-D.
        """

        assert self._idx_to_vec is not None, '`idx_to_vec` has not been initialized.'

        if not isinstance(tokens, (list, tuple)) or len(tokens) == 1:
            assert isinstance(new_embedding, nd.NDArray) and len(new_embedding.shape) in [1, 2], \
                '`new_embedding` must be a 1-D or 2-D NDArray if `tokens` is a single token.'
            if not isinstance(tokens, (list, tuple)):
                tokens = [tokens]
            if len(new_embedding.shape) == 1:
                new_embedding = new_embedding.expand_dims(0)

        else:
            assert isinstance(new_embedding, nd.NDArray) and len(new_embedding.shape) == 2, \
                '`new_embedding` must be a 2-D NDArray if `tokens` is a list of multiple strings.'
        assert new_embedding.shape == (len(tokens), self._idx_to_vec.shape[1]), \
            'The length of `new_embedding` must be equal to the number of tokens and the width of' \
            'new_embedding must be equal to the dimension of embedding of the glossary.'

        indices = []
        for token in tokens:
            if token in self._token_to_idx:
                indices.append(self._token_to_idx[token])
            else:
                if self.unknown_token:
                    raise KeyError('Token "{}" is unknown. To update the embedding vector for an'
                                   ' unknown token, please explicitly include "{}" as the '
                                   '`unknown_token` in `tokens`. This is to avoid unintended '
                                   'updates.'.format(token, self._idx_to_token[C.UNK_IDX]))
                else:
                    raise KeyError('Token "{}" is unknown. Updating the embedding vector for an '
                                   'unknown token is not allowed because `unknown_token` is not '
                                   'specified.'.format(token))

        self._idx_to_vec[nd.array(indices)] = new_embedding

    @classmethod
    def _check_pretrained_file_names(cls, file_name):
        """Checks if a pre-trained token embedding file name is valid.


        Parameters
        ----------
        file_name : str
            The pre-trained token embedding file.
        """

        embedding_name = cls.__name__.lower()
        if file_name not in cls.pretrained_file_name_sha1:
            raise KeyError('Cannot find pre-trained file {} for token embedding {}. Valid '
                           'pre-trained file names for embedding {}: {}'.format(
                               file_name, embedding_name, embedding_name,
                               ', '.join(cls.pretrained_file_name_sha1.keys())))

    @staticmethod
    def from_file(file_path, elem_delim=' ', encoding='utf8', init_unknown_vec=nd.zeros, **kwargs):
        """Creates a user-defined token embedding from a pre-trained embedding file.


        This is to load embedding vectors from a user-defined pre-trained token embedding file.
        For example, if `elem_delim` = ' ', the expected format of a custom pre-trained token
        embedding file may look like:

        'hello 0.1 0.2 0.3 0.4 0.5\\\\nworld 1.1 1.2 1.3 1.4 1.5\\\\n'

        where embedding vectors of words `hello` and `world` are [0.1, 0.2, 0.3, 0.4, 0.5] and
        [1.1, 1.2, 1.3, 1.4, 1.5] respectively.


        Parameters
        ----------
        file_path : str
            The path to the user-defined pre-trained token embedding file.
        elem_delim : str, default ' '
            The delimiter for splitting a token and every embedding vector element value on the same
            line of the custom pre-trained token embedding file.
        encoding : str, default 'utf8'
            The encoding scheme for reading the custom pre-trained token embedding file.
        init_unknown_vec : callback
            The callback used to initialize the embedding vector for the unknown token.


        Returns
        -------
        instance of :class:`gluonnlp.embedding.TokenEmbedding`
            The user-defined token embedding instance.
        """
        embedding = TokenEmbedding(**kwargs)
        embedding._load_embedding(file_path, elem_delim, init_unknown_vec, encoding)

        return embedding


@register
class GloVe(TokenEmbedding):
    """The GloVe word embedding.


    GloVe is an unsupervised learning algorithm for obtaining vector representations for words.
    Training is performed on aggregated global word-word co-occurrence statistics from a corpus, and
    the resulting representations showcase interesting linear substructures of the word vector
    space. (Source from https://nlp.stanford.edu/projects/glove/)

    Reference:

    GloVe: Global Vectors for Word Representation.
    Jeffrey Pennington, Richard Socher, and Christopher D. Manning.
    https://nlp.stanford.edu/pubs/glove.pdf

    Website:

    https://nlp.stanford.edu/projects/glove/

    To get the updated URLs to the externally hosted pre-trained token embedding
    files, visit https://nlp.stanford.edu/projects/glove/

    License for pre-trained embedding:

    https://opendatacommons.org/licenses/pddl/


    Parameters
    ----------
    source : str, default 'glove.6B.50d.txt'
        The name of the pre-trained token embedding file.
    embedding_root : str, default os.path.join('~', '.mxnet', 'embedding')
        The root directory for storing embedding-related files.
    init_unknown_vec : callback
        The callback used to initialize the embedding vector for the unknown token.


    Properties
    ----------
    idx_to_vec : mxnet.ndarray.NDArray
        For all the indexed tokens in this embedding, this NDArray maps each token's index to an
        embedding vector.
    unknown_token : hashable object
        The representation for any unknown token. In other words, any unknown token will be indexed
        as the same representation.
    """

    # Map a pre-trained token embedding archive file and its SHA-1 hash.
    pretrained_archive_name_sha1 = C.GLOVE_PRETRAINED_FILE_SHA1

    # Map a pre-trained token embedding file and its SHA-1 hash.
    pretrained_file_name_sha1 = C.GLOVE_PRETRAINED_ARCHIVE_SHA1

    @classmethod
    def _get_download_file_name(cls, file_name):
        # Map a pre-trained embedding file to its archive to download.
        src_archive = {archive.split('.')[1]: archive for archive in
                       GloVe.pretrained_archive_name_sha1.keys()}
        archive = src_archive[file_name.split('.')[1]]
        return archive

    def __init__(self, source='glove.6B.50d.txt',
                 embedding_root=os.path.join('~', '.mxnet', 'embedding'),
                 init_unknown_vec=nd.zeros, **kwargs):
        GloVe._check_pretrained_file_names(source)

        super(GloVe, self).__init__(**kwargs)
        pretrained_file_path = GloVe._get_pretrained_file(embedding_root, source)

        self._load_embedding(pretrained_file_path, ' ', init_unknown_vec)


@register
class FastText(TokenEmbedding):
    """The fastText word embedding.


    FastText is an open-source, free, lightweight library that allows users to learn text
    representations and text classifiers. It works on standard, generic hardware. Models can later
    be reduced in size to even fit on mobile devices. (Source from https://fasttext.cc/)


    References:

    Enriching Word Vectors with Subword Information.
    Piotr Bojanowski, Edouard Grave, Armand Joulin, and Tomas Mikolov.
    https://arxiv.org/abs/1607.04606

    Bag of Tricks for Efficient Text Classification.
    Armand Joulin, Edouard Grave, Piotr Bojanowski, and Tomas Mikolov.
    https://arxiv.org/abs/1607.01759

    FastText.zip: Compressing text classification models.
    Armand Joulin, Edouard Grave, Piotr Bojanowski, Matthijs Douze, Herve Jegou, and Tomas Mikolov.
    https://arxiv.org/abs/1612.03651

    For 'wiki.multi' embedding:
    Word Translation Without Parallel Data
    Alexis Conneau, Guillaume Lample, Marc'Aurelio Ranzato, Ludovic Denoyer, and Herve Jegou.
    https://arxiv.org/abs/1710.04087

    Website:

    https://fasttext.cc/

    To get the updated URLs to the externally hosted pre-trained token embedding files, visit
    https://github.com/facebookresearch/fastText/blob/master/pretrained-vectors.md

    License for pre-trained embedding:

    https://creativecommons.org/licenses/by-sa/3.0/


    Parameters
    ----------
    source : str, default 'glove.6B.50d.txt'
        The name of the pre-trained token embedding file.
    embedding_root : str, default os.path.join('~', '.mxnet', 'embedding')
        The root directory for storing embedding-related files.
    init_unknown_vec : callback
        The callback used to initialize the embedding vector for the unknown token.


    Properties
    ----------
    idx_to_vec : mxnet.ndarray.NDArray
        For all the indexed tokens in this embedding, this NDArray maps each token's index to an
        embedding vector.
    unknown_token : hashable object
        The representation for any unknown token. In other words, any unknown token will be indexed
        as the same representation.
    """

    # Map a pre-trained token embedding archive file and its SHA-1 hash.
    pretrained_archive_name_sha1 = C.FAST_TEXT_ARCHIVE_SHA1

    # Map a pre-trained token embedding file and its SHA-1 hash.
    pretrained_file_name_sha1 = C.FAST_TEXT_FILE_SHA1

    @classmethod
    def _get_download_file_name(cls, file_name):
        # Map a pre-trained embedding file to its archive to download.
        return '.'.join(file_name.split('.')[:-1]) + '.zip'

    def __init__(self, source='wiki.simple.vec',
                 embedding_root=os.path.join('~', '.mxnet', 'embedding'),
                 init_unknown_vec=nd.zeros, **kwargs):
        FastText._check_pretrained_file_names(source)

        super(FastText, self).__init__(**kwargs)
        pretrained_file_path = FastText._get_pretrained_file(embedding_root, source)

        self._load_embedding(pretrained_file_path, ' ', init_unknown_vec)
