"""Utility Functions Module.

Provides factory functions and helper utilities for AWS resources.
"""

from typing import Any

from models import (
    CloudResource,
    EC2Instance,
    LambdaFunction,
    S3Bucket,
    EBSVolume,
    RDSDatabase,
)


# Resource type registry (supports multiple aliases)
_RESOURCE_CLASSES: dict[str, type[CloudResource]] = {
    'ec2': EC2Instance,
    'ec2instance': EC2Instance,
    'lambda': LambdaFunction,
    'lambdafunction': LambdaFunction,
    's3': S3Bucket,
    's3bucket': S3Bucket,
    'ebs': EBSVolume,
    'ebsvolume': EBSVolume,
    'rds': RDSDatabase,
    'rdsdatabase': RDSDatabase,
}


def get_supported_resource_types() -> list[str]:
    """Get all supported resource type names.

    Returns:
        list[str]: List of supported resource types (deduplicated).
    """
    return sorted(set(cls.__name__ for cls in _RESOURCE_CLASSES.values()))


def create_resource(resource_type: str, **kwargs: Any) -> CloudResource:
    """Create resource instance by type.

    Args:
        resource_type: Resource type name, supports aliases (e.g., 'ec2', 'EC2Instance').
        **kwargs: Arguments to pass to resource constructor.

    Returns:
        CloudResource: Created resource instance.

    Raises:
        ValueError: If resource type is not supported.

    Example:
        >>> ec2 = create_resource('ec2',
        ...     resource_id='i-123',
        ...     region='us-east-1',
        ...     instance_type='t2.micro'
        ... )
    """
    resource_class = _RESOURCE_CLASSES.get(resource_type.lower())
    if resource_class is None:
        supported = get_supported_resource_types()
        raise ValueError(
            f"Unknown resource type: '{resource_type}'. "
            f"Supported types: {supported}"
        )
    return resource_class(**kwargs)


def create_resource_from_dict(data: dict[str, Any]) -> CloudResource:
    """Create resource instance from dictionary.

    Dictionary must contain 'type' key to specify resource type,
    remaining keys are passed as constructor arguments.

    Args:
        data: Resource configuration dictionary.

    Returns:
        CloudResource: Created resource instance.

    Raises:
        KeyError: If dictionary is missing 'type' key.
        ValueError: If resource type is not supported.

    Example:
        >>> config = {
        ...     'type': 'ec2',
        ...     'resource_id': 'i-123',
        ...     'region': 'us-east-1',
        ...     'instance_type': 't2.micro'
        ... }
        >>> ec2 = create_resource_from_dict(config)
    """
    data = data.copy()
    try:
        resource_type = data.pop('type')
    except KeyError as e:
        raise KeyError("Resource dict must contain 'type' key") from e
    return create_resource(resource_type, **data)


def create_resources_from_list(
    data_list: list[dict[str, Any]]
) -> list[CloudResource]:
    """Batch create resources from list of dictionaries.

    Args:
        data_list: List of resource configuration dictionaries, each must contain 'type' key.
            Empty list will return empty result.

    Returns:
        list[CloudResource]: List of created resource instances.

    Raises:
        KeyError: If any dictionary is missing 'type' key.
        ValueError: If any resource type is unsupported or parameters are invalid.

    Example:
        >>> configs = [
        ...     {'type': 'ec2', 'resource_id': 'i-1', 'region': 'us-east-1',
        ...      'instance_type': 't2.micro'},
        ...     {'type': 's3', 'resource_id': 'bucket-1', 'region': 'us-east-1',
        ...      'storage_gb': 100},
        ... ]
        >>> resources = create_resources_from_list(configs)
    """
    resources = []
    for index, data in enumerate(data_list):
        try:
            resources.append(create_resource_from_dict(data))
        except (KeyError, ValueError, TypeError) as e:
            raise type(e)(f"Error at index {index}: {e}") from e
    return resources
