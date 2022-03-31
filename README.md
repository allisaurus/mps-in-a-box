
# O3DE MultiplayerSample in a box

This project encapsulates a release build of [o3de-multiplayersample](https://github.com/o3de/o3de-multiplayersample) into a container image and uses the [AWS CDK](https://aws.amazon.com/cdk/) to deploy it's `ServerLauncher` and `GameLauncher` into an Amazon ECS cluster as separate services.

### What it does
 - creates a new VPC and an ECS cluster that deploys into that VPC
 - creates 2 ECS services which leverage the _AWS Fargate_ launch type
 - automatically creates log groups per service 


### What it _doesn't_ do (yet)

 - Build a release layout of [o3de-multiplayersample](https://github.com/o3de/o3de-multiplayersample) for you. How to do this will vary based on your local project configuration. See [O3DE docs](https://docs.o3de.org/docs/user-guide/packaging/windows-release-builds/) for more information.
 - Connect the `GameLauncher` to the `ServerLauncher` in the cluster. This is a near-term goal of this project, but doesn't happen automatically yet. See [TODOs](#todos)
 - Open either service "to the world". Once deployed, you can manually add ingress rules to whichever service you want to try and hit.

### Requirements
 - AWS CLI (installed and configured)
 - AWS CDK (installed and [bootstrapped](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html#getting_started_bootstrap) to your desired region)
 - docker desktop in _[Windows Container](https://docs.docker.com/desktop/windows/) mode_
 - [o3de-multiplayersample](https://github.com/o3de/o3de-multiplayersample) configured locally


## How to deploy

**WARNING**: Resources created by this stack are not free. Please make sure you're using an account that can accomodate the cost and destroy the stack when it's no longer in use. 

1. Install and/or configure the required tools.
2. Copy your release layout of [o3de-multiplayersample](https://github.com/o3de/) into the [container_assets/mps](/container_assets/mps/) directory.
3. Build the container image
    ```bash
    cd container_assets
    docker build -t o3de-mps-windows .
    ```
4. Create an ECR repository called "o3de-mps-windows" and push the built image to it
    ```bash
    # create repo
    aws ecr create-repository --repository-name o3de-mps-windows --region <AWS_REGION>

    # login to repo
    aws ecr get-login-password --region <AWS_REGION> | docker login --username AWS --password-stdin <MY_AWS_ACCT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com

    # tag the image with the repository
    docker tag o3de-mps-windows:latest <MY_AWS_ACCT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/o3de-mps-windows:latest

    # push the image
    docker push <MY_AWS_ACCT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/o3de-mps-windows:latest
    ```
5. Run `cdk synth` to ensure CloudFormation can be generated & review what will be created
6. Run `cdk deploy` to deploy the stack
7. Stack deployment will complete when both services are stable (i.e., the desired number (1 by default) of tasks are running). Logs for the running tasks can now be seen via the ECS web console:
    
    ![server log web view](/serverlog_web_view.PNG)

8. When done with testing/etc., clean up stack by running `cdk destroy`


# Useful Links

### CDK
 - https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/Vpc.html
 - https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/FargateService.html
 - https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/FargateTaskDefinition.html
 - https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/LogDriver.html#aws_cdk.aws_ecs.LogDriver.aws_logs
 - https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/ContainerImage.html#aws_cdk.aws_ecs.ContainerImage.from_ecr_repository

### O3DE
 - https://docs.o3de.org/docs/user-guide/packaging/windows-release-builds/
 - https://github.com/o3de/o3de-multiplayersample

# TODOs
 
 - service discovery between client & server services
    -   ingress rules between client & server security groups
    -   pass private IP address of server to client via env var
 - create ECR repo in stack and build MPS image from docker asset
 - stack output for: server task IP address, AWS web console deep-link logs tabs
 - parameterize whether or not to make server port open to the internet
 - use Linux containers