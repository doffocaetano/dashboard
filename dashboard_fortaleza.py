import pandas as pd
import streamlit as st
import plotly.express as px
import os # Importa o módulo os para verificar a existência do arquivo

# ==============================================================================
# ATENÇÃO CRÍTICA:
# VOCÊ DEVE SUBSTITUIR 'Tipo de Voo' ABAIXO
# PELO NOME EXATO DA COLUNA NO SEU ARQUIVO CSV PARA O 'TIPO DE VOO'.
# CERTIFIQUE-SE DE QUE ESTEJA ENTRE ASPAS SIMPLES!
# EX: SE NO SEU CSV A COLUNA É 'TIPO_VOO', MUDE PARA:
# COLUNA_TIPO_DE_VOO = 'TIPO_VOO'
# ==============================================================================
COLUNA_TIPO_DE_VOO = 'Tipo de Voo' # <<<< SUBSTITUA APENAS O TEXTO ENTRE ASPAS AQUI!

# --- Verificação de tipo da constante COLUNA_TIPO_DE_VOO (DEBUG) ---
if not isinstance(COLUNA_TIPO_DE_VOO, str):
    st.error("❌ ERRO GRAVE: A variável COLUNA_TIPO_DE_VOO não está definida como um texto (string).")
    st.error("Por favor, certifique-se de que está entre aspas simples, por exemplo: COLUNA_TIPO_DE_VOO = 'Meu Tipo de Voo'")
    st.stop() # Interrompe a execução para que você possa corrigir

# --- 1. Configurações Iniciais e Mapeamento de Meses ---

# Define um mapeamento de nomes de meses para números para garantir a ordenação correta nos gráficos
month_to_num = {
    'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4, 'Maio': 5, 'Junho': 6,
    'Julho': 7, 'Agosto': 8, 'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
}
# Define a ordem dos meses para filtros e gráficos
month_order = list(month_to_num.keys())

# Configuração da página Streamlit
st.set_page_config(
    page_title="Dashboard de Tráfego Aéreo - Fortaleza", # Título que aparece na aba do navegador
    layout="wide", # Define o layout da página como 'wide' para usar toda a largura disponível
    initial_sidebar_state="expanded" # Faz com que a barra lateral comece expandida
)

st.title("✈️ Dashboard Interativo de Tráfego Aéreo - Fortaleza")
st.markdown("Este dashboard apresenta uma análise do tráfego turístico aéreo no Aeroporto de Fortaleza, Ceará.")

# --- 2. Carregamento dos Dados ---
# Tenta carregar o arquivo CSV. Se o arquivo não for encontrado, usa dados de exemplo para demonstração.
file_path = "TABELA ATUALIZADA.xlsx - Planilha1.csv"
df = pd.DataFrame() # Inicializa df para evitar erro se nenhum dado for carregado
try:
    # Carrega o arquivo CSV para um DataFrame pandas
    df = pd.read_csv(file_path)
    st.success(f"Dados carregados com sucesso de '{file_path}'!")
    st.info("⚠️ **Importante:** Este dashboard espera as colunas 'Ano', 'Mês', 'Passageiros' e a coluna de Tipo de Voo (definida acima). Verifique se seu CSV as possui.")
    
    # --- LINHA PARA DEBUGAR: MOSTRAR NOMES DAS COLUNAS (TEMPORÁRIO) ---
    st.subheader("💡 **DEBUG:** Nomes das Colunas no seu CSV:")
    st.write(df.columns.tolist()) # Isso exibirá a lista exata de nomes das colunas no seu dashboard
    st.markdown("---") # Separador para facilitar a leitura
    # --- FIM DA LINHA DE DEBUG ---

except FileNotFoundError:
    st.error(f"Arquivo '{file_path}' não encontrado. Carregando dados de exemplo para demonstração.")
    # Dados de exemplo para demonstração caso o arquivo não seja encontrado.
    # Estes dados simulam a estrutura esperada do seu CSV.
    data = {
        'Ano': [2022, 2022, 2022, 2022, 2023, 2023, 2023, 2023, 2024, 2024, 2024, 2024],
        'Mês': ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Janeiro', 'Fevereiro', 'Março', 'Abril'],
        'Tipo de Voo': ['Nacional', 'Internacional', 'Nacional', 'Internacional', 'Nacional', 'Internacional', 'Nacional', 'Internacional', 'Nacional', 'Internacional', 'Nacional', 'Internacional'],
        'Passageiros': [10000, 5000, 12000, 6000, 11000, 6500, 13000, 7000, 12000, 7500, 14000, 8000]
    }
    df = pd.DataFrame(data)
    # Se usando dados de exemplo, a coluna 'Tipo de Voo' é definida automaticamente.
    # Se a constante COLUNA_TIPO_DE_VOO for diferente, ela será ignorada para os dados de exemplo.
    st.warning("Por favor, substitua os dados de exemplo pelos seus dados reais para uma análise completa.")


# --- 3. Pré-processamento dos Dados (Com Verificações e Correções Robustas) ---
if not df.empty:
    st.subheader("🛠️ Verificação e Limpeza dos Dados")

    # Mostrar as primeiras linhas do DF e seus tipos de dados antes do processamento
    st.write("#### 1. Dados Brutos (Primeiras Linhas):")
    st.dataframe(df.head())
    st.write("#### 2. Tipos de Dados Originais:")
    st.text(df.dtypes) # Usar st.text para exibir dtypes no dashboard

    # --- Limpeza e Validação da coluna 'Mês' ---
    if 'Mês' in df.columns:
        # 1. Limpeza da coluna 'Mês': Remove espaços em branco e capitaliza a primeira letra de cada palavra
        df['Mês'] = df['Mês'].astype(str).str.strip().str.capitalize()
        st.write("#### 3. Valores Únicos da Coluna 'Mês' Após Limpeza:")
        st.text(df['Mês'].unique()) # Mostrar os meses únicos após a limpeza
    else:
        st.error("❌ Erro Crítico: Coluna 'Mês' não encontrada no seu arquivo CSV. Por favor, verifique o nome da coluna no seu CSV.")
        st.stop() # Para a execução se a coluna crucial estiver faltando

    # --- Validação e Conversão da coluna 'Ano' ---
    if 'Ano' in df.columns:
        # Tenta converter 'Ano' para numérico, forçando erros para NaN e depois removendo-os
        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce')
        if df['Ano'].isnull().any():
            st.warning("⚠️ Foram encontrados valores não numéricos ou em branco na coluna 'Ano'. As linhas com problemas serão removidas.")
            df.dropna(subset=['Ano'], inplace=True)
        # Após garantir que são números, converte para inteiro
        df['Ano'] = df['Ano'].astype(int)
    else:
        st.error("❌ Erro Crítico: Coluna 'Ano' não encontrada no seu arquivo CSV. Por favor, verifique o nome da coluna no seu CSV.")
        st.stop()
    
    # --- Validação da coluna 'Passageiros' ---
    if 'Passageiros' in df.columns:
        df['Passageiros'] = pd.to_numeric(df['Passageiros'], errors='coerce')
        if df['Passageiros'].isnull().any():
            st.warning("⚠️ Foram encontrados valores não numéricos ou em branco na coluna 'Passageiros'. As linhas com problemas serão removidas.")
            df.dropna(subset=['Passageiros'], inplace=True)
    else:
        st.error("❌ Erro Crítico: Coluna 'Passageiros' não encontrada no seu arquivo CSV. Por favor, verifique o nome da coluna no seu CSV.")
        st.stop()

    # Cria uma coluna numérica para o mês usando o mapeamento
    # Se algum mês não for encontrado no 'month_to_num', ele se tornará NaN
    df['Mês_Num'] = df['Mês'].map(month_to_num)

    # --- Verificação de Mês_Num após mapeamento ---
    if df['Mês_Num'].isnull().any():
        st.warning("⚠️ Foram encontrados meses no seu CSV que NÃO PUDERAM SER MAPEADOS (resultaram em NaN). Verifique a coluna 'Mês' para typos ou formatos inesperados.")
        st.dataframe(df[df['Mês_Num'].isnull()]) # Mostra as linhas com problema
        # Remove linhas com meses inválidos se não for possível corrigi-los, para evitar erros futuros
        df.dropna(subset=['Mês_Num'], inplace=True)
        st.info("Linhas com meses inválidos (não mapeados) foram removidas para evitar erros.")

    # --- Criação e Validação da coluna 'Data' ---
    # 'errors='coerce'' vai transformar qualquer erro de conversão em NaT (Not a Time)
    df['Data'] = pd.to_datetime(
        df['Ano'].astype(str) + '-' + df['Mês_Num'].astype(str) + '-01',
        errors='coerce'
    )

    # --- Verificação de Data após conversão ---
    if df['Data'].isnull().any():
        st.warning("⚠️ Foram encontradas datas inválidas (NaT) após a conversão. As linhas com datas inválidas serão removidas para evitar erros nos gráficos.")
        st.dataframe(df[df['Data'].isnull()]) # Mostra as linhas com datas problemáticas
        df.dropna(subset=['Data'], inplace=True) # Remover linhas com datas inválidas
    
    # Verifica o tipo final da coluna 'Data' para garantir que é datetime
    if not pd.api.types.is_datetime64_any_dtype(df['Data']):
        st.error("❌ Erro Final: A coluna 'Data' não foi convertida para o tipo datetime. Isso indica um problema grave nos dados de Ano ou Mês que não pôde ser corrigido.")
        st.stop() # Para a execução se a coluna crítica não for do tipo correto

    # Ordena o DataFrame pela coluna 'Data' para garantir a correta exibição nos gráficos de tempo
    df = df.sort_values(by='Data')
    
    st.write("#### 4. Dados Processados (Primeiras Linhas e Tipos Finais):")
    st.dataframe(df.head())
    st.write("#### 5. Tipos de Dados Finais:")
    st.text(df.dtypes)

# --- 4. Barra Lateral para Filtros ---
# Só exibe os filtros se o DataFrame não estiver vazio após o pré-processamento
if not df.empty:
    st.sidebar.header("⚙️ Filtros de Análise")

    # Filtro por Ano: Permite selecionar um ou mais anos
    anos_disponiveis = sorted(df['Ano'].unique())
    ano_selecionado = st.sidebar.multiselect(
        "Selecione o(s) Ano(s)",
        options=anos_disponiveis,
        default=anos_disponiveis # Por padrão, todos os anos são selecionados
    )

    # Filtro por Mês: Permite selecionar um ou mais meses
    meses_selecionados = st.sidebar.multiselect(
        "Selecione o(s) Mês(es)",
        options=month_order, # Usa a ordem predefinida dos meses
        default=month_order # Por padrão, todos os meses são selecionados
    )

    # Filtro por Tipo de Voo: Verifica se a coluna de Tipo de Voo existe antes de criar o filtro
    # Usa a constante COLUNA_TIPO_DE_VOO
    if COLUNA_TIPO_DE_VOO in df.columns:
        tipos_voo_disponiveis = df[COLUNA_TIPO_DE_VOO].unique()
        tipo_voo_selecionado = st.sidebar.multiselect(
            "Selecione o Tipo de Voo",
            options=tipos_voo_disponiveis,
            default=tipos_voo_disponiveis # Por padrão, todos os tipos de voo são selecionados
        )
    else:
        tipo_voo_selecionado = None
        st.sidebar.warning(f"Coluna '{COLUNA_TIPO_DE_VOO}' (Tipo de Voo) não encontrada nos dados. Este filtro e gráficos relacionados não serão exibidos.")

    # --- 5. Aplicação dos Filtros ---
    # Filtra o DataFrame com base nas seleções do usuário
    df_filtrado = df[
        (df['Ano'].isin(ano_selecionado)) &
        (df['Mês'].isin(meses_selecionados))
    ]

    # Aplica o filtro de Tipo de Voo se a coluna existir e o filtro foi selecionado
    if tipo_voo_selecionado is not None and COLUNA_TIPO_DE_VOO in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado[COLUNA_TIPO_DE_VOO].isin(tipo_voo_selecionado)]

    # Exibir mensagem se não houver dados após a filtragem
    if df_filtrado.empty:
        st.warning("🚫 Nenhum dado encontrado com os filtros selecionados. Por favor, ajuste os filtros ou verifique os dados.")
    else:
        # --- 6. Métricas Chave ---
        st.subheader("📊 Métricas Chave")
        # Cria três colunas para exibir as métricas lado a lado
        col1, col2, col3 = st.columns(3)

        # Calcula e exibe o total de passageiros no período filtrado
        total_passageiros = df_filtrado['Passageiros'].sum()
        col1.metric("Total de Passageiros", f"{total_passageiros:,.0f}")

        # Média de passageiros por mês no período filtrado
        media_passageiros_mes = df_filtrado.groupby('Data')['Passageiros'].sum().mean()
        col2.metric("Média de Passageiros por Mês", f"{media_passageiros_mes:,.0f}")

        # Número de anos únicos filtrados
        num_anos_filtrados = len(df_filtrado['Ano'].unique())
        col3.metric("Anos Analisados", num_anos_filtrados)


        # --- 7. Visualizações de Dados (Gráficos) ---
        st.subheader("📈 Visualizações de Dados")

        # Gráfico de Linha: Tráfego de Passageiros ao Longo do Tempo
        st.markdown("#### Tráfego Total de Passageiros por Mês/Ano")
        # Agrupa por data para garantir um ponto por mês/ano e soma os passageiros
        df_time_series = df_filtrado.groupby('Data')['Passageiros'].sum().reset_index()
        fig_time_series = px.line(
            df_time_series,
            x='Data',
            y='Passageiros',
            title='Evolução do Tráfego de Passageiros ao Longo do Tempo',
            labels={'Passageiros': 'Número de Passageiros', 'Data': 'Data'},
            markers=True # Adiciona marcadores nos pontos de dados para melhor visualização
        )
        fig_time_series.update_layout(hovermode="x unified") # Melhora a interatividade ao passar o mouse
        st.plotly_chart(fig_time_series, use_container_width=True) # Exibe o gráfico, usando a largura total do contêiner

        # Gráfico de Barras: Passageiros por Tipo de Voo (se a coluna existir)
        # Usa a constante COLUNA_TIPO_DE_VOO
        if COLUNA_TIPO_DE_VOO in df.columns:
            st.markdown("#### Distribuição de Passageiros por Tipo de Voo")
            # Agrupa os dados por 'Tipo de Voo' e soma os passageiros
            df_type_of_flight = df_filtrado.groupby(COLUNA_TIPO_DE_VOO)['Passageiros'].sum().reset_index()
            fig_type_of_flight = px.bar(
                df_type_of_flight,
                x=COLUNA_TIPO_DE_VOO,
                y='Passageiros',
                title=f'Passageiros por {COLUNA_TIPO_DE_VOO}', # Título dinâmico
                labels={'Passageiros': 'Número de Passageiros', COLUNA_TIPO_DE_VOO: COLUNA_TIPO_DE_VOO},
                color=COLUNA_TIPO_DE_VOO # Usa cores diferentes para cada tipo de voo
            )
            st.plotly_chart(fig_type_of_flight, use_container_width=True)

        # Gráfico de Barras: Tráfego Médio de Passageiros por Mês (Agregado por todos os anos filtrados)
        st.markdown("#### Tráfego Médio de Passageiros por Mês (Sazonalidade)")
        # Calcula a média de passageiros por mês, reindexando para manter a ordem cronológica dos meses
        # Filtra apenas os meses que ainda existem no df_filtrado para evitar NaNs no gráfico se meses foram removidos
        valid_months_in_filtered_df = [m for m in month_order if m in df_filtrado['Mês'].unique()]
        df_monthly_avg = df_filtrado.groupby('Mês')['Passageiros'].mean().reindex(valid_months_in_filtered_df).reset_index()
        fig_monthly_avg = px.bar(
            df_monthly_avg,
            x='Mês',
            y='Passageiros',
            title='Média de Passageiros por Mês',
            labels={'Passageiros': 'Média de Passageiros', 'Mês': 'Mês'},
            color='Mês', # Usa cores diferentes para cada mês
            category_orders={"Mês": valid_months_in_filtered_df} # Garante a ordem correta dos meses no eixo X
        )
        st.plotly_chart(fig_monthly_avg, use_container_width=True)


        # --- 8. Análise Descritiva ---
        st.subheader("🔬 Análise Descritiva dos Dados Filtrados")
        st.write("Aqui você pode ver estatísticas descritivas para o número de passageiros no período e filtros selecionados. Estas medidas fornecem um resumo estatístico dos dados.")

        # Gera estatísticas descritivas para a coluna 'Passageiros'
        desc_stats = df_filtrado['Passageiros'].describe().to_frame()
        st.dataframe(desc_stats)

        st.markdown("""
        **Interpretação das Estatísticas:**
        * **count:** O número de observações (registros) não nulas na coluna 'Passageiros' do conjunto de dados filtrado.
        * **mean (média):** A média aritmética do número de passageiros. Indica o valor central dos dados.
        * **std (desvio padrão):** Uma medida da dispersão ou variabilidade dos dados em torno da média. Um valor alto indica que os pontos de dados estão espalhados por uma ampla gama de valores.
        * **min (mínimo):** O menor número de passageiros registrado no conjunto de dados filtrado.
        * **25% (primeiro quartil):** O valor abaixo do qual 25% dos dados se encontram.
        * **50% (mediana):** O valor do meio do conjunto de dados quando ordenado. É menos sensível a valores extremos (outliers) do que a média.
        * **75% (terceiro quartil):** O valor abaixo do qual 75% dos dados se encontram.
        * **max (máximo):** O maior número de passageiros registrado no conjunto de dados filtrado.
        """)

        # --- 9. Tabela de Dados Filtrados ---
        st.subheader("📋 Tabela de Dados Filtrados")
        st.write("Visualize os dados brutos após a aplicação dos filtros.")
        # Exibe o DataFrame filtrado, ordenado por data para facilitar a leitura
        # Verifica se 'Tipo de Voo' existe antes de incluir na tabela final
        cols_to_display = ['Ano', 'Mês', 'Passageiros', 'Data']
        if COLUNA_TIPO_DE_VOO in df_filtrado.columns:
            cols_to_display.insert(2, COLUNA_TIPO_DE_VOO) # Adiciona 'Tipo de Voo' antes de 'Passageiros'
        st.dataframe(df_filtrado[cols_to_display].sort_values(by='Data'))
