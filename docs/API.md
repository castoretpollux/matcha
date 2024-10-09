***Disclaimer*** : this documentation corresponds to old notes and needs to be updated

# DOC API

## Get CSRF Token :
```javascript
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
```

## Log user :

Request :

```javascript
const csrftoken = getCookie('csrftoken');
const URL = '/api/login/';
const BODY = {
	'username': <username>,
	'password': <password>
}
const METHOD = 'POST';
const HEADERS = {
	'Accept': 'application/json',
	'X-Requested-With': 'XMLHttpRequest',
	'X-CSRFToken': csrftoken,
}
```

Response (Object) :

```javascript
{'status': 'logged'}
// OR
{'status': 'not logged'}
```

## List user session :

Request : 
```javascript
const URL = '/api/chats';
const METHOD = 'GET';
const HEADERS = {};
```
Response :

```javascript
[
	{
		'id': <session_uuid>, 
		'user': <user_id>, 
		'datetime': <datetime_str>,
		'description': null,
		'channel_id': <channel_uuid>,
	},...
]
```

## Session retrieval :

Request : 
```javascript
const URL = `/api/chat/${uuid}`;
const METHOD = 'GET';
const HEADERS = {};
```

Response :

```javascript
{
	'id': <session_uuid>, 
	'user': <user_id>, 
	'datetime': <datetime_str>,
	'description': <description_str>,
	'channel_id': <channel_uuid>,
	'form': <crispy_form>,
	'messages': <msg_array> (ex :[
			{
				'id': <message_id>,
				'created_on': <date_time_string>,
				'kind': <user\system>,
				'content': <html_of_content>
			},...
	],
}
```

## Create/Delete session :

### Creation

Request :

```javascript
const csrftoken = getCookie('csrftoken');
const URL = '/api/chat/';
const METHOD = 'POST';
const HEADERS = {
	'Accept': 'application/json',
	'X-Requested-With': 'XMLHttpRequest',
	'X-CSRFToken': csrftoken,
}
```

Response :
```javascript
{
	'session_id': <session_id>,
	'channel_id': <channel_id>,
	'form': <crispy_form>,
	'pipeline':  <pipeline_str>, // first time is : textcreation
}
```

### Deletion

Request :

```javascript
const csrftoken = getCookie('csrftoken');
const URL = `/api/chat/${uuid}`;
const METHOD = 'DELETE';
const HEADERS = {
	'Accept': 'application/json',
	'X-Requested-With': 'XMLHttpRequest',
	'X-CSRFToken': csrftoken,
}
```

Response :

```javascript
{'status': 'deleted'}
```

## Start pipeline

Request :
```javascript
// Get CSRF && Build payload

// create new form data
let formData = new FormData(form);

// get toekn
let csrfToken = formData.get('csrfmiddlewaretoken')

// remove token
formData.delete('csrfmiddlewaretoken')

// build body payload
let body 			= {}
body['pipeline'] 	= <pipeline_str>
body['payload']  	= {}
for  (let  [key, value]  of formData.entries())  {
	body['payload'][key] = value;
}

// Build request
const URL = `/api/chat/${uuid}/run/`;
const METHOD = 'POST';
const BODY = body
const HEADERS = {
	'Accept': 'application/json',
	'X-Requested-With': 'XMLHttpRequest',
	'X-CSRFToken': csrftoken,
}
```

Reponse to initiate websocket :
```javascript
{'channel_id': <channel_id>}
```

