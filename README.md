# Animeska API

Uma API RESTful robusta e assíncrona para extrair informações e links de vídeo de animes de múltiplas fontes brasileiras populares (`AnimesHD`, `AnimesDigital`, `AnimesOnlineCC`).

Construída com **FastAPI** e **Playwright**, esta API é capaz de navegar em sites modernos, contornar proteções básicas (com `playwright-stealth`) e extrair URLs diretas de vídeo (`.mp4`, `.m3u8`) através de interceptação de rede (network sniffing).

## 🚀 Funcionalidades

*   **Busca Unificada & Enriquecida:** Pesquise animes em múltiplas fontes simultaneamente, com resultados enriquecidos com metadados do **AniList** (Nota, Status, Descrição).
*   **Detalhes Completos:** Título, Capa, Sinopse, Gêneros, Ano, Status, Temporada e lista de Episódios.
*   **Links de Vídeo Diretos:**
    *   Extração inteligente de links de vídeo (`.mp4`, `.m3u8`).
    *   **Playback Inteligente:** Descoberta automática da melhor fonte para assistir (priorizando `AnimesDigital`).
    *   Suporte a interceptação de requisições de rede para players ofuscados.
    *   Navegação automática em iframes de players (ex: Blogger, MP4Upload).
*   **Stealth Mode:** Utiliza técnicas para evitar detecção por anti-bots.
*   **Documentação Automática:** Swagger UI e ReDoc integrados.

## 🛠️ Tecnologias

*   [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno e rápido.
*   [Playwright](https://playwright.dev/) - Automação de navegador para scraping avançado.
*   [Playwright Stealth](https://pypi.org/project/playwright-stealth/) - Evasão de detecção de bots.
*   [Uvicorn](https://www.uvicorn.org/) - Servidor ASGI.

## 📦 Instalação

### Pré-requisitos

*   Python 3.8+
*   Navegadores do Playwright

### Passos

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/SEU_USUARIO/AnimeskaAPI.git
    cd AnimeskaAPI
    ```

2.  **Crie um ambiente virtual (Recomendado):**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Instale os navegadores do Playwright:**
    ```bash
    playwright install chromium
    ```

### Usando Makefile (Mais Simples)

Se você tiver `make` instalado, pode usar comandos simplificados:

```bash
make install # Instala dependências e browsers
make dev     # Roda em modo desenvolvimento (reload ativado)
make run     # Roda em modo normal
make build   # Constrói a imagem Docker
```

### Manualmente

Inicie o servidor:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em `http://localhost:8000`.

*   **Docs Interativa (Swagger):** `http://localhost:8000/docs`
*   **ReDoc:** `http://localhost:8000/redoc`

### Docker

```bash
docker build -t animeska-api .
docker run -p 8000:8000 animeska-api
```

## 📁 Estrutura do Projeto

*   `app/`: Código fonte principal (FastAPI).
*   `scripts/`: Scripts utilitários de teste e inspeção.
*   `deploy/`: Arquivos de configuração para deploy (Vercel, etc).
*   `Makefile`: Comandos de atalho para desenvolvimento.
*   `pyproject.toml`: Metadados modernos do projeto Python.

## 🌐 Demo Online

A API está rodando em produção no Render:
**Base URL:** `https://animeska-api.onrender.com`

> **Nota:** O primeiro request pode demorar até 50 segundos pois o Render "adormece" o serviço gratuito por inatividade.

## 📖 Endpoints e Exemplos de Uso

### 1. Buscar Animes
**GET** `/api/v1/search`

**Parâmetros:**
*   `q`: Termo de busca (ex: `Naruto`).
*   `source`: (Opcional) Filtrar por fonte. Valores: `animes_hd`, `animes_digital`, `animes_online_cc`.

```bash
```bash
curl "https://animeska-api.onrender.com/api/v1/search?q=Jujutsu&source=animes_digital"
```

**Exemplo de Resposta:**
```json
[
  {
    "slug": "jujutsu-kaisen-2-dublado",
    "title": "Jujutsu Kaisen 2 Dublado",
    "url": "https://animesdigital.org/...",
    "cover_image": "https://...",
    "source": "AnimesDigital",
    "description": "A boy fights... for 'the right death'...",
    "score": 84,
    "status": "FINISHED",
    "genres": ["Action", "Fantasy"]
  }
]
```

### 2. Detalhes do Anime
**GET** `/api/v1/anime/details`

```bash
# Exemplo com URL codificada (recomendado)
curl "https://animeska-api.onrender.com/api/v1/anime/details?source=AnimesHD&url=https%3A%2F%2Fanimeshd.to%2Fanimes%2Fnaruto-shippuden-dublado%2F"
```

**Exemplo de Resposta:**
```json
{
  "slug": "naruto-shippuden-dublado",
  "title": "Naruto Shippuden",
  "description": "Naruto Uzumaki quer ser o melhor ninja...",
  "genres": ["Ação", "Aventura"],
  "year": "2007",
  "status": "Completo",
  "season": "1",
  "source": "AnimesHD",
  "episodes": [
    {
      "number": "1",
      "title": "Episódio 1",
      "url": "https://animeshd.to/episodio/1"
    }
  ]
}
```

### 3. Link do Episódio
**GET** `/api/v1/episode/link`

```bash
curl "https://animeska-api.onrender.com/api/v1/episode/link?source=AnimesHD&url=https%3A%2F%2Fanimeshd.to%2Fepisodio%2F..."
```

### 4. Play Rápido (Simplificado) ✅
**GET** `/api/v1/anime/play`

Este endpoint tenta encontrar e extrair o link do vídeo automaticamente. Se o `source` não for informado, a API escolhe a melhor fonte automaticamente (priorizando `AnimesDigital`).

```bash
# Modo "Discovery" (Automático)
curl "https://animeska-api.onrender.com/api/v1/anime/play?slug=jujutsu-kaisen&number=1"
```

**Parâmetros:**
*   `slug`: O identificador ou título aproximado do anime (ex: `jujutsu-kaisen`).
*   `number`: O número do episódio (ex: `1`).
*   `source`: (Opcional) Forçar uma fonte específica (`AnimesDigital`, `AnimesHD`, `AnimesOnlineCC`).


### Render (Recomendado)

1.  Crie um novo **Web Service** no Render.
2.  Conecte seu repositório GitHub/GitLab.
3.  **Runtime:** Python 3.
4.  **Build Command:** `pip install -r requirements.txt && playwright install chromium`
5.  **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Vercel (Experimental)

Arquivos de configuração para Vercel estão disponíveis em `deploy/vercel`.

> **Nota:** Deploy em Serverless (como Vercel) pode encontrar limitações devido ao tamanho dos binários do navegador Playwright. Recomendamos o uso de containers (Docker/Render/Railway) para maior estabilidade, mas oferecemos suporte experimental para Vercel via `@vercel/python`.

## 📝 Fontes Suportadas

| Fonte | Status | Observações |
| :--- | :--- | :--- |
| **AnimesHD** | ✅ Online | Busca, Detalhes Ricos, Extração via Network Sniffing |
| **AnimesDigital** | ✅ Online | Busca, Detalhes Ricos, Extração via Network Sniffing |
| **AnimesOnlineCC** | ✅ Online | Busca, Detalhes Ricos, Extração via Network Sniffing |

## ⚠️ Aviso Legal

Esta API é apenas para fins educacionais e de aprendizado. O desenvolvedor não incentiva a pirataria nem se responsabiliza pelo uso indevido. Todo o conteúdo é propriedade de seus respectivos donos.
