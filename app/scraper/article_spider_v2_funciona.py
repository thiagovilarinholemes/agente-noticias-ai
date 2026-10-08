"""
Spider responsável por pesquisar artigos no Google News.

Nesta versão utilizamos o RSS do Google News.

Por que utilizar RSS?

A página HTML do Google News possui uma estrutura dinâmica.
Os links podem existir no HTML, mas os títulos podem estar
em elementos diferentes ou serem manipulados pelo JavaScript.

O RSS fornece os resultados em uma estrutura XML muito mais
estável.

Fluxo:

1. Recebe o termo pesquisado.
2. Recebe a quantidade de artigos desejada.
3. Acessa o RSS do Google News.
4. Extrai os artigos.
5. Extrai título, URL, fonte, data e descrição.
6. Evita URLs duplicadas.
7. Envia os artigos para o Pipeline.
"""

import scrapy


class ArticleSpider(scrapy.Spider):
    """
    Spider responsável por pesquisar artigos.
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

        Parâmetros
        ----------
        search_term : str
            Termo ou frase que será pesquisado.

        max_articles : int
            Quantidade máxima de artigos desejada.
        """

        super().__init__(*args, **kwargs)

        # Guarda o termo pesquisado.
        self.search_term = search_term

        # Converte a quantidade para inteiro.
        self.max_articles = int(max_articles)

        # Contador de artigos encontrados.
        self.articles_found = 0

        # Conjunto utilizado para evitar URLs duplicadas.
        self.urls_encontradas = set()

        self.logger.info(
            "Termo recebido: %s",
            self.search_term
        )

        self.logger.info(
            "Quantidade solicitada: %s",
            self.max_articles
        )

    async def start(self):
        """
        Inicia o Spider.

        O Scrapy 2.18 exige que o método start()
        seja um gerador assíncrono.
        """

        # Verifica se o usuário informou um termo.
        if not self.search_term:

            self.logger.error(
                "Nenhum termo de pesquisa foi informado."
            )

            return

        # Codifica o termo para ser utilizado na URL.
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

        # User-Agent utilizado na requisição.
        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        self.logger.info("=" * 70)

        self.logger.info(
            "INICIANDO PESQUISA VIA RSS"
        )

        self.logger.info(
            "TERMO: %s",
            self.search_term
        )

        self.logger.info(
            "QUANTIDADE: %s",
            self.max_articles
        )

        self.logger.info(
            "URL RSS: %s",
            url
        )

        self.logger.info("=" * 70)

        # Faz a requisição para o RSS.
        yield scrapy.Request(
            url=url,
            callback=self.parse,
            headers=headers,
            dont_filter=True,
        )

    def parse(self, response):
        """
        Processa o XML retornado pelo RSS.

        Cada notícia é representada por um elemento <item>.
        """

        self.logger.info("=" * 70)

        self.logger.info(
            "RSS RECEBIDO"
        )

        self.logger.info(
            "STATUS HTTP: %s",
            response.status
        )

        self.logger.info(
            "TAMANHO DA RESPOSTA: %s bytes",
            len(response.body)
        )

        self.logger.info("=" * 70)

        # Localiza todos os elementos <item>.
        itens = response.xpath(
            "//item"
        )

        self.logger.info(
            "ITENS ENCONTRADOS NO RSS: %s",
            len(itens)
        )

        # Percorre os resultados.
        for item in itens:

            # Verifica se já atingimos a quantidade solicitada.
            if self.articles_found >= self.max_articles:

                self.logger.info(
                    "Quantidade máxima de artigos atingida."
                )

                break

            # --------------------------------------------------
            # TÍTULO
            # --------------------------------------------------

            titulo = item.xpath(
                "./title/text()"
            ).get()

            # Remove espaços desnecessários.
            if titulo:

                titulo = " ".join(
                    titulo.split()
                )

            # Se não encontrou título, ignora o resultado.
            if not titulo:

                self.logger.warning(
                    "Resultado encontrado sem título."
                )

                continue

            # --------------------------------------------------
            # URL
            # --------------------------------------------------

            url = item.xpath(
                "./link/text()"
            ).get()

            # Remove espaços.
            if url:

                url = url.strip()

            # Verifica se encontrou URL.
            if not url:

                self.logger.warning(
                    "Artigo sem URL: %s",
                    titulo
                )

                continue

            # Evita artigos duplicados.
            if url in self.urls_encontradas:

                self.logger.info(
                    "URL duplicada ignorada: %s",
                    url
                )

                continue

            # Registra a URL.
            self.urls_encontradas.add(url)

            # --------------------------------------------------
            # FONTE
            # --------------------------------------------------

            fonte = item.xpath(
                "./source/text()"
            ).get()

            if fonte:

                fonte = fonte.strip()

            else:

                fonte = "Não informada"

            # --------------------------------------------------
            # DATA DE PUBLICAÇÃO
            # --------------------------------------------------

            data_publicacao = item.xpath(
                "./pubDate/text()"
            ).get()

            if data_publicacao:

                data_publicacao = data_publicacao.strip()

            else:

                data_publicacao = "Não informada"

            # --------------------------------------------------
            # DESCRIÇÃO
            # --------------------------------------------------

            descricao = item.xpath(
                "./description/text()"
            ).get()

            if descricao:

                descricao = descricao.strip()

            else:

                descricao = ""

            # --------------------------------------------------
            # ITEM
            # --------------------------------------------------

            artigo = {
                "titulo": titulo,
                "url": url,
                "fonte": fonte,
                "data_publicacao": data_publicacao,
                "descricao": descricao,
                "termo_busca": self.search_term,
            }

            # --------------------------------------------------
            # LOG
            # --------------------------------------------------

            self.logger.info("=" * 70)

            self.logger.info(
                "ARTIGO ENCONTRADO #%s",
                self.articles_found + 1
            )

            self.logger.info(
                "TÍTULO: %s",
                titulo
            )

            self.logger.info(
                "FONTE: %s",
                fonte
            )

            self.logger.info(
                "DATA: %s",
                data_publicacao
            )

            self.logger.info(
                "URL: %s",
                url
            )

            self.logger.info("=" * 70)

            # Envia o artigo para o Pipeline.
            yield artigo

            # Incrementa o contador.
            self.articles_found += 1

        # ------------------------------------------------------
        # FINALIZAÇÃO
        # ------------------------------------------------------

        self.logger.info("=" * 70)

        self.logger.info(
            "TOTAL DE ARTIGOS GERADOS: %s",
            self.articles_found
        )

        self.logger.info(
            "TOTAL DE URLs ÚNICAS: %s",
            len(self.urls_encontradas)
        )

        self.logger.info("=" * 70)
