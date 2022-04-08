from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ecs as ecs
)
from constructs import Construct

class MpsInABoxStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # stack variables
        server_port = 33450                 # the port the server will be listening on. Should match the `sv_port` specified in server.cfg
        mps_repo_name = "o3de-mps-windows"  # the ECR repo in the local region which contains the MPS image
        client_count = 1                    # how many copies of the client we want to run

        # vpc + cluster (fargate first, then ec2 windows)
        vpc = ec2.Vpc(self, "MpsEcsVpc")
        cluster = ecs.Cluster(self, "EcsCLuster", vpc=vpc)

        # Existing ecr repo with container image - TODO: create within stack, from Docker image asset
        mpsRepo = ecr.Repository.from_repository_name(self, "MpsRepo", mps_repo_name)

        
        # ECS task def + service for MPS SERVER
        mps_server_task_def = self.get_mps_taskdef("MpsServerTaskDef")
        mps_server_task_def.add_container("MpsServerContainer",
            image=ecs.ContainerImage.from_ecr_repository(mpsRepo), # takes latest tag by default
            port_mappings=[ecs.PortMapping(container_port=server_port)],
            entry_point=["powershell.exe"],
            command=["cd 'c:\\mps'; pwd; ./MultiplayerSample.ServerLauncher.exe --console-command-file=server.cfg --rhi=null; start-sleep -seconds 15; get-content -path user/log/Server.log -Wait"],
            logging=ecs.LogDriver.aws_logs( # creates new
                stream_prefix="mps-server"
            )
        )
        serverService = ecs.FargateService(self, "MpsServerService", cluster=cluster, task_definition=mps_server_task_def)
        


        # ECS task def + service for MPS CLIENT
        mps_client_task_def = self.get_mps_taskdef("MpsClientTaskDef")
        mps_client_task_def.add_container("MpsClientContainer",
            image=ecs.ContainerImage.from_ecr_repository(mpsRepo), # takes latest tag by default
            port_mappings=[ecs.PortMapping(container_port=server_port)],
            entry_point=["powershell.exe"],
            command=["cd 'c:\\mps'; pwd; ./MultiplayerSample.GameLauncher.exe --console-command-file=client.cfg; start-sleep -seconds 15; get-content -path user/log/Game.log -Wait"],
            logging=ecs.LogDriver.aws_logs( # creates new
                stream_prefix="mps-client"
            )
        )
        clientService = ecs.FargateService(self, "MpsClientService" , 
            cluster=cluster, 
            task_definition=mps_client_task_def, 
            desired_count=client_count
        ) 

        # allow connections between the server and client services
        serverService.connections.allow_from(clientService, ec2.Port.udp(server_port))
        clientService.connections.allow_from(serverService, ec2.Port.udp(server_port))

    def get_mps_taskdef(self, id: str ) -> ecs.FargateTaskDefinition:
        return ecs.FargateTaskDefinition(self, id,
            memory_limit_mib=10240, # TODO: see if this can be smaller
            cpu=4096,               # TODO: see if this can be smaller
            runtime_platform=ecs.RuntimePlatform(
                operating_system_family=ecs.OperatingSystemFamily.WINDOWS_SERVER_2019_CORE,
                cpu_architecture=ecs.CpuArchitecture.X86_64
            )
        )