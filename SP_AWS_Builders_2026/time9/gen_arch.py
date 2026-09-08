from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.ml import Sagemaker  # usado como icone de IA/Bedrock (proxy)
from diagrams.aws.network import CloudFront
from diagrams.aws.storage import S3
from diagrams.aws.compute import Lambda
from diagrams.aws.network import APIGateway
from diagrams.onprem.client import User
from diagrams.onprem.database import Mysql  # proxy para TiDB (MySQL-compatible)
from diagrams.programming.framework import Vue, Fastapi

graph_attr = {"fontsize": "13", "bgcolor": "white", "pad": "0.5", "dpi": "200", "ranksep": "1.0"}

with Diagram("AirRevenue - Arquitetura (deploy EC2, sa-east-1)",
             filename="docs/architecture", outformat="png", show=False,
             direction="LR", graph_attr=graph_attr):

    analyst = User("Revenue Manager\n(companhia aerea)")

    with Cluster("AWS sa-east-1 (Sao Paulo) - EC2 do time"):
        with Cluster("EC2 (portas 8000/3000, 0.0.0.0)"):
            fe = Vue("Frontend Vue\n(SPA, area por cia)")
            be = Fastapi("Backend FastAPI\n(JWT zero-trust)")
            fe >> Edge(label="REST /api + Bearer JWT") >> be

    with Cluster("TiDB Cloud Starter (AWS)"):
        tidb = Mysql("airportdb\n+ campanhas\n+ VECTOR (busca vetorial)")

    with Cluster("AWS ap-southeast-1 (Singapura)"):
        bedrock = Sagemaker("Amazon Bedrock\nClaude 3 Haiku\n(texto da promocao)")

    analyst >> Edge(label="HTTPS") >> fe
    be >> Edge(label="SQL/TLS :4000\nleitura+escrita") >> tidb
    be >> Edge(label="invoke_model\n(fallback: template)", style="dashed") >> bedrock

    with Cluster("Deploy serverless alternativo (documentado em infra/, nao executado)"):
        cf = CloudFront("CloudFront")
        s3 = S3("S3 (SPA)")
        apigw = APIGateway("API Gateway")
        lmb = Lambda("Lambda (Mangum)")
        cf >> s3
        apigw >> lmb >> Edge(style="dashed") >> tidb
