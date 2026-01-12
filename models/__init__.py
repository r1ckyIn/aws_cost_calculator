"""AWS Resource Models Package.

Provides convenient imports for all AWS resource classes.
"""

from models.base import CloudResource
from models.compute import EC2Instance, LambdaFunction
from models.storage import S3Bucket, EBSVolume
from models.database import RDSDatabase

__all__ = [
    'CloudResource',
    'EC2Instance',
    'LambdaFunction',
    'S3Bucket',
    'EBSVolume',
    'RDSDatabase',
]
