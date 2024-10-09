from django.urls import path, re_path
from . import views as api_views


urlpatterns = [

    # user management
    path('user/info', api_views.UserInfoView.as_view(), name='api_user'),  # GET
    path('user/login/', api_views.UserLoginView.as_view(), name="api_user_login"),  # POST
    path('user/logout/', api_views.UserLogoutView.as_view(), name="api_user_logout"),  # GET
    path('user/prompt/', api_views.UserPromptListView.as_view(), name="api_user_prompt"),  # GET, POST
    path('user/prompt/<str:id>/', api_views.UserPromptDetailView.as_view(), name="api_user_prompt_detail"),  # DELETE
    path('user/validate_token/', api_views.ValidateUserTokenView.as_view(), name='validate-token'),  # POST

    # file management
    path('file/', api_views.FileListView.as_view(), name="api_file"),  # POST
    path('file/<str:uuid>/', api_views.FileDetailView.as_view(), name="api_file_detail"),  # GET
    path('file/<str:uuid>/<str:action>/', api_views.FileActionView.as_view(), name="api_file_action"),  # POST

    # chat management
    path('chat/', api_views.ChatSessionListView.as_view(), name="api_chatsession"),  # GET, POST
    path('chat/<str:id>/', api_views.ChatSessionDetailView.as_view(), name="api_chatsession_detail"),  # GET, PUT, DELETE
    path('chat/<str:id>/<str:action>/', api_views.ChatSessionActionView.as_view(), name="api_chatsession_action"),  # POST

    # message management
    path('message/<str:id>/<str:action>/', api_views.MessageActionView.as_view(), name="api_message_action"),

    # Pipeline management
    path('pipeline/', api_views.PipelineListView.as_view(), name="api_pipeline"),  # GET, POST
    path('pipeline/<str:alias>/', api_views.PipelineDetailView.as_view(), name="api_pipeline"),  # GET, POST
    path('pipeline/all/suggestions/', api_views.PipelineSuggestionView.as_view(), name="api_pipeline_suggestions"),  # POST

    # Factories
    path('factory/', api_views.FactoryListView.as_view(), name="api_factory"),  # GET
    path('factory/<str:alias>/', api_views.FactoryDetailView.as_view(), name="api_factory_detail"),  # GET

    # Folders
    path('folder/', api_views.FolderDetailView.as_view(), name="api_folder"),
    path('folder/documents/<str:id>/', api_views.FolderDocumentView.as_view(), name='api_folder_documents'),  # GET / POST
    path('folders/', api_views.FolderListView.as_view(), name="api_folders"),
    path('folders/research/', api_views.FolderResearchListView.as_view(), name="api_folders"),

    # Documents
    path('document/', api_views.DocumentDetailView.as_view(), name="api_document"),
    path('documents/', api_views.DocumentListView.as_view(), name="api_documents"),

    path('folder_document_rights/', api_views.FolderDocumentRights.as_view(), name="api_folder_document_rights"),

    # Kept for future use :
    # path('webhook/<slug:channel_id>', api_views.webhook, name="api_webhook"),
]
