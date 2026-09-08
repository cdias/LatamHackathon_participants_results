"""Geração de texto promocional via Amazon Bedrock (Claude 3 Haiku, ap-southeast-1).
Se o Bedrock falhar (sem chave, região, indisponível), cai num template local — o produto
continua funcionando (RF-005, RNF-002)."""
import json
import logging
from .config import get_settings

log = logging.getLogger("airrevenue.bedrock")


def _fmt(v: float) -> str:
    return f"US$ {v:,.2f}"


def _fallback(route: str, discount_pct: int, airline: str,
              price_old: float, price_new: float) -> str:
    return (
        f"Oferta {airline}: voo {route} com {discount_pct}% de desconto! "
        f"De {_fmt(price_old)} por {_fmt(price_new)}. "
        f"Assentos limitados — garanta o seu e viaje pagando menos. Reserve agora."
    )


def generate_promo_copy(*, route: str, discount_pct: int, airline: str,
                        price_old: float = 0.0, context: str = "") -> tuple[str, str]:
    """Retorna (texto, origem) onde origem ∈ {'bedrock','fallback'}.
    Inclui preço antigo e preço com desconto no texto."""
    s = get_settings()
    price_new = round(price_old * (1 - discount_pct / 100), 2)

    if not s.aws_bearer_token_bedrock:
        return _fallback(route, discount_pct, airline, price_old, price_new), "fallback"
    try:
        import boto3
        client = boto3.client("bedrock-runtime", region_name=s.aws_region)
        prompt = (
            f"Você é redator de marketing da companhia aérea {airline}. "
            f"Escreva UMA promoção curta (máx 350 caracteres), em português, tom animado e "
            f"profissional, para preencher assentos ociosos do voo {route} com {discount_pct}% "
            f"de desconto. INCLUA obrigatoriamente o preço antigo ({_fmt(price_old)}) e o preço "
            f"com desconto ({_fmt(price_new)}) no texto. {context} "
            f"Não use emojis em excesso. Responda só com o texto."
        )
        resp = client.invoke_model(
            modelId=s.bedrock_model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}],
            }),
        )
        text = json.loads(resp["body"].read())["content"][0]["text"].strip()
        return text[:500], "bedrock"
    except Exception as e:  # noqa: BLE001 — qualquer falha vira fallback
        log.warning("Bedrock indisponível, usando fallback: %s", type(e).__name__)
        return _fallback(route, discount_pct, airline, price_old, price_new), "fallback"
