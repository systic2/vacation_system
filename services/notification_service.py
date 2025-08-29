# services/notification_service.py
from models import Notification, db
from datetime import datetime


class NotificationService:
    def create_notification(self, user_id, message):
        notification = Notification(
            user_id=user_id,
            message=message,
            timestamp=datetime.utcnow()
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    def get_user_notifications(self, user_id):
        return Notification.query.filter_by(user_id=user_id).order_by(
            Notification.timestamp.desc()
        ).all()
    
    def get_unread_count(self, user_id):
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()
    
    def mark_all_as_read(self, user_id):
        notifications = Notification.query.filter_by(user_id=user_id, is_read=False).all()
        for notification in notifications:
            notification.is_read = True
        db.session.commit()
    
    def mark_as_read(self, notification_id):
        notification = Notification.query.get(notification_id)
        if notification:
            notification.is_read = True
            db.session.commit()
