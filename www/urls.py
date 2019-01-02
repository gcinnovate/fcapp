# -*- coding: utf-8 -*-

"""URL definitions of the application. Regex based URLs are mapped to their
class handlers.
"""

from app.controllers.main_handler import Index, Logout
from app.controllers.users_handler import Users
from app.controllers.groups_handler import Groups
from app.controllers.auditlog_handler import AuditLog
from app.controllers.forgotpass_handler import ForgotPass
from app.controllers.eventmessage_handler import EventMessageForLanguage
from app.controllers.secreceivers_handler import SecondaryReceivers, OptOutSecondaryReceiver

URLS = (
    r'^/', Index,
    r'/auditlog', AuditLog,
    r'/users', Users,
    r'/groups', Groups,
    r'/logout', Logout,
    r'/forgotpass', ForgotPass,
    # API stuff follows
    r'/eventmessage', EventMessageForLanguage,
    r'/secreceivers', SecondaryReceivers,
    r'/optout_secondaryreceiver', OptOutSecondaryReceiver
)
