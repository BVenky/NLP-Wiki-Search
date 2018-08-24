from django.conf.urls import url
from WSearch import views

urlpatterns = [
    #url(r'^$', views.HomePageView.as_view()),
    #url(r'^about/$', views.AboutPageView.as_view()),
    url(r'^$', views.index, name='start'),
    url(r'^forms/', views.form, name='search'),
    url(r'^post/', views.post_details, name='post_details'),
    #url('post/new/', views.post_new, name='post_new'),
#    url('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
]
'''from django.conf.urls import url
from WSearch import views

urlpatterns = [
    url(r'^$', views.HomePageView.as_view()),
    url(r'^$', views.form, name='search'),
    url(r'^post/', views.post_details, name='post_details'),
]
'''
