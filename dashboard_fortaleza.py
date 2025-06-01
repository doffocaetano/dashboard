import pandas as pd
import streamlit as st
import plotly.express as px
import os # Importa o módulo os para verificar a existência do arquivo

# ==============================================================================
# ATENÇÃO CRÍTICA:
# VOCÊ DEVE SUBSTITUIR 'NOME_REAL_DA_COLUNA_TIPO_DE_VOO'
# PELO NOME EXATO DA COLUNA NO SEU ARQUIVO CSV PARA O 'TIPO DE VOO'.
# EX: SE NO SEU CSV A COLUNA É 'TIPO_VOO', MUDE PARA:
# COLUNA_TIPO_DE_VOO = 'TIPO_VOO'
# ==============================================================================
COLUNA_TIPO_DE_VOO = 'Tipo de Voo' # <<<< SUBSTITUA AQUI COM O NOME EXATO DO SEU CSV!


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
try:
    # Carrega o arquivo CSV para um DataFrame pandas
    df = pd.read_csv(file_path)
    st.success(f"Dados carregados com sucesso de '{file_path}'!")
    st.info("⚠️ **Importante:** Este dashboard espera as colunas 'Ano', 'Mês', 'Passageiros' e a coluna de Tipo de Voo (definida acima). Verifique se seu CSV as possui.")

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
        st.error("❌ Erro Crítico: Coluna '
