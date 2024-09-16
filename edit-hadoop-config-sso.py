#!/usr/local/bin/python3
prog_desc = 'Edit a Hadoop Configuration File to add support for SSO Credentials provider'

default_provider_chain: str = "com.amazonaws.auth.DefaultAWSCredentialsProviderChain"
sso_provider_chain: str = "com.medianovens.aws.sdkv1.auth.sso.DefaultAWSCredentialsProviderChainWithSSO"

default_provider_chain_factory: str = "com.amazonaws.glue.catalog.metastore.DefaultAWSCredentialsProviderFactory"
sso_provider_chain_factory: str = "com.medianovens.aws.sdkv1.auth.sso.DefaultAWSCredentialsProviderFactoryWithSSO"

config_prop_name_s3_fs_impl = "fs.s3.impl"
config_prop_name_s3a_fs_impl = "fs.s3a.impl"
config_prop_val_s3a_fs_impl = "org.apache.hadoop.fs.s3a.S3AFileSystem"

config_prop_name_s3_creds_provider = "fs.s3.aws.credentials.provider"
config_prop_name_s3a_creds_provider = "fs.s3a.aws.credentials.provider"
config_prop_name_awscatalog_creds_providerfactory = "aws.catalog.credentials.provider.factory.class"

prog_epilog = f"""
Edit the Hadoop configuration file at <file_pathname>
using the following procedure:

- Create or set the property value of '{config_prop_name_s3_fs_impl}' and '{config_prop_name_s3a_fs_impl}'
to '{config_prop_val_s3a_fs_impl}'.

- Create or set the property value of '{config_prop_name_awscatalog_creds_providerfactory}'
to '{sso_provider_chain_factory}'.

- Create or set the property value of '{config_prop_name_s3_creds_provider}' and '{config_prop_name_s3a_creds_provider}'
to '{sso_provider_chain}'.

- Replace occurrences of the property value '{default_provider_chain}'
with '{sso_provider_chain}'

- Replace occurrences of the property value '{default_provider_chain_factory}'
with '{sso_provider_chain_factory}'.

These new values refers to classes found in /home/glue_user/aws-glue-libs/sso-support-*.jar,
which extend the default credentials providers.

These new classes first attempt to use the default providers (AWS SDK v1 for Java).
If they fail, the system will use an adapter that wraps
the AWS SDK v2 for Java SSO credential provider in a class compatible with
AWS SDK v1 for Java interfaces.

If <output_jar_pathname> is specified, a jar containing a copy of the created
or updated Hadoop configuration file, will also be generated.
"""

import os
from typing import List
import shutil
from pathlib import Path
import argparse
import zipfile

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, tostring, canonicalize

parser = argparse.ArgumentParser(description=prog_desc, epilog=prog_epilog, formatter_class=argparse.RawDescriptionHelpFormatter)

default_core_site_xml: str = f"{os.environ['HADOOP_CONF_DIR']}/core-site.xml" if 'HADOOP_CONF_DIR' in os.environ else 'core-site.xml'
parser.add_argument('-f', '--file', metavar='<file_pathname>', default=default_core_site_xml, help='the pathname to the newly generated or updated hadoop configuration file (default: either `${HADOOP_CONF_DIR}/core-site.xml` OR `./core-site.xml` if ${HADOOP_CONF_DIR} is not defined)')

parser.add_argument('-u', '--update', action='store_true', help='required to edit an existing file at <file_pathname>')
parser.add_argument('-j', '--jar', metavar='<output_jar_pathname>', help='also, creates a JAR containing the new Hadoop configuration file')

args = parser.parse_args()

class HadoopConf:
    def __init__(self, xml_file: str, update: bool):
        if update:
            self.root = ElementTree.parse(xml_file).getroot()
        else:
            self.root = Element("configuration")


    class Prop:
        def __init__(self, *, name :str = None, value :str = None, property_element :Element = None):
            assert ((property_element is not None and name is None and value is None)
                    or (property_element is None and name is not None and value is not None)),\
                "You must either specify 'property_element' alone, or both 'name' and 'value'."

            if property_element is not None:
                self.as_element = property_element
            else:
                el_prop = Element("property")

                el_name = Element("name")
                el_name.text = name
                el_prop.append(el_name)

                el_value = Element("value")
                el_value.text = value
                el_prop.append(el_value)

                self.as_element = el_prop

        def _get_subelement(self, tag: str):
            return self.as_element.find(tag).text

        def _set_subelement(self, tag: str, text :str):
            self.as_element.find(tag).text = text

        def get_name(self):
            return self._get_subelement("name")

        def set_name(self, name :str):
            self._set_subelement("name", name)

        def get_value(self):
            return self._get_subelement("value")

        def set_value(self, value :str):
            self._set_subelement("value", value)

    def add_prop(self, name, value):
        prop = HadoopConf.Prop(name=name, value=value)
        self.root.append(prop.as_element)

    def find_props(self, tag: str, text: str) -> list[Prop] | None:
        """
        Find all properties in the XML tree where the text matches `{text}` and is enclosed by `{tag}` tags.
        """
        result_elements = self.root.findall(f".//property/[{tag}='{text}']")
        return None if result_elements is None \
            else [HadoopConf.Prop(property_element = e) for e in result_elements]

    def find_prop(self, tag: str, text: str) -> Prop | None:
        """
        Find the first property in the XML tree where the text matches `{text}` and is enclosed by `{tag}` tags.
        """
        result_element = self.root.find(f".//property/[{tag}='{text}']")
        return None if result_element is None else HadoopConf.Prop(property_element=result_element)

    def find_prop_by_name(self, name: str) -> Prop | None:
        """ Find the first property in the XML tree with the specified name. """

        return self.find_prop("name", name)

    def find_prop_by_value(self, value: str) -> Prop | None:
        """ Find the first property in the XML tree with the specified value. """
        return self.find_prop("value", value)

    def find_props_by_value(self, value: str) -> List[Prop] | None:
        """ Find all properties in the XML tree with the specified value. """
        return self.find_props("value", value)

    def set(self, name, value):
        """ Set the value for the property with the specified name. Create it if it does not exist """
        prop = self.find_prop_by_name(name)

        if prop is None:
            self.add_prop(name, value)
        else:
            prop.set_value(value)

    def prettify(self):
        """ Format the xml to make it look prettier """
        xml_str = tostring(self.root, encoding="utf-8")

        # Canonicalize the XML string by removing all spaces and parse it into the root element
        canon_xml_str = canonicalize(xml_str, strip_text=True)
        self.root = ElementTree.fromstring(canon_xml_str)

        # Re-indent the XML tree by adding 4 spaces at every new level
        ElementTree.indent(self.root, space="    ")

    def write(self, output_xml: str):
        """ Write the xml to the specified output """
        self.prettify()
        ElementTree.ElementTree(self.root).write(output_xml, encoding="utf-8")

def main():
    assert (args.update or not Path(args.file).exists()), f"{args.file} already exists, but the --update option was not provided."

    hadoop_conf = HadoopConf(xml_file=args.file, update=args.update)
    hadoop_conf.set(config_prop_name_s3_fs_impl, config_prop_val_s3a_fs_impl)
    hadoop_conf.set(config_prop_name_s3a_fs_impl, config_prop_val_s3a_fs_impl)
    hadoop_conf.set(config_prop_name_s3_creds_provider, sso_provider_chain)
    hadoop_conf.set(config_prop_name_s3a_creds_provider, sso_provider_chain)
    hadoop_conf.set(config_prop_name_awscatalog_creds_providerfactory, sso_provider_chain_factory)

    for prop in hadoop_conf.find_props_by_value(default_provider_chain):
        prop.set_value(sso_provider_chain)

    for prop in hadoop_conf.find_props_by_value(default_provider_chain_factory):
        prop.set_value(sso_provider_chain_factory)

    hadoop_conf.write(args.file)

    if args.jar is not None:
        with zipfile.ZipFile(args.jar, "w") as jar:
            jar.write(args.file, os.path.basename(args.file))

if __name__ == "__main__":
    main()
