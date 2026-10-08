"""
Interface Web do Agente de IA.

Tecnologia:
    Streamlit

Funções:

1. Pesquisar notícias.
2. Definir quantidade.
3. Executar o Scrapy.
4. Mostrar os artigos encontrados.
5. Consultar artigos armazenados no DynamoDB.
6. Excluir artigos.
"""

import streamlit as st
import pandas as pd

from app.services.scraper_service import (
    executar_scraper
)

from app.database.dynamodb import ( consultar_artigos, excluir_artigo, limpar_dados, apagar_tabela )


# -------------------------------------------------------
# CONFIGURAÇÃO
# -------------------------------------------------------

st.set_page_config(
    page_title="Agente de Notícias IA",
    page_icon="📰",
    layout="wide"
)


# -------------------------------------------------------
# TÍTULO
# -------------------------------------------------------

st.title(
    "📰 Agente de Notícias com IA"
)

st.caption(
    "Scrapy + Google News + DynamoDB + Streamlit"
)


# -------------------------------------------------------
# ABAS
# -------------------------------------------------------

aba_pesquisa, aba_consulta = st.tabs(
    [
        "🔎 Pesquisar notícias",
        "🗄️ Consultar DynamoDB"
    ]
)


# =======================================================
# ABA DE PESQUISA
# =======================================================

with aba_pesquisa:

    st.subheader(
        "Pesquisar artigos"
    )

    termo = st.text_input(
        "Nome ou frase",
        placeholder=(
            "Exemplo: inteligência artificial"
        )
    )

    quantidade = st.number_input(
        "Quantidade de artigos",
        min_value=1,
        max_value=100,
        value=5
    )

    pesquisar = st.button(
        "🔎 Pesquisar",
        use_container_width=True
    )

    if pesquisar:

        if not termo.strip():

            st.warning(
                "Digite um termo para pesquisar."
            )

        else:

            with st.spinner(
                "Pesquisando e extraindo artigos..."
            ):

                try:

                    artigos = executar_scraper(
                        termo,
                        quantidade
                    )

                    if not artigos:

                        st.warning(
                            "Nenhum artigo encontrado."
                        )

                    else:

                        st.success(
                            f"{len(artigos)} artigo(s) encontrado(s)."
                        )

                        for artigo in artigos:

                            with st.expander(
                                artigo.get(
                                    "titulo",
                                    "Sem título"
                                )
                            ):

                                st.write(
                                    "**Fonte:**",
                                    artigo.get(
                                        "fonte",
                                        ""
                                    )
                                )

                                st.write(
                                    "**Autor:**",
                                    artigo.get(
                                        "autor",
                                        ""
                                    )
                                )

                                st.write(
                                    "**Data:**",
                                    artigo.get(
                                        "data_publicacao",
                                        ""
                                    )
                                )

                                st.write(
                                    "**Descrição:**"
                                )

                                st.write(
                                    artigo.get(
                                        "descricao",
                                        ""
                                    )
                                )

                                st.write(
                                    "**Conteúdo:**"
                                )

                                conteudo = artigo.get(
                                    "conteudo",
                                    ""
                                )

                                if conteudo:

                                    st.write(
                                        conteudo
                                    )

                                else:

                                    st.info(
                                        "Conteúdo completo não encontrado."
                                    )

                                st.write(
                                    "**URL:**"
                                )

                                st.write(
                                    artigo.get(
                                        "url",
                                        ""
                                    )
                                )

                except Exception as erro:

                    st.error(
                        f"Erro: {erro}"
                    )


# =======================================================
# ABA DE CONSULTA
# =======================================================

with aba_consulta:

    st.subheader(
        "🗄️ Artigos armazenados"
    )

    # ---------------------------------------------------
    # CONSULTA DOS ARTIGOS
    # ---------------------------------------------------

    if st.button(
        "🔄 Atualizar consulta",
        use_container_width=True
    ):

        st.rerun()

    try:

        # Consulta os artigos no DynamoDB.
        artigos = consultar_artigos()

        # ------------------------------------------------
        # VERIFICA SE EXISTEM ARTIGOS
        # ------------------------------------------------

        if not artigos:

            st.info(
                "Nenhum artigo armazenado."
            )

        else:

            st.success(
                f"{len(artigos)} artigo(s) armazenado(s)."
            )

            # Cria um DataFrame com os artigos.
            df = pd.DataFrame(
                artigos
            )

            # Define as principais colunas
            # que serão exibidas.
            colunas = [
                "id",
                "titulo",
                "fonte",
                "autor",
                "data_publicacao",
                "termo_busca"
            ]

            # Mantém somente as colunas
            # que realmente existem.
            colunas_existentes = [
                coluna
                for coluna in colunas
                if coluna in df.columns
            ]

            # Exibe os artigos.
            st.dataframe(
                df[colunas_existentes],
                use_container_width=True,
                hide_index=True
            )

            # ------------------------------------------------
            # EXCLUIR UM ARTIGO
            # ------------------------------------------------

            st.divider()

            st.subheader(
                "🗑️ Excluir artigo"
            )

            # Obtém os IDs dos artigos.
            ids = [
                artigo["id"]
                for artigo in artigos
                if "id" in artigo
            ]

            if ids:

                # Permite selecionar um artigo.
                id_selecionado = st.selectbox(
                    "Selecione o ID do artigo",
                    ids
                )

                # Botão de exclusão individual.
                if st.button(
                    "🗑️ Excluir artigo selecionado",
                    use_container_width=True
                ):

                    excluir_artigo(
                        id_selecionado
                    )

                    st.success(
                        "Artigo excluído com sucesso."
                    )

                    st.rerun()

        # =================================================
        # ÁREA ADMINISTRATIVA
        # =================================================

        st.divider()

        st.subheader(
            "⚙️ Administração do banco"
        )

        st.warning(
            "As opções abaixo são operações destrutivas."
        )

        # -------------------------------------------------
        # LIMPAR DADOS
        # -------------------------------------------------

        st.markdown(
            "### 🧹 Limpar dados"
        )

        st.caption(
            "Remove todos os artigos, mas mantém a tabela DynamoDB."
        )

        if st.button(
            "🧹 Limpar todos os dados",
            use_container_width=True
        ):

            try:

                quantidade_removida = limpar_dados()

                st.success(
                    f"{quantidade_removida} artigo(s) removido(s)."
                )

                st.rerun()

            except Exception as erro:

                st.error(
                    f"Erro ao limpar os dados: {erro}"
                )

        # -------------------------------------------------
        # APAGAR TABELA
        # -------------------------------------------------

        st.markdown(
            "### 🗑️ Apagar tabela"
        )

        st.caption(
            "Exclui completamente a tabela DynamoDB e todos os seus dados."
        )

        # Checkbox de confirmação.
        confirmar_exclusao = st.checkbox(
            "Eu entendo que esta operação apagará a tabela inteira."
        )

        if confirmar_exclusao:

            if st.button(
                "🚨 APAGAR TABELA INTEIRA",
                use_container_width=True
            ):

                try:

                    apagar_tabela()

                    st.success(
                        "Tabela DynamoDB excluída com sucesso."
                    )

                    st.info(
                        "Para utilizar novamente o sistema, "
                        "recrie a tabela através do script "
                        "'scripts/criar_tabela.py'."
                    )

                except Exception as erro:

                    st.error(
                        f"Erro ao apagar a tabela: {erro}"
                    )

    except Exception as erro:

        st.error(
            f"Erro ao consultar DynamoDB: {erro}"
        )

