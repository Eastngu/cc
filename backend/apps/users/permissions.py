from rest_framework.permissions import BasePermission


class IsBoss(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'boss'


class IsFinance(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'finance'


class IsWorkshop(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'workshop'


class IsBossOrFinance(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ('boss', 'finance')
        )
