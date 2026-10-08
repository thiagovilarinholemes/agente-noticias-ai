"""
Serviço responsável por executar o Scrapy.

IMPORTANTE:
O Scrapy será executado em um processo separado.

Isso evita conflitos entre:
    Streamlit
    Twisted
    Reactor
    Threads
    Signals
"""

import json
import os
import subprocess
import sys
import tempfile


def executar_scraper(termo, quantidade):
    """
    Executa o Scrapy em um processo separado.

    Parameters
    ----------
    termo : str
        Nome ou frase que será pesquisada.

    quantidade : int
        Quantidade máxima de artigos.

    Returns
    -------
    list
        Lista de artigos encontrados.
    """

    # ---------------------------------------------------------
    # ARQUIVO TEMPORÁRIO
    # ---------------------------------------------------------

    # Criamos um arquivo temporário para o Scrapy
    # devolver os resultados para o Streamlit.
    arquivo_saida = tempfile.NamedTemporaryFile(
        suffix=".json",
        delete=False,
    )

    caminho_saida = arquivo_saida.name

    arquivo_saida.close()

    # ---------------------------------------------------------
    # CAMINHO DO RUNNER
    # ---------------------------------------------------------

    # Descobre a raiz do projeto.
    raiz_projeto = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )

    # Caminho do script responsável por executar o Scrapy.
    runner = os.path.join(
        raiz_projeto,
        "app",
        "scraper",
        "runner.py",
    )

    # ---------------------------------------------------------
    # COMANDO
    # ---------------------------------------------------------

    comando = [
        sys.executable,
        runner,
        "--termo",
        termo,
        "--quantidade",
        str(quantidade),
        "--saida",
        caminho_saida,
    ]

    try:

        # -----------------------------------------------------
        # EXECUTA O SCRAPY
        # -----------------------------------------------------

        processo = subprocess.run(
            comando,

            # Executa dentro da raiz do projeto
            cwd=raiz_projeto,

            # Captura saída e erros
            capture_output=True,

            # Trabalha com texto
            text=True,

            # Não levanta exceção automaticamente
            check=False,
        )

        # -----------------------------------------------------
        # VERIFICA ERRO
        # -----------------------------------------------------

        if processo.returncode != 0:

            raise RuntimeError(
                "Erro ao executar o Scrapy:\n\n"
                + processo.stderr
            )

        # -----------------------------------------------------
        # LÊ RESULTADOS
        # -----------------------------------------------------

        if not os.path.exists(caminho_saida):

            return []

        with open(
            caminho_saida,
            "r",
            encoding="utf-8",
        ) as arquivo:

            resultados = json.load(
                arquivo
            )

        return resultados

    finally:

        # -----------------------------------------------------
        # REMOVE ARQUIVO TEMPORÁRIO
        # -----------------------------------------------------

        if os.path.exists(caminho_saida):

            os.remove(
                caminho_saida
            )