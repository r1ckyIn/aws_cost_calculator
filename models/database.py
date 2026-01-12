"""Database Resources Module.

This module defines AWS database-related resource classes, including RDSDatabase.
"""

from typing import Any, ClassVar

from models.base import CloudResource


class RDSDatabase(CloudResource):
    """AWS RDS Database instance resource class.

    RDS Billing Rules:
    - Instance cost: Only billed when running, Multi-AZ doubles the cost
    - Storage cost: Billed regardless of whether instance is running

    Attributes:
        resource_id: Database instance identifier (e.g., 'mydb-instance').
        region: AWS region.
        instance_class: Instance type (e.g., 'db.t3.micro').
        engine: Database engine (e.g., 'mysql').
        storage_gb: Storage capacity (GB).
        multi_az: Whether Multi-AZ deployment is enabled.
    """

    # RDS instance class pricing (USD/hour)
    INSTANCE_PRICING: ClassVar[dict[str, float]] = {
        'db.t3.micro': 0.017,
        'db.t3.small': 0.034,
        'db.t3.medium': 0.068,
        'db.r5.large': 0.24,
        'db.r5.xlarge': 0.48,
    }

    # RDS storage price (USD/GB/month)
    STORAGE_PRICE_PER_GB: ClassVar[float] = 0.115

    # Supported database engines
    SUPPORTED_ENGINES: ClassVar[set[str]] = {
        'mysql', 'postgresql', 'mariadb', 'oracle', 'sqlserver'
    }

    # Storage size limits (GB)
    MIN_STORAGE_GB: ClassVar[int] = 20
    MAX_STORAGE_GB: ClassVar[int] = 65536  # 64TB

    # Hours per month
    HOURS_PER_MONTH: ClassVar[int] = 730

    def __init__(
        self,
        resource_id: str,
        region: str,
        instance_class: str,
        engine: str,
        storage_gb: int,
        multi_az: bool = False
    ) -> None:
        """Initialize RDS database instance.

        Args:
            resource_id: Unique database instance identifier.
            region: AWS region code.
            instance_class: Instance type, e.g., 'db.t3.micro'.
            engine: Database engine, e.g., 'mysql'.
            storage_gb: Storage capacity (GB), must be an integer between 20-65536.
            multi_az: Whether to enable Multi-AZ deployment, default False.

        Raises:
            TypeError: If storage_gb is not an integer.
            ValueError: If instance_class is unsupported, engine is unsupported,
                or storage_gb is out of valid range (20-65536).
        """
        super().__init__(resource_id, region)

        if instance_class not in self.INSTANCE_PRICING:
            raise ValueError(
                f"Unsupported instance class '{instance_class}'. "
                f"Supported classes: {', '.join(sorted(self.INSTANCE_PRICING))}"
            )

        engine_lower = engine.lower()
        if engine_lower not in self.SUPPORTED_ENGINES:
            raise ValueError(
                f"Unsupported engine '{engine}'. "
                f"Supported engines: {', '.join(sorted(self.SUPPORTED_ENGINES))}"
            )

        self._validate_storage_gb(storage_gb)

        self._instance_class = instance_class
        self._engine = engine_lower
        self._storage_gb = storage_gb
        self._multi_az = bool(multi_az)

    @classmethod
    def _validate_storage_gb(cls, value: int, current_size: int | None = None) -> None:
        """Validate storage capacity.

        Args:
            value: Storage capacity value to validate.
            current_size: Current capacity (for expansion check), None for new instance.

        Raises:
            TypeError: If value is not an integer.
            ValueError: If value is out of valid range or less than current capacity.
        """
        if not isinstance(value, int):
            raise TypeError(
                f"storage_gb must be int, got {type(value).__name__}"
            )
        if value < cls.MIN_STORAGE_GB:
            raise ValueError(
                f"storage_gb must be >= {cls.MIN_STORAGE_GB}, got {value}"
            )
        if value > cls.MAX_STORAGE_GB:
            raise ValueError(
                f"storage_gb cannot exceed {cls.MAX_STORAGE_GB}GB (64TB)"
            )
        if current_size is not None and value < current_size:
            raise ValueError(
                f"RDS storage can only be expanded, not shrunk. "
                f"Current: {current_size}GB, requested: {value}GB"
            )

    @classmethod
    def supported_instance_classes(cls) -> list[str]:
        """Get all supported instance classes.

        Returns:
            list[str]: List of supported instance classes.
        """
        return sorted(cls.INSTANCE_PRICING)

    @classmethod
    def supported_engines(cls) -> list[str]:
        """Get all supported database engines.

        Returns:
            list[str]: List of supported engines.
        """
        return sorted(cls.SUPPORTED_ENGINES)

    @property
    def instance_class(self) -> str:
        """Get instance class (read-only)."""
        return self._instance_class

    @property
    def engine(self) -> str:
        """Get database engine (read-only)."""
        return self._engine

    @property
    def storage_gb(self) -> int:
        """Get storage capacity (GB)."""
        return self._storage_gb

    @storage_gb.setter
    def storage_gb(self, value: int) -> None:
        """Expand storage capacity (GB).

        Note: RDS storage can only be expanded, not shrunk.

        Args:
            value: New storage capacity, must be >= current capacity.

        Raises:
            ValueError: If value is invalid or less than current capacity.
        """
        self._validate_storage_gb(value, self._storage_gb)
        self._storage_gb = value

    @property
    def multi_az(self) -> bool:
        """Get Multi-AZ deployment status (read-only)."""
        return self._multi_az

    def get_hourly_cost(self) -> float:
        """Calculate hourly cost of RDS instance.

        Only running instances incur instance costs.
        Multi-AZ deployment doubles the instance cost.

        Returns:
            float: Hourly cost in USD, excluding storage cost.
        """
        if not self.is_running:
            return 0.0
        hourly = self.INSTANCE_PRICING[self._instance_class]
        if self._multi_az:
            hourly *= 2
        return hourly

    def get_cost(self) -> float:
        """Calculate monthly cost of RDS instance.

        Cost = Instance cost + Storage cost
        - Instance cost: Only billed when running, Multi-AZ doubles cost
        - Storage cost: Billed regardless of running status

        Returns:
            float: Monthly cost in USD.
        """
        instance_cost = self.get_hourly_cost() * self.HOURS_PER_MONTH
        storage_cost = self._storage_gb * self.STORAGE_PRICE_PER_GB
        return instance_cost + storage_cost

    def get_info(self) -> dict[str, Any]:
        """Get detailed RDS instance information.

        Returns:
            dict: Dictionary containing instance details.
        """
        return {
            'resource_id': self.resource_id,
            'resource_type': self.resource_type,
            'region': self.region,
            'status': self.status,
            'instance_class': self._instance_class,
            'engine': self._engine,
            'storage_gb': self._storage_gb,
            'multi_az': self._multi_az,
            'hourly_cost': self.get_hourly_cost(),
            'monthly_cost': self.get_cost(),
        }

    def __str__(self) -> str:
        """Return user-friendly string for RDS instance."""
        az_suffix = " (Multi-AZ)" if self._multi_az else ""
        return (
            f"RDS: {self.resource_id} "
            f"({self._engine}, {self._instance_class}){az_suffix} - {self.status}"
        )

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"id={self.resource_id!r}, "
            f"region={self.region!r}, "
            f"instance_class={self._instance_class!r}, "
            f"engine={self._engine!r}, "
            f"storage_gb={self._storage_gb}, "
            f"multi_az={self._multi_az})"
        )
