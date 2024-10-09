from django.conf import settings
from django.http import HttpResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from core.models import Folder, Document, Part, PipelineDocumentVector

from lib.utils import convert_to_text, generate_summary
from lib.tokenize import extract_parts
from lib.vectorize import vectorize

from .serializers import DocumentSerializer
from .permissions import Permission

import logging
logger = logging.getLogger("django")


class DocumentListView(ListAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = DocumentSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        path = self.request.data.get('path', None)
        if path:
            folder = Folder.get_by_full_path(path)
        else:
            folder = None

        return Document._query_documents({"folder": folder}, self.request.user).order_by('created_on')

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DocumentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get document
        data = request.data
        document_id = data.get('document_id', None)
        document = Document.objects.get(id=document_id)

        if Permission._get_read_permission(document, request.user):
            return Response({"document": document.as_dict()})

        return HttpResponse("Forbiden", status=403)

    def post(self, request):
        # Add document
        # namespace = request.data.get('namespace', None)
        path = request.data.get('path', None)

        if not path:
            return Response({'error': 'Path is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get folder
        folder = Folder.get_by_full_path(path)
        if not folder:
            # Split path
            path_splited = path.split('/')

            # Get last path part
            folder_name = path_splited.pop()

            # Get parent folder
            folder_parent_path = '/'.join(path_splited)
            folder = Folder.get_or_create_folder_tree(folder_parent_path, folder_name, request.user)

        # Check folder permission
        if Permission._get_write_permission(folder, request.user):
            data = {
                "namespace": path,
                "generate_summary": True,
                "parts_size": 1024,
                "parts_overlap": 128,
                "folder": folder,
            }

            # Get file
            file = request.FILES.get('file')
            document = Document.objects.filter(
                folder=folder,
                title=file.name,
            ).first()

            if document is None:
                data['title'] = file.name
                document = Document.create_from_data(data, file, request.user)

            return Response({"path": path, "file": file.name, 'state': document.state, 'url': document.url}, status=status.HTTP_200_OK)

        return HttpResponse("Forbiden", status=403)

    def patch(self, request):
        data = request.data
        context = data.get('context', None)
        document_id = data.get('id', None)

        if not context or not document_id:
            return Response({'error': 'Context and document id are required'}, status=status.HTTP_400_BAD_REQUEST)

        document = Document.objects.get(id=document_id)

        # Check document permission
        if Permission._get_update_permission(document, request.user):
            document.context.update(context)
            document.save()

            return Response({"updated": True})

        return HttpResponse("Forbiden", status=403)

    def delete(self, request):
        data = request.data
        path = data.get('path', None)
        title = data.get('title', None)

        if not path and not title:
            return Response({'error': 'Path and title are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get folder
        folder = Folder.get_by_full_path(path)

        # Get document
        document = Document.objects.get(title=title, folder=folder)

        # Check document permission
        if Permission._get_delete_permission(document, request.user):
            document._delete_file()
            document.delete()
            return Response({"deleted": True})

        return HttpResponse("Forbiden", status=403)


class PipelineDocumentVectorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, attr, id):
        raise NotImplementedError

    def post(self, request, attr, id):
        data = request.data
        pipeline_alias = data.get('pipeline_alias', None)

        if not pipeline_alias:
            return Response({'error': 'Pipeline alias is required'}, status=status.HTTP_400_BAD_REQUEST)

        document = Document.objects.get(id=id)
        if Permission._get_write_permission(document, request.user):
            # VECTORIZE CONTEXT
            if pipeline_alias and attr == 'context':
                vector = vectorize(document.context)
                PipelineDocumentVector(
                    document=document,
                    vector=vector,
                    pipeline=pipeline_alias
                ).save()

                return Response({"pipeline document vector added": True})
        return HttpResponse("Forbiden", status=403)


class ImportExternalDocument(APIView):

    def post(self, request):
        # FIXME: need to get or create folder tree here
        # then create_document with datas
        data = request.data
        logger.info(data)
        return Response({}, status=status.HTTP_200_OK)


def create_document(data, file, user):
    # NOTE: NORMALY GLOBAL FUNCTION TO ADD DOCUMENT

    # Create document
    document = Document(
        title=data['title'],
        namespace=data['namespace'],
        context=data.get('context', {}),
        folder=data['folder'],
        file=file,
        user=user,
        user_can_read=True,
        user_can_write=True,
        user_can_update=True,
        user_can_delete=True,
        group=data['folder'].group,
        group_can_read=data['folder'].group_can_read,
        group_can_write=data['folder'].group_can_write,
        group_can_update=data['folder'].group_can_update,
        group_can_delete=data['folder'].group_can_delete
    )
    # Save it to get file path
    document.save()
    path = document.file.path.replace(settings.MEDIA_ROOT, '')

    try:
        # Convert document into text
        text = convert_to_text(document.file.path)

        # Vectorize the document text
        vector = vectorize(text)

        summary = ""
        # Generate a summary of the document text
        if data.get('generate_summary'):
            summary = generate_summary(text)

        # Update a new Document instance with the extracted data
        document.url = '/media' + path
        document.summary = summary
        document.content = text
        document.embedding = vector

        # Save the document to the database
        document.save()

        # Vectorize parts of the document for later tests
        if (data.get('parts_size') and data.get('parts_overlap')):
            parts = extract_parts(text, size=data['parts_size'], overlap=data['parts_overlap'])
        else:
            parts = extract_parts(text, size=settings.PART_SIZE, overlap=settings.PART_OVERLAP)

        # Iterate over the parts and create Part instances
        for content in parts:
            vector = vectorize(content)
            part = Part(
                document=document,
                content=content,
                embedding=vector
            )
            part.save()
        return 'added', settings.SITE_ROOT + document.url

    except Exception as e:
        logger.info(str(e))
        document.delete()
        return 'error', None
