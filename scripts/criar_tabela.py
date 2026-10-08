"""
Cria a tabela artigos no DynamoDB do LocalStack.
"""

import os

import boto3

from dotenv import load_dotenv


# Carrega o arquivo .env.
load_dotenv()


# Cria conexão com DynamoDB.
dynamodb = boto3.resource(
    "dynamodb",
    region_name=os.getenv(
        "AWS_REGION",
        "us-east-1"
    ),
    endpoint_url=os.getenv(
        "DYNAMODB_ENDPOINT",
        "http://localhost:4566"
    ),
    aws_access_key_id=os.getenv(
        "AWS_ACCESS_KEY_ID",
        "test"
    ),
    aws_secret_access_key=os.getenv(
        "AWS_SECRET_ACCESS_KEY",
        "test"
    )
)


# Nome da tabela.
nome_tabela = os.getenv(
    "DYNAMODB_TABLE",
    "artigos"
)


# Verifica se a tabela já existe.
tabelas = dynamodb.meta.client.list_tables(
    Limit=100
)


if nome_tabela in tabelas["TableNames"]:

    print(
        f"A tabela '{nome_tabela}' já existe."
    )

else:

    # Cria a tabela.
    tabela = dynamodb.create_table(
        TableName=nome_tabela,

        KeySchema=[
            {
                "AttributeName": "id",
                "KeyType": "HASH"
            }
        ],

        AttributeDefinitions=[
            {
                "AttributeName": "id",
                "AttributeType": "S"
            }
        ],

        BillingMode="PAY_PER_REQUEST"
    )

    # Aguarda a criação.
    tabela.wait_until_exists()

    print(
        f"Tabela '{nome_tabela}' criada com sucesso."
    )
