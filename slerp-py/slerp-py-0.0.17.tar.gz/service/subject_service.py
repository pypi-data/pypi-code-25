from slerp.logger import logging
from slerp.validator import Key, Blank, Number

log = logging.getLogger(__name__)


class SubjectService(object):

    def __init__(self):
        super(SubjectService, self).__init__()


    @Key(['id', 'name', 'tag', 'school_id', 'user_profile_id', 'school', 'user_profile'])
    def add_subject(self, domain):
        subject = Subject(domain)
        subject.save()
        return {'payload': subject.to_dict()}
    
    @Blank(['id'])
    @Number(['page', 'size'])
    def get_subject_by_id(self, domain):
    
        page = int(domain['page'])
        size = int(domain['size'])
        subject_q = Subject.query.filter_by(id=domain['id']).order_by(Subject.id.desc()).paginate(page, size, error_out=False)
        subject_list = list(map(lambda x: x.to_dict(), subject_q.items))
        return {'payload': subject_list, 'total': subject_q.total, 'total_pages': subject_q.pages}