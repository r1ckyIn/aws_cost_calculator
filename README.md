# AWS Cost Calculator

A Python-based AWS resource cost calculator that demonstrates Object-Oriented Programming principles including inheritance, polymorphism, abstract classes, and composition patterns.

## Features

- **Multi-resource Support**: EC2, Lambda, S3, EBS, RDS
- **Cost Calculation**: Automatic monthly cost calculation based on resource configuration
- **Resource Management**: Add, remove, filter resources by region or type
- **Report Generation**: Generate comprehensive cost reports
- **Factory Pattern**: Create resources using flexible factory functions

## Project Structure

```
aws_cost_calculator/
├── models/
│   ├── __init__.py        # Package exports
│   ├── base.py            # CloudResource abstract base class
│   ├── compute.py         # EC2Instance, LambdaFunction
│   ├── storage.py         # S3Bucket, EBSVolume
│   └── database.py        # RDSDatabase
├── manager.py             # AWSResourcesManager
├── utils.py               # Factory functions
├── main.py                # Demo entry point
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/aws-cost-calculator.git
cd aws-cost-calculator

# No external dependencies required - uses Python standard library only
# Requires Python 3.10+
```

## Usage

### Run the Demo

```bash
python main.py
```

### Basic Usage

```python
from manager import AWSResourcesManager
from utils import create_resource

# Create a manager
manager = AWSResourcesManager()

# Create resources using factory function
ec2 = create_resource(
    'ec2',
    resource_id='i-123456',
    region='us-east-1',
    instance_type='t2.micro'
)
ec2.start()  # EC2 only charges when running

s3 = create_resource(
    's3',
    resource_id='my-bucket',
    region='us-east-1',
    storage_gb=100
)

# Add to manager
manager.add_aws_resource(ec2)
manager.add_aws_resource(s3)

# Get total cost
print(f"Total: ${manager.get_total_cost():.2f}/month")

# Generate report
report = manager.generate_report()
print(report)
```

### Batch Resource Creation

```python
from utils import create_resources_from_list

configs = [
    {'type': 'ec2', 'resource_id': 'i-1', 'region': 'us-east-1', 'instance_type': 't2.micro'},
    {'type': 's3', 'resource_id': 'bucket-1', 'region': 'us-east-1', 'storage_gb': 100},
    {'type': 'rds', 'resource_id': 'db-1', 'region': 'us-east-1',
     'instance_class': 'db.t3.micro', 'engine': 'mysql', 'storage_gb': 20},
]

resources = create_resources_from_list(configs)
```

## Supported Resources

| Resource | Pricing Model |
|----------|---------------|
| EC2 | Per hour (only when running) |
| Lambda | Per million requests + GB-seconds |
| S3 | Per GB storage |
| EBS | Per GB based on volume type |
| RDS | Per hour + storage (Multi-AZ doubles instance cost) |

## Resource Pricing

### EC2 Instance Types
| Type | Price/Hour |
|------|------------|
| t2.micro | $0.0116 |
| t2.small | $0.023 |
| t2.medium | $0.0464 |

### EBS Volume Types
| Type | Price/GB/Month |
|------|----------------|
| gp2 | $0.10 |
| gp3 | $0.08 |
| io1/io2 | $0.125 |
| st1 | $0.045 |
| sc1 | $0.015 |

### Other Services
- **S3**: $0.023/GB/month
- **RDS Storage**: $0.115/GB/month
- **Lambda**: $0.20/million requests + $0.0000166667/GB-second

## Technical Highlights

- **Abstract Base Class**: `CloudResource` with `@abstractmethod` decorators
- **Inheritance & Polymorphism**: 5 resource classes implementing common interface
- **Encapsulation**: Private attributes with `@property` decorators
- **Composition**: `AWSResourcesManager` manages multiple resources
- **Factory Pattern**: Flexible resource creation with aliases
- **Type Annotations**: Full type hints with `ClassVar`, `NoReturn`, etc.
- **PEP8 Compliant**: Google-style docstrings, proper naming conventions

## Supported Regions

- us-east-1
- us-west-2
- eu-west-1
- ap-southeast-1
- ap-northeast-1

## License

MIT License

## Author

Ricky

## Acknowledgments

This project was created as part of a Python OOP learning curriculum.
