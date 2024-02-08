from django.urls import path, include

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('api.users.urls')),
    path('', include('api.recipes.urls')),
]
