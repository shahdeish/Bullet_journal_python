"""Modèles des entrées d'un Bullet Journal."""

from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from enum import Enum
from uuid import uuid4

from .exceptions import InvalidEntryError, InvalidTransitionError


class TaskStatus(str, Enum):
    """États possibles d'une tâche."""

    TODO = "à faire"
    DONE = "terminée"
    MIGRATED = "migrée"
    SCHEDULED = "planifiée"
    ABANDONED = "abandonnée"


class Signifier(str, Enum):
    """Signifiants pouvant être associés à une entrée."""

    PRIORITY = "*"
    IDEA = "!"


@dataclass
class Entry:
    """Entrée commune à tous les éléments du journal."""

    name: str
    description: str
    log_date: date
    signifiers: set[Signifier] = field(default_factory=set, init=False)
    collections: set[str] = field(default_factory=set, init=False)
    id: str = field(default_factory=lambda: str(uuid4()), init=False)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc),
        init=False,
    )

    def __post_init__(self) -> None:
        """Vérifie les données communes de l'entrée."""
        if not self.name.strip():
            raise InvalidEntryError("Le nom de l'entrée ne peut pas être vide.")

    def add_signifier(self, signifier: Signifier) -> None:
        """Ajoute un signifiant à l'entrée."""
        self.signifiers.add(signifier)

    def remove_signifier(self, signifier: Signifier) -> None:
        """Retire un signifiant de l'entrée."""
        self.signifiers.discard(signifier)

    def _signifier_prefix(self) -> str:
        """Renvoie les signifiants dans un ordre stable."""
        markers = [
            signifier.value
            for signifier in (Signifier.PRIORITY, Signifier.IDEA)
            if signifier in self.signifiers
        ]
        return " ".join(markers)

    @property
    def rapid_symbol(self) -> str:
        """Renvoie le symbole de rapid logging de cette entrée."""
        return "–"

    def to_rapid_logging(self) -> str:
        """Formate l'entrée avec ses signifiants et son symbole."""
        prefix = self._signifier_prefix()
        if prefix:
            prefix += " "
        return f"{prefix}{self.rapid_symbol} {self.name}: {self.description}"


@dataclass
class Task(Entry):
    """Tâche à accomplir dans le journal."""

    status: TaskStatus = TaskStatus.TODO
    migrated_from_id: str | None = None
    migrated_to_id: str | None = None
    scheduled_for: date | None = None

    def complete(self) -> None:
        """Marque la tâche comme terminée."""
        if self.status not in (TaskStatus.TODO, TaskStatus.SCHEDULED):
            raise InvalidTransitionError(
                f"Impossible de terminer une tâche à l'état '{self.status.value}'."
            )

        self.status = TaskStatus.DONE

    def migrate(self, new_log_date: date) -> "Task":
        """Migre la tâche vers une date ultérieure et renvoie sa copie."""
        if self.status not in (TaskStatus.TODO, TaskStatus.SCHEDULED):
            raise InvalidTransitionError(
                f"Impossible de migrer une tâche à l'état '{self.status.value}'."
            )

        if new_log_date <= self.log_date:
            raise InvalidTransitionError(
                "La date de migration doit être postérieure à la date actuelle."
            )

        self.status = TaskStatus.MIGRATED
        migrated_task = Task(
            name=self.name,
            description=self.description,
            log_date=new_log_date,
            migrated_from_id=self.id,
        )
        self.migrated_to_id = migrated_task.id
        migrated_task.signifiers = self.signifiers.copy()
        migrated_task.collections = self.collections.copy()
        return migrated_task

    @property
    def rapid_symbol(self) -> str:
        """Renvoie le symbole correspondant à l'état de la tâche."""
        symbols = {
            TaskStatus.TODO: "•",
            TaskStatus.DONE: "×",
            TaskStatus.MIGRATED: ">",
            TaskStatus.SCHEDULED: "<",
            TaskStatus.ABANDONED: "",
        }
        return symbols[self.status]

    def to_rapid_logging(self) -> str:
        """Formate la tâche, en barrant celles qui sont abandonnées."""
        text = f"{self.name}: {self.description}"
        prefix = self._signifier_prefix()
        if prefix:
            prefix += " "

        if self.status == TaskStatus.ABANDONED:
            return f"{prefix}~~{text}~~"
        return super().to_rapid_logging()

    def schedule(self, target_date: date) -> None:
        """Planifie la tâche pour une date ultérieure."""
        if self.status not in (TaskStatus.TODO, TaskStatus.SCHEDULED):
            raise InvalidTransitionError(
                f"Impossible de planifier une tâche à l'état '{self.status.value}'."
            )

        if target_date <= self.log_date:
            raise InvalidTransitionError(
                "La date prévue doit être postérieure à la date de création."
            )

        self.status = TaskStatus.SCHEDULED
        self.scheduled_for = target_date

    def abandon(self) -> None:
        """Marque la tâche comme abandonnée."""
        if self.status not in (TaskStatus.TODO, TaskStatus.SCHEDULED):
            raise InvalidTransitionError(
                f"Impossible d'abandonner une tâche à l'état '{self.status.value}'."
            )

        self.status = TaskStatus.ABANDONED


@dataclass
class Event(Entry):
    """Événement prévu à une date, avec une heure facultative."""

    event_date: date
    event_time: time | None = None

    @property
    def rapid_symbol(self) -> str:
        """Renvoie le symbole d'un événement."""
        return "○"


@dataclass
class Note(Entry):
    """Note libre inscrite dans le journal."""
