from django.urls import path, include

urlpatterns = [
    path('', include('api.api_users.urls')),
    path('', include('api.api_recipes.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
