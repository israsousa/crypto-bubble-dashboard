![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-green.svg)
![License](https://img.shields.io/badge/License-MIT-red.svg)
![GitHub Stars](https://img.shields.io/github/stars/SEU-USERNAME/crypto-bubble-dashboard)
![GitHub Forks](https://img.shields.io/github/forks/SEU-USERNAME/crypto-bubble-dashboard)
![GitHub Issues](https://img.shields.io/github/issues/SEU-USERNAME/crypto-bubble-dashboard)

# 🚀 Crypto Bubble Dashboard

Um dashboard interativo em tempo real para visualização de criptomoedas com bolhas flutuantes, gráficos detalhados e análise de mercado.

![Dashboard Preview](https://img.shields.io/badge/Python-3.8+-blue.svg) ![Pygame](https://img.shields.io/badge/Pygame-2.5+-green.svg) ![License](https://img.shields.io/badge/License-MIT-red.svg)

## ✨ Características

### 🎨 Interface Visual
- **500+ Bolhas Flutuantes**: Cada criptomoeda é representada por uma bolha com física realista
- **Cores Dinâmicas**: Verde para ganhos, vermelho para perdas
- **Animações Suaves**: Movimentos fluidos com detecção de colisão
- **Interface Responsiva**: Adapta-se a diferentes tamanhos de tela

### 📊 Dados em Tempo Real
- **Integração com APIs**: CoinGecko para dados de mercado
- **Atualizações Automáticas**: Dados refreshed a cada 30 segundos
- **Índice Fear & Greed**: Análise de sentimento do mercado
- **Notícias Cripto**: Feed de notícias atualizado

### 📈 Gráficos Interativos
- **Modais Detalhados**: Clique em qualquer bolha para ver detalhes
- **Múltiplos Timeframes**: 1D, 7D, 30D, 90D, 1Y
- **Gráficos Realistas**: Dados históricos simulados
- **Estatísticas Completas**: Market cap, volume, ranking

### 🏆 Rastreamento de Rankings
- **Mudanças Diárias**: Acompanha subidas/descidas no ranking
- **Indicadores Visuais**: Setas para mostrar movimento
- **Persistência de Dados**: Salva dados entre sessões

## 🛠️ Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos de Instalação

1. **Clone o repositório**:
```bash
git clone https://github.com/seu-usuario/crypto-bubble-dashboard.git
cd crypto-bubble-dashboard
```

2. **Crie um ambiente virtual** (recomendado):
```bash
python -m env env

# Windows
env\Scripts\activate

# Linux/macOS
source env/bin/activate
```

3. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

4. **Execute o programa**:
```bash
python main.py
```

## 📁 Estrutura do Projeto

```
crypto_dashboard/
│
├── main.py                    # Arquivo principal
├── requirements.txt           # Dependências
├── README.md                  # Este arquivo
├── .gitignore                # Arquivos ignorados pelo Git
│
├── config/                   # Configurações
│   ├── __init__.py
│   └── settings.py          # Configurações globais
│
├── data/                     # Gerenciamento de dados
│   ├── __init__.py
│   ├── crypto_api.py        # APIs de criptomoedas
│   └── chart_data.py        # Geração de dados para gráficos
│
├── physics/                  # Sistema de física
│   ├── __init__.py
│   ├── bubble.py            # Classe das bolhas
│   └── bubble_manager.py    # Gerenciador de bolhas
│
├── ui/                       # Interface do usuário
│   ├── __init__.py
│   ├── dashboard.py         # Dashboard principal
│   ├── loading_screen.py    # Tela de carregamento
│   ├── crypto_table.py      # Tabela de criptomoedas
│   ├── news_panel.py        # Painel de notícias
│   ├── fear_greed_chart.py  # Gráfico Fear & Greed
│   ├── modal_manager.py     # Gerenciador de modais
│   ├── crypto_modal.py      # Modal de detalhes
│   └── effects.py           # Efeitos visuais
│
├── utils/                    # Utilitários
│   ├── __init__.py
│   ├── data_loader.py       # Carregamento de dados
│   ├── rate_limiter.py      # Limitador de API
│   ├── data_cache.py        # Sistema de cache
│   ├── rank_tracker.py      # Rastreamento de rankings
│   ├── logo_loader.py       # Carregamento de logos
│   └── formatters.py        # Formatação de dados
│
├── assets/                   # Recursos
│   └── logos/               # Logos das criptomoedas
│
└── cache/                    # Cache de dados
    ├── chart_cache.pkl      # Cache de gráficos
    └── daily_ranks.json     # Rankings diários
```

## 🎮 Como Usar

### Controles Básicos
- **Clique**: Clique em qualquer bolha para abrir detalhes
- **ESC**: Fechar modal ou sair do programa
- **Espaço**: Pular tela de carregamento (durante loading)

### Interface
1. **Área de Bolhas** (75% da tela, superior): Visualização principal das criptomoedas
2. **Tabela** (75% da tela, inferior): Lista detalhada com paginação automática
3. **Notícias** (25% da tela, superior direita): Feed de notícias
4. **Fear & Greed** (25% da tela, inferior direita): Índice de sentimento

### Modais de Detalhes
- **Timeframes**: Selecione períodos diferentes (1D, 7D, 30D, 90D, 1Y)
- **Gráficos**: Visualização de preços históricos
- **Estatísticas**: Market cap, volume, ranking, supply

## ⚙️ Configuração

### Arquivo `config/settings.py`
```python
# Dimensões da tela
WIDTH, HEIGHT = 1280, 720

# Intervalos de atualização (segundos)
UPDATE_INTERVAL = 30
NEWS_UPDATE_INTERVAL = 60
FEAR_GREED_UPDATE_INTERVAL = 1800

# Número máximo de bolhas
MAX_BUBBLES = 500
```

### APIs Utilizadas
- **CoinGecko API**: Dados de mercado de criptomoedas
- **CryptoCompare API**: Notícias de criptomoedas
- **Alternative.me API**: Índice Fear & Greed

## 🔧 Dependências

### Principais
- `pygame>=2.5.0`: Engine de jogos e interface gráfica
- `pymunk>=6.4.0`: Motor de física 2D
- `requests>=2.31.0`: Requisições HTTP para APIs
- `Pillow>=10.0.0`: Processamento de imagens

### Opcionais
- `matplotlib>=3.7.0`: Gráficos avançados (futuras versões)
- `numpy>=1.24.0`: Computação numérica

### Desenvolvimento
- `pytest>=7.4.0`: Testes unitários
- `black>=23.0.0`: Formatação de código
- `flake8>=6.0.0`: Linting

## 🚀 Funcionalidades Avançadas

### Sistema de Cache
- **Cache de Logos**: Downloads automáticos e armazenamento local
- **Cache de Dados**: Reduz chamadas desnecessárias às APIs
- **Persistência**: Dados salvos entre sessões

### Rate Limiting
- **Proteção de API**: Limita requisições para evitar bloqueios
- **Fallback Inteligente**: Usa dados em cache quando necessário

### Física Realista
- **Colisão**: Bolhas colidem e interagem naturalmente
- **Flutuação**: Movimento suave e orgânico
- **Boundaries**: Bordas invisíveis mantêm bolhas na tela

## 🛡️ Tratamento de Erros

- **Conectividade**: Funciona offline com dados em cache
- **APIs Indisponíveis**: Fallbacks e retry automático
- **Dados Inválidos**: Validação e sanitização
- **Recursos Faltando**: Degradação graciosa

## 📝 TODO / Roadmap

### Próximas Versões
- [ ] **Portfolio Tracking**: Rastreamento de carteira pessoal
- [ ] **Alertas**: Notificações de preços
- [ ] **Temas**: Modo escuro/claro
- [ ] **Exportação**: Dados para CSV/Excel
- [ ] **Gráficos Reais**: Integração com matplotlib
- [ ] **WebSocket**: Dados em tempo real mais rápidos
- [ ] **Multi-monitor**: Suporte a múltiplas telas
- [ ] **Configurações**: Interface para ajustes

### Melhorias Técnicas
- [ ] **Testes Unitários**: Cobertura completa
- [ ] **CI/CD**: Pipelines automáticos
- [ ] **Documentação**: Sphinx/MkDocs
- [ ] **Performance**: Otimizações de renderização
- [ ] **Logs**: Sistema de logging estruturado

## 🤝 Contribuição

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

### Padrões de Código
- **PEP 8**: Siga as convenções Python
- **Docstrings**: Documente funções e classes
- **Testes**: Adicione testes para novas funcionalidades
- **Commits**: Mensagens claras e descritivas

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/crypto-bubble-dashboard/issues)
- **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/crypto-bubble-dashboard/discussions)
- **Email**: isra_sousa@hotmail.com

## 🙏 Agradecimentos

- **CoinGecko**: Pela excelente API de dados
- **Pygame Community**: Pela documentação e suporte
- **PyMunk**: Pelo motor de física robusto
- **Comunidade Python**: Pelo ecossistema incrível

---

⭐ **Se este projeto foi útil, considere dar uma estrela!** ⭐

---

## .gitignore

```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# poetry
poetry.lock

# pdm
.pdm.toml

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# Project specific
cache/
*.pkl
*.json
assets/logos/
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Local configuration
config/local_settings.py
.env.local
```