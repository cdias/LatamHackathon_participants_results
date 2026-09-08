# Ask the Airport — Produto

## Problema
Analistas de operações aeroportuárias (ex: Marina, analista de ops de uma companhia aérea)
precisam responder perguntas sobre voos, reservas e disrupções, mas não sabem SQL e não têm
tempo de esperar um analista de dados montar uma query.

## Solução
Um copiloto conversacional: a pessoa pergunta em português, o sistema gera o SQL sobre o
banco `airportdb` no TiDB, executa, e devolve uma explicação em linguagem simples — incluindo,
quando relevante, um alerta de risco de atraso cruzando o voo com as condições de clima
(`weatherdata`) no aeroporto e horário do voo.

## Usuário
Marina, analista de operações. Ela quer saber rápido "esse voo vai atrasar? por quê?" sem
abrir um editor SQL.

## Diferencial
Não é só texto-para-SQL genérico: o sistema explica o "porquê" da disrupção cruzando clima e
voo, e usa busca vetorial (`EMBED_TEXT` no TiDB) para achar voos com padrões de risco
parecidos — "me ache voos parecidos com esse risco de chuva".
