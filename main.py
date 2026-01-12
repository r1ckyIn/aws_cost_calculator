"""AWS Cost Calculator Entry Module.

Demonstrates AWS resource management and cost calculation functionality.
"""

from typing import Any

from manager import AWSResourcesManager
from models import EC2Instance, RDSDatabase
from utils import create_resources_from_list


def create_sample_resources() -> list[dict[str, Any]]:
    """Create sample resource configuration list."""
    return [
        # EC2 Instances
        {
            'type': 'ec2',
            'resource_id': 'i-web-server-01',
            'region': 'us-east-1',
            'instance_type': 't2.small',
        },
        {
            'type': 'ec2',
            'resource_id': 'i-api-server-01',
            'region': 'us-east-1',
            'instance_type': 't2.medium',
        },
        # Lambda Function
        {
            'type': 'lambda',
            'resource_id': 'data-processor',
            'region': 'us-east-1',
            'memory_mb': 1024,
            'monthly_invocations': 5_000_000,
            'avg_duration_ms': 200,
        },
        # S3 Buckets
        {
            'type': 's3',
            'resource_id': 'app-assets-bucket',
            'region': 'us-west-2',
            'storage_gb': 500,
        },
        {
            'type': 's3',
            'resource_id': 'backup-bucket',
            'region': 'us-west-2',
            'storage_gb': 2000,
        },
        # EBS Volume
        {
            'type': 'ebs',
            'resource_id': 'vol-data-01',
            'region': 'us-east-1',
            'volume_type': 'gp3',
            'size_gb': 500,
        },
        # RDS Database
        {
            'type': 'rds',
            'resource_id': 'prod-database',
            'region': 'ap-northeast-1',
            'instance_class': 'db.r5.large',
            'engine': 'postgresql',
            'storage_gb': 200,
            'multi_az': True,
        },
    ]


def print_separator(title: str = '') -> None:
    """Print separator line."""
    if title:
        print(f"\n{'=' * 20} {title} {'=' * 20}")
    else:
        print('=' * 50)


def main() -> None:
    """Main function: Demonstrate AWS cost calculator functionality."""
    print_separator("AWS Cost Calculator Demo")

    # 1. Create resource manager
    manager = AWSResourcesManager()

    # 2. Batch create resources using factory functions
    configs = create_sample_resources()
    resources = create_resources_from_list(configs)

    # 3. Add resources to manager
    for resource in resources:
        manager.add_aws_resource(resource)

    print(f"\nLoaded {len(resources)} resources")

    # 4. Start some resources (EC2 and RDS need to be started for billing)
    print_separator("Starting Resources")
    for resource in manager.get_aws_resources():
        if isinstance(resource, (EC2Instance, RDSDatabase)):
            resource.start()
            print(f"  Started: {resource.resource_id}")

    # 5. View resources by type
    print_separator("Resources by Type")
    for resource_type in manager.get_resource_types():
        type_resources = manager.get_resources_by_type(resource_type)
        total = sum(r.get_cost() for r in type_resources)
        print(f"\n  [{resource_type}] ({len(type_resources)} resources, ${total:.2f}/month)")
        for r in type_resources:
            print(f"    - {r.resource_id}: ${r.get_cost():.2f}")

    # 6. View resources by region
    print_separator("Resources by Region")
    for region in manager.get_regions():
        region_resources = manager.get_resources_by_region(region)
        total = sum(r.get_cost() for r in region_resources)
        print(f"\n  [{region}] ({len(region_resources)} resources, ${total:.2f}/month)")
        for r in region_resources:
            print(f"    - {r.resource_id}: ${r.get_cost():.2f}")

    # 7. Generate full report
    print_separator("Cost Report")
    report = manager.generate_report()

    print(f"\n  Total Resources: {report['total_count']}")
    print(f"  Total Monthly Cost: ${report['total_cost']:.2f}")

    print("\n  By Region:")
    for region, count in sorted(report['resources_by_region'].items()):
        print(f"    - {region}: {count} resources")

    print("\n  By Type:")
    for rtype, count in sorted(report['resources_by_type'].items()):
        print(f"    - {rtype}: {count} resources")

    # 8. Demonstrate stopping resource
    print_separator("Stop EC2 Instance")
    ec2 = manager.get_resources_by_type('EC2Instance')[0]
    print(f"  Before: {ec2} - ${ec2.get_cost():.2f}/month")
    ec2.stop()
    print(f"  After:  {ec2} - ${ec2.get_cost():.2f}/month")

    # 9. Final cost
    print_separator("Final Summary")
    print(f"\n  Total Monthly Cost: ${manager.get_total_cost():.2f}")

    print_separator()


if __name__ == '__main__':
    main()
