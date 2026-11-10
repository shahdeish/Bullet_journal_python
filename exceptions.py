"""Exceptions métier de la bibliothèque Bullet Journal."""


class BulletJournalError(Exception):
    """Exception de base pour les erreurs du Bullet Journal."""


class InvalidEntryError(BulletJournalError):
    """Levée lorsqu'une entrée contient des données invalides."""


class EntryNotFoundError(BulletJournalError):
    """Levée lorsqu'une entrée demandée est introuvable."""


class InvalidTransitionError(BulletJournalError):
    """Levée lorsqu'une transition d'état n'est pas autorisée."""


class CollectionNotFoundError(BulletJournalError):
    """Levée lorsqu'une collection demandée n'existe pas."""


class InvalidDateRangeError(BulletJournalError):
    """Levée lorsque la date de début dépasse la date de fin."""


class PersistenceError(BulletJournalError):
    """Levée lorsqu'un journal JSON ne peut pas être lu ou écrit."""


class MarkdownExportError(BulletJournalError):
    """Levée lorsqu'un export Markdown ne peut pas être écrit."""
