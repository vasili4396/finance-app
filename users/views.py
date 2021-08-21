from dateutil import parser
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, serializers
from rest_framework.response import Response

from users.serializers import AccountingSerializer


class UserAccounting(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = get_user_model().objects.prefetch_related('wallet_set')
    serializer_class = AccountingSerializer

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        date = request.query_params.get('date')

        if date:
            try:
                date = timezone.make_aware(parser.parse(date))
            except parser.ParserError:
                raise serializers.ValidationError('Invalid date supplied. Use ISO 8601 format')

        serializer = self.get_serializer(user, context={'date': date})
        return Response(serializer.data)
