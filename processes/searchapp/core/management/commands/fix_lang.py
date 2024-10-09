from django.core.management.base import BaseCommand, CommandParser
from django.db.models import F

from core.models import Document
from lib.utils import generate_summary

from langdetect import detect

from bs4 import BeautifulSoup


class Command(BaseCommand):
    help = 'Ensure that summary use the same language as original document content'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('namespace', type=str, help='Namespace of the document')

    def handle(self, *args, **kwargs):
        namespace = kwargs['namespace']
        documents = Document.objects.filter(namespace=namespace)

        # 1st pass : setting content_lang for documents where it's not filled
        document_counter = 0
        queryset = documents.filter(content_lang__isnull=True)
        document_count = queryset.count()
        for document in queryset:
            print(f"Content language detection: {document_counter}/{document_count}")
            document_counter += 1
            document.content_lang = detect(document.content)
            document.save()

        # 2nd pass : summary_lang for documents where it's not filled
        document_counter = 0
        queryset = documents.filter(summary_lang__isnull=True)
        document_count = queryset.count()
        for document in queryset:
            print(f"Summary language detection: {document_counter}/{document_count}")
            document_counter += 1
            document.summary_lang = detect(document.summary)
            document.save()

        # 3rd pass : regenerating summary until it is ok
        document_counter = 0
        queryset = documents.exclude(summary_lang=F('content_lang'))
        document_count = queryset.count()
        for document in queryset:
            document_counter += 1
            print(f"Summary regeneration: {document_counter}/{document_count}")
            fixed = False
            max_tries = 5
            counter = 0
            while not fixed and counter < max_tries:
                summary = generate_summary(document.content)
                soup = BeautifulSoup(summary, 'html.parser')
                summary = soup.get_text()
                if detect(summary) == document.content_lang:
                    fixed = True
                    document.summary = summary
                    document.summary_lang = document.content_lang
                    document.save()
                    self.stdout.write(f'Summary of {document.title} regenerated')
                counter += 1
