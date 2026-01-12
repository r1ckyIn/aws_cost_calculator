"""AWS Cloud Resource Base Module.

This module defines the abstract base class CloudResource for all AWS resources.
"""

from abc import ABC, abstractmethod
from typing import Any


class CloudResource(ABC):
    """Abstract base class for AWS cloud resources.

    All concrete AWS resources (EC2, S3, RDS, etc.) should inherit from this class
    and implement the get_cost() and get_info() methods.

    Attributes:
        resource_id: Unique identifier for the resource.
        region: AWS region (e.g., 'us-east-1').
        status: Resource status ('running' or 'stopped').
    """

    # Status constants
    _STATUS_RUNNING = "running"
    _STATUS_STOPPED = "stopped"

    VALID_REGIONS = {
        'us-east-1', 'us-west-2', 'eu-west-1',
        'ap-southeast-1', 'ap-northeast-1'
    }
    VALID_STATUSES = {_STATUS_RUNNING, _STATUS_STOPPED}

    def __init__(self, resource_id: str, region: str) -> None:
        """Initialize cloud resource.

        Args:
            resource_id: Unique resource identifier, cannot be empty.
            region: AWS region code.

        Raises:
            ValueError: If resource_id is empty or region is invalid.
        """
        if not resource_id or not isinstance(resource_id, str):
            raise ValueError("resource_id must be a non-empty string")
        if region not in self.VALID_REGIONS:
            raise ValueError(
                f"Invalid region: {region}. "
                f"Valid regions: {sorted(self.VALID_REGIONS)}"
            )

        self._resource_id = resource_id
        self._region = region
        self._status = self._STATUS_STOPPED

    @property
    def resource_id(self) -> str:
        """Get resource ID."""
        return self._resource_id

    @property
    def region(self) -> str:
        """Get resource region."""
        return self._region

    @property
    def status(self) -> str:
        """Get current resource status."""
        return self._status

    @property
    def resource_type(self) -> str:
        """Get resource type name."""
        return self.__class__.__name__

    @property
    def is_running(self) -> bool:
        """Check if resource is running."""
        return self._status == self._STATUS_RUNNING

    def start(self) -> bool:
        """Start the resource.

        Returns:
            bool: True if status changed, False otherwise.
        """
        if self._status == self._STATUS_RUNNING:
            return False
        self._status = self._STATUS_RUNNING
        return True

    def stop(self) -> bool:
        """Stop the resource.

        Returns:
            bool: True if status changed, False otherwise.
        """
        if self._status == self._STATUS_STOPPED:
            return False
        self._status = self._STATUS_STOPPED
        return True

    @abstractmethod
    def get_cost(self) -> float:
        """Calculate monthly cost of the resource.

        Returns:
            float: Monthly cost in USD.
        """
        ...

    @abstractmethod
    def get_info(self) -> dict[str, Any]:
        """Get detailed resource information.

        Returns:
            dict: Dictionary containing resource details.
        """
        ...

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"id={self._resource_id!r}, "
            f"region={self._region!r}, "
            f"status={self._status!r})"
        )

    def __str__(self) -> str:
        """Return user-friendly string representation."""
        return f"{self.resource_type}: {self._resource_id} ({self._status})"

    def __eq__(self, other: object) -> bool:
        """Check if two resources are equal.

        Args:
            other: Object to compare with.

        Returns:
            bool: True if same type and resource_id.
        """
        if not isinstance(other, CloudResource):
            return NotImplemented
        return (
            type(self) is type(other)
            and self._resource_id == other._resource_id
        )

    def __hash__(self) -> int:
        """Return hash value of the resource.

        Returns:
            int: Hash based on type and resource_id.
        """
        return hash((type(self), self._resource_id))
