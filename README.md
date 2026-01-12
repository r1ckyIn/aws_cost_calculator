# AWS Cost Calculator

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![AWS](https://img.shields.io/badge/AWS-Cloud-FF9900?style=flat-square&logo=amazon-aws&logoColor=white)](https://aws.amazon.com)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

**A Python-based AWS resource cost calculator demonstrating OOP principles**

[English](#english) | [中文](#中文)

</div>

---

## English

### Overview

AWS Cost Calculator is a command-line tool that calculates monthly costs for various AWS resources. This project demonstrates Object-Oriented Programming principles including inheritance, polymorphism, abstract classes, and composition patterns.

### Features

- **Multi-resource Support**: EC2, Lambda, S3, EBS, RDS
- **Cost Calculation**: Automatic monthly cost calculation based on resource configuration
- **Resource Management**: Add, remove, filter resources by region or type
- **Report Generation**: Generate comprehensive cost reports
- **Factory Pattern**: Create resources using flexible factory functions

### Quick Start

```bash
# Clone the repository
git clone https://github.com/r1ckyIn/aws_cost_calculator.git
cd aws_cost_calculator

# Run the demo (no dependencies required)
python main.py
```

### Usage

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

### Project Structure

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
└── main.py                # Demo entry point
```

### Tech Stack

- **Abstract Base Class**: `CloudResource` with `@abstractmethod` decorators
- **Inheritance & Polymorphism**: 5 resource classes implementing common interface
- **Encapsulation**: Private attributes with `@property` decorators
- **Composition**: `AWSResourcesManager` manages multiple resources
- **Factory Pattern**: Flexible resource creation with aliases
- **Type Annotations**: Full type hints with `ClassVar`, `NoReturn`, etc.

### Supported Resources

| Resource | Pricing Model |
|----------|---------------|
| EC2 | Per hour (only when running) |
| Lambda | Per million requests + GB-seconds |
| S3 | Per GB storage |
| EBS | Per GB based on volume type |
| RDS | Per hour + storage (Multi-AZ doubles instance cost) |

---

## 中文

### 项目概述

AWS Cost Calculator 是一个基于命令行的 AWS 资源成本计算工具。该项目展示了面向对象编程原则，包括继承、多态、抽象类和组合模式。

### 功能特性

- **多资源支持**：EC2、Lambda、S3、EBS、RDS
- **成本计算**：根据资源配置自动计算月度成本
- **资源管理**：按区域或类型添加、删除、筛选资源
- **报告生成**：生成综合成本报告
- **工厂模式**：使用灵活的工厂函数创建资源

### 快速开始

```bash
# 克隆仓库
git clone https://github.com/r1ckyIn/aws_cost_calculator.git
cd aws_cost_calculator

# 运行演示（无需安装依赖）
python main.py
```

### 技术亮点

- **抽象基类**：使用 `@abstractmethod` 装饰器的 `CloudResource`
- **继承与多态**：5 个资源类实现统一接口
- **封装**：使用 `@property` 装饰器的私有属性
- **组合**：`AWSResourcesManager` 管理多个资源
- **工厂模式**：支持别名的灵活资源创建
- **类型注解**：完整的类型提示，包括 `ClassVar`、`NoReturn` 等

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**Ricky** - CS Student @ University of Sydney

[![GitHub](https://img.shields.io/badge/GitHub-r1ckyIn-181717?style=flat-square&logo=github)](https://github.com/r1ckyIn)

Interested in Cloud Engineering & DevOps
