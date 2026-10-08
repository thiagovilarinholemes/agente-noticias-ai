"""
Módulo responsável pela comunicação com o DynamoDB.

Neste projeto utilizamos o DynamoDB disponibilizado pelo
LocalStack durante o desenvolvimento local.

A aplicação pode posteriormente ser adaptada para utilizar
o DynamoDB real da AWS.
"""

import os

import boto3

from dotenv import load_dotenv


# Carrega as variáveis existentes no arquivo .env.
load_dotenv()


# Região utilizada pelo DynamoDB.
AWS_REGION = os.getenv(
    "AWS_REGION",
    "us-east-1"
)


# Endpoint do LocalStack.
DYNAMODB_ENDPOINT = os.getenv(
    "DYNAMODB_ENDPOINT",
    "http://localhost:4566"
)


# Nome da tabela.
DYNAMODB_TABLE = os.getenv(
    "DYNAMODB_TABLE",
    "artigos"
)


# Cria o recurso DynamoDB.
dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    endpoint_url=DYNAMODB_ENDPOINT,
    aws_access_key_id=os.getenv(
        "AWS_ACCESS_KEY_ID",
        "test"
    ),
    aws_secret_access_key=os.getenv(
        "AWS_SECRET_ACCESS_KEY",
        "test"
    ),
)


# Obtém uma referência para a tabela.
tabela = dynamodb.Table(
    DYNAMODB_TABLE
)


def salvar_artigo(artigo):
    """
    Salva um artigo no DynamoDB.

    Parameters
    ----------
    artigo : dict
        Dicionário contendo os dados da notícia.

    Returns
    -------
    dict
        Resposta retornada pelo DynamoDB.
    """

    return tabela.put_item(
        Item=artigo
    )


def consultar_artigos():
    """
    Consulta os artigos armazenados.

    Returns
    -------
    list
        Lista contendo os artigos encontrados.
    """

    resposta = tabela.scan()

    return resposta.get(
        "Items",
        []
    )


def buscar_artigo(id_artigo):
    """
    Busca um artigo específico pelo ID.

    Parameters
    ----------
    id_artigo : str
        Identificador do artigo.

    Returns
    -------
    dict
        Artigo encontrado.
    """

    resposta = tabela.get_item(
        Key={
            "id": id_artigo
        }
    )

    return resposta.get(
        "Item"
    )


def excluir_artigo(id_artigo):
    """
    Exclui um artigo pelo ID.

    Parameters
    ----------
    id_artigo : str
        Identificador do artigo.
    """

    return tabela.delete_item(
        Key={
            "id": id_artigo
        }
    )


def limpar_dados():
    """
    Remove todos os itens existentes na tabela.

    IMPORTANTE:
    Esta função NÃO exclui a tabela.

    Exemplo:

        Antes:
        tabela artigos
        ├── artigo 1
        ├── artigo 2
        └── artigo 3

        Depois:
        tabela artigos
        └── vazia
    """

    # Primeiro fazemos uma consulta para obter
    # todos os artigos existentes.
    resposta = tabela.scan()

    # Obtém os itens encontrados.
    itens = resposta.get(
        "Items",
        []
    )

    # Utiliza o batch_writer para realizar
    # várias exclusões de maneira eficiente.
    with tabela.batch_writer() as batch:

        for item in itens:

            # Obtém o ID utilizado como chave
            # primária da tabela.
            id_artigo = item.get(
                "id"
            )

            # Se existir um ID, remove o item.
            if id_artigo:

                batch.delete_item(
                    Key={
                        "id": id_artigo
                    }
                )

    return len(itens)


def apagar_tabela():
    """
    Exclui completamente a tabela DynamoDB.

    IMPORTANTE:
    Esta operação remove:

        - todos os artigos
        - a tabela
        - a estrutura da tabela

    A tabela precisará ser recriada posteriormente
    através do script criar_tabela.py.
    """

    # Exclui a tabela.
    resposta = tabela.delete()

    return resposta

