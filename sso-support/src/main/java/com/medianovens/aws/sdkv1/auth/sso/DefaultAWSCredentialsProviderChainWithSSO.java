package com.medianovens.aws.sdkv1.auth.sso;

import com.amazonaws.auth.*;
import com.amazonaws.auth.profile.ProfileCredentialsProvider;

public class DefaultAWSCredentialsProviderChainWithSSO extends AWSCredentialsProviderChain {
    private static final DefaultAWSCredentialsProviderChainWithSSO INSTANCE = new DefaultAWSCredentialsProviderChainWithSSO();

    public DefaultAWSCredentialsProviderChainWithSSO() {
        super(
                new EnvironmentVariableCredentialsProvider(),
                new SystemPropertiesCredentialsProvider(),
                WebIdentityTokenCredentialsProvider.create(),
                new ProfileCredentialsProvider(),
                new EC2ContainerCredentialsProviderWrapper(),
                new SsoCredentialsProvider()
        );
    }

    public static DefaultAWSCredentialsProviderChainWithSSO getInstance() {
        return INSTANCE;
    }
}
