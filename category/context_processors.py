from .models import Category


# creating a context processor so that we can filter based on category

def menu_links(request):
    links = Category.objects.all()
    
    return dict(links=links)