"""
Pipeline responsável por processar os artigos.

O Pipeline:

1. Recebe o artigo do Spider.
2. Cria um ID único.
3. Salva o artigo no DynamoDB.
4. Mantém o artigo na lista de resultados.
"""

import uuid

from app.database.dynamodb import salvar_artigo


# Lista utilizada pelo runner para gerar o JSON.
resultados = []


class ArticlePipeline:
    """
    Pipeline responsável pelo armazenamento dos artigos.
    """

    @classmethod
    def from_crawler(cls, crawler):
        """
        Cria uma instância do Pipeline.
        """

        return cls()

    def process_item(self, item):
        """
        Processa cada artigo encontrado.
        """

        # Converte o Item do Scrapy
        # para um dicionário normal.
        artigo = dict(item)

        # Cria um ID único.
        artigo["id"] = str(
            uuid.uuid4()
        )

        # Salva o artigo no DynamoDB.
        salvar_artigo(
            artigo
        )

        # Adiciona também ao resultado.
        resultados.append(
            artigo
        )

        return item
