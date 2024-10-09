import sys
from django.db import migrations
import mptt
import mptt.managers


def forward(apps, schema_editor):
    Document = apps.get_model("core", "Document")  # NOSONAR
    Folder = apps.get_model("core", "Folder")  # NOSONAR

    manager = mptt.managers.TreeManager()
    manager.model = Folder
    mptt.register(Folder, order_insertion_by=['name'])
    manager.contribute_to_class(Folder, 'objects')
    manager.rebuild()

    # HELP FUNCTIONS
    def display_counter(counter, row_count):
        percent = int(counter * 100 / row_count)
        print(
            '\rProgression : [{0}{1}] {2}%'.format(
                '#' * int(percent / 10),
                ' ' * (10 - int(percent / 10)),
                percent
            ),
            end=''
        )
        return percent

    def transform(document, search_folder):
        # SET NAMESPACE UPPER
        namespace = str(document.namespace).upper()
        if not namespace:
            namespace = 'UNKNOWN'

        parent_folder = search_folder
        namespace_splited = namespace.split('/')
        for name in namespace_splited:
            folder, created = Folder.objects.get_or_create(name=name, parent=parent_folder)
            if created:
                folder.save()
            parent_folder = folder

        # UPDATE DOCUMENT
        document.folder = folder
        document.namespace = 'ROOT/SEARCH/' + namespace
        document.save()

    """
    MAIN FUNCTION
    """
    def main(verbose=False):
        if 'py.test' in sys.argv[0] or 'test' in sys.argv:
            return

        if verbose:
            print('\n$> Create ROOT and SEARCH folder if doesn\'t exist')

        root_folder = Folder.objects.filter(name='ROOT', parent=None).first()
        if not root_folder:
            root_folder = Folder.objects.create(name='ROOT', parent=None)
            root_folder.save()

        search_folder = Folder.objects.filter(name='SEARCH', parent=root_folder).first()
        if not search_folder:
            search_folder = Folder.objects.create(name='SEARCH', parent=root_folder)
            search_folder.save()

        # LOAD DOCUMENTS
        if verbose:
            print('\n$> Loading all documents wich havent folder')
        documents = Document.objects.filter(folder=None)

        # TRANSFORM EACH DOCUMENT
        if verbose:
            print(' \n$> Transform document')
            counter = 0
            total = len(documents)

        for document in documents:
            transform(document, search_folder)

            if verbose:
                counter += 1
                display_counter(counter, total)

        if verbose:
            print('\n$> Done')

    main(verbose=True)


def backward(apps, schema_editor):
    # Nothing to do...
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_suggestionfill'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
