"""
===========================================================
ARTICLE SPIDER
===========================================================

Responsável por:

1. Pesquisar notícias no Google News através do RSS.
2. Obter a quantidade solicitada pelo usuário.
3. Acessar a URL original de cada notícia.
4. Extrair:
       - título
       - URL
       - fonte
       - autor
       - data de publicação
       - descrição
       - conteúdo completo
5. Evitar URLs duplicadas.
6. Enviar os artigos para o Pipeline.

IMPORTANTE
----------

O Google News RSS pode retornar dezenas ou centenas
de resultados.

Porém, se o usuário solicitar 5 artigos, queremos
processar somente 5 URLs.

Por isso existem dois controles:

    articles_scheduled
        Controla quantas URLs foram enviadas para
        processamento.

    articles_found
        Controla quantos artigos realmente foram
        processados.

Isso evita que o Scrapy agende 100 páginas quando
o usuário solicitou somente 5.
"""

import re

import scrapy


class ArticleSpider(scrapy.Spider):
    """
    Spider responsável pela coleta das notícias.
    """

    # Nome interno do Spider.
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

        Parameters
        ----------
        search_term : str
            Termo que será pesquisado.

        max_articles : int
            Quantidade máxima de artigos.
        """

        # Inicializa a classe pai do Scrapy.
        super().__init__(*args, **kwargs)

        # Guarda o termo pesquisado.
        self.search_term = search_term

        # Converte a quantidade para inteiro.
        self.max_articles = int(
            max_articles
        )

        # Quantidade de artigos realmente
        # processados.
        self.articles_found = 0

        # Quantidade de URLs que já foram
        # enviadas para o Scrapy.
        #
        # Esse contador é muito importante.
        #
        # O Scrapy trabalha de forma assíncrona.
        # Portanto, várias URLs podem ser agendadas
        # antes que as respostas sejam recebidas.
        self.articles_scheduled = 0

        # Conjunto utilizado para evitar
        # URLs duplicadas.
        self.urls_encontradas = set()

        # Exibe informações no log.
        self.logger.info(
            "=" * 70
        )

        self.logger.info(
            "SPIDER INICIADO"
        )

        self.logger.info(
            "TERMO: %s",
            self.search_term
        )

        self.logger.info(
            "QUANTIDADE SOLICITADA: %s",
            self.max_articles
        )

        self.logger.info(
            "=" * 70
        )

    async def start(self):
        """
        Inicia a pesquisa no Google News RSS.
        """

        # Verifica se o usuário informou
        # um termo de pesquisa.
        if not self.search_term:

            self.logger.error(
                "Nenhum termo de pesquisa foi informado."
            )

            return

        # Substitui os espaços por +.
        #
        # Exemplo:
        #
        # inteligência artificial
        #
        # vira:
        #
        # inteligência+artificial
        termo = self.search_term.replace(
            " ",
            "+"
        )

        # URL do Google News RSS.
        url = (
            "https://news.google.com/rss/search"
            f"?q={termo}"
            "&hl=pt-BR"
            "&gl=BR"
            "&ceid=BR:pt-419"
        )

        # User-Agent utilizado para identificar
        # o navegador para o servidor.
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
            "Pesquisando Google News RSS..."
        )

        # Faz a requisição para o RSS.
        yield scrapy.Request(
            url=url,
            callback=self.parse_rss,
            headers=headers,
            dont_filter=True
        )

    def parse_rss(self, response):
        """
        Processa os resultados do Google News RSS.

        IMPORTANTE:

        Aqui limitamos a quantidade de URLs
        ANTES de enviá-las para processamento.

        Se o usuário pediu 5:

            URL 1
            URL 2
            URL 3
            URL 4
            URL 5

        Depois disso paramos.
        """

        self.logger.info(
            "=" * 70
        )

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

        # Localiza todos os elementos <item>
        # existentes no RSS.
        itens = response.xpath(
            "//item"
        )

        self.logger.info(
            "RESULTADOS ENCONTRADOS NO RSS: %s",
            len(itens)
        )

        self.logger.info(
            "QUANTIDADE SOLICITADA: %s",
            self.max_articles
        )

        self.logger.info(
            "=" * 70
        )

        # Percorre os resultados.
        for item in itens:

            # ------------------------------------------------
            # CONTROLE PRINCIPAL
            # ------------------------------------------------
            #
            # Verificamos articles_scheduled e não somente
            # articles_found.
            #
            # Isso impede que 100 URLs sejam agendadas
            # enquanto aguardamos as respostas.
            if (
                self.articles_scheduled
                >= self.max_articles
            ):

                self.logger.info(
                    "Limite de URLs agendadas atingido."
                )

                break

            # ------------------------------------------------
            # TÍTULO
            # ------------------------------------------------

            titulo = item.xpath(
                "./title/text()"
            ).get()

            # Limpa espaços.
            if titulo:

                titulo = " ".join(
                    titulo.split()
                )

            # Se não existir título,
            # ignora o resultado.
            if not titulo:

                self.logger.warning(
                    "Resultado sem título. Ignorando."
                )

                continue

            # ------------------------------------------------
            # URL
            # ------------------------------------------------

            url = item.xpath(
                "./link/text()"
            ).get()

            # Remove espaços.
            if url:

                url = url.strip()

            # Se não existir URL,
            # ignora o resultado.
            if not url:

                self.logger.warning(
                    "Artigo sem URL. Ignorando."
                )

                continue

            # ------------------------------------------------
            # DUPLICIDADE
            # ------------------------------------------------

            if url in self.urls_encontradas:

                self.logger.info(
                    "URL duplicada ignorada."
                )

                continue

            # Adiciona a URL ao conjunto.
            self.urls_encontradas.add(
                url
            )

            # ------------------------------------------------
            # FONTE
            # ------------------------------------------------

            fonte = item.xpath(
                "./source/text()"
            ).get()

            if fonte:

                fonte = fonte.strip()

            else:

                fonte = ""

            # ------------------------------------------------
            # DATA
            # ------------------------------------------------

            data_publicacao = item.xpath(
                "./pubDate/text()"
            ).get()

            if data_publicacao:

                data_publicacao = (
                    data_publicacao.strip()
                )

            else:

                data_publicacao = ""

            # ------------------------------------------------
            # DESCRIÇÃO
            # ------------------------------------------------

            descricao = item.xpath(
                "./description/text()"
            ).get()

            if descricao:

                descricao = descricao.strip()

            else:

                descricao = ""

            # ------------------------------------------------
            # DADOS DO RSS
            # ------------------------------------------------

            dados_rss = {

                "titulo_rss": titulo,

                "url": url,

                "fonte": fonte,

                "data_publicacao": (
                    data_publicacao
                ),

                "descricao_rss": (
                    descricao
                ),

                "termo_busca": (
                    self.search_term
                )
            }

            # ------------------------------------------------
            # CONTROLE DE AGENDAMENTO
            # ------------------------------------------------
            #
            # IMPORTANTE:
            #
            # Incrementamos ANTES de executar
            # o yield scrapy.Request().
            #
            # Dessa forma, mesmo que o Scrapy ainda
            # não tenha recebido a resposta, a URL
            # já conta como uma URL agendada.
            self.articles_scheduled += 1

            self.logger.info(
                "URL agendada: %s/%s",
                self.articles_scheduled,
                self.max_articles
            )

            self.logger.info(
                "Título: %s",
                titulo
            )

            # ------------------------------------------------
            # ACESSA A PÁGINA ORIGINAL
            # ------------------------------------------------

            yield scrapy.Request(
                url=url,

                callback=self.parse_artigo,

                meta={
                    "dados_rss": dados_rss
                },

                # Permite que o Scrapy faça a requisição
                # mesmo que a URL já tenha aparecido
                # anteriormente.
                dont_filter=True
            )

        self.logger.info(
            "=" * 70
        )

        self.logger.info(
            "TOTAL DE URLs AGENDADAS: %s",
            self.articles_scheduled
        )

        self.logger.info(
            "TOTAL SOLICITADO: %s",
            self.max_articles
        )

        self.logger.info(
            "=" * 70
        )

    def parse_artigo(self, response):
        """
        Processa a página original da notícia.

        Tenta extrair:

            título
            descrição
            autor
            data
            conteúdo
        """

        # Recupera os dados obtidos pelo RSS.
        dados_rss = response.meta[
            "dados_rss"
        ]

        # ------------------------------------------------
        # TÍTULO
        # ------------------------------------------------

        titulo = (
            response.css(
                "meta[property='og:title']::attr(content)"
            ).get()
            or response.css(
                "h1::text"
            ).get()
            or dados_rss[
                "titulo_rss"
            ]
        )

        if titulo:

            titulo = " ".join(
                titulo.split()
            )

        # ------------------------------------------------
        # DESCRIÇÃO
        # ------------------------------------------------

        descricao = (
            response.css(
                "meta[name='description']::attr(content)"
            ).get()
            or response.css(
                "meta[property='og:description']::attr(content)"
            ).get()
            or dados_rss[
                "descricao_rss"
            ]
        )

        if descricao:

            descricao = " ".join(
                descricao.split()
            )

        # ------------------------------------------------
        # AUTOR
        # ------------------------------------------------

        autor = (
            response.css(
                "meta[name='author']::attr(content)"
            ).get()
            or response.css(
                "meta[property='article:author']::attr(content)"
            ).get()
            or ""
        )

        if autor:

            autor = " ".join(
                autor.split()
            )

        # ------------------------------------------------
        # DATA DE PUBLICAÇÃO
        # ------------------------------------------------

        data = (
            response.css(
                "meta[property='article:published_time']::attr(content)"
            ).get()
            or response.css(
                "meta[name='date']::attr(content)"
            ).get()
            or dados_rss[
                "data_publicacao"
            ]
        )

        if data:

            data = data.strip()

        # ------------------------------------------------
        # CONTEÚDO
        # ------------------------------------------------

        # Primeira tentativa:
        #
        # procura parágrafos dentro de <article>.
        paragrafos = response.css(
            "article p::text"
        ).getall()

        # Segunda tentativa:
        #
        # procura dentro de <main>.
        if not paragrafos:

            paragrafos = response.css(
                "main p::text"
            ).getall()

        # Terceira tentativa:
        #
        # procura qualquer <p>.
        if not paragrafos:

            paragrafos = response.css(
                "p::text"
            ).getall()

        # Lista que armazenará os parágrafos
        # considerados válidos.
        paragrafos_limpos = []

        # Processa cada parágrafo.
        for paragrafo in paragrafos:

            # Remove espaços desnecessários.
            texto = " ".join(
                paragrafo.split()
            )

            # Ignora textos muito pequenos.
            #
            # Isso ajuda a evitar:
            #
            # - menus
            # - botões
            # - publicidade
            # - links
            #
            if len(texto) >= 40:

                paragrafos_limpos.append(
                    texto
                )

        # Junta os parágrafos.
        conteudo = "\n\n".join(
            paragrafos_limpos
        )

        # Remove excesso de quebras de linha.
        conteudo = re.sub(
            r"\n{3,}",
            "\n\n",
            conteudo
        )

        # ------------------------------------------------
        # ARTIGO FINAL
        # ------------------------------------------------

        artigo = {

            "titulo": titulo,

            "url": response.url,

            "url_google_news": (
                dados_rss["url"]
            ),

            "fonte": (
                dados_rss["fonte"]
            ),

            "autor": autor,

            "data_publicacao": data,

            "descricao": descricao,

            "conteudo": conteudo,

            "termo_busca": (
                dados_rss[
                    "termo_busca"
                ]
            )
        }

        # Incrementa somente quando o artigo
        # realmente foi processado.
        self.articles_found += 1

        self.logger.info(
            "=" * 70
        )

        self.logger.info(
            "ARTIGO PROCESSADO: %s/%s",
            self.articles_found,
            self.max_articles
        )

        self.logger.info(
            "TÍTULO: %s",
            titulo
        )

        self.logger.info(
            "FONTE: %s",
            dados_rss["fonte"]
        )

        self.logger.info(
            "CONTEÚDO: %s caracteres",
            len(conteudo)
        )

        self.logger.info(
            "URL: %s",
            response.url
        )

        self.logger.info(
            "=" * 70
        )

        # Envia o artigo para o Pipeline.
        yield artigo

        # ------------------------------------------------
        # FINALIZAÇÃO
        # ------------------------------------------------

        if (
            self.articles_found
            >= self.max_articles
        ):

            self.logger.info(
                "=" * 70
            )

            self.logger.info(
                "QUANTIDADE SOLICITADA ATINGIDA."
            )

            self.logger.info(
                "ARTIGOS PROCESSADOS: %s",
                self.articles_found
            )

            self.logger.info(
                "URLs AGENDADAS: %s",
                self.articles_scheduled
            )

            self.logger.info(
                "=" * 70
            )
