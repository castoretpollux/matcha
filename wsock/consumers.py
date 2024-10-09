# chat/consumers.py
import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class Consumer(WebsocketConsumer):

    def connect(self):
        self.channel_id = self.scope["url_route"]["kwargs"]["channel_id"]
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.channel_id, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.channel_id, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'runner.checkstatus':
            async_to_sync(self.channel_layer.group_send)(self.channel_id, data)

    def runner_status(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))

    def runner_checkstatus(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))

    def runner_log(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))

    def runner_partial(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))

    def runner_result(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))

    def runner_error(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))

    def runner_message(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))

    def runner_title(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))
