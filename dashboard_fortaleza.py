import pandas as pd
import streamlit as st
import plotly.express as px
import os # Importa o módulo os para verificar a existência do arquivo

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
    st.info("⚠️ **Importante:** Este dashboard espera as colunas 'Ano', 'Mês', 'Total Passageiros', 'Nacional', 'Internacional'.")
    
    # --- RENOMEAR COLUNAS PARA PADRONIZAÇÃO ---
    # Renomeia 'Total Passageiros' para 'Passageiros' para ser usado no código
    df = df.rename(columns={'Total Passageiros': 'Passageiros'})
    
    # --- LINHA PARA DEBUGAR: MOSTRAR NOMES DAS COLUNAS (TEMPORÁRIO) ---
    st.subheader("💡 **DEBUG:** Nomes das Colunas Após Renomeação:")
    st.write(df.columns.tolist()) # Isso exibirá a lista exata de nomes das colunas no seu dashboard
    st.markdown("---") # Separador para facilitar a leitura
    # --- FIM DA LINHA DE DEBUG ---

except FileNotFoundError:
    st.error(f"Arquivo '{file_path}' não encontrado. Carregando dados de exemplo para demonstração.")
    # Dados de exemplo para demonstração caso o arquivo não seja encontrado.
    # Estes dados simulam a estrutura esperada do seu CSV com as novas colunas.
    data = {
        'Ano': [2022, 2022, 2022, 2022, 2023, 2023, 2023, 2023, 2024, 2024, 2024, 2024],
        'Mês': ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Janeiro', 'Fevereiro', 'Março', 'Abril'],
        'Total Passageiros': [15000, 7000, 18000, 9000, 16000, 8000, 19000, 9500, 17000, 8500, 20000, 10000],
        'Nacional': [10000, 5000, 12000, 6000, 11000, 6500, 13000, 7000, 12000, 7500, 14000, 8000],
        'Internacional': [5000, 2000, 6000, 3000, 5000, 1500, 6000, 2500, 5000, 1000, 6000, 2000],
        'Doméstico': [10000, 5000, 12000, 6000, 11000, 6500, 13000, 7000, 12000, 7500, 14000, 8000] # Incluindo para exemplo
    }
    df = pd.DataFrame(data)
    # Renomear para manter a consistência com o resto do código
    df = df.rename(columns={'Total Passageiros': 'Passageiros'})
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
        # Remove espaços em branco e capitaliza a primeira letra de CADA PALAVRA
        df['Mês'] = df['Mês'].astype(str).str.strip().str.title()
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
        # Tenta converter para inteiro APÓS a limpeza de NaNs. Se falhar, é porque há valores não-inteiros.
        try:
            df['Ano'] = df['Ano'].astype(int)
        except ValueError:
            st.error("❌ Erro: Coluna 'Ano' contém valores que não podem ser convertidos para inteiro após a limpeza de NaNs. Verifique os dados brutos.")
            st.dataframe(df[df['Ano'].apply(lambda x: not isinstance(x, (int, float))) | df['Ano'].isnull()])
            st.stop()
    else:
        st.error("❌ Erro Crítico: Coluna 'Ano' não encontrada no seu arquivo CSV. Por favor, verifique o nome da coluna no seu CSV.")
        st.stop()
    
    # --- Validação da coluna 'Passageiros' (agora 'Total Passageiros' original) ---
    if 'Passageiros' in df.columns: # Já renomeado de 'Total Passageiros'
        df['Passageiros'] = pd.to_numeric(df['Passageiros'], errors='coerce')
        if df['Passageiros'].isnull().any():
            st.warning("⚠️ Foram encontrados valores não numéricos ou em branco na coluna 'Passageiros' (Total Passageiros). As linhas com problemas serão removidas.")
            df.dropna(subset=['Passageiros'], inplace=True)
    else:
        st.error("❌ Erro Crítico: Coluna 'Passageiros' (Total Passageiros) não encontrada no seu CSV após a renomeação. Por favor, verifique o nome da coluna original.")
        st.stop()

    # --- Validação das colunas 'Nacional' e 'Internacional' ---
    if 'Nacional' in df.columns and 'Internacional' in df.columns:
        df['Nacional'] = pd.to_numeric(df['Nacional'], errors='coerce').fillna(0)
        df['Internacional'] = pd.to_numeric(df['Internacional'], errors='coerce').fillna(0)
    else:
        st.warning("⚠️ Colunas 'Nacional' ou 'Internacional' não encontradas. Gráficos de tipo de voo podem não ser exibidos.")

    # Cria uma coluna numérica para o mês usando o mapeamento
    df['Mês_Num'] = df['Mês'].map(month_to_num)

    # --- Verificação de Mês_Num após mapeamento ---
    if df['Mês_Num'].isnull().any():
        st.warning("⚠️ Foram encontrados meses no seu CSV que NÃO PUDERAM SER MAPEADOS (resultaram em NaN). Verifique a coluna 'Mês' para typos ou formatos inesperados.")
        st.dataframe(df[df['Mês_Num'].isnull()]) # Mostra as linhas com problema
        df.dropna(subset=['Mês_Num'], inplace=True)
        st.info("Linhas com meses inválidos (não mapeados) foram removidas para evitar erros.")

    # Tenta converter Mês_Num para inteiro APÓS a limpeza de NaNs
    try:
        df['Mês_Num'] = df['Mês_Num'].astype(int)
    except ValueError:
        st.error("❌ Erro: Coluna 'Mês_Num' contém valores que não podem ser convertidos para inteiro após a limpeza de NaNs. Verifique os dados brutos.")
        st.dataframe(df[df['Mês_Num'].apply(lambda x: not isinstance(x, (int, float))) | df['Mês_Num'].isnull()])
        st.stop()

    # --- Criação e Validação da coluna 'Data' ---
    # Agora Ano e Mês_Num devem ser inteiros limpos
    date_strings_series = df['Ano'].astype(str) + '-' + df['Mês_Num'].astype(str) + '-01'
    
    # DEBUG: Mostrar as strings que estão sendo passadas para pd.to_datetime
    st.write("#### 6. DEBUG: Primeiras strings de data para conversão:")
    st.text(date_strings_series.head().to_string())

    df['Data'] = pd.to_datetime(
        date_strings_series, # Passando a série de strings já construída
        errors='coerce' # 'coerce' will turn invalid parsing into NaT (Not a Time)
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
    
    st.write("#### 7. Dados Processados (Primeiras Linhas e Tipos Finais):")
    st.dataframe(df.head())
    st.write("#### 8. Tipos de Dados Finais:")
    st.text(df.dtypes)

    # --- 4. Preparação para Gráficos de Tipo de Voo (Nacional/Internacional) ---
    # Cria um DataFrame 'derretido' para facilitar a filtragem e visualização por tipo de voo
    if 'Nacional' in df.columns and 'Internacional' in df.columns:
        df_tipo_voo_melted = df.melt(
            id_vars=['Ano', 'Mês', 'Mês_Num', 'Data'], # Colunas de identificação
            value_vars=['Nacional', 'Internacional'], # Colunas a serem 'derretidas'
            var_name='Tipo de Voo', # Novo nome da coluna para as categorias 'Nacional'/'Internacional'
            value_name='Passageiros_por_Tipo' # Novo nome da coluna para os valores correspondentes
        )
        # Garante que 'Passageiros_por_Tipo' é numérico
        df_tipo_voo_melted['Passageiros_por_Tipo'] = pd.to_numeric(df_tipo_voo_melted['Passageiros_por_Tipo'], errors='coerce').fillna(0)
        # st.dataframe(df_tipo_voo_melted.head()) # DEBUG
    else:
        df_tipo_voo_melted = pd.DataFrame() # DataFrame vazio se as colunas não existirem
        st.warning("Colunas 'Nacional' ou 'Internacional' não encontradas para gráficos de tipo de voo.")


# --- 5. Barra Lateral para Filtros ---
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

    # Filtro por Tipo de Voo (usando df_tipo_voo_melted)
    tipo_voo_selecionado = None
    if not df_tipo_voo_melted.empty:
        tipos_voo_disponiveis = df_tipo_voo_melted['Tipo de Voo'].unique()
        tipo_voo_selecionado = st.sidebar.multiselect(
            "Selecione o Tipo de Voo (Nacional/Internacional)",
            options=tipos_voo_disponiveis,
            default=tipos_voo_disponiveis # Por padrão, todos os tipos de voo são selecionados
        )

    # --- 6. Aplicação dos Filtros ---
    # Filtra o DataFrame principal para métricas e gráfico de linha total
    df_filtrado_principal = df[
        (df['Ano'].isin(ano_selecionado)) &
        (df['Mês'].isin(meses_selecionados))
    ]

    # Filtra o DataFrame 'derretido' para o gráfico de tipo de voo
    df_filtrado_tipo_voo = df_tipo_voo_melted[
        (df_tipo_voo_melted['Ano'].isin(ano_selecionado)) &
        (df_tipo_voo_melted['Mês'].isin(meses_selecionados))
    ]
    if tipo_voo_selecionado is not None and not df_filtrado_tipo_voo.empty:
        df_filtrado_tipo_voo = df_filtrado_tipo_voo[df_filtrado_tipo_voo['Tipo de Voo'].isin(tipo_voo_selecionado)]


    # Exibir mensagem se não houver dados após a filtragem
    if df_filtrado_principal.empty:
        st.warning("🚫 Nenhum dado encontrado com os filtros selecionados. Por favor, ajuste os filtros ou verifique os dados.")
    else:
        # --- 7. Métricas Chave ---
        st.subheader("📊 Métricas Chave")
        # Cria três colunas para exibir as métricas lado a lado
        col1, col2, col3 = st.columns(3)

        # Calcula e exibe o total de passageiros no período filtrado
        total_passageiros = df_filtrado_principal['Passageiros'].sum()
        col1.metric("Total de Passageiros", f"{total_passageiros:,.0f}")

        # Média de passageiros por mês no período filtrado
        media_passageiros_mes = df_filtrado_principal.groupby('Data')['Passageiros'].sum().mean()
        col2.metric("Média de Passageiros por Mês", f"{media_passageiros_mes:,.0f}")

        # Número de anos únicos filtrados
        num_anos_filtrados = len(df_filtrado_principal['Ano'].unique())
        col3.metric("Anos Analisados", num_anos_filtrados)


        # --- 8. Visualizações de Dados (Gráficos) ---
        st.subheader("📈 Visualizações de Dados")

        # Gráfico de Linha: Tráfego de Passageiros ao Longo do Tempo (Total)
        st.markdown("#### Tráfego Total de Passageiros por Mês/Ano")
        # Agrupa por data para garantir um ponto por mês/ano e soma os passageiros
        df_time_series = df_filtrado_principal.groupby('Data')['Passageiros'].sum().reset_index()
        fig_time_series = px.line(
            df_time_series,
            x='Data',
            y='Passageiros',
            title='Evolução do Tráfego Total de Passageiros',
            labels={'Passageiros': 'Número de Passageiros', 'Data': 'Data'},
            markers=True # Adiciona marcadores nos pontos de dados para melhor visualização
        )
        fig_time_series.update_layout(hovermode="x unified") # Melhora a interatividade ao passar o mouse
        st.plotly_chart(fig_time_series, use_container_width=True) # Exibe o gráfico, usando a largura total do contêiner

        # Gráfico de Barras: Passageiros por Tipo de Voo (Nacional/Internacional)
        if not df_filtrado_tipo_voo.empty:
            st.markdown("#### Distribuição de Passageiros por Tipo de Voo (Nacional/Internacional)")
            # Agrupa os dados por 'Tipo de Voo' e soma os passageiros
            df_type_of_flight_agg = df_filtrado_tipo_voo.groupby('Tipo de Voo')['Passageiros_por_Tipo'].sum().reset_index()
            fig_type_of_flight = px.bar(
                df_type_of_flight_agg,
                x='Tipo de Voo',
                y='Passageiros_por_Tipo',
                title='Passageiros por Tipo de Voo',
                labels={'Passageiros_por_Tipo': 'Número de Passageiros', 'Tipo de Voo': 'Tipo de Voo'},
                color='Tipo de Voo' # Usa cores diferentes para cada tipo de voo
            )
            st.plotly_chart(fig_type_of_flight, use_container_width=True)
        else:
            st.info("Dados para o gráfico de 'Tipo de Voo' não disponíveis com os filtros selecionados ou colunas ausentes.")


        # Gráfico de Barras: Tráfego Médio de Passageiros por Mês (Total Agregado)
        st.markdown("#### Tráfego Médio de Passageiros por Mês (Sazonalidade - Total)")
        # Calcula a média de passageiros por mês, reindexando para manter a ordem cronológica dos meses
        valid_months_in_filtered_df = [m for m in month_order if m in df_filtrado_principal['Mês'].unique()]
        df_monthly_avg = df_filtrado_principal.groupby('Mês')['Passageiros'].mean().reindex(valid_months_in_filtered_df).reset_index()
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


        # --- 9. Análise Descritiva ---
        st.subheader("🔬 Análise Descritiva dos Dados Filtrados (Total de Passageiros)")
        st.write("Aqui você pode ver estatísticas descritivas para o número total de passageiros no período e filtros selecionados.")

        # Gera estatísticas descritivas para a coluna 'Passageiros'
        desc_stats = df_filtrado_principal['Passageiros'].describe().to_frame()
        st.dataframe(desc_stats)

        st.markdown("""
        **Interpretação das Estatísticas:**
        * **count:** O número de observações (registros) não nulas na coluna 'Passageiros'.
        * **mean (média):** A média aritmética do número de passageiros.
        * **std (desvio padrão):** Medida da dispersão dos dados.
        * **min (mínimo):** O menor número de passageiros registrado.
        * **25%, 50% (mediana), 75% (terceiro quartil):** Indicam a distribuição dos dados.
        * **max (máximo):** O maior número de passageiros registrado.
        """)

        # --- 10. Tabela de Dados Filtrados ---
        st.subheader("📋 Tabela de Dados Filtrados")
        st.write("Visualize os dados brutos principais após a aplicação dos filtros.")
        # Exibe o DataFrame filtrado, ordenado por data para facilitar a leitura
        # Inclui todas as colunas relevantes que existem no DataFrame principal
        cols_to_display_main_df = ['Ano', 'Mês', 'Passageiros', 'Nacional', 'Internacional', 'Data']
        # Adiciona 'Doméstico' se presente
        if 'Doméstico' in df_filtrado_principal.columns:
            cols_to_display_main_df.insert(cols_to_display_main_df.index('Internacional') + 1, 'Doméstico')

        # Filtra as colunas que realmente existem no df_filtrado_principal
        final_cols_to_display = [col for col in cols_to_display_main_df if col in df_filtrado_principal.columns]
        
        st.dataframe(df_filtrado_principal[final_cols_to_display].sort_values(by='Data'))
