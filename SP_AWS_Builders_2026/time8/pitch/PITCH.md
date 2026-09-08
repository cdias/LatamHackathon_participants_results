# GateMate — Copiloto Pessoal do Passageiro Conectado

## O Pitch (2 minutos)

---

### 1. O Problema (15 segundos)

Você está no aeroporto. Seu voo atrasou 2 horas.
Você não sabe o que fazer, onde ir, ou quanto tempo tem.
O app da companhia aérea te mostra o número do portão. Só isso.

---

### 2. A Solução (20 segundos)

**GateMate.** Você digita seu código de reserva.
O sistema já sabe seu voo, seu status, quanto tempo você tem.
Você escreve em linguagem natural: *"preciso de café e uma tomada perto do portão"*.
Em segundos: um plano de 3 passos. Empático. Acionável. Seu.

---

### 3. A Demo (60 segundos)

> **Mostrar ao vivo em https://airport-concierge-ai.lovable.app/**

1. Digitar um código de reserva → sistema mostra nome, voo, status (Delayed)
2. Digitar: *"Meu voo atrasou 3 horas, preciso carregar o celular e tomar um café"*
3. GateMate retorna:
   - **Passo 1** — Dirija-se ao Café Gourmet no Terminal 2, portão B12 (3 min a pé)
   - **Passo 2** — Há tomadas disponíveis no lounge próximo ao portão B14
   - **Passo 3** — Você tem tempo de sobra — seu portão reabre às 19h40

---

### 4. A Tech Stack (20 segundos)

- **TiDB Cloud** — banco relacional + busca vetorial nativa com `EMBED_TEXT` e `VEC_COSINE_DISTANCE`
- **Amazon Bedrock** — Claude 3 Haiku em `ap-southeast-1` para geração do plano empático
- **FastAPI + React** — backend e frontend publicados na EC2 em `sa-east-1`
- **Construído com Kiro** — spec-driven, `.kiro/` commitado

---

### 5. O Valor de Negócio (5 segundos)

**Usuário**: o passageiro perdido num aeroporto estressante.
**Resultado**: menos ansiedade, mais tempo aproveitado, experiência que fideliza.

---

## Frase de fechamento

> *"A companhia aérea te dá o número do portão. O GateMate te dá o próximo passo."*

