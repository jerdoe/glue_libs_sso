ARG MAVEN_DOCKER_IMAGE="maven:3.9.9-eclipse-temurin-22-alpine"
ARG AWSGLUE_DOCKER_IMAGE="amazon/aws-glue-libs:glue_libs_4.0.0_image_01"

ARG GLUE_USER="glue_user"
ARG GLUE_HOME="/home/${GLUE_USER}"
ARG GLUE_AWS="${GLUE_HOME}/.aws"
ARG GLUE_LIBS_DIR="${GLUE_HOME}/aws-glue-libs/jars"

##############################
#### STAGE: build-jar-sso ####
##############################

FROM ${MAVEN_DOCKER_IMAGE} AS build-jar-sso

WORKDIR /project
COPY sso-support /project
RUN <<EOF
  # Build a sso java adapter that makes aws sdk v2 sso credentials provider
  # compatible with aws sdk v1 credentials provider interfaces
  mvn package

  # Copy aws sdk v2 sso libraries into target
  cp ${MAVEN_CONFIG}/repository/software/amazon/awssdk/sso/**/*.jar /project/target/
  cp ${MAVEN_CONFIG}/repository/software/amazon/awssdk/ssooidc/**/*.jar /project/target/
EOF

##############################
#### STAGE: awsglue ##########
##############################

FROM ${AWSGLUE_DOCKER_IMAGE} AS awsglue

# Consume build arguments in this build stage
# (global scope build arguments are not automatically inherited into the build stages)
ARG GLUE_USER
ARG GLUE_LIBS_DIR
ARG GLUE_HOME
ARG GLUE_AWS

COPY --chown=${GLUE_USER}:root --from=build-jar-sso "/project/target/*.jar" "${GLUE_LIBS_DIR}/"
COPY --chown=${GLUE_USER}:root "edit-hadoop-config-sso.py" "${GLUE_HOME}/.local/bin/"
COPY --chown=${GLUE_USER}:root "configure-glue-region.py" "${GLUE_HOME}/.local/bin/"

RUN <<EOF
  # Make a backup of core-site.xml
  cp ${GLUE_HOME}/spark/conf/core-site.xml ${GLUE_HOME}/spark/conf/core-site.xml.orig

  # Update hadoop config file to use sso crendentials providers
  "${GLUE_HOME}/.local/bin/edit-hadoop-config-sso.py" -u

  # Change dir to ${GLUE_HOME}
  cd "${GLUE_HOME}"

  # Install aws-cli-v2 without replacing existing version
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
  unzip awscliv2.zip
  cd aws
  mkdir bin aws-cli
  ./install -b "${PWD}/bin" -i "${PWD}/aws-cli"

  # Allow to run it by typing 'aws2'
  ln -s "${PWD}/bin/aws" "${GLUE_HOME}/.local/bin/aws2"

  # Create .aws folder
  mkdir "${GLUE_AWS}"
EOF

# Resetting the default entrypoint 
# The default entrypoint cannot be inherited from the base image, 
# so it must be explicitly reset
ENTRYPOINT ["bash","-l"]
