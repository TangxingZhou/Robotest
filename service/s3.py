import os
import io
import re
import logging
import oss2
import boto3
from botocore.config import Config
from minio import Minio
from minio.deleteobjects import DeleteObject
from itertools import islice


logger = logging.getLogger(__name__)


class S3Bucket:

    def __init__(self, endpoint, access_key_id, access_key_secret, bucket_name, path_prefix='', region=None, path_style=True):
        self._bucket = boto3.resource(
            's3',
            region_name=region,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=access_key_secret,
            endpoint_url=endpoint,
            config=Config(
                s3={
                    'addressing_style': 'path' if path_style else 'virtual',
                    'payload_signing_enabled': True
                },
                signature_version='s3v4'
            )
        ).Bucket(bucket_name)
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/bucket/index.html
        self._prefix_path = path_prefix

    def clear_objects(self, prefix: str, recursive=True):
        batch_size = 10
        if not prefix.startswith(self._prefix_path):
            prefix = os.path.join(self._prefix_path, prefix)
        while True:
            response = self._bucket.meta.client.list_objects_v2(
                Bucket=self._bucket.node_name,
                Prefix=prefix,
                Delimiter='/',
                MaxKeys=batch_size
            )
            if 'CommonPrefixes' in response and recursive:
                for prefix in response['CommonPrefixes']:
                    self.clear_objects(prefix['Prefix'])
            if 'Contents' in response:
                objs = [obj['Key'] for obj in response['Contents'] if obj['Key'] != response['Prefix']]
                logger.debug(f"Delete objects in oss bucket '{self._bucket.node_name}': {', '.join(objs)}")
                # TODO: 删除失败，MissingContentMD5的错误
                response = self._bucket.delete_objects(
                    Delete={'Objects': [{'Key': obj} for obj in objs]}
                )
                if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                    raise Exception(f"Failed to delete objects in oss bucket '{self._bucket.node_name}'.")
            else:
                break
        logger.debug(f"Delete object in oss bucket '{self._bucket.node_name}': {prefix}")
        response = self._bucket.meta.client.delete_object(Bucket=self._bucket.node_name, Key=prefix)
        if response['ResponseMetadata']['HTTPStatusCode'] != 204:
            raise Exception(f"Failed to delete object in oss bucket '{self._bucket.node_name}'.")

    def create_directory(self, path: str, clear_if_exists: bool = True):
        if not path.endswith('/'):
            path += '/'
        path_prefix = os.path.join(self._prefix_path, path)
        if clear_if_exists:
            self.clear_objects(path_prefix)
        result = self._bucket.put_object(Key=path_prefix, Body=b'', ContentLength=0)
        if result.status == 200:
            return path_prefix
        else:
            raise Exception(f"Failed to create directory '{path_prefix}' in oss bucket '{self._bucket.bucket_name}'.\n{result.resp.response.reason}")

    def list_files(self, path='', recursive=False):
        path_prefix = os.path.join(self._prefix_path, path)
        if recursive:
            return [
                obj for obj in
                self._bucket.objects.filter(Prefix=path_prefix)
            ]
        else:
            return [
                obj for obj in
                self._bucket.objects.filter(Prefix=path_prefix, Delimiter='/')
            ]


class OSSBucket:
    def __init__(self, endpoint, access_key_id, access_key_secret, bucket_name, path_prefix=''):
        self._bucket: oss2.Bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
        self._prefix_path = path_prefix

    def clear_objects(self, prefix: str, recursive=True):
        batch_size = 100
        if not prefix.startswith(self._prefix_path):
            prefix = os.path.join(self._prefix_path, prefix)
        objs = []
        while True:
            obj_iterator = oss2.ObjectIterator(self._bucket, prefix=prefix, delimiter='/')
            for obj in islice(obj_iterator, 0, batch_size):
                if obj.is_prefix():
                    if recursive:
                        self.clear_objects(obj.key)
                else:
                    if obj.key != obj_iterator.prefix:
                        objs.append(obj.key)
            if objs:
                logger.debug(f"Delete objects in oss bucket '{self._bucket.bucket_name}': {', '.join(objs)}")
                result = self._bucket.batch_delete_objects(objs)
                if result.status == 200:
                    objs.clear()
                else:
                    raise Exception(f"Failed to delete objects in oss bucket '{self._bucket.bucket_name}'.\n{result.resp.response.reason}")
            else:
                break
        logger.debug(f"Delete object in oss bucket '{self._bucket.bucket_name}': {prefix}")
        result = self._bucket.delete_object(prefix)
        if result.status == 204:
            objs.clear()
        else:
            raise Exception(f"Failed to delete object in oss bucket '{self._bucket.bucket_name}'.\n{result.resp.response.reason}")

    def create_directory(self, prefix: str, clear_if_exists: bool = True):
        if not prefix.endswith('/'):
            prefix += '/'
        prefix = os.path.join(self._prefix_path, prefix)
        if clear_if_exists:
            self.clear_objects(prefix)
        result = self._bucket.put_object(prefix, '')
        if result.status == 200:
            return prefix
        else:
            raise Exception(f"Failed to create directory '{prefix}' in oss bucket '{self._bucket.bucket_name}'.\n{result.resp.response.reason}")

    def list_objects(self, prefix='', recursive=False):
        prefix = os.path.join(self._prefix_path, prefix)
        if recursive:
            return [
                obj for obj in
                oss2.ObjectIterator(self._bucket, prefix=prefix)
                if not obj.key.endswith('/')
            ]
        else:
            return [
                obj for obj in
                oss2.ObjectIterator(self._bucket, prefix=prefix, delimiter='/')
                if not obj.is_prefix() and not obj.key.endswith('/')
            ]


class MinioClient:
    def __init__(self, endpoint, access_key_id, access_key_secret, bucket_name, path_prefix='', region=None):
        self._client = Minio(
            re.sub(r'^https?://', '', endpoint, flags=re.IGNORECASE),
            access_key=access_key_id,
            secret_key=access_key_secret,
            region=region,
            secure=True if 'https://' in endpoint else False
        )
        self._bucket_name = bucket_name
        self._prefix_path = path_prefix

    def clear_objects(self, prefix: str, recursive=True):
        if not prefix.startswith(self._prefix_path):
            prefix = os.path.join(self._prefix_path, prefix)
        delete_object_list = map(
            lambda x: DeleteObject(x.object_name),
            self._client.list_objects(self._bucket_name, prefix, recursive=recursive),
        )
        errors = self._client.remove_objects(self._bucket_name, delete_object_list)
        has_error = False
        for error in errors:
            logger.error(error)
            has_error = True
        if has_error:
            raise Exception(f"Failed to delete files under path '{prefix}'")

    def create_directory(self, prefix: str, clear_if_exists: bool = True):
        if not prefix.endswith('/'):
            prefix += '/'
        prefix = os.path.join(self._prefix_path, prefix)
        if clear_if_exists:
            self.clear_objects(prefix)
        _ = self._client.put_object(self._bucket_name, prefix, io.BytesIO(b""), 0)
        return prefix

    def list_objects(self, prefix='', recursive=False):
        objects = self._client.list_objects(
            self._bucket_name, prefix=os.path.join(self._prefix_path, prefix), recursive=recursive,
        )
        return [obj for obj in objects]
