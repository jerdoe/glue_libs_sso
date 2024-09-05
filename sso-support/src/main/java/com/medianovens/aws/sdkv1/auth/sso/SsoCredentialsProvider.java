package com.medianovens.aws.sdkv1.auth.sso;

import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.auth.BasicSessionCredentials;
import software.amazon.awssdk.auth.credentials.AwsCredentials;
import software.amazon.awssdk.auth.credentials.AwsSessionCredentials;
import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;

/**
 * <p>
 * Adapter to reuse SSO Credentials Provider from AWS Java SDK2
 * in AWS Java SDK1.
 * </p>
 * <p>
 * Credits to <a href=https://github.com/millems>millems</a>
 * in <a href="https://github.com/aws/aws-sdk-java/issues/803#issuecomment-593530484">
 *     his github comment</a>
 * </p>
 */
public class SsoCredentialsProvider implements AWSCredentialsProvider {
    private final ProfileCredentialsProvider delegate;

    public SsoCredentialsProvider() {
        this.delegate = ProfileCredentialsProvider.create();
    }

    public SsoCredentialsProvider(String profileName) {
        this.delegate = ProfileCredentialsProvider.create(profileName);
    }

    @Override
    public AWSCredentials getCredentials() {
        AwsCredentials credentials = delegate.resolveCredentials();

        if (credentials instanceof AwsSessionCredentials) {
            AwsSessionCredentials sessionCredentials = (AwsSessionCredentials) credentials;
            return new BasicSessionCredentials(sessionCredentials.accessKeyId(),
                    sessionCredentials.secretAccessKey(),
                    sessionCredentials.sessionToken());
        }

        return new BasicAWSCredentials(credentials.accessKeyId(), credentials.secretAccessKey());
    }

    @Override
    public void refresh() {
        throw new UnsupportedOperationException();
    }
}