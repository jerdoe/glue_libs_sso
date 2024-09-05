package org.apache.hadoop.conf;

/**
 * This class is originally located in the JAR file
 * `/home/glue_user/spark/jars/hadoop-common-3.3.3-amzn-0.jar`
 * within the AWS Glue Docker image `amazon/aws-glue-libs:glue_libs_4.0.0_image_01`.
 *
 * While it could be included as a dependency in `pom.xml`:
 * <pre>
 * {@code
 * <dependency>
 *   <groupId>org.apache.hadoop</groupId>
 *   <artifactId>hadoop-common</artifactId>
 *   <version>3.3.3</version>
 * </dependency>
 * }
 * </pre>
 * a stub is used instead because only a reference to
 * {@code org.apache.hadoop.conf.Configuration} is needed for compilation.
 * This class is not utilized in the actual implementation,
 * so avoiding the full dependency prevents the unnecessary inclusion of
 * external libraries during the build process.
 */
public class Configuration {
}
