"""
Spider responsável por pesquisar e extrair notícias.

Fluxo:

1. Pesquisa o termo no Google News RSS.
2. Obtém as notícias encontradas.
3. Obtém a URL original de cada notícia.
4. Acessa a página original.
5. Tenta identificar título, descrição, autor e conteúdo.
6. Envia o artigo completo para o Pipeline.
"""

import json
import re

import scrapy


class ArticleSpider(scrapy.Spider):
    """
    Spider responsável pela coleta das notícias.
    """

    name = "article_spider"

    def __init__(
        self,
        search_term=None,
        max_articles=10,
        *args,
        **kwargs
    ):
        """
        Inicializa o Spider.
        """

        super().__init__(*args, **kwargs)

        # Termo utilizado na pesquisa.
        self.search_term = search_term

        # Quantidade máxima solicitada.
        self.max_articles = int(
            max_articles
        )

        # Contador de artigos.
        self.articles_found = 0

        # Guarda URLs já processadas.
        self.urls_encontradas = set()

    async def start(self):
        """
        Inicia a pesquisa no Google News RSS.
        """

        if not self.search_term:

            self.logger.error(
                "Nenhum termo de pesquisa foi informado."
            )

            return

        # Substitui espaços por +.
        termo = self.search_term.replace(
            " ",
            "+"
        )

        # URL do RSS do Google News.
        url = (
            "https://news.google.com/rss/search"
            f"?q={termo}"
            "&hl=pt-BR"
            "&gl=BR"
            "&ceid=BR:pt-419"
        )

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        self.logger.info(
            "Pesquisando: %s",
            self.search_term
        )

        yield scrapy.Request(
            url=url,
            callback=self.parse_rss,
            headers=headers,
            dont_filter=True
        )

    def parse_rss(self, response):
        """
        Processa o RSS do Google News.
        """

        itens = response.xpath(
            "//item"
        )

        self.logger.info(
            "Notícias encontradas no RSS: %s",
            len(itens)
        )

        for item in itens:

            # Interrompe quando atingir
            # a quantidade solicitada.
            if (
                self.articles_found
                >= self.max_articles
            ):
                break

            # Obtém o título.
            titulo = item.xpath(
                "./title/text()"
            ).get()

            if titulo:
                titulo = " ".join(
                    titulo.split()
                )

            # Obtém a URL.
            url = item.xpath(
                "./link/text()"
            ).get()

            if url:
                url = url.strip()

            # Valida os dados.
            if not titulo or not url:

                continue

            # Evita duplicidade.
            if url in self.urls_encontradas:

                continue

            self.urls_encontradas.add(
                url
            )

            # Obtém fonte.
            fonte = item.xpath(
                "./source/text()"
            ).get()

            if fonte:
                fonte = fonte.strip()

            # Obtém data.
            data_publicacao = item.xpath(
                "./pubDate/text()"
            ).get()

            if data_publicacao:
                data_publicacao = (
                    data_publicacao.strip()
                )

            # Obtém descrição.
            descricao = item.xpath(
                "./description/text()"
            ).get()

            if descricao:
                descricao = descricao.strip()

            # Guarda os dados do RSS.
            dados_rss = {
                "titulo_rss": titulo,
                "url": url,
                "fonte": fonte or "",
                "data_publicacao": (
                    data_publicacao or ""
                ),
                "descricao_rss": (
                    descricao or ""
                ),
                "termo_busca": (
                    self.search_term
                )
            }

            # Acessa a página original.
            yield scrapy.Request(
                url=url,
                callback=self.parse_artigo,
                meta={
                    "dados_rss": dados_rss
                },
                dont_filter=True
            )

    def parse_artigo(self, response):
        """
        Extrai o conteúdo da página original.
        """

        dados_rss = response.meta[
            "dados_rss"
        ]

        # -------------------------------------------------
        # TÍTULO
        # -------------------------------------------------

        titulo = (
            response.css(
                "meta[property='og:title']::attr(content)"
            ).get()
            or response.css(
                "h1::text"
            ).get()
            or dados_rss["titulo_rss"]
        )

        if titulo:
            titulo = " ".join(
                titulo.split()
            )

        # -------------------------------------------------
        # DESCRIÇÃO
        # -------------------------------------------------

        descricao = (
            response.css(
                "meta[name='description']::attr(content)"
            ).get()
            or response.css(
                "meta[property='og:description']::attr(content)"
            ).get()
            or dados_rss["descricao_rss"]
        )

        if descricao:
            descricao = " ".join(
                descricao.split()
            )

        # -------------------------------------------------
        # AUTOR
        # -------------------------------------------------

        autor = (
            response.css(
                "meta[name='author']::attr(content)"
            ).get()
            or response.css(
                "meta[property='article:author']::attr(content)"
            ).get()
            or ""
        )

        # -------------------------------------------------
        # DATA
        # -------------------------------------------------

        data = (
            response.css(
                "meta[property='article:published_time']::attr(content)"
            ).get()
            or response.css(
                "meta[name='date']::attr(content)"
            ).get()
            or dados_rss["data_publicacao"]
        )

        # -------------------------------------------------
        # CONTEÚDO
        # -------------------------------------------------

        paragrafos = response.css(
            "article p::text"
        ).getall()

        # Alguns sites não utilizam <article>.
        if not paragrafos:

            paragrafos = response.css(
                "main p::text"
            ).getall()

        # Última tentativa.
        if not paragrafos:

            paragrafos = response.css(
                "p::text"
            ).getall()

        # Limpa os parágrafos.
        paragrafos_limpos = []

        for paragrafo in paragrafos:

            texto = " ".join(
                paragrafo.split()
            )

            if len(texto) >= 40:

                paragrafos_limpos.append(
                    texto
                )

        # Junta todos os parágrafos.
        conteudo = "\n\n".join(
            paragrafos_limpos
        )

        # Remove espaços excessivos.
        conteudo = re.sub(
            r"\n{3,}",
            "\n\n",
            conteudo
        )

        # -------------------------------------------------
        # MONTA O ARTIGO FINAL
        # -------------------------------------------------

        artigo = {
            "titulo": titulo,
            "url": response.url,
            "url_google_news": dados_rss["url"],
            "fonte": dados_rss["fonte"],
            "autor": autor,
            "data_publicacao": data,
            "descricao": descricao,
            "conteudo": conteudo,
            "termo_busca": dados_rss[
                "termo_busca"
            ]
        }

        self.articles_found += 1

        self.logger.info(
            "Artigo %s/%s extraído: %s",
            self.articles_found,
            self.max_articles,
            titulo
        )

        yield artigo

        # Fecha o Spider quando atingir
        # a quantidade solicitada.
        if (
            self.articles_found
            >= self.max_articles
        ):
            self.logger.info(
                "Quantidade solicitada atingida."
            )
