import json

from pgvector.django import L2Distance

from django.db.models import F, Count
from django.db.models.fields.json import KT

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.models import Document, Part,  Folder, PipelineDocumentVector

from lib.vectorize import vectorize
from lib.json_datetime import DateTimeEncoder


class Search(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.GET.get('query', None)
        namespace = request.GET.get('namespace', None)

        data = {
            'query': query,
            'namespace': namespace
        }
        self.check_data(data)

        results = self.process(data, request.user)
        return Response({"results": results})

    def post(self, request):
        data = request.data
        self.check_data(data)

        results = self.process(data, request.user)
        return Response({"results": results})

    def check_data(self, data):
        if not data.get('query', None) or not data.get('namespace', None):
            return Response({'error': 'Query and namespace are required'}, status=status.HTTP_400_BAD_REQUEST)

    def process(self, data, user):
        query = data['query']
        vector = vectorize(query)  # noqa

        # Perform a search query using the vectorized query
        filtered_documents = Document._query_documents({"namespace": data['namespace']}, user)
        documents = filtered_documents.annotate(
            distance=L2Distance('embedding', vector)
        ).order_by(L2Distance('embedding', vector))[:6]

        # Iterate over the search results and create a list of dictionaries
        results = []
        for document in documents:
            document_as_dict = document.as_dict()
            document_as_dict['distance'] = document.distance
            results.append(document_as_dict)

        return results


class SearchContext(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.GET.get('query')
        pipeline = request.GET.get('pipeline')
        path = request.GET.get('path')

        data = {
            'query': query,
            'pipeline': pipeline,
            'path': path
        }
        self.check_data(data)

        result = self.process(data, request.user)
        return Response(json.dumps(result, cls=DateTimeEncoder))

    def post(self, request):
        data = request.data
        self.check_data(data)

        return self.process(data, request.user)

    def check_data(self, data):
        if not data.get('query', None) or not data.get('pipeline', None) or not data.get('path', None):
            return Response({'error': 'Query and pipeline and path are required'}, status=status.HTTP_400_BAD_REQUEST)

    def process(self, data, user):
        folder = Folder.get_by_full_path(data['path'])
        documents = Document._query_documents({"folder": folder}, user)

        query = data['query']
        vector = vectorize(query)  # noqa

        # Perform a search query using the vectorized query
        pipeline_document_vectors = PipelineDocumentVector.objects.annotate(
            distance=L2Distance('vector', vector)
        ).filter(pipeline=data['pipeline'], document__in=documents).order_by(L2Distance('vector', vector))[:9]

        # Iterate over the search results and create a list of dictionaries
        results = []
        for document_vector in pipeline_document_vectors:
            document_as_dict = document_vector.document.as_dict()
            results.append(document_as_dict)

        # Return the search results as a JSON response
        return Response({"results": results})


class SearchParts(APIView):
    def post(self, request):
        data = request.data
        query = data.get('query', None)
        namespace = data.get('namespace', None)

        if not query or not namespace:
            return Response({'error': 'Query and namespace are required'}, status=status.HTTP_400_BAD_REQUEST)

        vector = vectorize(query)

        # Perform a search query using the vectorized query and check user authorisation
        documents = Document._query_documents({"namespace": namespace}, request.user)
        parts = Part.objects.annotate(
            distance=L2Distance('embedding', vector)
        ).filter(document__in=documents).order_by(L2Distance('embedding', vector))[:6]

        # Iterate over the search ss and create a list of dictionaries
        results = []
        for part in parts:
            part_as_dict = part.as_dict()
            part_as_dict['distance'] = part.distance
            results.append(part_as_dict)

        # Return the search results as a JSON response
        return Response({"results": results})


class Aggregate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # convert json to dict
        data = request.data

        filters = data['filters']
        aggregate = data['aggregate']

        # aggregate: 'context__thema'
        result = {}
        if '__' in aggregate:
            for item in Document.objects.filter(**filters).annotate(annotation=KT(aggregate)).values('annotation').annotate(annotation_count=Count('annotation')):
                result[item['annotation']] = item['annotation_count']
        else:
            for item in Document.objects.filter(**filters).annotate(annotation=F(aggregate)).values('annotation').annotate(annotation_count=Count('annotation')):
                result[item['annotation']] = item['annotation_count']

        return Response(result)
