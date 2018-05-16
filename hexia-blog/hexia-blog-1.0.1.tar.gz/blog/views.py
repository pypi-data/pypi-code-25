import operator, functools

from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from blog.models import Blog, Tag
from blog.utils import BLOG_PAGINATION

# Create your views here.

class BlogDetailView(DetailView):
    ''' Blog Detail Page
    '''
    model = Blog
    
class BlogCreateView(LoginRequiredMixin, CreateView):
    ''' Create new Blog
    '''
    model = Blog
    fields = '__all__'

class BlogListView(ListView):
    ''' List of Blogs
        Allows for Search as well.
        INPUTS
           search_string: string for the search - optional
           tag: tag to limit to only blogs in that tag - optional
        OUTPUT
           list of blogs meeting criteria
    '''
    model = Blog
    paginate_by = BLOG_PAGINATION
    
    def get_queryset(self):
        try: search_string = self.request.GET['search_string'].split()
        except: search_string = None

        try:
            title_query = functools.reduce(operator.or_, (Q(name__icontains=x) for x in search_string)) # these are the search parameters
            short_description_query = functools.reduce(operator.or_, (Q(short_description__icontains=x) for x in search_string))
        except:
            title_query = Q()
            short_description_query = Q()

        try: 
            tag_id = self.request.GET['tag']
            tag = Tag.objects.get(id=int(tag_id))
            tag_query = Q(tag=tag)
        except: tag_query = Q()

        query = Q(title_query | short_description_query) & Q(tag_query)

        return Blog.objects.text_search(query)

    def get_context_data(self, *args, **kwargs):
        context = super(BlogListView, self).get_context_data(**kwargs)
        try: context['search_string'] = self.request.GET['search_string']
        except: context['search_string'] = ''

        try: context['selected_tag'] = Tag.objects.get(id=int(self.request.GET['tag']))
        except: context['selected_tag'] = 0

        return context
