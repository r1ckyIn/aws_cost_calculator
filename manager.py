"""AWS Resource Manager Module.

Provides unified management functionality for AWS cloud resources,
including adding, removing, filtering, and report generation.
"""

from collections import Counter
from collections.abc import Callable
from typing import Any

from models.base import CloudResource


class AWSResourcesManager:
    """AWS Resource Manager class.

    Manages multiple AWS cloud resources, providing add, remove, filter, and report generation functions.

    Attributes:
        _aws_resources: Internal dictionary storing resources (private, use public methods to access)

    Example:
        >>> manager = AWSResourcesManager()
        >>> ec2 = EC2Instance("i-123", "ap-southeast-1", "t2.micro")
        >>> ec2.start()
        True
        >>> manager.add_aws_resource(ec2)
        >>> manager.get_total_cost()
        8.468
    """

    def __init__(self) -> None:
        """Initialize resource manager with empty resource dictionary."""
        self._aws_resources: dict[str, CloudResource] = {}

    def __repr__(self) -> str:
        """Return string representation of manager."""
        return f"{self.__class__.__name__}(resources={len(self._aws_resources)})"

    def add_aws_resource(self, aws_resource: CloudResource) -> None:
        """Add AWS resource to manager.

        Args:
            aws_resource: Instance of CloudResource subclass

        Raises:
            ValueError: If resource_id already exists
        """
        if aws_resource.resource_id in self._aws_resources:
            raise ValueError(
                f"Resource with ID {aws_resource.resource_id} already exists"
            )

        self._aws_resources[aws_resource.resource_id] = aws_resource

    def remove_aws_resource(self, resource_id: str) -> CloudResource:
        """Remove specified resource from manager.

        Args:
            resource_id: ID of resource to remove

        Returns:
            CloudResource: The removed resource object

        Raises:
            ValueError: If resource_id does not exist
        """
        if resource_id not in self._aws_resources:
            raise ValueError(
                f"Resource with ID {resource_id} does not exist"
            )
        return self._aws_resources.pop(resource_id)

    def get_aws_resources(self) -> list[CloudResource]:
        """Get list of all resources.

        Returns:
            list[CloudResource]: List containing all CloudResource objects
        """
        return list(self._aws_resources.values())

    def get_total_cost(self) -> float:
        """Calculate total cost of all resources.

        Returns:
            float: Sum of all resource costs
        """
        return sum(
            aws_resource.get_cost()
            for aws_resource in self._aws_resources.values()
        )

    def get_resources_by_region(self, region: str) -> list[CloudResource]:
        """Filter resources by region.

        Args:
            region: AWS region name, e.g., 'ap-southeast-1'

        Returns:
            list[CloudResource]: List of all resources in specified region
        """
        return [
            resource for resource in self._aws_resources.values()
            if resource.region == region
        ]

    def get_resources_by_type(self, resource_type: str) -> list[CloudResource]:
        """Filter resources by type (case-insensitive).

        Args:
            resource_type: Resource type name, e.g., 'EC2Instance', 's3bucket'

        Returns:
            list[CloudResource]: List of all resources of specified type
        """
        resource_type_lower = resource_type.lower()
        return [
            resource for resource in self._aws_resources.values()
            if resource.resource_type.lower() == resource_type_lower
        ]

    def _get_unique_values(
        self, extractor: Callable[[CloudResource], str]
    ) -> list[str]:
        """Generic helper method to extract unique values from all resources.

        Args:
            extractor: Function to extract string value from resource object

        Returns:
            list[str]: List of unique values, empty list if no resources
        """
        return sorted(set(
            extractor(resource) for resource in self._aws_resources.values()
        ))

    def get_regions(self) -> list[str]:
        """Get list of all regions used by resources.

        Returns:
            list[str]: List of unique region names, empty list if no resources
        """
        return self._get_unique_values(lambda r: r.region)

    def get_resource_types(self) -> list[str]:
        """Get list of all resource types.

        Returns:
            list[str]: List of unique resource type names, empty list if no resources
        """
        return self._get_unique_values(lambda r: r.resource_type)

    def generate_report(self) -> dict[str, Any]:
        """Generate resource cost report.

        Returns:
            dict[str, Any]: Report dictionary containing:
                - total_cost: Total cost
                - total_count: Total resource count
                - resources: List of all resources
                - resources_by_region: Resource count by region
                - resources_by_type: Resource count by type
        """
        total_cost = 0.0
        resources: list[CloudResource] = []
        region_counter: Counter[str] = Counter()
        type_counter: Counter[str] = Counter()

        for resource in self._aws_resources.values():
            total_cost += resource.get_cost()
            resources.append(resource)
            region_counter[resource.region] += 1
            type_counter[resource.resource_type] += 1

        return {
            'total_cost': total_cost,
            'total_count': len(resources),
            'resources': resources,
            'resources_by_region': dict(region_counter),
            'resources_by_type': dict(type_counter),
        }
