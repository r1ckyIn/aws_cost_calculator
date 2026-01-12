"""Compute Resources Module.

This module defines AWS compute-related resource classes, including EC2Instance and LambdaFunction.
"""

from typing import Any, ClassVar, NoReturn

from models.base import CloudResource


class EC2Instance(CloudResource):
    """AWS EC2 Instance resource class.

    Attributes:
        resource_id: Instance ID (e.g., 'i-1234567890abcdef0').
        region: AWS region.
        instance_type: Instance type (e.g., 't2.micro').
        status: Instance status ('running' or 'stopped').
    """

    # EC2 instance type pricing (USD/hour)
    INSTANCE_PRICING: ClassVar[dict[str, float]] = {
        't2.micro': 0.0116,
        't2.small': 0.023,
        't2.medium': 0.0464,
    }

    # Hours per month (for monthly cost calculation)
    HOURS_PER_MONTH: ClassVar[int] = 730

    def __init__(
        self,
        resource_id: str,
        region: str,
        instance_type: str
    ) -> None:
        """Initialize EC2 instance.

        Args:
            resource_id: Unique instance identifier.
            region: AWS region code.
            instance_type: Instance type, e.g., 't2.micro'.

        Raises:
            ValueError: If resource_id is empty, region is invalid, or instance_type is unsupported.
        """
        super().__init__(resource_id, region)

        if instance_type not in self.INSTANCE_PRICING:
            raise ValueError(
                f"Unsupported instance type '{instance_type}'. "
                f"Supported types: {', '.join(sorted(self.INSTANCE_PRICING))}"
            )

        self._instance_type = instance_type

    @classmethod
    def supported_types(cls) -> list[str]:
        """Get all supported instance types.

        Returns:
            list[str]: List of supported instance types.
        """
        return sorted(cls.INSTANCE_PRICING)

    @property
    def instance_type(self) -> str:
        """Get instance type (read-only).

        Instance type cannot be modified after creation. Create a new instance if change is needed.

        Returns:
            str: Instance type identifier, e.g., 't2.micro'.
        """
        return self._instance_type

    def get_hourly_cost(self) -> float:
        """Calculate hourly cost of EC2 instance.

        Only running instances are billed. Stopped instances cost $0.

        Returns:
            float: Hourly cost in USD.
        """
        if not self.is_running:
            return 0.0
        return self.INSTANCE_PRICING[self._instance_type]

    def get_cost(self) -> float:
        """Calculate monthly cost of EC2 instance.

        Only running instances are billed. Stopped instances cost $0.

        Returns:
            float: Monthly cost in USD.
        """
        return self.get_hourly_cost() * self.HOURS_PER_MONTH

    def get_info(self) -> dict[str, Any]:
        """Get detailed EC2 instance information.

        Returns:
            dict: Dictionary containing instance details.
        """
        return {
            'resource_id': self.resource_id,
            'resource_type': self.resource_type,
            'region': self.region,
            'status': self.status,
            'instance_type': self._instance_type,
            'hourly_cost': self.get_hourly_cost(),
            'monthly_cost': self.get_cost(),
        }

    def __str__(self) -> str:
        """Return user-friendly string for EC2 instance."""
        return f"EC2: {self.resource_id} ({self._instance_type}) - {self.status}"

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"id={self.resource_id!r}, "
            f"region={self.region!r}, "
            f"instance_type={self._instance_type!r}, "
            f"status={self.status!r})"
        )


class LambdaFunction(CloudResource):
    """AWS Lambda Function resource class.

    Lambda is billed by invocation count and execution time, independent of traditional status
    (functions are always callable once deployed).

    Attributes:
        resource_id: Function name.
        region: AWS region.
        memory_mb: Allocated memory (MB).
        monthly_invocations: Monthly invocation count.
        avg_duration_ms: Average execution time (milliseconds).
    """

    # Lambda pricing constants
    PRICE_PER_MILLION_REQUESTS: ClassVar[float] = 0.20
    PRICE_PER_GB_SECOND: ClassVar[float] = 0.0000166667

    # Unit conversion constants
    MB_PER_GB: ClassVar[int] = 1024
    MS_PER_SECOND: ClassVar[int] = 1000
    REQUESTS_PER_PRICING_UNIT: ClassVar[int] = 1_000_000

    # Supported memory configurations (MB)
    VALID_MEMORY_SIZES: ClassVar[list[int]] = [
        128, 256, 512, 1024, 2048, 4096, 8192, 10240
    ]

    def __init__(
        self,
        resource_id: str,
        region: str,
        memory_mb: int,
        monthly_invocations: int = 0,
        avg_duration_ms: float = 0.0
    ) -> None:
        """Initialize Lambda function.

        Args:
            resource_id: Function name.
            region: AWS region code.
            memory_mb: Allocated memory (MB), must be a valid configuration.
            monthly_invocations: Monthly invocation count, default 0.
            avg_duration_ms: Average execution time (milliseconds), default 0.

        Raises:
            ValueError: If parameters are invalid.
        """
        super().__init__(resource_id, region)

        if memory_mb not in self.VALID_MEMORY_SIZES:
            raise ValueError(
                f"Unsupported memory size '{memory_mb}MB'. "
                f"Supported sizes: {self.VALID_MEMORY_SIZES}"
            )

        if monthly_invocations < 0:
            raise ValueError("monthly_invocations must be non-negative")

        if avg_duration_ms < 0:
            raise ValueError("avg_duration_ms must be non-negative")

        self._memory_mb = memory_mb
        self._monthly_invocations = monthly_invocations
        self._avg_duration_ms = avg_duration_ms
        # Lambda functions are always available once deployed
        self._status = self._STATUS_RUNNING

    def start(self) -> NoReturn:
        """Lambda functions do not support start operation.

        Raises:
            NotImplementedError: Lambda functions are always callable.
        """
        raise NotImplementedError(
            "Lambda functions are always available when deployed"
        )

    def stop(self) -> NoReturn:
        """Lambda functions do not support stop operation.

        Raises:
            NotImplementedError: Lambda functions cannot be stopped.
        """
        raise NotImplementedError("Lambda functions cannot be stopped")

    @classmethod
    def supported_memory_sizes(cls) -> list[int]:
        """Get all supported memory configurations.

        Returns:
            list[int]: List of supported memory sizes (MB).
        """
        return cls.VALID_MEMORY_SIZES.copy()

    @property
    def memory_mb(self) -> int:
        """Get allocated memory (MB) (read-only)."""
        return self._memory_mb

    @property
    def monthly_invocations(self) -> int:
        """Get monthly invocation count."""
        return self._monthly_invocations

    @monthly_invocations.setter
    def monthly_invocations(self, value: int) -> None:
        """Set monthly invocation count.

        Args:
            value: Invocation count, must be non-negative.

        Raises:
            ValueError: If value is negative.
        """
        if not isinstance(value, int) or value < 0:
            raise ValueError("monthly_invocations must be a non-negative integer")
        self._monthly_invocations = value

    @property
    def avg_duration_ms(self) -> float:
        """Get average execution time (milliseconds)."""
        return self._avg_duration_ms

    @avg_duration_ms.setter
    def avg_duration_ms(self, value: float) -> None:
        """Set average execution time (milliseconds).

        Args:
            value: Execution time, must be non-negative.

        Raises:
            ValueError: If value is negative.
        """
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("avg_duration_ms must be a non-negative number")
        self._avg_duration_ms = float(value)

    def get_cost(self) -> float:
        """Calculate monthly cost of Lambda function.

        Cost = Request cost + Compute cost
        - Request cost: $0.20 / million requests
        - Compute cost: $0.0000166667 / GB-second

        Returns:
            float: Monthly cost in USD.
        """
        # Request cost
        request_cost = (
            (self._monthly_invocations / self.REQUESTS_PER_PRICING_UNIT)
            * self.PRICE_PER_MILLION_REQUESTS
        )

        # Compute cost: GB-seconds = (memory MB / 1024) * (time ms / 1000) * invocations
        gb_seconds = (
            (self._memory_mb / self.MB_PER_GB)
            * (self._avg_duration_ms / self.MS_PER_SECOND)
            * self._monthly_invocations
        )
        compute_cost = gb_seconds * self.PRICE_PER_GB_SECOND

        return request_cost + compute_cost

    def get_info(self) -> dict[str, Any]:
        """Get detailed Lambda function information.

        Returns:
            dict: Dictionary containing function details.
        """
        return {
            'resource_id': self.resource_id,
            'resource_type': self.resource_type,
            'region': self.region,
            'status': self.status,
            'memory_mb': self._memory_mb,
            'monthly_invocations': self._monthly_invocations,
            'avg_duration_ms': self._avg_duration_ms,
            'monthly_cost': self.get_cost(),
        }

    def __str__(self) -> str:
        """Return user-friendly string for Lambda function."""
        return f"Lambda: {self.resource_id} ({self._memory_mb}MB)"

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"id={self.resource_id!r}, "
            f"region={self.region!r}, "
            f"memory_mb={self._memory_mb})"
        )
