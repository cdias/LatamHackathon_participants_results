# AirRevenue — Descritivo de Negócio

## Visão Geral

**AirRevenue** é um copiloto de *revenue management* para companhias aéreas. Ele identifica
voos que vão partir nos próximos dias com **assentos ociosos** e recomenda **promoções
direcionadas** aos **passageiros frequentes** com maior probabilidade de comprar aquele
assento — gerando o texto da campanha com IA generativa (Amazon Bedrock) e encontrando
públicos "parecidos" por **busca vetorial** no TiDB.

- **Contexto:** cada assento que decola vazio é receita perdida de forma irreversível
  (*perishable inventory*). O trabalho do *revenue manager* é encher o voo antes da partida,
  ao maior preço possível, sem canibalizar vendas que aconteceriam de qualquer forma.
- **Stakeholders:**
  - *Revenue Manager / Analista de Malha* (usuário primário) — decide quais voos promover.
  - *Marketing / CRM* — dispara as campanhas aprovadas aos passageiros.
  - *Passageiro frequente* — recebe a oferta relevante.
- **Escopo macro:** uma aplicação web multi-tenant (uma área por companhia) que lê a base
  operacional (voos, reservas, passageiros) no TiDB, calcula ociosidade e propensão,
  recomenda alvos e permite criar/salvar campanhas promocionais.

## Situação Atual (As-Is)

- A companhia enxerga a ociosidade **depois**, em relatórios de BI, quando o voo já partiu.
- A seleção de "quem recebe promoção" é feita por regras manuais e planilhas, sem cruzar
  histórico do passageiro com o voo específico que precisa ser preenchido.
- O texto das campanhas é redigido manualmente pelo marketing, com atraso de dias.
- Ferramentas: sistemas de reservas (PSS), BI (Tableau/PowerBI), planilhas, ferramenta de
  e-mail marketing — desconectados entre si.

## Desafios e Dores

1. **Ociosidade só visível tarde demais** — *impacto:* receita perdida por voo. *Prioridade:* crítico.
2. **Seleção de público genérica** — promoções vão para toda a base, com baixa conversão e
   desconto desnecessário a quem compraria mesmo. *Prioridade:* alto.
3. **Tempo de produção da campanha** — redação manual leva dias; o voo parte antes. *Prioridade:* alto.
4. **Falta de priorização** — o analista não sabe *qual* voo promover primeiro (maior ganho marginal). *Prioridade:* médio.
5. **Isolamento de dados entre companhias** — em um cenário multi-tenant, cada companhia só
   pode ver os próprios voos/passageiros. *Prioridade:* crítico (segurança).

## Oportunidades de Melhoria

- **Quick win:** ranquear voos por *assentos ociosos × dias-até-partida* e sugerir os top N.
- **Propensão:** priorizar passageiros frequentes que já voaram a rota/companhia.
- **IA generativa:** rascunhar o texto da promoção em segundos, no tom da marca.
- **Busca semântica:** "encontre passageiros/rotas parecidos com este perfil" via vetores.
- **Métricas de sucesso:** assentos ociosos recomendados por dia, campanhas criadas,
  tempo de produção da campanha (de dias para segundos), cobertura de passageiros-alvo.

## Premissas e Restrições

- **Dados:** dataset `airportdb` do hackathon (janela 2015-06-02 a 2015-06-09) no TiDB Cloud.
  O dado é sintético; a lógica de negócio é real e transferível a dados de produção.
- **Segurança:** modelo *zero-trust* — toda requisição autenticada por JWT curto; todo dado
  filtrado pelo `airline_id` do token (isolamento multi-tenant); segredos só em `.env`.
- **Infra:** backend Python/FastAPI e frontend Vue publicados na **EC2 do time (sa-east-1)**.
  A conta do hackathon nega Lambda/CloudFront/S3-create (chave *bedrock-only*), então o
  deploy serverless (SAM + S3/CloudFront) é entregue **pronto e documentado** em `infra/`
  como alternativa, mas o deploy executado é na EC2 (que pontua igual).
- **IA:** Amazon Bedrock em **ap-southeast-1** (Claude 3 Haiku para texto). Fallback: se o
  Bedrock estiver indisponível, a recomendação funciona sem o texto gerado.
- **Restrição de tempo:** protótipo de hackathon (2h30) — foco no loop principal funcionando.
