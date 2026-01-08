from rest_framework import permissions
from .services import RBACService

class HasRPermission(permissions.BasePermission):
    """
    Использование: permission_classes = [HasRPermission('incidents.resolve')]
    """
    def __init__(self, required_perm):
        self.required_perm = required_perm

    def __call__(self):
        return self

    def has_permission(self, request, view):
        return RBACService.has_permission(request.user, self.required_perm)

# Фабрика для удобного использования в декораторах, если нужно
def RPerm(perm):
    return HasRPermission(perm)