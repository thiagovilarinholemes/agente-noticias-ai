"""
Spider responsável por pesquisar artigos na internet.

Fluxo do Spider:

1. Recebe o termo pesquisado pelo usuário.
2. Recebe a quantidade de artigos desejada.
3. Acessa o Google News.
4. Localiza os resultados da pesquisa.
5. Extrai título e URL dos resultados.
6. Evita artigos duplicados.
7. Envia cada artigo para o ArticlePipeline.

O Spider é executado pelo runner.py.
O runner.py, por sua vez, é executado em um
processo separado do Streamlit.
"""


# ============================================================
# IMPORTAÇÃO DO SCRAPY
# ============================================================

import scrapy


# ============================================================
# CLASSE PRINCIPAL DO SPIDER
# ============================================================

class ArticleSpider(scrapy.Spider):
    """
    Spider responsável por pesquisar artigos.

    O Scrapy utiliza esta classe para controlar:

    - início da pesquisa;
    - requisições HTTP;
    - processamento das respostas;
    - geração dos itens.
    """

    # --------------------------------------------------------
    # Nome interno do Spider.
    #
    # Esse nome identifica o Spider dentro do Scrapy.
    # --------------------------------------------------------

    name = "article_spider"


    # ========================================================
    # CONSTRUTOR
    # ========================================================

    def __init__(
        self,
        search_term=None,
        max_articles=10,
        *args,
        **kwargs
    ):
        """
        Inicializa o Spider.

        Parâmetros:

        search_term:
            Termo ou frase que será pesquisado.

        max_articles:
            Quantidade máxima de artigos que queremos
            encontrar.

        Exemplo:

            search_term="inteligência artificial"
            max_articles=5
        """

        # ----------------------------------------------------
        # Chama o construtor da classe pai.
        #
        # Isso permite que o Scrapy faça sua inicialização
        # normalmente.
        # ----------------------------------------------------

        super().__init__(*args, **kwargs)


        # ----------------------------------------------------
        # Armazena o termo de pesquisa.
        # ----------------------------------------------------

        self.search_term = search_term


        # ----------------------------------------------------
        # Converte a quantidade de artigos para inteiro.
        #
        # Isso garante que:
        #
        # "3"
        #
        # seja convertido para:
        #
        # 3
        # ----------------------------------------------------

        self.max_articles = int(max_articles)


        # ----------------------------------------------------
        # Contador de artigos encontrados.
        #
        # Começa em zero.
        # ----------------------------------------------------

        self.articles_found = 0


        # ----------------------------------------------------
        # Conjunto utilizado para armazenar URLs já encontradas.
        #
        # O set() permite verificar rapidamente se uma URL
        # já foi processada.
        # ----------------------------------------------------

        self.urls_encontradas = set()


        # ----------------------------------------------------
        # Exibe informações no log do Scrapy.
        # ----------------------------------------------------

        self.logger.info(
            "Termo recebido: %s",
            self.search_term
        )

        self.logger.info(
            "Quantidade solicitada: %s",
            self.max_articles
        )


    # ========================================================
    # MÉTODO START
    # ========================================================

    async def start(self):
        """
        Inicia a primeira requisição do Spider.

        IMPORTANTE:

        No Scrapy 2.18, o método start precisa ser
        um gerador assíncrono.

        Por isso utilizamos:

            async def start()

        e posteriormente:

            yield scrapy.Request(...)
        """


        # ----------------------------------------------------
        # Verifica se o usuário informou algum termo.
        # ----------------------------------------------------

        if not self.search_term:

            self.logger.error(
                "Nenhum termo de pesquisa foi informado."
            )

            return


        # ----------------------------------------------------
        # Converte espaços para o formato utilizado na URL.
        #
        # Exemplo:
        #
        # inteligência artificial
        #
        # será enviado como:
        #
        # inteligência+artificial
        # ----------------------------------------------------

        termo = self.search_term.replace(
            " ",
            "+"
        )


        # ----------------------------------------------------
        # Monta a URL de pesquisa do Google News.
        #
        # q:
        # termo pesquisado
        #
        # hl:
        # idioma da interface
        #
        # gl:
        # país
        #
        # ceid:
        # configuração regional
        # ----------------------------------------------------

        url = (
            "https://news.google.com/search"
            f"?q={termo}"
            "&hl=pt-BR"
            "&gl=BR"
            "&ceid=BR:pt-419"
        )


        # ----------------------------------------------------
        # Define um User-Agent semelhante ao de um navegador.
        #
        # Isso ajuda a evitar que o servidor trate a requisição
        # como um cliente HTTP muito simples.
        # ----------------------------------------------------

        headers = {

            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )

        }


        # ----------------------------------------------------
        # Exibe informações sobre a pesquisa.
        # ----------------------------------------------------

        self.logger.info(
            "=" * 60
        )

        self.logger.info(
            "INICIANDO PESQUISA"
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
            "URL: %s",
            url
        )

        self.logger.info(
            "=" * 60
        )


        # ----------------------------------------------------
        # Envia a requisição para o Google News.
        #
        # callback:
        # método que será chamado quando a resposta chegar.
        #
        # dont_filter=True:
        # permite que essa requisição seja executada mesmo
        # que o Scrapy considere a URL já conhecida.
        # ----------------------------------------------------

        yield scrapy.Request(

            url=url,

            callback=self.parse,

            headers=headers,

            dont_filter=True,

        )


    # ========================================================
    # MÉTODO PARSE
    # ========================================================

    def parse(self, response):
        """
        Processa a resposta recebida do Google News.

        O Google News atualmente pode representar seus
        resultados através de links no formato:

            ./read/...

        Portanto, não dependemos de elementos <article>.
        """

        # ----------------------------------------------------
        # Informações da resposta.
        # ----------------------------------------------------

        self.logger.info(
            "=" * 60
        )

        self.logger.info(
            "RESPOSTA RECEBIDA"
        )

        self.logger.info(
            "Status HTTP: %s",
            response.status
        )

        self.logger.info(
            "URL: %s",
            response.url
        )

        self.logger.info(
            "Tamanho HTML: %s bytes",
            len(response.text)
        )

        self.logger.info(
            "=" * 60
        )


        # ====================================================
        # LOCALIZAÇÃO DOS RESULTADOS
        # ====================================================

        # ----------------------------------------------------
        # Procuramos links que começam com:
        #
        # ./read/
        #
        # Esses links representam resultados de notícias
        # dentro do Google News.
        # ----------------------------------------------------

        links_resultados = response.css(
            'a[href^="./read/"]'
        )


        # ----------------------------------------------------
        # Exibe a quantidade encontrada.
        # ----------------------------------------------------

        self.logger.info(
            "RESULTADOS ENCONTRADOS: %s",
            len(links_resultados)
        )


        # ----------------------------------------------------
        # Se nenhum resultado foi encontrado, encerra.
        # ----------------------------------------------------

        if not links_resultados:

            self.logger.warning(
                "Nenhum resultado de notícia foi encontrado."
            )

            return


        # ====================================================
        # PROCESSAMENTO DOS RESULTADOS
        # ====================================================

        for resultado in links_resultados:


            # ------------------------------------------------
            # Verifica se já atingimos a quantidade solicitada.
            # ------------------------------------------------

            if self.articles_found >= self.max_articles:

                self.logger.info(
                    "Quantidade máxima de artigos atingida."
                )

                break


            # ------------------------------------------------
            # Obtém o endereço armazenado no atributo href.
            # ------------------------------------------------

            link = resultado.attrib.get(
                "href"
            )


            # ------------------------------------------------
            # Se não existir URL, ignora o resultado.
            # ------------------------------------------------

            if not link:

                continue


            # ------------------------------------------------
            # Converte a URL relativa para absoluta.
            #
            # Exemplo:
            #
            # ./read/ABC123
            #
            # torna-se:
            #
            # https://news.google.com/read/ABC123
            # ------------------------------------------------

            link = response.urljoin(
                link
            )


            # ------------------------------------------------
            # Verifica se a URL já foi encontrada.
            # ------------------------------------------------

            if link in self.urls_encontradas:

                continue


            # ------------------------------------------------
            # Guarda a URL no conjunto de URLs processadas.
            # ------------------------------------------------

            self.urls_encontradas.add(
                link
            )


            # =================================================
            # EXTRAÇÃO DO TÍTULO
            # =================================================

            # ------------------------------------------------
            # Primeiro tentamos pegar o primeiro texto
            # existente dentro do link.
            # ------------------------------------------------

            # Obtém todo o HTML do elemento <a>.
            html_resultado = resultado.get()

            self.logger.info("=" * 80)
            self.logger.info("HTML DO RESULTADO:")
            self.logger.info(html_resultado[:2000])
            self.logger.info("=" * 80)

            # Tenta obter qualquer texto dentro do elemento.
            textos = resultado.xpath(
                ".//text()"
            ).getall()

            self.logger.info(
                "TEXTOS ENCONTRADOS: %s",
                textos
            )

            titulo = " ".join(
                texto.strip()
                for texto in textos
                if texto.strip()
            )



            # ------------------------------------------------
            # Se não encontrou através do CSS,
            # tentamos através do XPath.
            # ------------------------------------------------

            if not titulo:

                titulo = resultado.xpath(
                    ".//text()"
                ).get()


            # ------------------------------------------------
            # Limpa espaços extras.
            #
            # Exemplo:
            #
            # " Inteligência   Artificial "
            #
            # vira:
            #
            # "Inteligência Artificial"
            # ------------------------------------------------

            if titulo:

                titulo = " ".join(
                    titulo.split()
                )


            # ------------------------------------------------
            # Se o título estiver vazio, ignoramos o resultado.
            # ------------------------------------------------

            if not titulo:

                self.logger.warning(
                    "Resultado encontrado sem título."
                )

                continue


            # =================================================
            # CRIAÇÃO DO ITEM
            # =================================================

            item = {

                # --------------------------------------------
                # Título da notícia.
                # --------------------------------------------

                "titulo": titulo,


                # --------------------------------------------
                # URL do resultado no Google News.
                # --------------------------------------------

                "url": link,


                # --------------------------------------------
                # Fonte.
                #
                # Nesta primeira etapa informamos Google News.
                #
                # Posteriormente podemos acessar a matéria
                # original e descobrir a fonte real.
                # --------------------------------------------

                "fonte": "Google News",


                # --------------------------------------------
                # Data da publicação.
                #
                # Ainda não estamos acessando a página original.
                # --------------------------------------------

                "data_publicacao": "Não informada",


                # --------------------------------------------
                # Descrição.
                #
                # Será preenchida em uma etapa posterior.
                # --------------------------------------------

                "descricao": "",


                # --------------------------------------------
                # Termo utilizado na pesquisa.
                # --------------------------------------------

                "termo_busca": self.search_term,

            }


            # =================================================
            # LOG DO ARTIGO
            # =================================================

            self.logger.info(
                "=" * 60
            )

            self.logger.info(
                "ARTIGO ENCONTRADO #%s",
                self.articles_found + 1
            )

            self.logger.info(
                "TÍTULO: %s",
                titulo
            )

            self.logger.info(
                "URL: %s",
                link
            )

            self.logger.info(
                "=" * 60
            )


            # =================================================
            # ENVIO DO ITEM PARA O PIPELINE
            # =================================================

            # ------------------------------------------------
            # O yield entrega o item para o Scrapy.
            #
            # O ArticlePipeline receberá esse item e poderá
            # armazená-lo na lista resultados.
            # ------------------------------------------------

            yield item


            # ------------------------------------------------
            # Incrementa o contador.
            # ------------------------------------------------

            self.articles_found += 1


        # ====================================================
        # FINALIZAÇÃO
        # ====================================================

        self.logger.info(
            "=" * 60
        )

        self.logger.info(
            "TOTAL DE ARTIGOS GERADOS: %s",
            self.articles_found
        )

        self.logger.info(
            "TOTAL DE URLs ÚNICAS: %s",
            len(self.urls_encontradas)
        )

        self.logger.info(
            "=" * 60
        )
