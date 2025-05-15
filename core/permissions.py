from rest_framework import permissions

class IsOrganizer(permissions.BasePermission):
    """
    Permission personnalisée pour restreindre l'accès aux seuls organisateurs.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'organizer'

class IsSpeaker(permissions.BasePermission):
    """
    Permission personnalisée pour restreindre l'accès aux seuls conférenciers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'speaker'
    
class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour autoriser les organisateurs à modifier
    et tous les autres à lire uniquement.
    """
    def has_permission(self, request, view):
        # Lecture autorisée pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Écriture uniquement pour les organisateurs
        return request.user.is_authenticated and request.user.role == 'organizer'
        
class IsSpeakerOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour autoriser les conférenciers à modifier leurs propres talks
    et tous les autres à lire uniquement.
    """
    def has_permission(self, request, view):
        # Lecture autorisée pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Écriture uniquement pour les conférenciers ou organisateurs
        return request.user.is_authenticated and (request.user.role == 'speaker' or request.user.role == 'organizer')
        
    def has_object_permission(self, request, view, obj):
        # Lecture autorisée pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Un conférencier ne peut modifier que ses propres talks
        if request.user.role == 'speaker':
            return obj.speaker == request.user
            
        # Organisateurs peuvent modifier tous les talks
        return request.user.role == 'organizer'
