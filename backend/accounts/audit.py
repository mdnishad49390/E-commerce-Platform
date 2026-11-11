from .models import AdminAuditLog


def log_admin_action(actor, action: str, target_type: str, target_id='', detail: str = '') -> None:
    AdminAuditLog.objects.create(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=str(target_id or ''),
        detail=detail or '',
    )
