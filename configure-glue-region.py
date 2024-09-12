#!/usr/local/bin/python3
"""
Configure AWS Glue to use the SSO credentials provider.

This script generates two configuration files:

1. **glue-default.conf** with the following content:
{
  credentials_provider: "com.medianovens.aws.sdkv1.auth.sso.DefaultAWSCredentialsProviderChainWithSSO",
  region: <sys.argv[1]>,
  glue {
    endpoint: "https://glue.<sys.argv[1]>.amazonaws.com"
  }
}

2. **glue-override.conf**, an empty file.

These files will be packaged into a JAR named `glue-conf.jar`, which will be saved to `~/aws_glue_libs/jars`,
overriding any existing JAR with the same name.
"""
import sys
import os
import zipfile

def main():
    script_name = sys.argv[0]

    # Check if a region is provided as an argument
    if len(sys.argv) != 2:
        print(f"Usage: {script_name} <region>")
        sys.exit(1)

    # Get the region from the argument
    region = sys.argv[1]

    # Paths for the configuration files and JAR
    glue_jars_dir = os.path.expanduser("~/aws-glue-libs/jars")
    jar_path = os.path.join(glue_jars_dir, "glue-conf.jar")

    # Content for glue-default.conf
    glue_default_content = f"""\
    {{
      credentials_provider: "com.medianovens.aws.sdkv1.auth.sso.DefaultAWSCredentialsProviderChainWithSSO",
      region: "{region}",
      glue {{
        endpoint: "https://glue.{region}.amazonaws.com"
      }}
    }}
    """

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
