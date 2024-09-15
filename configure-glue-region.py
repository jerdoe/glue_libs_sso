#!/usr/local/bin/python3
prog_desc :str = 'Builds a JAR that configures AWS Glue to include SSO in the authentication chain'

prog_epilog :str = """
This script generates two configuration files:

1. **glue-default.conf** with the following content:
{
  credentials_provider: "com.medianovens.aws.sdkv1.auth.sso.DefaultAWSCredentialsProviderChainWithSSO",
  region: <region>,
  glue {
    endpoint: "https://glue.<region>.amazonaws.com"
  }
}

2. **glue-override.conf**, an empty file.

These files will be packaged into a JAR saved to <output_jar>, which should be part of the AWS Glue classpath.

If not present, AWS Glue will use the Default AWS Credentials Provider Chain and the Default AWS Region Provider Chain.

For more information, see:
- https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/credentials.html#credentials-default
- https://docs.aws.amazon.com/AWSJavaSDK/latest/javadoc/com/amazonaws/auth/DefaultAWSCredentialsProviderChain.html

- https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/java-dg-region-selection.html#default-region-provider-chain
- https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/regions/providers/DefaultAwsRegionProviderChain.html
"""
import sys
import os
import zipfile
import argparse
import textwrap

class RawDescArgDefaultsFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

def main():
    parser = argparse.ArgumentParser(description=prog_desc, epilog=prog_epilog, formatter_class=RawDescArgDefaultsFormatter)
    parser.add_argument('region', metavar='<region>', help='the region to use for glue endpoint configuration')
    parser.add_argument('-o', '--output', metavar='<output_jar>', default="~/aws-glue-libs/jars/glue-conf.jar",
                        help='the pathname of the output jar', dest='output_jar')

    args = parser.parse_args()

    # Get the region from the argument
    region = args.region

    jar_path = os.path.expanduser(args.output_jar)

    # Content for glue-default.conf
    glue_default_content = textwrap.dedent(f"""\
      {{
        credentials_provider: "com.medianovens.aws.sdkv1.auth.sso.DefaultAWSCredentialsProviderChainWithSSO",
        region: "{region}",
        glue {{
          endpoint: "https://glue.{region}.amazonaws.com"
        }}
      }}
      """)

    # Create glue-default.conf and glue-override.conf
    with open("glue-default.conf", "w") as default_conf:
        default_conf.write(glue_default_content)

    with open("glue-override.conf", "w") as override_conf:
        override_conf.write("")

    # Create a ZIP file (JAR) and add the configuration files
    with zipfile.ZipFile(jar_path, "w") as jar:
        jar.write("glue-default.conf")
        jar.write("glue-override.conf")

    # Cleanup - Remove the configuration files after zipping
    os.remove("glue-default.conf")
    os.remove("glue-override.conf")

    print(f"Configuration JAR created at {jar_path}")

if __name__ == "__main__":
    main()
