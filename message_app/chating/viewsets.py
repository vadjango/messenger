from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from message_app.auth.user.models import User
from message_app.chating import OneSignal
from message_app.chating.models import Message, Chat
from message_app.chating.serializers import MessageSerializer, ChatSerializer


class ChatViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "delete"]
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer
    lookup_field = "public_id"

    def get_queryset(self):
        return Chat.objects.filter(Q(first_user=self.request.user) | Q(second_user=self.request.user))

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        for chat in serializer.data:
            unread_count = Message.objects.filter(Q(chat__public_id=chat["public_id"]) &
                                                  ~Q(sender=request.user) &
                                                  Q(is_read=False)).count()
            chat["unread_count"] = unread_count
        return self.get_paginated_response(serializer.data)

    @action(detail=False)
    def get_chat_by_user(self, request):
        phone_number = request.query_params.get("phone_number")
        if not phone_number:
            return Response(data={"detail": "The query parameter 'phone_number' is unfilled!"},
                            status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, phone_number=phone_number)
        chats = (Chat.objects.filter(first_user=self.request.user, second_user=user) |
                 Chat.objects.filter(first_user=user, second_user=self.request.user))
        if not chats.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(chats[0])
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    http_method_names = ["get", "post", "patch", "put", "delete"]
    permission_classes = [IsAuthenticated]
    lookup_field = "public_id"

    def get_queryset(self):
        chat_public_id = self.kwargs.get("chat_public_id")
        if chat_public_id is None:
            return Message.objects.all()
        return Message.objects.filter(chat__public_id=chat_public_id)

    def create(self, request, *args, **kwargs):
        if "chat" in request.data and "second_user" not in request.data:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            OneSignal.Push.create_message_notification(ms=serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        elif "second_user" in request.data and "chat" not in request.data:
            second_user = get_object_or_404(User, public_id=request.data["second_user"])
            chat = Chat.objects.create(first_user=request.user, second_user=second_user)
            request.data["chat"] = chat.public_id
            del request.data["second_user"]
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            OneSignal.Push.create_chat_notification(cs=ChatSerializer(chat))
            OneSignal.Push.create_message_notification(ms=serializer, only_for_sender=True)
            headers = self.get_success_headers(serializer.data)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response("Invalid request: you must provide either 'chat' or 'second_user'",
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=True)
    def read(self, request, *args, **kwargs):
        message = get_object_or_404(Message, **kwargs)
        message.is_read = True
        message.save()
        return Response(status=status.HTTP_200_OK)
