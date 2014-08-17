from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from views import *
from chargen.models import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns("",
    url(r"^list/?$", list),
    url(r"^view/(.*)$", view),
    url(r"^printview/(.*)$", printview),
    url(r"^create/?$", create),
    url(r"^delete/(.*)/?$", delete),
    url(r"^stats/(\d*)/?$", statform),
    url(r"^basics/(\d*)/?$", basicsform),
    url(r"^assignstats/(\d*)/(.*?)/?$", assignstats),
    url(r"^classpage/(\d*)/?$", classpage),
    url(r"^Mage/(\d*)/?$", mage),
    url(r"^Thief/(\d*)/?$", thief),
    url(r"^Fighter/(\d*)/?$", fighter),
    url(r"^Cleric/(\d*)/?$", cleric),
    
    url(r'^admin/', include(admin.site.urls)),
    )
    
if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )
