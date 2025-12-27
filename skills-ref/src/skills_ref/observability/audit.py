"""
Immutable audit logging for compliance.
"""

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AuditAction(Enum):
    """Types of auditable actions."""
    # Skill execution
    SKILL_EXECUTE = "skill_execute"
    SKILL_COMPLETE = "skill_complete"
    SKILL_FAIL = "skill_fail"

    # Authentication
    AUTH_LOGIN = "auth_login"
    AUTH_LOGOUT = "auth_logout"
    AUTH_FAIL = "auth_fail"
    TOKEN_REFRESH = "token_refresh"
    TOKEN_REVOKE = "token_revoke"

    # Authorization
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"

    # Secrets
    SECRET_ACCESS = "secret_access"
    SECRET_ROTATE = "secret_rotate"
    SECRET_CREATE = "secret_create"
    SECRET_DELETE = "secret_delete"

    # Role management
    ROLE_ASSIGN = "role_assign"
    ROLE_REVOKE = "role_revoke"
    ROLE_CREATE = "role_create"
    ROLE_DELETE = "role_delete"

    # API keys
    API_KEY_CREATE = "api_key_create"
    API_KEY_REVOKE = "api_key_revoke"
    API_KEY_ROTATE = "api_key_rotate"

    # Data access
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"


class AuditStatus(Enum):
    """Status of audited action."""
    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"
    ERROR = "error"


@dataclass
class AuditEntry:
    """
    An immutable audit log entry.

    Each entry has a hash chain for integrity verification.
    """
    id: str
    timestamp: datetime
    action: AuditAction
    status: AuditStatus

    # Who
    user_id: str
    workspace_id: Optional[str] = None

    # What
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None

    # Context
    skill_name: Optional[str] = None
    skill_execution_id: Optional[str] = None
    trace_id: Optional[str] = None

    # Details
    details: Dict[str, Any] = field(default_factory=dict)
    reason: Optional[str] = None

    # Request context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Integrity
    previous_hash: Optional[str] = None
    entry_hash: Optional[str] = None

    def compute_hash(self, previous_hash: str = "") -> str:
        """Compute hash for integrity verification."""
        data = {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.value,
            "status": self.status.value,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "previous_hash": previous_hash,
        }
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.value,
            "status": self.status.value,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "skill_name": self.skill_name,
            "skill_execution_id": self.skill_execution_id,
            "trace_id": self.trace_id,
            "details": self.details,
            "reason": self.reason,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEntry":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            action=AuditAction(data["action"]),
            status=AuditStatus(data["status"]),
            user_id=data["user_id"],
            workspace_id=data.get("workspace_id"),
            resource_type=data.get("resource_type"),
            resource_id=data.get("resource_id"),
            skill_name=data.get("skill_name"),
            skill_execution_id=data.get("skill_execution_id"),
            trace_id=data.get("trace_id"),
            details=data.get("details", {}),
            reason=data.get("reason"),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            previous_hash=data.get("previous_hash"),
            entry_hash=data.get("entry_hash"),
        )


@dataclass
class AuditFilter:
    """Filter for querying audit logs."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    actions: Optional[List[AuditAction]] = None
    status: Optional[AuditStatus] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    skill_name: Optional[str] = None
    limit: int = 100
    offset: int = 0


class AuditLog(ABC):
    """
    Abstract base for audit log storage.

    Implement for different backends (file, database, cloud).
    """

    @abstractmethod
    async def append(self, entry: AuditEntry) -> None:
        """Append an entry (immutable)."""
        pass

    @abstractmethod
    async def query(self, filter: AuditFilter) -> List[AuditEntry]:
        """Query entries with filter."""
        pass

    @abstractmethod
    async def get_entry(self, entry_id: str) -> Optional[AuditEntry]:
        """Get a specific entry by ID."""
        pass

    @abstractmethod
    async def verify_chain(self, start_id: str, end_id: str) -> bool:
        """Verify hash chain integrity between entries."""
        pass


class ImmutableAuditLog(AuditLog):
    """
    In-memory immutable audit log.

    For production, extend with file or database storage.
    """

    def __init__(self):
        self._entries: List[AuditEntry] = []
        self._index: Dict[str, int] = {}  # id -> position
        self._last_hash: str = ""

    async def append(self, entry: AuditEntry) -> None:
        """Append entry with hash chain."""
        import secrets

        # Generate ID if not set
        if not entry.id:
            entry.id = secrets.token_hex(16)

        # Compute hash chain
        entry.previous_hash = self._last_hash
        entry.entry_hash = entry.compute_hash(self._last_hash)
        self._last_hash = entry.entry_hash

        # Store
        self._index[entry.id] = len(self._entries)
        self._entries.append(entry)

    async def query(self, filter: AuditFilter) -> List[AuditEntry]:
        """Query with filter."""
        results = []

        for entry in self._entries:
            # Apply filters
            if filter.start_time and entry.timestamp < filter.start_time:
                continue
            if filter.end_time and entry.timestamp > filter.end_time:
                continue
            if filter.user_id and entry.user_id != filter.user_id:
                continue
            if filter.workspace_id and entry.workspace_id != filter.workspace_id:
                continue
            if filter.actions and entry.action not in filter.actions:
                continue
            if filter.status and entry.status != filter.status:
                continue
            if filter.resource_type and entry.resource_type != filter.resource_type:
                continue
            if filter.resource_id and entry.resource_id != filter.resource_id:
                continue
            if filter.skill_name and entry.skill_name != filter.skill_name:
                continue

            results.append(entry)

        # Apply offset and limit
        return results[filter.offset : filter.offset + filter.limit]

    async def get_entry(self, entry_id: str) -> Optional[AuditEntry]:
        """Get entry by ID."""
        idx = self._index.get(entry_id)
        if idx is not None:
            return self._entries[idx]
        return None

    async def verify_chain(self, start_id: str, end_id: str) -> bool:
        """Verify hash chain integrity."""
        start_idx = self._index.get(start_id)
        end_idx = self._index.get(end_id)

        if start_idx is None or end_idx is None:
            return False

        if start_idx > end_idx:
            return False

        # Verify each link
        prev_hash = self._entries[start_idx].previous_hash or ""
        for i in range(start_idx, end_idx + 1):
            entry = self._entries[i]
            expected_hash = entry.compute_hash(prev_hash)
            if entry.entry_hash != expected_hash:
                return False
            prev_hash = entry.entry_hash

        return True

    async def export_json(self, filter: Optional[AuditFilter] = None) -> str:
        """Export entries as JSON."""
        if filter:
            entries = await self.query(filter)
        else:
            entries = self._entries

        return json.dumps(
            [e.to_dict() for e in entries],
            indent=2,
            default=str,
        )

    @property
    def count(self) -> int:
        """Get total entry count."""
        return len(self._entries)


class AuditLogBuilder:
    """
    Builder for creating audit entries.

    Example:
        entry = (AuditLogBuilder()
            .action(AuditAction.SKILL_EXECUTE)
            .user("user123")
            .skill("research")
            .success()
            .build())
    """

    def __init__(self):
        self._action: Optional[AuditAction] = None
        self._status: AuditStatus = AuditStatus.SUCCESS
        self._user_id: Optional[str] = None
        self._workspace_id: Optional[str] = None
        self._resource_type: Optional[str] = None
        self._resource_id: Optional[str] = None
        self._skill_name: Optional[str] = None
        self._execution_id: Optional[str] = None
        self._trace_id: Optional[str] = None
        self._details: Dict[str, Any] = {}
        self._reason: Optional[str] = None
        self._ip_address: Optional[str] = None
        self._user_agent: Optional[str] = None

    def action(self, action: AuditAction) -> "AuditLogBuilder":
        self._action = action
        return self

    def user(self, user_id: str, workspace_id: Optional[str] = None) -> "AuditLogBuilder":
        self._user_id = user_id
        self._workspace_id = workspace_id
        return self

    def resource(self, resource_type: str, resource_id: str) -> "AuditLogBuilder":
        self._resource_type = resource_type
        self._resource_id = resource_id
        return self

    def skill(self, name: str, execution_id: Optional[str] = None) -> "AuditLogBuilder":
        self._skill_name = name
        self._execution_id = execution_id
        return self

    def trace(self, trace_id: str) -> "AuditLogBuilder":
        self._trace_id = trace_id
        return self

    def success(self, reason: Optional[str] = None) -> "AuditLogBuilder":
        self._status = AuditStatus.SUCCESS
        self._reason = reason
        return self

    def failure(self, reason: str) -> "AuditLogBuilder":
        self._status = AuditStatus.FAILURE
        self._reason = reason
        return self

    def denied(self, reason: str) -> "AuditLogBuilder":
        self._status = AuditStatus.DENIED
        self._reason = reason
        return self

    def error(self, reason: str) -> "AuditLogBuilder":
        self._status = AuditStatus.ERROR
        self._reason = reason
        return self

    def details(self, **kwargs) -> "AuditLogBuilder":
        self._details.update(kwargs)
        return self

    def request_context(self, ip: str, user_agent: str) -> "AuditLogBuilder":
        self._ip_address = ip
        self._user_agent = user_agent
        return self

    def build(self) -> AuditEntry:
        import secrets

        if not self._action:
            raise ValueError("Action is required")
        if not self._user_id:
            raise ValueError("User ID is required")

        return AuditEntry(
            id=secrets.token_hex(16),
            timestamp=datetime.utcnow(),
            action=self._action,
            status=self._status,
            user_id=self._user_id,
            workspace_id=self._workspace_id,
            resource_type=self._resource_type,
            resource_id=self._resource_id,
            skill_name=self._skill_name,
            skill_execution_id=self._execution_id,
            trace_id=self._trace_id,
            details=self._details,
            reason=self._reason,
            ip_address=self._ip_address,
            user_agent=self._user_agent,
        )
