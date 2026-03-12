# Plano de Desenvolvimento — MCP Server "Developer Guru"

## Visão Geral

Um servidor MCP via **FastMCP** que atua como consultor de código. A IDE envia um problema com nível, tecnologias, contexto e raciocínio, e o servidor roteia para a IA adequada (Gemini, Claude Opus, GPT 5.3 Codex) via **Agno**, retornando um pensamento refinado e sugestões acionáveis.

---

## Referências

- [FastMCP](https://github.com/fastmcp/fastmcp)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Agno](https://github.com/agno-ai/agno)
- [Claude Code](https://docs.claude.com/code)
- [Cursor](https://cursor.sh/)
- [GPT 5.3 Codex](https://openai.com/index/gpt-5-3-codex/)
- Agent Skills Criar sistema de instalação de skills parecido com o projeto skills_mcp_server que está em /mnt/d/Projetos/skills_mcp_server (POST /kills, POST /skills/upload, GET /skills, DELETE /skills/{unique_name})

---

## Arquitetura

```
IDE (MCP Client)
    │
    ▼
FastMCP Server ("developer-guru")
    │
    ├── Tool: consult(level, technologies, context, thinking)
    │
    ├── Prompt Builder (monta o system + user prompt)
    │
    ├── Router (level → provider)
    │   ├── novice   → Gemini (via Agno)
    │   ├── medium   → Claude Opus (via Agno)
    │   └── expert   → GPT 5.3 Codex (via Agno)
    │
    └── Response Parser → { thinking, suggestions }
```

---

## Estrutura de Pastas

```
developer-guru/
├── pyproject.toml
├── .env.example
├── README.md
├── .gitignore
├── routes/
    ├── skills.py
├── skills/
├── src/
│   ├── __init__.py
│   ├── server.py          # FastMCP server + tool registration
│   ├── models.py          # Pydantic: input/output schemas
│   ├── router.py          # level → provider mapping
│   ├── providers.py       # Agno agents (Gemini, Claude, GPT)
│   ├── prompts.py         # System prompt + user prompt builder
│   └── config.py          # Settings via pydantic-settings / .env
└── tests/
    ├── test_router.py
    ├── test_prompts.py
    └── test_server.py
```

---

## Etapas de Desenvolvimento

### 1. Setup do projeto

- Inicializar com `uv init` ou `pyproject.toml` manual.
- Dependências: `fastapi`, `fastmcp`, `agno`, `pydantic`, `pydantic-settings`, `python-dotenv`.
- Criar `.env.example` com placeholders para `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` e ou OPENROUTER_API_KEY.
- `config.py` carrega as keys e valida que a key correspondente ao nível requisitado existe.

### 2. Schemas (models.py)

- `ConsultInput` — Pydantic model com:
  - `level`: `Literal["novice", "medium", "expert"]`
  - `technologies`: `str` (comma-separated)
  - `context`: `str` (markdown)
  - `thinking`: `str` (markdown)
- `ConsultOutput` — Pydantic model com:
  - `thinking`: `str` (markdown)
  - `suggestions`: `list[str]` (cada item é markdown, pode conter código)

### 3. Prompt Engineering (prompts.py)

Dois componentes:

**System Prompt** — define o papel do consultor:
- Você é um consultor de desenvolvimento sênior.
- Analise o raciocínio do agente, identifique falhas ou confirme a abordagem.
- Responda SEMPRE em JSON com exatamente dois campos: `thinking` (string markdown) e `suggestions` (array de strings markdown).
- Adapte a profundidade e linguagem ao nível (`novice` = didático com exemplos, `medium` = direto com trade-offs, `expert` = conciso e avançado).
- As tecnologias informadas definem o escopo; não sugira migrar para outro stack.

**User Prompt** — template que injeta os 4 campos:
```
## Nível: {level}
## Tecnologias: {technologies}

### Contexto (código relevante)
{context}

### Raciocínio do agente
{thinking}

Analise o raciocínio acima, refine-o e forneça sugestões práticas.
Responda em JSON: { "thinking": "...", "suggestions": ["...", ...] }
```

### 4. Router (router.py)

Mapeamento simples:

```python
PROVIDER_MAP = {
    "novice": "gemini",
    "medium": "claude",
    "expert": "openai",
}
```

Uma função `get_agent(level: str) -> Agent` que retorna o agente Agno configurado com o provider correto e o system prompt.

### 5. Providers via Agno (providers.py)

Para cada provider, instanciar o `Agent` do Agno com:
- Model correspondente (ex: `Gemini(id="gemini-2.5-flash")`, `Claude(id="claude-opus-4-20250514")`, `OpenAIChat(id="gpt-5.3-codex")`)
- System prompt vindo de `prompts.py`
- `response_model=None` (resposta livre em JSON, parseada depois) **ou** usar structured output do Agno se o provider suportar
- Configurações de temperature baixa (~0.2) para respostas determinísticas

### 6. Server MCP (server.py)

```python
from fastmcp import FastMCP

mcp = FastMCP("developer-guru")

@mcp.tool()
async def consult(level, technologies, context, thinking) -> dict:
    # 1. Validar input com ConsultInput
    # 2. Montar prompt via prompts.build_user_prompt(...)
    # 3. Obter agent via router.get_agent(level)
    # 4. Chamar agent.arun(prompt)
    # 5. Parsear resposta JSON → ConsultOutput
    # 6. Retornar dict com thinking + suggestions
    ...
```

Registrar o tool com descrição clara para que o MCP client saiba quando invocá-lo.

### 7. Parsing e Error Handling

- Tentar `json.loads` na resposta do modelo.
- Se falhar, fazer fallback: extrair bloco ```json``` da resposta via regex.
- Se ainda falhar, retornar o texto bruto em `thinking` e uma suggestion pedindo para reformular.
- Timeout configurável por provider (Gemini rápido, GPT pode demorar mais).
- Retry com backoff para erros 429/5xx.

### 8. Testes

- **test_prompts.py** — Verifica que o prompt gerado contém os campos corretos e respeita o nível.
- **test_router.py** — Verifica que cada nível mapeia para o provider certo.
- **test_server.py** — Teste de integração com mock dos providers; envia input e valida que o output é um `ConsultOutput` válido.
- Opcionalmente, um teste e2e que chama o provider real (marcado como `@pytest.mark.integration`, não roda no CI).

### 9. Documentação e Configuração da IDE

- `README.md` com instruções de instalação, configuração das API keys, e como registrar o servidor no Claude Code / Cursor / outra IDE com suporte MCP.
- Exemplo de configuração MCP no `claude_desktop_config.json` ou equivalente.

---

## Decisões Técnicas a Validar

Antes de codar, vale definir:

1. **Structured output vs JSON livre** — Agno suporta `response_model` com Pydantic em alguns providers. Testar se funciona para os três ou se é melhor parsear manualmente.
2. **Streaming** — O MCP client da IDE espera resposta completa ou aceita streaming? Se aceitar, vale implementar para melhor UX.
3. **Modelo exato do GPT 5.3 Codex** — Verificar o model ID correto na API da OpenAI quando for implementar (o nome pode variar).
4. **Cache** — Vale cachear respostas para inputs idênticos? Provavelmente não, dado que contexto varia muito.
5. **Rate limiting** — Se múltiplas IDEs chamarem ao mesmo tempo, considerar semáforo ou fila.

---

Esse é o plano completo. Quando quiser partir para a implementação, é só dizer.