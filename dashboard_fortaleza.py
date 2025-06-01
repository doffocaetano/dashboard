import pandas as pd
import streamlit as st
import plotly.express as px
import os # Importa o módulo os para verificar a existência do arquivo

# --- Configurações Iniciais e Mapeamento de Meses ---

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

# --- Título Principal do Dashboard ---
st.title("✈️ Dashboard Interativo de Tráfego Aéreo - Fortaleza")
st.markdown("Este dashboard apresenta uma análise do tráfego turístico aéreo no Aeroporto de Fortaleza, Ceará.")

# --- Carregamento dos Dados ---
# Tenta carregar o arquivo CSV. Se o arquivo não for encontrado, usa dados de exemplo para demonstração.
file_path = "TABELA ATUALIZADA.xlsx - Planilha1.csv"
try:
    # Carrega o arquivo CSV para um DataFrame pandas
    df = pd.read_csv(file_path)
    st.success(f"Dados carregados com sucesso de '{file_path}'!")
    st.info("⚠️ **Importante:** Certifique-se de que as colunas 'Ano', 'Mês', 'Tipo de Voo' e 'Passageiros' existem no seu arquivo CSV, ou ajuste o código conforme necessário.")
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
    st.warning("Por favor, substitua os dados de exemplo pelos seus dados reais para uma análise completa.")

# --- Pré-processamento dos Dados ---
if not df.empty:
    # Garante que a coluna 'Ano' é do tipo inteiro
    df['Ano'] = df['Ano'].astype(int)
    # Cria uma coluna numérica para o mês usando o mapeamento, facilitando a ordenação cronológica
    df['Mês_Num'] = df['Mês'].map(month_to_num)
    # Cria uma coluna 'Data' combinando Ano e Mês, útil para gráficos de série temporal
    df['Data'] = pd.to_datetime(df['Ano'].astype(str) + '-' + df['Mês_Num'].astype(str) + '-01')
    # Ordena o DataFrame pela coluna 'Data' para garantir a correta exibição nos gráficos de tempo
    df = df.sort_values(by='Data')

# --- Barra Lateral para Filtros ---
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

# Filtro por Tipo de Voo: Verifica se a coluna 'Tipo de Voo' existe antes de criar o filtro
if 'Tipo de Voo' in df.columns:
    tipos_voo_disponiveis = df['Tipo de Voo'].unique()
    tipo_voo_selecionado = st.sidebar.multiselect(
        "Selecione o Tipo de Voo",
        options=tipos_voo_disponiveis,
        default=tipos_voo_disponiveis # Por padrão, todos os tipos de voo são selecionados
    )
else:
    tipo_voo_selecionado = None
    st.sidebar.warning("Coluna 'Tipo de Voo' não encontrada nos dados. Este filtro não será exibido.")

# --- Aplicação dos Filtros ---
# Filtra o DataFrame com base nas seleções do usuário
df_filtrado = df[
    (df['Ano'].isin(ano_selecionado)) &
    (df['Mês'].isin(meses_selecionados))
]

# Aplica o filtro de Tipo de Voo se a coluna existir e o filtro foi selecionado
if tipo_voo_selecionado is not None:
    df_filtrado = df_filtrado[df_filtrado['Tipo de Voo'].isin(tipo_voo_selecionado)]

# Exibe uma mensagem de aviso se nenhum dado for encontrado após a filtragem
if df_filtrado.empty:
    st.warning("🚫 Nenhum dado encontrado com os filtros selecionados. Por favor, ajuste os filtros.")
else:
    # --- Métricas Chave ---
    st.subheader("📊 Métricas Chave")
    # Cria três colunas para exibir as métricas lado a lado
    col1, col2, col3 = st.columns(3)

    # Calcula e exibe o total de passageiros no período filtrado
    total_passageiros = df_filtrado['Passageiros'].sum()
    col1.metric("Total de Passageiros", f"{total_passageiros:,.0f}")

    # Calcula e exibe a média de passageiros por mês no período filtrado
    media_passageiros_mes = df_filtrado.groupby('Data')['Passageiros'].sum().mean()
    col2.metric("Média de Passageiros por Mês", f"{media_passageiros_mes:,.0f}")

    # Calcula e exibe o número de anos únicos considerados na análise
    num_anos_filtrados = len(df_filtrado['Ano'].unique())
    col3.metric("Anos Analisados", num_anos_filtrados)


    # --- Visualizações de Dados (Gráficos) ---
    st.subheader("📈 Visualizações de Dados")

    # Gráfico de Linha: Tráfego de Passageiros ao Longo do Tempo
    st.markdown("#### Tráfego Total de Passageiros por Mês/Ano")
    # Agrupa os dados por 'Data' e soma os passageiros para criar a série temporal
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
    if 'Tipo de Voo' in df.columns:
        st.markdown("#### Distribuição de Passageiros por Tipo de Voo")
        # Agrupa os dados por 'Tipo de Voo' e soma os passageiros
        df_type_of_flight = df_filtrado.groupby('Tipo de Voo')['Passageiros'].sum().reset_index()
        fig_type_of_flight = px.bar(
            df_type_of_flight,
            x='Tipo de Voo',
            y='Passageiros',
            title='Passageiros por Tipo de Voo (Nacional vs. Internacional)',
            labels={'Passageiros': 'Número de Passageiros', 'Tipo de Voo': 'Tipo de Voo'},
            color='Tipo de Voo' # Usa cores diferentes para cada tipo de voo
        )
        st.plotly_chart(fig_type_of_flight, use_container_width=True)

    # Gráfico de Barras: Tráfego Médio de Passageiros por Mês (Agregado por todos os anos filtrados)
    st.markdown("#### Tráfego Médio de Passageiros por Mês (Agregado)")
    # Calcula a média de passageiros por mês, reindexando para manter a ordem cronológica dos meses
    df_monthly_avg = df_filtrado.groupby('Mês')['Passageiros'].mean().reindex(month_order).reset_index()
    fig_monthly_avg = px.bar(
        df_monthly_avg,
        x='Mês',
        y='Passageiros',
        title='Média de Passageiros por Mês (Sazonalidade)',
        labels={'Passageiros': 'Média de Passageiros', 'Mês': 'Mês'},
        color='Mês' # Usa cores diferentes para cada mês
    )
    st.plotly_chart(fig_monthly_avg, use_container_width=True)


    # --- Análise Descritiva ---
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

    # --- Tabela de Dados Filtrados ---
    st.subheader("📋 Tabela de Dados Filtrados")
    st.write("Visualize os dados brutos após a aplicação dos filtros.")
    # Exibe o DataFrame filtrado, ordenado por data para facilitar a leitura
    st.dataframe(df_filtrado[['Ano', 'Mês', 'Tipo de Voo', 'Passageiros', 'Data']].sort_values(by='Data'))

