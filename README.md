# CaseSimulado – Negreiros NET Dashboard

Dashboard interativo desenvolvido com Streamlit para monitorar clientes de um provedor local de internet em Petrolina/PE. O projeto reúne KPIs, filtros avançados, gráficos, mapa e exportação de dados para apoiar decisões sobre consumo de banda larga.

## Principais recursos
- **Dados reais com fallback**: utiliza `clientes_petrolina.csv` quando disponível e gera dados simulados automaticamente em caso de falha.
- **Hero dinâmico**: banner principal sincronizado com os filtros exibindo total de clientes, críticos e consumo médio.
- **Filtros responsivos**: seleção de bairros, planos, criticidade e consumo mínimo distribuídos em duas linhas para melhor uso em telas menores.
- **Visualizações completas**: pizza por tipo de plano, barras por bairro, ranking de consumo, tendência mensal e mapa interativo com Plotly.
- **KPIs resilientes**: indicadores com tratamento para conjuntos vazios e cálculo de excedentes em 50%.
- **Exportação de dados**: tabela filtrada com opção de download em CSV.
- **Desempenho**: carregamento de dados e geração de séries temporais cacheados com `st.cache_data`.

## Estrutura do projeto
```
.
├── datacase.py              # Aplicação Streamlit principal
├── clientes_petrolina.csv   # Fonte de dados (opcional, com fallback para dados simulados)
├── teste.txt                # Artefato auxiliar
└── README.md                # Este guia
```

## Pré-requisitos
- Python 3.9 ou superior
- Ambiente virtual recomendado (`venv`, `conda`, etc.)

- ## Instalação
1. Clone o repositório:
   ```bash
   git clone <url-do-repositorio>
   cd casesimluado
   ```
2. Crie e ative um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
   > Caso não exista um arquivo `requirements.txt`, instale manualmente: `pip install streamlit pandas numpy plotly`.

## Como executar
```bash
streamlit run datacase.py
```
O navegador abrirá automaticamente em `http://localhost:8501` exibindo o dashboard.

## Testes e validações
O projeto não possui suíte de testes automatizados, mas é possível garantir a integridade básica do código executando:
```bash
python -m compileall datacase.py
```
Esse comando valida a compilação do script e acusa erros de sintaxe rapidamente.

## Personalização
- Adicione novos bairros ou coordenadas atualizando o dicionário `BAIRRO_COORDS` em `datacase.py`.
- Para incluir novas métricas, utilize a função `compute_kpis` como ponto central.
- A função `render_charts` é o local indicado para ampliar ou customizar visualizações.

## Licença
Projeto desenvolvido para fins de estudo e demonstração. Ajuste conforme necessário para uso comercial.
