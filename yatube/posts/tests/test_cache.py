# from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

key = make_template_fragment_key('index_page')
print(key)
