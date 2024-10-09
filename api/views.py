import json
import logging

import requests

from django.conf import settings
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.middleware.csrf import get_token
from django.contrib.auth.models import Group, User

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from core.models import ChatSession, ChatSessionMessage, ChatSessionFile, UserPreference, UserPrompt, DynamicPipeline
from core.serializers import ChatSessionSerializer

from lib.utils import get_best_suggestion, generate_pipeline_dict
from lib.app_requests import SearchRequest

from machinery.router import get_pipeline_dict, get_factory_dict, get_pipeline_class, get_output_kind_to_pipeline_dict
from machinery.factories.common_schema import BaseFactorySchema
from machinery.router import get_factory_class

from .permissions import PipelinePermission

logger = logging.getLogger("django")


###################
# USER MANAGEMENT #
###################

class UserInfoView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        result = {}
        user = request.user

        if not request.user.is_anonymous:
            result['connected'] = True

            result['user'] = {
                'id': user.id,
                'username': user.username,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff,
            }
            user_preference = UserPreference.objects.filter(user=user).first()
            if user.is_superuser:
                groups = Group.objects.all()
                users = User.objects.all()
            else:
                groups = Group.objects.filter(id__in=user.groups.values_list('id', flat=True))
                users = User.objects.filter(groups__in=groups).distinct()
            result['preferences'] = user_preference.as_dict() if user_preference else {}
            result['groups'] = [(group.id, group.name) for group in groups]
            result['users'] = [(user.id, user.username) for user in users]

        else:
            result['connected'] = False
        return JsonResponse(result)


class UserLoginView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            data = {
                'status': 'success',
                'token': token.key,
                # 'csrfToken': csrf_token,
                'max_age': settings.SESSION_COOKIE_AGE,  # in seconds
            }
            return Response(data)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    """
    View to logout the user and delete the token.
    """
    def get(self, request):
        # Logout the user
        request.user.auth_token.delete()

        return Response({})


class UserPromptListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_preferences = UserPreference.objects.filter(user=request.user).first()
        if user_preferences:
            user_prompts = UserPrompt.objects.filter(preference=user_preferences)
            return Response({
                'prompts': [prompt.as_dict() for prompt in user_prompts]
            })
        else:
            return Response({
                'prompts': []
            })

    def post(self, request):
        json_data = json.loads(request.body)
        user_preferences = UserPreference.objects.get_or_create(user=request.user)[0]
        # check if chat session message is provided
        if 'message' in json_data:
            # get chat session message
            chat_session_message = ChatSessionMessage.objects.get(id=json_data['message'])
            user_prompt = UserPrompt.objects.get_or_create(preference=user_preferences, message=chat_session_message, content=json_data['prompt'])[0]
        else:
            user_prompt = UserPrompt.objects.get_or_create(preference=user_preferences, content=json_data['prompt'])[0]
        user_prompt.save()

        return Response({'UserPreferencesSet': True})


class UserPromptDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        raise NotImplementedError

    def delete(self, request, id):
        # get user preference
        user_preferences = UserPreference.objects.filter(user=request.user).first()
        user_prompt = UserPrompt.objects.get(preference=user_preferences, message__id=id)
        user_prompt.delete()

        return Response({'PromptDeleted': True})


class ValidateUserTokenView(APIView):
    def post(self, request):
        token_key = request.data.get('token', '')
        try:
            token = Token.objects.get(key=token_key)
            return Response({'valid': True, 'user_id': token.user.id}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'valid': False}, status=status.HTTP_400_BAD_REQUEST)


###################
# FILE MANAGEMENT #
###################

class FileListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        raise NotImplementedError

    def post(self, request):
        result = {'valid': False}

        session_id = request.POST.get('session_id')
        session = ChatSession.objects.get(id=session_id, user=request.user)

        files = request.FILES.getlist('files')

        files_added = []
        for file in files:
            file_exist = ChatSessionFile.objects.filter(
                session=session,
                name=file.name,
            ).first()

            if not file_exist:
                chat_session_file = ChatSessionFile(
                    session=session,
                    file=file,
                    name=file.name,
                )
                chat_session_file.save()

            files_added.append(file.name)

        result['valid'] = True

        files = session.files
        for file in files:
            if file['name'] in files_added:
                file['selected'] = True

        result['files'] = files

        return JsonResponse(result)


class FileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uuid):
        raise NotImplementedError


class FileActionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uuid):
        raise NotImplementedError

    def post(self, request, uuid, action):
        json_data = json.loads(request.body)

        file = ChatSessionFile.objects.get(id=uuid)

        if action == 'favorite':
            file.favorite = json_data['state']

        file.save()

        return JsonResponse({})


###################
# CHAT MANAGEMENT #
###################

class ChatSessionListView(APIView):
    permission_classes = [IsAuthenticated]
    """
    List all chat sessions.
    """
    def get(self, request, format=None):
        chat_session = ChatSession.objects.filter(user=request.user).order_by('-datetime')
        serializer = ChatSessionSerializer(chat_session, many=True)

        return Response(serializer.data)

    def post(self, request):
        chat_session = ChatSession(
            user=request.user,
        )
        chat_session.save()
        serializer = ChatSessionSerializer(chat_session)

        data = serializer.data

        cls_default = get_pipeline_class(settings.DEFAULT_PIPELINE, request.user)
        default_pipeline_settings = generate_pipeline_dict(cls_default, settings.DEFAULT_PIPELINE)
        data.update(default_pipeline_settings)

        return Response(data)


class ChatSessionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    """
    Retrieve, create or delete a chat session instance.
    """
    def get_object(self, id, user):
        try:
            return ChatSession.objects.get(id=id, user=user)
        except ChatSession.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        user = request.user

        if id == 'default':
            cls_default = get_pipeline_class(settings.DEFAULT_PIPELINE, user)
            default_pipeline_settings = generate_pipeline_dict(cls_default, settings.DEFAULT_PIPELINE)
            return Response(default_pipeline_settings)

        chat_session = self.get_object(id=id, user=request.user)
        serializer = ChatSessionSerializer(chat_session)

        data = serializer.data

        if len(data['messages']):
            alias = data['messages'][-1]['pipeline']
        else:
            alias = settings.DEFAULT_PIPELINE

        cls = get_pipeline_class(alias, user)

        pipeline_settings = generate_pipeline_dict(cls, alias)
        data.update(pipeline_settings)

        return Response(data)

    def put(self, request, id, format=None):
        chat_session = self.get_object(id, request.user)
        json_data = json.loads(request.body)

        chat_session.title = json_data['title']
        chat_session.save()

        return Response({'status': 'updated'})

    def delete(self, request, id, format=None):
        if id == 'all':
            chat_sessions = ChatSession.objects.filter(user=request.user)
            for session in chat_sessions:
                self.delete_files(session)
                session.delete()
        else:
            chat_session = self.get_object(id, request.user)
            self.delete_files(chat_session)
            chat_session.delete()

        return Response({'status': 'deleted'})

    def delete_files(self, session):
        chat_sessions_file_list = ChatSessionFile.objects.filter(session=session)
        for chat_session_file in chat_sessions_file_list:
            chat_session_file.delete_file()


class ChatSessionActionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, action):
        session = ChatSession.objects.get(id=id, user=request.user)
        if action == "messages":
            return Response({"messages": session.serialize_messages()})

        raise NotImplementedError

    def post(self, request, id, action):
        payload = json.loads(request.body)
        try:
            session = ChatSession.objects.get(id=id, user=request.user)
        except ChatSession.DoesNotExist:
            raise Http404

        if action == 'process':
            session.process(payload)

        return Response({'channel_id': session.channel_id})


######################
# MESSAGE MANAGEMENT #
######################

class MessageActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id, action):
        json_data = json.loads(request.body)

        session = ChatSession.objects.get(user=request.user, id=json_data['session_id'])
        session_message = ChatSessionMessage.objects.get(id=id, session=session)

        if action in ['favorite', 'valid']:
            setattr(session_message, action, json_data['state'])

        if action == 'selected':
            session_message.selected = json_data['state']
            session_message.save()

        return Response({'set': True})


#######################
# PIPELINE MANAGEMENT #
#######################

class PipelineListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pipeline_dict = get_pipeline_dict(request.user, use_cache=False)
        pipelines = []
        for alias, kls in pipeline_dict.items():
            # if alias != settings.DEFAULT_PIPELINE:
            label = kls.label
            description = kls.description
            input_type = kls.input
            output_type = kls.output
            kind = f'{input_type} -> {output_type}'
            pipeline = {
                "alias": alias,
                "label": label,
                "description": description,
                "type": kind,
                "schema": kls.json_schema,
                "uischema": kls.ui_schema,
                "ready": kls.READY,
                "active": kls.ACTIVE,
                "user": kls.USER,
                "group": kls.GROUP,
                'other_rights': kls.OTHER_RIGHTS,
                'group_rights': kls.GROUP_RIGHTS,
                'user_rights': kls.USER_RIGHTS,
                'editable': kls.EDITABLE,
            }
            try:
                pipeline['factory'] = kls.FACTORY
            except AttributeError:
                pass

            if PipelinePermission._get_read_permission(pipeline, request.user):
                pipelines.append(pipeline)

        return Response({'pipelines': pipelines})

    def post(self, request):
        json_data = json.loads(request.body)

        user = request.user

        new_pipeline = DynamicPipeline(
            user=user,
            group=None,
            label=json_data['common']['label'],
            factory=json_data['factory_name'],
            params=json_data['factory'],
        )

        # Common schema
        if json_data['common']['input']:
            new_pipeline.input = json_data['common']['input']
        if json_data['common']['output']:
            new_pipeline.output = json_data['common']['output']

        if json_data['common']['auto_generate_description']:
            description = new_pipeline.pipeline_class.generate_description()
        else:
            description = json_data['common']['description']
        new_pipeline.description = description
        new_pipeline.save()

        factory_cls = get_factory_class(json_data['factory_name'])
        additional_params, pipeline_attr = factory_cls.populate(request=request, **new_pipeline.as_dict())

        for key, value in additional_params.items():
            new_pipeline.params[key] = value

        for key, value in pipeline_attr.items():
            setattr(new_pipeline, key, value)

        new_pipeline.save()

        return Response({
            'created': True
        })

    def patch(self, request):
        json_data = json.loads(request.body)

        for pipeline in json_data['pipelines']:
            # Get DynamicPipeline obj
            pipeline_obj = DynamicPipeline.from_alias(pipeline['alias'])

            # Get rights
            other_rights_dict = self.set_rights_dict('other', pipeline['other_rights'])
            group_rights_dict = self.set_rights_dict('group', pipeline['group_rights'])
            user_rights_dict = self.set_rights_dict('user', pipeline['user_rights'])
            rights_dict = {
                **other_rights_dict,
                **group_rights_dict,
                **user_rights_dict
            }

            # Update rights
            for key, value in rights_dict.items():
                setattr(pipeline_obj, key, value)

            # Get user & group
            pipeline_user = User.objects.get(id=pipeline['user_id']) if pipeline['user_id'] else None
            pipeline_group = Group.objects.get(id=pipeline['group_id']) if pipeline['group_id'] else None

            # Update user & group
            pipeline_obj.user = pipeline_user
            pipeline_obj.group = pipeline_group

            # Save DynamicPipeline
            pipeline_obj.save()

        return Response({
            'patched': True
        })

    @classmethod
    def set_rights_dict(cls, key, rights):
        data_dict = {}
        for right, value in rights.items():
            data_dict[key + '_' + right] = value
        return data_dict


class PipelineDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, id, user):
        try:
            return DynamicPipeline.objects.get(id=id, user=user)
        except DynamicPipeline.DoesNotExist:
            raise Http404

    def get(self, request, alias):
        pipeline = self.get_pipeline_by_alias(request.user, alias)
        return Response({'pipeline': pipeline.as_dict()})

    def post(self, request, alias):
        raise NotImplementedError

    def patch(self, request, alias):
        json_data = json.loads(request.body)

        user = request.user
        dynamic_pipeline = self.get_pipeline_by_alias(user, alias)

        if json_data['type'] == 'attr':
            for key, value in json_data['data'].items():
                setattr(dynamic_pipeline, key, value)
            dynamic_pipeline.save()

        if json_data['type'] == 'params':
            dynamic_pipeline.params.update(**json_data['data'])
            dynamic_pipeline.save()

        return Response({'status': 'patched'})

    def delete(self, request, alias):
        user = request.user
        dynamic_pipeline = self.get_pipeline_by_alias(user, alias)
        dynamic_pipeline.delete()

        return Response({'status': 'deleted'})

    def get_pipeline_by_alias(self, user, alias):
        normalized_id = alias.replace('dynamic.', '')
        dynamic_pipeline_id = normalized_id.replace('_', '-')
        return self.get_object(dynamic_pipeline_id, user)


class PipelineSuggestionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get payload
        payload = json.loads(request.body)

        # Request suggestion to app
        new_payload = {
            "query": payload['prompt'],
            "namespace": "ROOT/SEARCH/CORE/SUGGESTIONAPP",
        }

        # Search app request
        sr = SearchRequest(request.user)
        output = sr.post('/api/search/', json=new_payload)

        try:
            json_output = output.json()
            output_suggestions = json_output['results']
        except Exception as e:
            logger.info(str(e))
            output_suggestions = []

        # get best suggestion from suggestions output by aggregation ratio
        best_suggestion = None
        if len(output_suggestions):
            best_suggestion = get_best_suggestion(output_suggestions, request.user)

        # get all pipeplines for best suggestion
        output_kind_to_pipeline_dict = get_output_kind_to_pipeline_dict(request.user)
        pipeline_class_suggestions = output_kind_to_pipeline_dict.get(best_suggestion, [])  # Empty list if none

        # Build pipeline suggestions list
        suggestions = []
        for kls in pipeline_class_suggestions:
            alias = kls.alias
            label = kls.label
            description = kls.description
            input_type = kls.input
            output_type = kls.output
            kind = f'{input_type} -> {output_type}'
            suggestions.append({
                "alias": alias,
                "label": label,
                "description": description,
                "type": kind,
                "schema": kls.json_schema,
                "uischema": kls.ui_schema,
                "ready": kls.READY,
                "active": kls.ACTIVE,
            })
        return Response({'data': suggestions})


########################
# RUN CHAT SESSION RUN #
########################

class Run(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        payload = json.loads(request.body)
        try:
            session = ChatSession.objects.get(id=id, user=request.user)
        except ChatSession.DoesNotExist:
            raise Http404
        session.process(payload)

        return Response({'channel_id': session.channel_id})


################
# SAVE MESSAGE #
################

class SaveMessage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        session_message = ChatSessionMessage.objects.get(id=id)
        json_data = json.loads(request.body)
        action = json_data['action']
        status = json_data['state']
        if action in ['favorite', 'valid']:
            setattr(session_message, action, status)
        return Response({'set': True})


########################
# SET USER PREFERENCES #
########################

class SetUserPreferences(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        json_data = json.loads(request.body)
        user_preferences = UserPreference.objects.get_or_create(user=request.user)[0]
        user_preferences.prompts = json_data['prompts']
        user_preferences.save()

        return Response({'UserPreferencesSet': True})


####################
# GET FACTORY LIST #
####################

class FactoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        factory_list = [{'key': factory, 'label': factory.split('.')[-1]} for factory in get_factory_dict().keys()]

        return Response({
            'factory_list': factory_list,
        })


class FactoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, alias):
        schema = {}
        uischema = {}

        if alias == 'common':
            schema = BaseFactorySchema.model_json_schema()
            uischema = BaseFactorySchema.model_ui_schema()
        else:
            factory_dict = get_factory_dict()
            selected_factory = factory_dict.get(alias)

            schema = selected_factory.pydantic_model.model_json_schema()
            uischema = selected_factory.pydantic_model.model_ui_schema()

        return Response({
            'schema': schema,
            'uischema': uischema
        })


#############################
# FOLDER & FOLDER DOCUMENTS #
#############################
class FolderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # GET FOLDERS
        data = {
            'is_superuser': request.user.is_superuser,
            'group': None
        }
        sr = SearchRequest(request.user)
        response = sr.get('/api/folders/', json=data)
        return Response(response.json())

    def post(self, request):
        # CREATE FOLDER
        json_data = json.loads(request.body)
        sr = SearchRequest(request.user)
        sr.post('/api/folders/', json=json_data)
        return Response({'added': True})


class FolderResearchListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = {
            "query": request.GET.get('query', None),
            "path": request.GET.get('path', 'ROOT')
        }

        sr = SearchRequest(request.user)
        response = sr.get('/api/folders/research/', json=data)
        return Response(response.json())

    def post(self, request):
        raise NotImplementedError


class FolderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        json_data = json.loads(request.body)
        sr = SearchRequest(request.user)
        response = sr.get('/api/folder/', json=json_data)
        return Response(response.json())

    def post(self, request):
        raise NotImplementedError

    def delete(self, request):
        json_data = json.loads(request.body)
        sr = SearchRequest(request.user)
        sr.delete('/api/folder/', json=json_data)
        return Response({'deleted': True})


class FolderDocumentView(APIView):
    def get(self, request, id):
        data = {"query": request.GET.get('query', None)}
        sr = SearchRequest(request.user)
        response = sr.get(f'/api/folder/documents/{id}', json=data)
        return Response(response.json())

    def post(self, request, id):
        raise NotImplementedError


class DocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        raise NotImplementedError

    def post(self, request):
        # GET Document list
        json_data = json.loads(request.body)
        sr = SearchRequest(request.user)
        response = sr.post(f"/api/documents/?page={json_data['page']}", json=json_data)
        return Response(response.json())


class DocumentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        raise NotImplementedError

    def post(self, request):
        # INSERT DOCUMENT
        post_data = request.POST.dict()
        file_data = request.FILES
        sr = SearchRequest(request.user)
        response = sr.post('/api/document/', data=post_data, files=file_data)
        return Response(response.json())

    def delete(self, request):
        # DELETE DOCUMENT
        json_data = json.loads(request.body)
        sr = SearchRequest(request.user)
        sr.delete('/api/document/', json=json_data)
        return Response({'deleted': True})


class FolderDocumentRights(APIView):

    def get(self, request):
        raise NotImplementedError

    def post(self, request):
        logger.info(request.method)
        raise NotImplementedError

    def patch(self, request):
        json_data = json.loads(request.body)
        sr = SearchRequest(request.user)
        sr.patch("/api/folder_document_rights/", json=json_data)
        return Response({'changed': True})


@csrf_exempt  # NOSONAR
def webhook(request, channel_id):
    return HttpResponse()
    # async_to_sync(self.channel_layer.group_send)(
    #     self.channel_id, {'type': 'pipeline.log', 'message': data}
    # )
