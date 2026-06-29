from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    # AUTH
    path("", views.home, name="home"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.register, name="register"),

    # DASHBOARD
    path("dashboard/", views.dashboard, name="dashboard"),
    path("citizen-dashboard/", views.citizen_dashboard, name="citizen_dashboard"),

    # COMPLAINTS
    path("submit/", views.submit_complaint, name="submit"),
    path("history/", views.complaint_history, name="history"),
    path("complaint/<int:id>/", views.complaint_detail, name="detail"),
    
    # POLICE
    path("police-dashboard/", views.police_dashboard, name="police_dashboard"),

    path("update-case/<int:id>/", views.update_case, name="update_case"),


    # ADMIN
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("assign/<int:complaint_id>/", views.assign_officer, name="assign_officer"),
    path("analytics/", views.analytics, name="analytics"),
    path("reports/", views.reports, name="reports"),

    # EXTRA
    path("pdf/<int:id>/", views.download_pdf, name="pdf"),
    path("map/<int:id>/", views.complaint_map, name="map"),
    path("heatmap/", views.heatmap_dashboard, name="heatmap"),

    path('complaint/<int:id>/', views.complaint_detail, name='complaint_detail'),
    path('complaint/<int:id>/pdf/', views.download_pdf, name='download_pdf'),
    path('submit-complaint/', views.submit_complaint, name='submit_complaint'),
    path('download-pdf/<int:id>/', views.download_pdf, name='download_pdf'),
    path('complaint/<int:id>/', views.edit_complaint, name='edit_complaint'),
    path('complaint/<int:id>/', views.delete_complaint, name='delete_complaint'),
    


    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='password_reset.html'
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset_confirm.html'
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
   
   
