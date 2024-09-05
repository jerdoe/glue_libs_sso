package com.amazonaws.glue.catalog.metastore;

import com.amazonaws.auth.AWSCredentialsProvider;
import org.apache.hadoop.conf.Configuration;

/**
 * <p>
 * This interface is located in the JAR file
 * `/home/glue_user/spark/jars/aws-glue-datacatalog-spark-client-3.7.0.jar`
 * within the AWS Glue Docker image `amazon/aws-glue-libs:glue_libs_4.0.0_image_01`.
 * </p>
 * <p>
 * This JAR does not appear to be available in the Maven Central Repository.
 * However, the source code for lower versions can be found on GitHub:
 * <a href="https://github.com/awslabs/aws-glue-data-catalog-client-for-apache-hive-metastore/blob/branch-3.4.0/aws-glue-datacatalog-client-common/src/main/java/com/amazonaws/glue/catalog/metastore/AWSCredentialsProviderFactory.java">
 * awslabs/aws-glue-data-catalog-client-for-apache-hive-metastore
 * </a>.
 * </p>
 * <p>
 * For convenience, a stub is used in place of referencing all dependencies
 * in the `pom.xml`.
 * </p>
 */

public interface AWSCredentialsProviderFactory {
    AWSCredentialsProvider buildAWSCredentialsProvider(Configuration conf);
}
