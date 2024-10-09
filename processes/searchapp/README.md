# Search APP

## Description

Application for uploading a file, converting it to text, storing it in a vector database, and enabling the search for the document closest to the user's query.

## Features

1. **Upload Feature**: Allows users to upload files to the application.
2. **Conversion Feature**: Converts the uploaded files into text format.
3. **Storage Feature**: Stores the converted text in a vector database.
4. **Search Feature**: Enables users to search for documents that are most relevant to their query within the database.

## Installation

1. Install Multiple system packages that will be used by langchain DocumentLoader
    ```
    sudo apt install libleptonica-dev tesseract-ocr libtesseract-dev libmagic-dev poppler-utils libreoffice pandoc tesseract-ocr-script-latn
    # optionnal, you can install tesseract-ocr for your language, for instance :
    sudo apt install tesseract-ocr-fra
    ```

2. Install the dependencies:
    ```
    pip install -r requirements.txt
    ```

3. Copy the example environment file to create your own `.env` file:
    ```
    cp .env.example .env
    ```

4. Apply database migrations:
    ```
    python manage.py migrate
    ```


## Usage

### Start the development server:

    ```shell
    python manage.py runserver
    ```
### API Endpoint: `/import_document`

This API endpoint allows for the uploading of a document through a multipart/form-data submission. The request should include three parts: `namespace`, `title`, and the file itself (`file`).

#### Request Parameters:

- `namespace` (string): A categorization or grouping parameter that helps in organizing the documents.
- `title` (string): The title of the document being uploaded.
- `file` (file): The document file that needs to be uploaded. Supported formats may vary.

### API Endpoint: `/search`

This API endpoint facilitates document searching within a specific namespace based on a query. The search functionality uses two JSON parameters: `query` and `namespace`.

#### Request Parameters (JSON):

- `query` (string): The search string or keywords to find documents related to.
- `namespace` (string): Specifies the namespace within which the search should be conducted.

#### Request Example:

```http
POST /search HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "query": "search keywords",
  "namespace": "myNamespace"
}
```