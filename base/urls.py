from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # Import auth_views

urlpatterns = [
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('actions/',views.view_records, name='actions'),
    path('employees/',views.view_emp, name='employees'),
    path('approvals/', views.approvals, name='approvals'),
    path('dashboard/', views.dashb, name='dashboard'),
    path('documents/', views.docs2, name='documents'),
    path('recover/', views.reset_password, name='reset_password'),
    path('recover2/', views.reset_password2, name='reset_password2'),
    path('logout/', views.logoutUser, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='base/recover.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='base/recover2.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='base/recoverfin.html'), name='password_reset_complete'),
    path('request_access/', views.request_access, name='request_access'),
    path('check_approved/', views.check_approved, name='check_approved'),
    
    path('view_employee/', views.view_employee, name='view_employee'),
    path('update_employee/', views.update_employee, name='update_employee'),
    path('approved/', views.approvedDocument, name='approved_document'),
    path('remove_emp<int:user_id>/', views.remove_emp, name='remove_emp'),
    #Search functions
    path('search_doc/', views.search_doc, name='search_doc'),
    path('search_doc2/', views.search_doc2, name='search_doc2'),
    path('search_emp/', views.search_emp, name='search_emp'),
    path('search_criticality/', views.search_criticality, name='search_criticality'),

    path('documents_admin/', views.upload_to_drive, name='documents_admin'),
    path('document_view/', views.generate_public_url, name='document_view'),
    path('delete_document/<int:doc_id>/', views.delete_document, name='delete_document'),
    path('approved/', views.approvedDocument, name='approved_document'),

    path('rejected/', views.rejectedDocument, name='rejected_document'),
    path('filter_docs/', views.filter_docs, name='filter_docs'),
    path('filter_docs2/', views.filter_docs2, name='filter_docs2'),
]
