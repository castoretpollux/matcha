import logging

from django.http import HttpResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.models import Folder, Document, PipelineFolderContext

from .permissions import Permission

logger = logging.getLogger("django")


class FolderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Folder tree
        try:
            root_folder = Folder.objects.get(name='ROOT')
            return Response({"folders": [root_folder._get_tree(request.user)]})
        except Folder.DoesNotExist:
            pass  # Default result will apply : returning an empty list
        return Response({"folders": []})

    def post(self, request):
        # Create folder
        data = request.data
        path = data.get('path', None)
        name = data.get('name', None)
        group_can_read = data.get('can_read', False)
        group_can_write = data.get('can_write', False)
        group_can_update = data.get('can_update', False)
        group_can_delete = data.get('can_delete', False)

        # Get parent folder
        parent_folder = Folder.get_by_full_path(path)

        # Get permission
        if Permission._get_write_permission(parent_folder, request.user):
            Folder(
                name=name,
                parent=parent_folder,
                user=request.user,
                user_can_read=True,
                user_can_write=True,
                user_can_update=True,
                user_can_delete=True,
                group=parent_folder.group,
                group_can_read=group_can_read,
                group_can_write=group_can_write,
                group_can_update=group_can_update,
                group_can_delete=group_can_delete,
            ).save()

            return Response({"added": True})

        return HttpResponse("Forbiden", status=403)


class FolderResearchListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Research a folder
        path = request.data.get('path', None)
        query = request.data.get('query', None)

        # Check datas
        if not path or not query:
            return Response({'error': 'Query and path are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get parent folder
        parent_folder = Folder.get_by_full_path(path)

        # Check permission of parent folder
        if Permission._get_read_permission(parent_folder, request.user):
            # Get descendants filter by name
            # _query_descendants while also filter sub descendants with read permission
            if query == 'all':
                filters = {}
            else:
                filters = {"name__icontains": query}

            descendants = parent_folder._query_descendants(filters, request.user)
            folders = list(dict.fromkeys(descendants))

            return Response({"results": folders})

        return HttpResponse("Forbiden", status=403)

    def post(self, request):
        raise NotImplementedError


class FolderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = request.data
        path = data.get('path', None)
        folder_id = data.get('id', None)

        if path:
            folder = Folder.get_by_full_path(path)
        elif folder_id:
            folder = Folder.objects.get(id=folder_id)
        else:
            return HttpResponse("Forbiden", status=403)

        # Check permission
        if Permission._get_read_permission(folder, request.user):
            return Response({
                "folder": folder.name,
                "folder_path": folder.full_path,
                "documents": folder._get_documents(request.user)
            })

        return HttpResponse("Forbiden", status=403)

    def post(self, request):
        raise NotImplementedError

    def delete(self, request):
        data = request.data
        path = data.get('path', None)
        folder = Folder.get_by_full_path(path)

        if Permission._get_delete_permission(folder, request.user):
            folder._delete_files()
            folder.delete()
            return Response({'deleted': True})

        return HttpResponse("Forbiden", status=403)


class FolderDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        folder = Folder.objects.get(id=id)
        query = request.data.get('query', None)

        if Permission._get_read_permission(folder, request.user):
            filters = {"folder": folder}
            if query:
                filters['title__icontains'] = query

            query_documents = Document._query_documents(filters, request.user)
            documents = [(document.title, document.id) for document in query_documents]

            return Response({"results": documents})
        else:
            return HttpResponse("Forbiden", status=403)

    def post(self, request, id):
        raise NotImplementedError


class PipelineFolderContextView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        data = request.data
        alias = data.get('pipeline_alias', None)

        folder = Folder.objects.get(id=id)

        if Permission._get_read_permission(folder, request.user):
            pipeline_folder = PipelineFolderContext.objects.filter(folder=folder, pipeline=alias).first()

            context = None
            if pipeline_folder:
                context = pipeline_folder.context

            return Response({"context": context})
        else:
            return HttpResponse("Forbiden", status=403)

    def post(self, request, id):
        data = request.data

        pipeline = data.get('pipeline_alias', None)
        context = data.get('context', {})
        folder = Folder.objects.get(id=id)

        if not pipeline:
            return Response({'error': 'Pipeline alias is required'}, status=status.HTTP_400_BAD_REQUEST)

        if Permission._get_write_permission(folder, request.user):
            PipelineFolderContext(
                folder=folder,
                context=context,
                pipeline=pipeline
            ).save()
        else:
            return HttpResponse("Forbiden", status=403)


class FolderDocumentRights(APIView):

    def get(self, request):
        raise NotImplementedError

    def post(self, request):
        raise NotImplementedError

    def patch(self, request):
        data = request.data

        # Get folder and documents
        folder = data.get('folder', None)
        documents = data.get('documents', None)

        if not folder or not documents:
            return Response({'error': 'Folder and documents are required'}, status=status.HTTP_400_BAD_REQUEST)

        # UPDATE EACH DOCUMENT RIGHTS
        for document in documents:
            document_obj = Document.objects.get(id=document['id'])
            other_rights_dict = self.set_rights_dict('other', document['other_rights'])
            group_rights_dict = self.set_rights_dict('group', document['group_rights'])
            user_rights_dict = self.set_rights_dict('user', document['user_rights'])
            rights_dict = {
                **other_rights_dict,
                **group_rights_dict,
                **user_rights_dict
            }

            for key, value in rights_dict.items():
                setattr(document_obj, key, value)
            document_obj.save()

        # UPDATE FOLDER RIGHTS
        folder_obj = Folder.objects.get(id=folder['id'])
        folder_other_rights_dict = self.set_rights_dict('other', folder['other_rights'])
        folder_group_rights_dict = self.set_rights_dict('group', folder['group_rights'])
        folder_user_rights_dict = self.set_rights_dict('user', folder['user_rights'])
        folder_rights_dict = {
            **folder_other_rights_dict,
            **folder_group_rights_dict,
            **folder_user_rights_dict
        }

        for key, value in folder_rights_dict.items():
            setattr(folder_obj, key, value)

        folder_obj.save()

        return Response({})

    def set_rights_dict(self, key, rights):
        data_dict = {}
        for right, value in rights.items():
            if right != 'id':
                data_dict[key + '_' + right] = value
        return data_dict
