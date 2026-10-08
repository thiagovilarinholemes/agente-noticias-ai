"""
Runner responsável por executar o Scrapy.

O Runner é executado em um processo separado
do Streamlit.
"""

import argparse
import json
import os
import sys


# ============================================================
# LOCALIZA A RAIZ DO PROJETO
# ============================================================

DIRETORIO_SCRAPER = os.path.dirname(
    os.path.abspath(__file__)
)

DIRETORIO_APP = os.path.dirname(
    DIRETORIO_SCRAPER
)

RAIZ_PROJETO = os.path.dirname(
    DIRETORIO_APP
)


# ============================================================
# CONFIGURA O PYTHON PATH
# ============================================================

if RAIZ_PROJETO not in sys.path:

    sys.path.insert(
        0,
        RAIZ_PROJETO
    )


# ============================================================
# IMPORTA SCRAPY
# ============================================================

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings


# ============================================================
# IMPORTA O SPIDER
# ============================================================

from app.scraper.article_spider import ArticleSpider


# ============================================================
# IMPORTA O PIPELINE
# ============================================================

from app.scraper.pipeline import resultados


def main():
    """
    Função principal do Runner.
    """

    # Cria o parser.
    parser = argparse.ArgumentParser(
        description="Executa o scraper de artigos."
    )

    # Termo da pesquisa.
    parser.add_argument(
        "--termo",
        required=True,
        help="Termo que será pesquisado."
    )

    # Quantidade de artigos.
    parser.add_argument(
        "--quantidade",
        required=True,
        type=int,
        help="Quantidade de artigos."
    )

    # Arquivo de saída.
    parser.add_argument(
        "--saida",
        required=True,
        help="Arquivo JSON de saída."
    )

    # Processa os argumentos.
    args = parser.parse_args()


    # ========================================================
    # CONFIGURAÇÕES DO SCRAPY
    # ========================================================

    settings = Settings()

    # Ativa logs.
    settings.set(
        "LOG_ENABLED",
        True
    )

    settings.set(
        "LOG_LEVEL",
        "INFO"
    )

    # Configura o Pipeline.
    settings.set(
        "ITEM_PIPELINES",
        {
            "app.scraper.pipeline.ArticlePipeline": 100
        }
    )


    # ========================================================
    # CRIA O PROCESSO SCRAPY
    # ========================================================

    processo = CrawlerProcess(
        settings=settings
    )


    # ========================================================
    # EXECUTA O SPIDER
    # ========================================================

    processo.crawl(
        ArticleSpider,
        search_term=args.termo,
        max_articles=args.quantidade
    )


    # ========================================================
    # INICIA O SCRAPY
    # ========================================================

    processo.start()


    # ========================================================
    # SALVA OS RESULTADOS
    # ========================================================

    with open(
        args.saida,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            resultados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


    # ========================================================
    # MOSTRA O RESULTADO
    # ========================================================

    print(
        f"\nArtigos encontrados: {len(resultados)}"
    )

    print(
        f"Arquivo gerado: {args.saida}"
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    main()