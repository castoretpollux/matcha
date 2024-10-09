import uuid
import os
import logging

from django.db import models
from django.conf import settings
from django.db.models import Q
from django_rq import get_queue

from pgvector.django import VectorField
from mptt.models import MPTTModel, TreeForeignKey

from api.permissions import Permission

from lib.auth import get_root_user, get_root_group
from lib.utils import convert_to_text, generate_summary
from lib.tokenize import extract_parts
from lib.vectorize import vectorize
from lib import constants

search_queue = get_queue('search')

logger = logging.getLogger("django")


def content_file_name(instance, filename):  # NOSONAR
    folder_name = str(uuid.uuid4())
    relative_path = f"uploads/{folder_name}/{filename}"
    return relative_path


def get_upload_path(instance, filename):
    return f"uploads/{instance.folder.full_path}/{filename}"


def process_document(document_id, data):
    document = Document.objects.get(id=document_id)
    Document.process(document, data)


class Document(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    content_lang = models.CharField(max_length=3, null=True)  # NOSONAR
    title = models.CharField(max_length=255, null=True)  # NOSONAR
    summary = models.TextField(null=True)  # NOSONAR
    summary_lang = models.CharField(max_length=3, null=True)  # NOSONAR
    url = models.TextField(null=True)  # NOSONAR
    image = models.TextField(null=True)  # NOSONAR
    embedding = VectorField(dimensions=768, null=True)
    namespace = models.CharField(max_length=255)
    file = models.FileField(upload_to=get_upload_path, null=True, blank=True)
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE, null=True, blank=True)
    context = models.JSONField(default=dict, null=True, blank=True)
    state = models.CharField(choices=constants.DOCUMENT_STATES, default=constants.DOCUMENT_STATE_INIT)
    # document credentials (inspired by linux file credentials) :
    user = models.ForeignKey("ExternalUser", null=True, on_delete=models.SET(get_root_user))  # if user is deleted document will be owned by root user (with id=0)
    group = models.ForeignKey("ExternalGroup", null=True, on_delete=models.SET(get_root_group))  # if group is deleted, document's group will be switched to root group (with id=0)
    user_can_read = models.BooleanField(default=False)
    user_can_write = models.BooleanField(default=False)
    user_can_update = models.BooleanField(default=False)
    user_can_delete = models.BooleanField(default=False)
    group_can_read = models.BooleanField(default=False)
    group_can_write = models.BooleanField(default=False)
    group_can_update = models.BooleanField(default=False)
    group_can_delete = models.BooleanField(default=False)
    other_can_read = models.BooleanField(default=False)
    other_can_write = models.BooleanField(default=False)
    other_can_update = models.BooleanField(default=False)
    other_can_delete = models.BooleanField(default=False)

    @classmethod
    def _query_documents(cls, filters: dict, user) -> list:
        query_documents = cls.objects.filter(**filters)

        document_ids = []
        for document in query_documents:
            if Permission._get_read_permission(document, user):
                document_ids.append(document.id)

        return cls.objects.filter(id__in=document_ids)

    @classmethod
    def create_from_data(cls, data:dict, file, user) -> dict:
        # Create document
        document = cls(
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
        file_path = document.file.path
        relative_path = file_path.replace(settings.MEDIA_ROOT, '')
        document.url = '/media' + relative_path
        document.save()
        # process file asynchronously :
        search_queue.enqueue(
            process_document,
            document.id,
            data
        )
        # Finally, return a (temporary) serialization :
        return document

    @classmethod
    def process(cls, document, data):
        document.state = constants.DOCUMENT_STATE_STARTPROCESS
        document.save()
        try:
            file_path = document.file.path
            relative_path = file_path.replace(settings.MEDIA_ROOT, '')
            # Convert document into text
            text = convert_to_text(file_path)
            document.state = constants.DOCUMENT_STATE_TEXTCONVERTED
            document.save()

            # Vectorize the document text
            vector = vectorize(text)
            document.state = constants.DOCUMENT_STATE_VECTORIZED
            document.save()

            summary = ""
            # Generate a summary of the document text
            if data.get('generate_summary'):
                summary = generate_summary(text)

            # Update documnet with the extracted data
            document.url = '/media' + relative_path
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
            document.state = constants.DOCUMENT_STATE_FINALIZED
            document.save()
        except Exception as e:
            logger.info(str(e))
            document.state = constants.DOCUMENT_STATE_ERROR
            document.save()

    @property
    def group_rights(self) -> dict:
        data = {
            'can_read': self.group_can_read,
            'can_write': self.group_can_write,
            'can_update': self.group_can_update,
            'can_delete': self.group_can_delete,
        }

        if self.group:
            data["id"] = self.group.gid
            data["name"] = self.group.groupname

        return data

    @property
    def user_rights(self) -> dict:
        data = {
            'can_read': self.user_can_read,
            'can_write': self.user_can_write,
            'can_update': self.user_can_update,
            'can_delete': self.user_can_delete,
        }

        if self.user:
            data["id"] = self.user.uid
            data["name"] = self.user.username

        return data

    @property
    def other_rights(self) -> dict:
        return {
            'can_read': self.other_can_read,
            'can_write': self.other_can_write,
            'can_update': self.other_can_update,
            'can_delete': self.other_can_delete,
        }

    def as_dict(self) -> dict:
        url = str(self.url)
        if not url.startswith('http'):
            url = settings.SITE_ROOT + url
        return {
            'id': self.id,
            'state': self.state,
            'created_on': self.created_on,
            'title': self.title or 'unknown',
            'summary': self.summary,
            'url': self.url,
            'image': self.image,
            'context': self.context,
            'namespace': self.namespace,
            'content': self.content,
            'group_rights': self.group_rights,
            'user_rights': self.user_rights,
            'other_rights': self.other_rights,
        }


    def _delete_file(self):
        folder_path = None
        if self.file and os.path.isfile(self.file.path):
            folder_path = os.path.dirname(self.file.path)
            os.remove(self.file.path)

        if folder_path and os.path.isdir(folder_path):
            try:
                os.rmdir(folder_path)
            except OSError:
                logger.info('Folder not empty')


class PipelineDocumentVector(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    vector = VectorField(dimensions=768)
    pipeline = models.CharField(max_length=255)  # NOSONAR
    # key = Not needed for now


class Part(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='parts')
    content = models.TextField()
    content_lang = models.CharField(max_length=3, null=True)
    embedding = VectorField(dimensions=768)
    summary = models.TextField(null=True)
    summary_lang = models.CharField(max_length=3, null=True)

    def as_dict(self):
        return {
            'created_on': self.created_on,
            'document': self.document.as_dict(),
            'content': self.content
        }


class Folder(MPTTModel):
    name = models.CharField(max_length=50, null=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    # folder credentials (inspired by linux file credentials) :
    user = models.ForeignKey("ExternalUser", null=True, on_delete=models.SET(get_root_user))  # if user is deleted document will be owned by root user (with id=0)
    group = models.ForeignKey("ExternalGroup", null=True, on_delete=models.SET(get_root_group))  # if group is deleted, document's group will be switched to root group (with id=0)
    user_can_read = models.BooleanField(default=False)
    user_can_write = models.BooleanField(default=False)
    user_can_update = models.BooleanField(default=False)
    user_can_delete = models.BooleanField(default=False)
    group_can_read = models.BooleanField(default=False)
    group_can_write = models.BooleanField(default=False)
    group_can_update = models.BooleanField(default=False)
    group_can_delete = models.BooleanField(default=False)
    other_can_read = models.BooleanField(default=False)
    other_can_write = models.BooleanField(default=False)
    other_can_update = models.BooleanField(default=False)
    other_can_delete = models.BooleanField(default=False)

    def __str__(self):
        return 'Folder: %s' % (self.full_path)

    @property
    def full_path(self):
        ancestors_list = [ancestor.name for ancestor in self.get_ancestors()]
        ancestors_list.append(self.name)
        return "/".join(ancestors_list)

    @property
    def group_rights(self):
        data = {
            'can_read': self.group_can_read,
            'can_write': self.group_can_write,
            'can_update': self.group_can_update,
            'can_delete': self.group_can_delete,
        }

        if self.group:
            data["id"] = self.group.gid
            data["name"] = self.group.groupname

        return data

    @property
    def user_rights(self):
        data = {
            'can_read': self.user_can_read,
            'can_write': self.user_can_write,
            'can_update': self.user_can_update,
            'can_delete': self.user_can_delete,
        }

        if self.user:
            data["id"] = self.user.uid
            data["name"] = self.user.username

        return data

    @property
    def other_rights(self):
        return {
            'can_read': self.other_can_read,
            'can_write': self.other_can_write,
            'can_update': self.other_can_update,
            'can_delete': self.other_can_delete,
        }

    @classmethod
    def get_or_create_folder(cls, parent_path, relative_path, user):
        # Get parent folder by path
        parent_folder = cls.get_by_full_path(parent_path)
        if parent_folder:
            if Permission._get_write_permission(parent_folder, user):
                # Split namespace if contains '/'
                relative_path_splited = relative_path.split('/')
                for name in relative_path_splited:
                    # Get or create folder
                    folder, created = Folder.objects.get_or_create(name=name, parent=parent_folder)
                    if created:
                        folder.save()
                    # Update Parent folder to create child folder
                    parent_folder = folder
                return folder
        else:
            cls.get_or_create_folder()

    @classmethod
    def get_or_create_folder_tree(cls, parent_path: str, name: str, user):
        parent_folder = cls.get_by_full_path(parent_path)

        if not parent_folder:
            new_parent_path_splited = parent_path.split('/')
            new_name = new_parent_path_splited.pop()
            new_parent_path = '/'.join(new_parent_path_splited)
            parent_folder = cls.get_or_create_folder_tree(new_parent_path, new_name, user)

        folder, created = cls.objects.get_or_create(
            name=name,
            parent=parent_folder,
        )

        if created:
            folder.user = user
            folder.user_can_read = True
            folder.user_can_write = True
            folder.user_can_update = True
            folder.user_can_delete = True
            folder.group_can_read = parent_folder.group_can_read
            folder.group_can_write = parent_folder.group_can_write
            folder.group_can_update = parent_folder.group_can_update
            folder.group_can_delete = parent_folder.group_can_delete
            folder.other_can_read = parent_folder.other_can_read
            folder.other_can_write = parent_folder.other_can_write
            folder.other_can_update = parent_folder.other_can_update
            folder.other_can_delete = parent_folder.other_can_delete
            folder.save()

        return folder

    @classmethod
    def get_by_full_path(cls, full_path):
        names = full_path.split('/')
        folder = None
        try:
            for name in names:
                if folder is None:
                    folder = cls.objects.get(name=name, parent__isnull=True)
                else:
                    folder = cls.objects.get(name=name, parent=folder)
        except Exception as e:
            logger.info(str(e))
            folder = None

        return folder

    def _get_tree(self, user):
        if Permission._get_read_permission(self, user):
            children = []
            for child in self.get_children().order_by('name'):
                child_tree = child._get_tree(user)
                if child_tree:
                    children.append(child_tree)

            can_write = Permission._get_write_permission(self, user)
            can_delete = Permission._get_delete_permission(self, user)

            documents = self._get_documents(user=user)

            return {
                'id': self.id,
                'name': self.name,
                'full_path': self.full_path,
                'children': children,
                'documents': documents[:10],
                'document_count': len(documents),
                'group_rights': self.group_rights,
                'user_rights': self.user_rights,
                'other_rights': self.other_rights,
                # Not necessary to add can_read, because folders that cannot be read are not added
                # Not necessary to add can_update, because folders that cannot be updated by front
                'can_write': can_write,
                'can_delete': can_delete,
            }

    def _query_descendants(self, filters, user):
        descendant_filtereds = self.get_descendants(include_self=False).filter(**filters)

        descendants = []
        for descendant in descendant_filtereds:
            stack = [descendant]
            while stack:
                # Get current folder from stack
                current_folder = stack.pop()
                # Get current folder descendants
                current_folder_descendants = current_folder.get_descendants(include_self=False)
                # Add to stack subdescendant
                for subdescendant in current_folder_descendants:
                    stack.append(subdescendant)
                # Check current folder permission
                if Permission._get_read_permission(current_folder, user):
                    descendants.append((current_folder.full_path, current_folder.id))

        return descendants

    def _get_documents(self, user):
        folder_documents = Document.objects.filter(folder=self)
        if user.is_superuser:
            query_documents = folder_documents.distinct().order_by('created_on')
        else:
            query_documents = folder_documents.filter(
                Q(user=user, user_can_read=True) |
                Q(group__in=user.groups, group_can_read=True) |
                Q(other_can_read=True)
            ).distinct().order_by('created_on')

        return [document.as_dict() for document in query_documents]

    def _delete_files(self):
        documents = Document.objects.filter(folder=self)
        for doc in documents:
            doc._delete_file()


class PipelineFolderContext(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    pipeline = models.CharField(max_length=255)
    context = models.JSONField(default=dict, null=True, blank=True)


class ExternalUser(models.Model):

    uid = models.IntegerField(primary_key=True)
    namespace = models.CharField(max_length=256)
    username = models.CharField(max_length=150)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        staff_label = 'staff' if self.is_staff else 'not staff'
        superuser_label = 'superuser' if self.is_superuser else 'normal'
        return '%s (uid: %s - %s, %s)' % (self.username, self.uid, staff_label, superuser_label)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def groups(self):
        return [group_user.group for group_user in GroupUser.objects.filter(user=self)]


class ExternalGroup(models.Model):

    gid = models.IntegerField(primary_key=True)
    namespace = models.CharField(max_length=256)
    groupname = models.CharField(max_length=150)

    def as_dict(self):
        return {
            "gid": self.gid,
            "namespace": self.namespace,
            "groupname": self.groupname
        }


class GroupUser(models.Model):
    user = models.ForeignKey(ExternalUser, on_delete=models.CASCADE)
    group = models.ForeignKey(ExternalGroup, on_delete=models.CASCADE)
