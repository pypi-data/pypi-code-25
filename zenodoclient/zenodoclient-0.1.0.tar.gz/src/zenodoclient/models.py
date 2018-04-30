# coding: utf8
from __future__ import unicode_literals, print_function, division
import re
from functools import partial
from datetime import date

import attr

UPLOAD_TYPES = [
    'publication',
    'poster',
    'presentation',
    'dataset',
    'image',
    'video',  # Video/Audio
    'software',
]

PUBLISHED = 'done'
UNSUBMITTED = 'unsubmitted'
STATES = [
    'inprogress',
    PUBLISHED,
    'error',
    UNSUBMITTED,
]

PUBLICATION_TYPES = [
    'book',
    'section',  # Book section
    'conferencepaper',  # Conference paper
    'article',  # Journal article
    'patent',
    'preprint',
    'report',
    'softwaredocumentation',  # Software documentation
    'thesis',
    'technicalnote',
    'workingpaper',  # Working paper
    'other',
]

IMAGE_TYPES = [
    'figure',
    'plot',
    'drawing',
    'diagram',
    'photo',
    'other',
]

ACCESS_RIGHTS = [
    'open',  # Open Access
    'embargoed',  # Embargoed Access
    'restricted',  # Restricted Access
    'closed',  # Closed Access
]

RELATION_TYPES = [
    'isCitedBy',
    'cites',
    'isSupplementTo',
    'isSupplementedBy',
    'isNewVersionOf',
    'isPreviousVersionOf',
    'isPartOf',
    'hasPart',
    'compiles',
    'isCompiledBy',
    'isIdenticalTo',
    'isAlternateIdentifier',
]

CONTRIBUTOR_TYPES = [
    'ContactPerson',
    'DataCollector',
    'DataCurator',
    'DataManager',
    'Editor',
    'Researcher',
    'RightsHolder',
    'Sponsor',
    'Other',
]


def check_controlled_vocabulary(vocab, condition, instance, attribute, value):
    if condition(instance) and value not in vocab:
        raise ValueError('invalid {0}'.format(attribute))


def check_regex(regex, instance, attribute, value):
    if not re.match(regex, value):
        raise ValueError('{0} must match {1}'.format(attribute, regex))


def check_list_of_objects(keys, instance, attribute, value):
    if not isinstance(value, list):
        raise ValueError(attribute)
    for v in value:
        # we expect a dict with no excess keys ...
        if not isinstance(v, dict) or any(k not in keys for k in v):
            raise ValueError(attribute)
        # ... and all required keys.
        for key, expected in keys.items():
            if expected and (key not in v or (
                    isinstance(expected, list) and v[key] not in expected)):
                raise ValueError(attribute)


def check_persons(instance, attribute, value, with_type=None):
    valid_keys = {'name': True, 'affiliation': False, 'orcid': False, 'gnd': False}
    if with_type:
        valid_keys['type'] = with_type
    check_list_of_objects(valid_keys, instance, attribute, value)


def check_access_right(access_right, instance, attribute, value):
    if instance.access_right == access_right and not value:
        raise ValueError(attribute)


def check_iso639_3(instance, attribute, value):
    if not re.match('[a-z]{3}$', value):
        raise ValueError('invalid ISO 639-3 code')


@attr.s
class Metadata(object):
    upload_type = attr.ib(
        default='dataset',
        validator=attr.validators.in_(UPLOAD_TYPES))
    publication_date = attr.ib(
        default=attr.Factory(lambda: date.today().isoformat()),
        validator=partial(check_regex, '\d{4}-\d{2}-\d{2}'))
    title = attr.ib(default='')
    creators = attr.ib(
        default=attr.Factory(list),
        validator=attr.validators.optional(check_persons))
    description = attr.ib(default='')
    access_right = attr.ib(
        default='open',
        validator=attr.validators.in_(ACCESS_RIGHTS))
    publication_type = attr.ib(
        default=None,
        validator=partial(
            check_controlled_vocabulary,
            PUBLICATION_TYPES,
            lambda i: i.upload_type == 'publication'),
    )
    image_type = attr.ib(
        default=None,
        validator=partial(
            check_controlled_vocabulary,
            IMAGE_TYPES,
            lambda i: i.upload_type == 'image'),
    )
    license = attr.ib(default='cc-by')
    embargo_date = attr.ib(
        default=attr.Factory(date.today),
        validator=[
            partial(check_access_right, 'embargoed'),
            attr.validators.optional(attr.validators.instance_of(date))
        ]
    )
    access_conditions = attr.ib(
        default=None, validator=partial(check_access_right, 'restricted'),
    )
    doi = attr.ib(default='')
    prereserve_doi = attr.ib(default=None)
    keywords = attr.ib(default=attr.Factory(list))
    notes = attr.ib(default='')
    related_identifiers = attr.ib(
        default=attr.Factory(list),
        validator=partial(
            check_list_of_objects,
            dict(scheme=True, identifier=True, relation=RELATION_TYPES))
    )
    contributors = attr.ib(
        default=attr.Factory(list),
        validator=partial(check_persons, with_type=CONTRIBUTOR_TYPES))
    references = attr.ib(default=attr.Factory(list))
    communities = attr.ib(
        default=attr.Factory(list),
        validator=partial(check_list_of_objects, dict(identifier=True))
    )
    grants = attr.ib(
        default=attr.Factory(list),
        validator=partial(check_list_of_objects, dict(id=True))
    )
    journal_title = attr.ib(default='')
    journal_volume = attr.ib(default='')
    journal_issue = attr.ib(default='')
    journal_pages = attr.ib(default='')
    conference_title = attr.ib(default='')
    conference_acronym = attr.ib(default='')
    conference_dates = attr.ib(default='')
    conference_place = attr.ib(default='')
    conference_url = attr.ib(default=None)
    conference_session = attr.ib(default='')
    conference_session_part = attr.ib(default='')
    imprint_publisher = attr.ib(default='')
    imprint_isbn = attr.ib(default='')
    imprint_place = attr.ib(default='')
    partof_title = attr.ib(default='')
    partof_pages = attr.ib(default='')
    thesis_supervisors = attr.ib(default=attr.Factory(list))
    thesis_university = attr.ib(default='')
    subjects = attr.ib(
        default=attr.Factory(list),
        validator=partial(
            check_list_of_objects, dict(term=True, identifier=True, scheme=True))
    )
    version = attr.ib(default='')
    language = attr.ib(
        default=None,
        validator=attr.validators.optional(check_iso639_3))

    def asdict(self):
        res = {}
        for f in attr.fields(self.__class__):
            v = getattr(self, f.name)
            if v or isinstance(v, bool):  # f.default != attr.NOTHING or isinstance(v, bool) or v is not None:
                if isinstance(v, date):
                    v = v.isoformat()
                res[f.name] = v
        return res


class Entity(object):
    def __str__(self):
        """
        To simplify formatting of API URLs, the string representation of entities is their
        id.
        """
        return '{0}'.format(getattr(self, 'id'))

    @classmethod
    def from_dict(cls, d):
        fields = [f.name for f in attr.fields(cls)]
        return cls(**{k: v for k, v in d.items() if k in fields})


@attr.s
class Deposition(Entity):
    """
    http://developers.zenodo.org/#representation
    """
    metadata = attr.ib(
        convert=lambda v: v if isinstance(v, Metadata) else Metadata(**v),
    )
    created = attr.ib()
    id = attr.ib(validator=attr.validators.instance_of(int))
    modified = attr.ib()
    owner = attr.ib()
    state = attr.ib(validator=attr.validators.in_(STATES))
    submitted = attr.ib(validator=attr.validators.instance_of(bool))
    title = attr.ib(default='')
    files = attr.ib(
        default=attr.Factory(list),
        convert=lambda v: [vv if isinstance(vv, DepositionFile) else DepositionFile.from_dict(vv) for vv in v],
    )
    doi = attr.ib(default=None)
    doi_url = attr.ib(default=None)
    record_id = attr.ib(default=None)
    record_url = attr.ib(default=None)

    def validate_update(self):
        if not self.metadata.creators:
            raise ValueError('at least one creator is required')
        if len(self.metadata.title) < 3:
            raise ValueError('title must be at least 3 characters long')
        if len(self.metadata.description) < 3:
            raise ValueError('description must be at least 3 characters long')

    def validate_publish(self):
        if not self.files:
            raise ValueError('at least one file must be uploaded')


@attr.s
class DepositionFile(Entity):
    id = attr.ib()
    filename = attr.ib()
    filesize = attr.ib()
    checksum = attr.ib()
