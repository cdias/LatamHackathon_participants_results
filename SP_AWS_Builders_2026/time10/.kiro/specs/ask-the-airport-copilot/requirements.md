# Requirements — Ask the Airport Copilot

1. Como Marina (analista de ops), quero perguntar em português sobre voos/reservas/clima e
   receber uma resposta direta, sem escrever SQL.
2. Como Marina, quero que o sistema me avise quando um voo tem risco de atraso por causa do
   clima, explicando o motivo em linguagem simples.
3. Como Marina, quero poder buscar voos com padrão de risco parecido com um voo específico
   (busca semântica sobre notas de risco).
4. O sistema não pode executar nada além de SELECT no banco.
5. A resposta completa (pergunta → SQL → execução → explicação) deve ficar dentro de poucos
   segundos, mesmo com a latência até o Bedrock em Singapura.
