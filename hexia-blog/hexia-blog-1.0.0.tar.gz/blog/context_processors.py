from blog.models import Tag

def hexia_blog (request):
    return {
        'hexia_blog_tags' : Tag.objects.all(),
        }