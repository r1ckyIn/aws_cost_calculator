"""Storage Resources Module.

This module defines AWS storage-related resource classes, including S3Bucket and EBSVolume.
"""

from typing import Any, ClassVar, NoReturn

from models.base import CloudResource


class S3Bucket(CloudResource):
    """AWS S3 Bucket resource class.

    S3 is billed by storage capacity, independent of status (buckets are always available).

    Attributes:
        resource_id: Bucket name.
        region: AWS region.
        storage_gb: Storage capacity (GB).
    """

    # S3 storage price (USD/GB/month)
    PRICE_PER_GB_MONTH: ClassVar[float] = 0.023

    @staticmethod
    def _validate_storage_gb(value: int | float) -> float:
        """Validate and convert storage capacity value.

        Args:
            value: Storage capacity value.

        Returns:
            float: Converted storage capacity.

        Raises:
            ValueError: If value is negative or invalid type.
        """
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("storage_gb must be a non-negative number")
        return float(value)

    def __init__(
        self,
        resource_id: str,
        region: str,
        storage_gb: int | float
    ) -> None:
        """Initialize S3 bucket.

        Args:
            resource_id: Bucket name, cannot be empty.
            region: AWS region code.
            storage_gb: Storage capacity (GB), must be non-negative.

        Raises:
            ValueError: If resource_id is empty, region is invalid, or storage_gb is negative.
        """
        super().__init__(resource_id, region)
        self._storage_gb = self._validate_storage_gb(storage_gb)
        # S3 buckets are always available once created
        self._status = self._STATUS_RUNNING

    def start(self) -> NoReturn:
        """S3 buckets do not support start operation.

        Raises:
            NotImplementedError: S3 buckets are always available.
        """
        raise NotImplementedError("S3 buckets are always available")

    def stop(self) -> NoReturn:
        """S3 buckets do not support stop operation.

        Raises:
            NotImplementedError: S3 buckets cannot be stopped.
        """
        raise NotImplementedError("S3 buckets cannot be stopped")

    @property
    def storage_gb(self) -> float:
        """Get storage capacity (GB)."""
        return self._storage_gb

    @storage_gb.setter
    def storage_gb(self, value: int | float) -> None:
        """Set storage capacity (GB).

        This value represents current storage usage, which changes with file uploads/deletions.

        Args:
            value: New storage capacity, must be non-negative.

        Raises:
            ValueError: If value is negative.
        """
        self._storage_gb = self._validate_storage_gb(value)

    def get_cost(self) -> float:
        """Calculate monthly cost of S3 bucket.

        Returns:
            float: Monthly cost in USD.
        """
        return self._storage_gb * self.PRICE_PER_GB_MONTH

    def get_info(self) -> dict[str, Any]:
        """Get detailed S3 bucket information.

        Returns:
            dict: Dictionary containing bucket details.
        """
        return {
            'resource_id': self.resource_id,
            'resource_type': self.resource_type,
            'region': self.region,
            'status': self.status,
            'storage_gb': self._storage_gb,
            'price_per_gb': self.PRICE_PER_GB_MONTH,
            'monthly_cost': self.get_cost(),
        }

    def __str__(self) -> str:
        """Return user-friendly string for S3 bucket."""
        return f"S3: {self.resource_id} ({self._storage_gb}GB)"

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"id={self.resource_id!r}, "
            f"region={self.region!r}, "
            f"storage_gb={self._storage_gb})"
        )


class EBSVolume(CloudResource):
    """AWS EBS Volume resource class.

    EBS is billed by storage capacity and volume type. Charges apply as long as the volume exists
    (regardless of whether it's attached).

    Attributes:
        resource_id: Volume ID (e.g., 'vol-1234567890abcdef0').
        region: AWS region.
        volume_type: Volume type (e.g., 'gp3').
        size_gb: Volume size (GB).
    """

    # EBS volume type pricing (USD/GB/month)
    VOLUME_PRICING: ClassVar[dict[str, float]] = {
        'gp2': 0.10,      # General Purpose SSD
        'gp3': 0.08,      # General Purpose SSD (newer)
        'io1': 0.125,     # Provisioned IOPS SSD
        'io2': 0.125,     # Provisioned IOPS SSD (newer)
        'st1': 0.045,     # Throughput Optimized HDD
        'sc1': 0.015,     # Cold HDD
    }

    # EBS volume size limits (GB)
    MIN_SIZE_GB: ClassVar[int] = 1
    MAX_SIZE_GB: ClassVar[int] = 65536  # 64TB

    def __init__(
        self,
        resource_id: str,
        region: str,
        volume_type: str,
        size_gb: int
    ) -> None:
        """Initialize EBS volume.

        Args:
            resource_id: Unique volume identifier.
            region: AWS region code.
            volume_type: Volume type, e.g., 'gp3'.
            size_gb: Volume size (GB), must be an integer between 1-65536.

        Raises:
            TypeError: If size_gb is not an integer.
            ValueError: If volume_type is unsupported or size_gb is out of valid range.
        """
        super().__init__(resource_id, region)

        if volume_type not in self.VOLUME_PRICING:
            raise ValueError(
                f"Unsupported volume type '{volume_type}'. "
                f"Supported types: {', '.join(sorted(self.VOLUME_PRICING))}"
            )

        self._validate_size_gb(size_gb)
        self._volume_type = volume_type
        self._size_gb = size_gb
        # EBS volumes are always available once created
        self._status = self._STATUS_RUNNING

    @classmethod
    def _validate_size_gb(cls, value: int, current_size: int | None = None) -> None:
        """Validate volume size.

        Args:
            value: Size value to validate.
            current_size: Current size (for expansion check), None for new volume.

        Raises:
            TypeError: If value is not an integer.
            ValueError: If value is out of valid range or less than current size.
        """
        if not isinstance(value, int):
            raise TypeError(
                f"size_gb must be int, got {type(value).__name__}"
            )
        if value < cls.MIN_SIZE_GB:
            raise ValueError(
                f"size_gb must be >= {cls.MIN_SIZE_GB}, got {value}"
            )
        if value > cls.MAX_SIZE_GB:
            raise ValueError(
                f"size_gb cannot exceed {cls.MAX_SIZE_GB}GB (64TB)"
            )
        if current_size is not None and value < current_size:
            raise ValueError(
                f"EBS volumes can only be expanded, not shrunk. "
                f"Current: {current_size}GB, requested: {value}GB"
            )

    def start(self) -> NoReturn:
        """EBS volumes do not support start operation.

        Raises:
            NotImplementedError: EBS volumes are always available.
        """
        raise NotImplementedError("EBS volumes are always available")

    def stop(self) -> NoReturn:
        """EBS volumes do not support stop operation.

        Raises:
            NotImplementedError: EBS volumes cannot be stopped.
        """
        raise NotImplementedError("EBS volumes cannot be stopped")

    @classmethod
    def supported_volume_types(cls) -> list[str]:
        """Get all supported volume types.

        Returns:
            list[str]: List of supported volume types.
        """
        return sorted(cls.VOLUME_PRICING)

    @property
    def volume_type(self) -> str:
        """Get volume type (read-only).

        Returns:
            str: Volume type identifier, e.g., 'gp3'.
        """
        return self._volume_type

    @property
    def size_gb(self) -> int:
        """Get volume size (GB)."""
        return self._size_gb

    @size_gb.setter
    def size_gb(self, value: int) -> None:
        """Expand volume size (GB).

        Note: AWS EBS volumes can only be expanded, not shrunk.

        Args:
            value: New volume size, must be >= current size and <= 64TB.

        Raises:
            ValueError: If value is invalid or less than current size.
        """
        self._validate_size_gb(value, self._size_gb)
        self._size_gb = value

    def get_cost(self) -> float:
        """Calculate monthly cost of EBS volume.

        Returns:
            float: Monthly cost in USD.
        """
        return self._size_gb * self.VOLUME_PRICING[self._volume_type]

    def get_info(self) -> dict[str, Any]:
        """Get detailed EBS volume information.

        Returns:
            dict: Dictionary containing volume details.
        """
        return {
            'resource_id': self.resource_id,
            'resource_type': self.resource_type,
            'region': self.region,
            'status': self.status,
            'volume_type': self._volume_type,
            'size_gb': self._size_gb,
            'price_per_gb': self.VOLUME_PRICING[self._volume_type],
            'monthly_cost': self.get_cost(),
        }

    def __str__(self) -> str:
        """Return user-friendly string for EBS volume."""
        return f"EBS: {self.resource_id} ({self._volume_type}, {self._size_gb}GB)"

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"id={self.resource_id!r}, "
            f"region={self.region!r}, "
            f"volume_type={self._volume_type!r}, "
            f"size_gb={self._size_gb})"
        )
