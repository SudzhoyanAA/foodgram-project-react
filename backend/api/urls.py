from django.urls import path, include

urlpatterns = [
    path('', include('api.users.urls')),
    path('', include('api.recipes.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
