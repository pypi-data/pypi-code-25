from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django_filters.rest_framework import (
    BooleanFilter, DjangoFilterBackend, FilterSet,
)
from rest_framework import viewsets, views, generics, serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter

from pretix.api.serializers.voucher import VoucherSerializer, RedeemSerializer
from pretix.base.models import Voucher, CartPosition, SubEvent
from pretix.base.models.organizer import TeamAPIToken
from pretix.presale.views.cart import get_or_create_cart_id
from pretix.presale.views.event import get_grouped_items
from pretix.base.services.cart import error_messages


class VoucherFilter(FilterSet):
    active = BooleanFilter(method='filter_active')

    class Meta:
        model = Voucher
        fields = ['code', 'max_usages', 'redeemed', 'block_quota', 'allow_ignore_quota',
                  'price_mode', 'value', 'item', 'variation', 'quota', 'tag', 'subevent']

    def filter_active(self, queryset, name, value):
        if value:
            return queryset.filter(Q(redeemed__lt=F('max_usages')) &
                                   (Q(valid_until__isnull=True) | Q(valid_until__gt=now())))
        else:
            return queryset.filter(Q(redeemed__gte=F('max_usages')) |
                                   (Q(valid_until__isnull=False) & Q(valid_until__lte=now())))


class VoucherViewSet(viewsets.ModelViewSet):
    serializer_class = VoucherSerializer
    queryset = Voucher.objects.none()
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    ordering = ('id',)
    ordering_fields = ('id', 'code', 'max_usages', 'valid_until', 'value')
    filter_class = VoucherFilter
    permission = 'can_view_vouchers'
    write_permission = 'can_change_vouchers'

    def get_queryset(self):
        return self.request.event.vouchers.all()

    def create(self, request, *args, **kwargs):
        with request.event.lock():
            return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(event=self.request.event)
        serializer.instance.log_action(
            'pretix.voucher.added',
            user=self.request.user,
            api_token=(self.request.auth if isinstance(self.request.auth, TeamAPIToken) else None),
            data=self.request.data
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['event'] = self.request.event
        return ctx

    def update(self, request, *args, **kwargs):
        with request.event.lock():
            return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save(event=self.request.event)
        serializer.instance.log_action(
            'pretix.voucher.changed',
            user=self.request.user,
            api_token=(self.request.auth if isinstance(self.request.auth, TeamAPIToken) else None),
            data=self.request.data
        )

    def perform_destroy(self, instance):
        if not instance.allow_delete():
            raise PermissionDenied('This voucher can not be deleted as it has already been used.')

        instance.log_action(
            'pretix.voucher.deleted',
            user=self.request.user,
            api_token=(self.request.auth if isinstance(self.request.auth, TeamAPIToken) else None),
        )
        super().perform_destroy(instance)

        class RedeemViewSet(generics.RetrieveAPIView):
            serializer_class = RedeemSerializer

            def get_object(self):
                err = None
                context = {}
                v = self.kwargs.get('voucher')

                if v:
                    v = v.strip()
                    try:
                        self.voucher = Voucher.objects.get(code__iexact=v, event=self.request.event)
                        if self.voucher.redeemed >= self.voucher.max_usages:
                            err = error_messages['voucher_redeemed']
                        if self.voucher.valid_until is not None and self.voucher.valid_until < now():
                            err = error_messages['voucher_expired']
                        if self.voucher.item is not None and self.voucher.item.is_available() is False:
                            err = error_messages['voucher_item_not_available']

                        redeemed_in_carts = CartPosition.objects.filter(
                            Q(voucher=self.voucher) & Q(event=self.request.event) &
                            (Q(expires__gte=now()) | Q(cart_id=get_or_create_cart_id(self.request)))
                        )
                        v_avail = self.voucher.max_usages - self.voucher.redeemed - redeemed_in_carts.count()
                        if v_avail < 1:
                            err = error_messages['voucher_redeemed']
                    except Voucher.DoesNotExist:
                        err = error_messages['voucher_invalid']
                else:
                    return

                if self.request.event.presale_start and now() < self.request.event.presale_start:
                    err = error_messages['not_started']
                if self.request.event.presale_end and now() > self.request.event.presale_end:
                    err = error_messages['ended']

                self.subevent = None
                if self.request.event.has_subevents:
                    if self.kwargs.get('subevent'):
                        self.subevent = get_object_or_404(SubEvent, event=self.request.event,
                                                          pk=self.kwargs.get('subevent'),
                                                          active=True)

                    if hasattr(self, 'voucher') and self.voucher.subevent:
                        self.subevent = self.voucher.subevent
                else:
                    pass

                if err:
                    raise serializers.ValidationError(_(err))

                context['voucher'] = self.voucher

                return context
