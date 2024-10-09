from django.core.management.base import BaseCommand, CommandParser
from core.models import Document
from lib.utils import generate_summary
import re

from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = 'Regenerate summary of a document from a namespace'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('namespace', type=str, help='Namespace of the document')

    def handle(self, *args, **kwargs):
        namespace = kwargs['namespace']
        documents = Document.objects.filter(namespace=namespace)
        for document in documents:
            summary = generate_summary(document.content)
            soup = BeautifulSoup(summary, 'html.parser')
            # use regex to remove all html tags
            summary = soup.get_text()
            document.summary = summary
            document.save()
            self.stdout.write(f'Summary of {document.title} regenerated')
