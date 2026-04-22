# Guia de Configuração do Stripe 💸

Para o RoboTutor cobrar os usuários, você precisa preencher 4 chaves no arquivo `.env` (local) ou nas Configurações da Vercel/Render (produção).

## 1. Pegar as Chaves de API
1.  Acesse o [Dashboard do Stripe](https://dashboard.stripe.com/).
2.  No menu esquerdo (ou busca), vá em **Developers (Desenvolvedores) -> API Keys**.
3.  Copie a **Secret Key** (começa com `sk_test_...`).
    *   *Variável:* `STRIPE_SECRET_KEY`

## 2. Criar o Produto (Plano Mensal)
1.  Vá em **Products (Produtos) -> Add Product**.
2.  **Nome**: "RoboTutor Premium".
3.  **Preço**: R$ 4,99.
4.  **Cobrança**: "Recurring" (Recorrente) -> "Monthly" (Mensal).
5.  Salve.
6.  Na página do produto criado, procure pelo **API ID** do preço (começa com `price_...`).
    *   *Variável:* `STRIPE_PRICE_ID`

## 3. Criar o Cupom (Promoção 1º Mês)
1.  Vá em **Products -> Coupons (Cupons)**.
2.  Clique em **+ New**.
3.  **Nome**: "Primeiro Mês Promocional".
4.  **Tipo**: "Fixed amount" (Valor fixo) -> R$ 10,00 off  **OU** "Percentage" -> 50% off.
5.  **Duração**: "Once" (Uma vez) - *Isso é importante para descontar só no 1º mês!*
6.  Salve e copie o **ID** (ex: `1MESOFF` ou `coupon_...`).
    *   *Variável:* `STRIPE_PROMO_COUPON_ID`

## 4. Configurar o Webhook (Para liberar o acesso)
1.  Vá em **Developers -> Webhooks**.
2.  Clique em **Add Endpoint**.
3.  **Endpoint URL**:
    *   Local: Use o CLI do Stripe (`stripe listen`).
    *   Produção: `https://site-do-seu-robo.vercel.app/webhook/` (Não esqueça da barra no final).
4.  **Events to send**: Selecione `checkout.session.completed`.
5.  Salve.
6.  Copie o **Signing Secret** (começa com `whsec_...`).
    *   *Variável:* `STRIPE_WEBHOOK_SECRET`

---

## Onde colar isso?
No seu arquivo `.env` ou no painel da Vercel:

```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PRICE_ID=price_...
STRIPE_PROMO_COUPON_ID=coupon_...
STRIPE_WEBHOOK_SECRET=whsec_...
```
