from flyingcircus.config import ExportYamlContext
from flyingcircus.core import Stack
from flyingcircus.core import Output
from flyingcircus.service import s3

import textwrap


def reflow(st):
    # TODO better name
    """Dedent a multiline string, whilst removing leading and trailing blank lines.

    This is perfect for text embedded inside indented Python code.
    """
    lines = st.split('\n')
    while lines:
        if not lines[0] or lines[0].isspace():
            lines = lines[1:]
            continue
        if not lines[-1] or lines[-1].isspace():
            lines = lines[:-1]
            continue
        break

    return textwrap.dedent('\n'.join(lines))


SIMPLE_S3_YAML = '''---
AWSTemplateFormatVersion: '2010-09-09'
Description: 'AWS CloudFormation Sample Template S3_Website_Bucket_With_Retain_On_Delete:
  Sample template showing how to create a publicly accessible S3 bucket configured
  for website access with a deletion policy of retail on delete.
  
  **WARNING** This template creates an S3 bucket that will NOT be deleted when
  the stack is deleted. You will be billed for the AWS resources used if you
  create a stack from this template.'

Resources:
  S3Bucket:
    DeletionPolicy: Retain
    Properties:
      AccessControl: PublicRead
      WebsiteConfiguration:
        ErrorDocument: error.html
        IndexDocument: index.html
    Type: AWS::S3::Bucket

Outputs:
  S3BucketSecureURL:
    Description: Name of S3 bucket to hold website content
    Value: !Join ['', ['https://', !GetAtt S3Bucket.DomainName]]
  WebsiteURL:
    Description: URL for website hosted on S3
    Value: !GetAtt S3Bucket.WebsiteURL
'''


class TestCoreServices:
    def test_s3_as_naive_python(self):
        """As a developer, I can use a straightforward python representation of YAML to create objects representing a basic S3 bucket."""
        # Exercise
        stack = Stack(
            AWSTemplateFormatVersion="2010-09-09",
            Description=reflow("""
                AWS CloudFormation Sample Template S3_Website_Bucket_With_Retain_On_Delete:
                Sample template showing how to create a publicly accessible S3 bucket configured
                for website access with a deletion policy of retail on delete.
                
                **WARNING** This template creates an S3 bucket that will NOT be deleted when
                the stack is deleted. You will be billed for the AWS resources used if you
                create a stack from this template."""),
        )
        stack.Resources["S3Bucket"] = s3.Bucket(
            Properties={
                "AccessControl": "PublicRead",
                "WebsiteConfiguration": {
                    "IndexDocument": "index.html",
                    "ErrorDocument": "error.html",
                }
            },
            DeletionPolicy="Retain",
        )
        stack.Outputs["WebsiteURL"] = Output(
            Value="!GetAtt S3Bucket.WebsiteURL",
            Description="URL for website hosted on S3",
        )
        stack.Outputs["S3BucketSecureURL"] = Output(
            Value='''!Join ["", ["https://", !GetAtt S3Bucket.DomainName]]''',
            Description="Name of S3 bucket to hold website content",
        )

        # Verify
        # TODO print(yaml.dump({'a': 42, 'b': 55, 'c': {"tag": "AWS::xyz", "foo":"HELLoworld"}}, line_break=True, default_flow_style=False))
        with ExportYamlContext():  # this context manager simply makes explicit the defualt behavious of stringifying as YAML
            print(str(stack))
            assert str(stack) == SIMPLE_S3_YAML

    def test_s3_as_magic_python(self):
        """As a developer, I can use a magic Python interface to create Python objects representing a basic S3 bucket."""
        # Exercise
        bucket = s3.Bucket(
            Name="S3Bucket",
            Properties={
                # TODO needs to be abstracted so we can export in a variable format
                "AccessControl": "PublicRead",
                "WebsiteConfiguration": {
                    "IndexDocument": "index.html",
                    "ErrorDocument": "error.html",
                }
            },
            DeletionPolicy="Retain",
        )
        stack = Stack(
            Description="vcvxcv",
            WebsiteURL=Output(
                Value=bucket.WebsiteURL,
                Description="URL for website hosted on S3",
            ),
            S3BucketSecureURL=Output(
                Value=Join("https://", bucket.DomainName),
                Description="Name of S3 bucket to hold website content",
            ),
        ).add(bucket)

        # Verify
        with ExportYamlContext():
            assert str(stack) == SIMPLE_S3_YAML
