from django.db import migrations

SUGGESTIONAPP_NAMESPACE = 'core/suggestionapp'


def forward(apps, schema_editor):
    from django.conf import settings
    from lib.vectorize import vectorize

    Document = apps.get_model("core", "Document")  # NOSONAR

    def bulk_documents_to_db(document_list):
        Document.objects.bulk_create(
            document_list, ignore_conflicts=True
        )

    def main(verbose=False):
        # LOAD TEXT DATASET
        if verbose:
            print('LOAD TEXT DATASET')

        text_rows = ''
        with open(f'{settings.BASE_DIR}/core/migrations/datasets/text_prompts.txt', 'r') as f:
            text_rows = f.readlines()
            text_documents = []
            for row in text_rows:
                vector = vectorize(row)

                document = Document(
                    namespace=SUGGESTIONAPP_NAMESPACE,
                    content=row,
                    embedding=vector,
                    context={"thema": "text"}
                )
                text_documents.append(document)

            if verbose:
                print('ADD TEXT DOCUMENTS TO DB')

            bulk_documents_to_db(text_documents)

        # LOAD IMAGE DATASET
        if verbose:
            print('\nLOAD IMAGE DATASET')

        image_rows = ''
        with open(f'{settings.BASE_DIR}/core/migrations/datasets/image_prompts.txt', 'r') as f:
            image_rows = f.readlines()
            image_documents = []
            for row in image_rows:
                vector = vectorize(row)

                document = Document(
                    namespace=SUGGESTIONAPP_NAMESPACE,
                    content=row,
                    embedding=vector,
                    context={"thema": "image"}
                )
                image_documents.append(document)

            if verbose:
                print('ADD IMAGE DOCUMENTS TO DB')

            bulk_documents_to_db(image_documents)

        # LOAD MUSIC DATASET
        if verbose:
            print('\nLOAD MUSIC DATASET')

        music_rows = ''
        with open(f'{settings.BASE_DIR}/core/migrations/datasets/music_prompts.txt', 'r') as f:
            music_rows = f.readlines()
            music_documents = []
            for row in music_rows:
                vector = vectorize(row)

                document = Document(
                    namespace=SUGGESTIONAPP_NAMESPACE,
                    content=row,
                    embedding=vector,
                    context={"thema": "music"}
                )
                music_documents.append(document)

            if verbose:
                print('ADD MUSIC DOCUMENTS TO DB')

            bulk_documents_to_db(music_documents)

        # LOAD SOUND DATASET
        if verbose:
            print('\nLOAD SOUND DATASET')

        sound_rows = ''
        with open(f'{settings.BASE_DIR}/core/migrations/datasets/sound_prompts.txt', 'r') as f:
            sound_rows = f.readlines()
            sound_documents = []
            for row in sound_rows:
                vector = vectorize(row)

                document = Document(
                    namespace=SUGGESTIONAPP_NAMESPACE,
                    content=row,
                    embedding=vector,
                    context={"thema": "sound"}
                )
                sound_documents.append(document)

            if verbose:
                print('ADD SOUND DOCUMENTS TO DB')

            bulk_documents_to_db(sound_documents)

        # LOAD SUMMARY DATASET
        if verbose:
            print('\nLOAD SUMMARY DATASET')

        summary_rows = ''
        with open(f'{settings.BASE_DIR}/core/migrations/datasets/summary_prompts.txt', 'r') as f:
            summary_rows = f.readlines()
            summary_documents = []
            for row in summary_rows:
                vector = vectorize(row)

                document = Document(
                    namespace=SUGGESTIONAPP_NAMESPACE,
                    content=row,
                    embedding=vector,
                    context={"thema": "summary"}
                )
                summary_documents.append(document)

            if verbose:
                print('ADD SUMMARY DOCUMENTS TO DB')

            bulk_documents_to_db(summary_documents)

    main(verbose=True)


def backward(apps, schema_editor):
    # No need to unfill..
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
