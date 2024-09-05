package com.medianovens.aws.sdkv1.auth.sso;

import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.glue.catalog.metastore.AWSCredentialsProviderFactory;
import org.apache.hadoop.conf.Configuration;

public class DefaultAWSCredentialsProviderFactoryWithSSO implements AWSCredentialsProviderFactory {
    public DefaultAWSCredentialsProviderFactoryWithSSO() {
    }

    public AWSCredentialsProvider buildAWSCredentialsProvider(Configuration conf) {
        return new DefaultAWSCredentialsProviderChainWithSSO();
    }
}
