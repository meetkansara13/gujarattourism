from django.contrib.auth import views as auth_views
from django.urls import path
from django.contrib.auth.decorators import login_required
from tourism import views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_destination, name='search-destination'),

    path('destinations/', views.destination_list, name='destination-list'),
    path('destinations-static/', views.destination_static, name='destinations-static'),
    path('destinations/add/', views.destination_create, name='destination-add'),
    path('destinations/<int:pk>/edit/', views.destination_update, name='destination-edit'),
    path('destinations/<int:pk>/delete/', views.destination_delete, name='destination-delete'),
    path('destinations/<int:pk>/', views.destination_detail, name='destination-detail'),
    path('destinations/<int:pk>/book/', views.book_tour, name='book-tour'),
    path('destinations/<int:pk>/package/', views.view_package, name='view-package'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("contact/", views.contact_view, name="contact"),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/bookings/', views.my_bookings, name='my_bookings'),
    path('festivals/', views.festivals, name='festivals'),
    path("heritage/", views.heritage_page, name="heritage"),
    path('book-heritage-tour/', views.book_heritage_tour, name='book_heritage_tour'),
    path('pricing/', views.pricing_view, name='pricing'),
    path('forgot-password/', 
         auth_views.PasswordResetView.as_view(template_name='forgot_password.html'), 
         name='forgot_password'),
    path('reset-password-sent/', 
         auth_views.PasswordResetDoneView.as_view(template_name='reset_password_sent.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='reset_password_form.html'), 
         name='password_reset_confirm'),
    path('reset-password-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='reset_password_done.html'), 
         name='password_reset_complete'),

     path('wishlist/add/<int:id>/', views.add_wishlist, name='add-wishlist'),
     path('wishlist/remove/<int:id>/', views.remove_wishlist, name='remove-wishlist'),
     path('wishlist/', views.my_wishlist, name='my_wishlist'),
     path('my-bookings/', views.my_bookings, name='my-bookings'),
# ai urlss-------------------------------------------------/
     
# AI CENTER
path("ai/", views.ai_hub, name="ai_hub"),

# AI APIs
path("api/ai/chat/", views.ai_chatbot_api, name="ai_chatbot_api"),
path("api/ai/trip-plan/", views.ai_trip_planner_api, name="ai_trip_planner_api"),
path("api/ai/translate/", views.ai_translate_api, name="ai_translate_api"),
path("api/ai/poster/", views.ai_poster_api, name="ai_poster_api"),
path("api/ai/recommend/", views.ai_recommend_api, name="ai_recommend_api"),
path("api/ai/audio-guide/", views.ai_audio_guide_api, name="ai_audio_guide_api"),

# footer side views////////

# Footer Pages
path('careers/', views.careers, name='careers'),
path('press/', views.press, name='press'),
path('faqs/', views.faqs, name='faqs'),
path('support/', views.support, name='support'),
path('terms/', views.terms, name='terms'),
path('privacy/', views.privacy, name='privacy'),
path('about/', views.about, name='about'),
path('our_team/', views.our_team, name='our_team'),
]

