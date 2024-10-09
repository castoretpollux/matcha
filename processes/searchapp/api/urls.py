from django.urls import path, re_path
from . import views as api_views
from . import views_document as api_document_views
from . import views_folder as api_folder_views


urlpatterns = [
    # VIEWS
    path("search/", api_views.Search.as_view(), name="api_search"),
    path("search_context/", api_views.SearchContext.as_view(), name="api_search_context"),
    path("search_parts/", api_views.SearchParts.as_view(), name="api_search_parts"),
    path("aggregate/", api_views.Aggregate.as_view(), name="api_aggregate"),

    # FOLDER VIEWS
    path('folder/', api_folder_views.FolderDetailView.as_view(), name='api_folder'),  # GET / POST
    path('folder/context/<str:id>/', api_folder_views.PipelineFolderContextView.as_view(), name='api_folder_context'),  # GET / POST
    path('folder/documents/<str:id>/', api_folder_views.FolderDocumentView.as_view(), name='api_folder_documents'),  # GET / POST
    path('folders/', api_folder_views.FolderListView.as_view(), name='folder_view'),
    path('folders/research/', api_folder_views.FolderResearchListView.as_view(), name='folder_view'),
    path('folder_document_rights/', api_folder_views.FolderDocumentRights.as_view(), name="api_folder_document_rights"),

    # DOCUMENT VIEWS
    path('document/', api_document_views.DocumentDetailView.as_view(), name='api_document'),  # GET / POST
    path('document/vectorize/<str:attr>/<str:id>/', api_document_views.PipelineDocumentVectorView.as_view(), name='api_document_vectorize'),  # GET / POST
    path('documents/', api_document_views.DocumentListView.as_view(), name='api_documents'),  # GET / POST

    path('import_external_documents/', api_document_views.ImportExternalDocument.as_view(), name="api_import_external_documents"),
]
