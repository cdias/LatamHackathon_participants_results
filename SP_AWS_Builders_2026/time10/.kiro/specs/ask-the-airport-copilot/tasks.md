# Tasks — Ask the Airport Copilot

- [x] Conferir schema real do dump (`python db.py`) e ajustar `seed_vector_notes.py`
- [x] Loop principal: pergunta → SQL → execução → explicação (`app.py`, `bedrock_client.py`)
- [x] Front-end mínimo funcionando (`static/index.html`)
- [x] Tabela `flight_notes` com `EMBED_TEXT` + query de exemplo com `VEC_COSINE_DISTANCE`
- [x] Auditar o dado antes de prometer feature: clima tem só 4 estações órfãs e o atraso é
      sempre 0 (flight.departure == flightschedule.departure). Recorte movido para
      ocupação/receita, que variam de verdade.
- [x] Expor a busca vetorial na aplicação (`vector_search.py`, `POST /api/similar`, bloco de
      busca semântica na tela)
- [ ] Deploy na EC2 (`0.0.0.0`, porta 8000)
- [ ] SUBMISSION.md: falta URL do deploy e link do vídeo
- [ ] Gravar demo de 2 minutos
