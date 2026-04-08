# 📊 Dashboard de Inadimplência Escolar

Este projeto é uma aplicação web interativa desenvolvida em **Python** utilizando o framework **Dash**. O objetivo é fornecer uma visão analítica e simulada sobre o status de pagamentos e inadimplência em uma instituição de ensino, utilizando técnicas modernas de visualização de dados e uma estética profissional.

## 🚀 Funcionalidades

- **Visão Geral (Dashboard):**
    - KPIs em tempo real: Total de inadimplência, ticket médio, taxa de inadimplência e valor arrecadado.
    - Gráficos de barras horizontais para análise mensal.
    - Evolução temporal da inadimplência.
    - Distribuição por turma e turno (Matutino/Vespertino).
    - Ranking dos alunos com maiores débitos.
- **Módulo de Simulação:**
    - Ajuste dinâmico através de um *slider* para projetar cenários de aumento ou redução da inadimplência (10% a 200%).
- **Interface Moderna:** Design responsivo com paleta de cores "Forest Deep" e elementos em estilo *Glassmorphism*.

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**
- **Dash** (Interface Web e Callbacks)
- **Plotly** (Gráficos Interativos)
- **Pandas** (Manipulação e Tratamento de Dados)
- **PyArrow** (Engine para leitura de arquivos Parquet)

## 📋 Pré-requisitos

Certifique-se de que o arquivo de dados esteja no diretório correto para que o app funcione:
- **Caminho:** `processed/fato_pagamento.parquet`

## 🔧 Instalação e Execução

Siga os comandos abaixo no seu terminal para configurar o ambiente e rodar o dashboard:

1. **Clone o repositório ou baixe os arquivos:**
   ```bash
   git clone https://github.com/iagonmic/school-debt-analysis.git

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv venv
    .\venv\Scripts\activate

3. **Crie e ative um ambiente virtual:**
   ```bash
   python3 -m venv venv
    source venv/bin/activate

4. **Instale as dependências necessárias:**
   ```bash
   pip install -r requirements.txt

5. **Inicie a aplicação:**
   ```bash
   python app.py


