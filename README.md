## Project Overview

This project enhances the `amazon/aws-glue-libs` Docker image to support Single Sign-On (SSO) functionality.  
With this enhancement, you can run `aws2 sso login` to authenticate instead of manually providing credentials for your Glue jobs.

**Current Tested Image:** `amazon/aws-glue-libs:glue_libs_4.0.0_image_01` 

For more information about amazon/aws-glue-libs Docker image, see:
- [Docker Container Image for AWS Glue ETL | hub.docker.com](https://hub.docker.com/r/amazon/aws-glue-libs)
- [Developing and testing AWS Glue job scripts locally, using a Docker image | docs.aws.amazon.com/glue](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-libraries.html#develop-local-docker-image)

### What It Does

- **Java Adapter Integration**: Builds a Java adapter that enables AWS Java SDK v2 SSO Credentials Providers
to work with AWS Java SDK v1 Credentials Provider interfaces.
(Credits to: [Millems](https://github.com/millems) on https://github.com/aws/aws-sdk-java/issues/803#issuecomment-593530484)

- **Docker Image Enhancement**: Adds the necessary SSO libraries to the Docker image and updates the Hadoop configuration file to utilize these libraries, facilitating seamless integration with SSO.

### Key Features

- Integration of SSO support in the AWS Glue Docker image.
- Compatibility with AWS Java SDK v2 and v1 credentials providers.
- Updated Hadoop configuration for new library usage.

## Table of Contents

- [Getting Started](#getting-started)
- [Advanced Configuration](#advanced-configuration)
- [License](#license)

## Prerequisites
As mentionned in the [prerequisites section](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-libraries.html#develop-local-docker-image-prereq) 
of [Developing and testing AWS Glue job scripts locally, using a Docker image | docs.aws.amazon.com/glue](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-libraries.html#develop-local-docker-image):

>Before you start, make sure that Docker is installed and the Docker daemon is running. For installation instructions,
>see the Docker documentation for [Mac](https://docs.docker.com/docker-for-mac/install/) or [Linux](https://docs.docker.com/engine/install/).
>The machine running the Docker hosts the AWS Glue container.
>Also make sure that you have at least 7 GB of disk space for the image on the host running the Docker.
>
>For more information about restrictions when developing AWS Glue code locally, see [Local development restrictions](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-libraries.html#local-dev-restrictions).


## Getting Started

1. **Clone the Repository**

   Use the following command to clone the repository:

   ```bash
   git clone https://github.com/jerdoe/glue_libs_sso.git

   cd glue_libs_sso
   ```

1. **Optional (only if using Docker Desktop): Add the workspace folder to the file-sharing resources**
   
   - Docker Desktop -> Settings -> Resources -> File sharing -> Virtual file shares -> Browse
   - Select `glue_libs_sso/binds/workspace`, then click on the `+` symbol
     
1. **Run the container**

   ```bash
   docker compose up -d   
   ```
1. **Configure SSO**
   ```bash
   # Do not miss the quotes after `bash -lc`
   docker compose exec aws-glue bash -lc 'aws2 configure sso'
   ```
1. **Optional: Specify your custom AWS Profile (only if not using the default aws profile)**
   - Open compose.yaml in an editor:
     
     ```bash
     # Open compose.yaml in the editor
     nano compose.yaml
     ```
   - Uncomment the following line and change its value
     
     ```yaml
     ...
     services:
       aws-glue:
         ...
         environment:
           ...
           #AWS_PROFILE: "my_aws_profile"   
           ...
     ```
   - Save your changes
     
1. **Configure the Glue Endpoint Region**
   - Click [here](https://docs.aws.amazon.com/general/latest/gr/glue.html) to see a list of valid regions
   - Open an interactive shell inside the container and run the [configuration script](https://github.com/jerdoe/glue_libs_sso/blob/main/configure-glue-region.py):

     ```bash
     docker compose exec aws-glue bash -l
     configure-glue-region.py <region> #e.g: ap-south-1
     ```

   - Alternatively, you can run the script directly:

     ```bash
     # DO NOT MISS THE QUOTES
     docker compose exec aws-glue bash -lc 'configure-glue-region.py <region>'
     ```


1. **Run your tasks**
   - You can run tasks in an interactive shell or via the `docker compose exec` command:

     ```bash     
     # The file `sample.py` on the host would be located at `glue_libs_sso/binds/workspace/src/sample.py`
     # and automatically mapped to `/home/glue_user/workspace/src/sample.py` inside the container.
     # Since the container's default working directory is `/home/glue_user/workspace`,
     # you only need to reference files starting from the `src` directory.

     # DO NOT MISS THE QUOTES
     docker compose exec aws-glue bash -lc 'spark-submit src/sample.py'

     docker compose exec aws-glue bash -lc pyspark

     # DO NOT MISS THE QUOTES
     docker compose exec aws-glue bash -lc '~/jupyter/jupyter_start.sh'
     ```
   

## Advanced configuration

   You might want to adjust the following settings by editing the `compose.yaml` file:
      
   - This Docker image enables you to configure your SSO profile within the container
     by running `aws2 configure sso`, and log in using `aws2 sso login`.
     
     If you prefer to reuse your existing AWS configuration from the host, uncomment the following line.
     Please note that in this last case, you may need to run `chmod g+rw` on the `~/.aws/sso/cache/xxxxx.json`
     file or on the `~/.aws/sso/cache` folder to ensure credentials refresh correctly.
     This is necessary because the host user ID may not match the Glue user ID (10000),
     which could prevent the container from updating the JSON file.
     Granting write access to the owner group can resolve this issue.
     
     ```yaml
     ...
     services:
       aws-glue:
         ...
         volumes:
           ...
           #- vol_aws_custom:${GLUE_AWS}
           ...
     ```
     
   - To automatically start the jupyter server when running `docker compose up`,
       uncomment the following line.
     
     ```yaml
     ...
     services:
       aws-glue:
         ...
         #command: ["${GLUE_HOME}/jupyter/jupyter_start.sh"]
     ```
     
   - To specify a custom path for your workspace on the host (instead of the default
     `./binds/workspace/`), update the value of the `device` option.
   
     ```yaml
     ...
     volumes:
       vol_workspace:
         ...
         driver_opts:
           ...
           device: "./binds/workspace/"
           ...
     ```
## License

This project is licensed under MIT license but depends on components that are under the Apache 2.0 License.
See [LICENSE-MIT](LICENSE-MIT), [LICENSE-APACHE-2.0](LICENSE-APACHE-2.0) and [NOTICE](NOTICE) files.
