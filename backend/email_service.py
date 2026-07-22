import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY", "re_6wFXY7ic_FNVQh4Su2rxXU9zxCY2eSzsi")

SELLER_EMAIL = os.getenv("SELLER_EMAIL", "minhhoangle2909@gmail.com")
FROM_EMAIL = "orders@resend.dev"


def build_buyer_email_html(order_id: str, items: list[dict], total: float) -> str:
    rows = ""
    for item in items:
        rows += f"""
        <tr>
            <td style="padding:8px;border-bottom:1px solid #eee;">{item.get('product_name', 'Produit')}</td>
            <td style="padding:8px;border-bottom:1px solid #eee;text-align:center;">{item.get('size', '')}</td>
            <td style="padding:8px;border-bottom:1px solid #eee;text-align:center;">{item.get('color', '')}</td>
            <td style="padding:8px;border-bottom:1px solid #eee;text-align:center;">{item.get('quantity', 1)}</td>
            <td style="padding:8px;border-bottom:1px solid #eee;text-align:right;">{item.get('subtotal', 0):.2f}€</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><title>Commande #{order_id}</title></head>
<body style="font-family:Arial,sans-serif;background:#f9f9f9;margin:0;padding:20px;">
  <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
    <div style="background:#1a1a1a;padding:30px;text-align:center;">
      <h1 style="color:#fff;margin:0;font-size:24px;">Commande confirmée ✓</h1>
    </div>
    <div style="padding:30px;">
      <p style="font-size:16px;color:#333;">Merci pour votre commande ! Voici votre récapitulatif :</p>
      <p style="color:#666;"><strong>Numéro de commande :</strong> #{order_id}</p>

      <table style="width:100%;border-collapse:collapse;margin:20px 0;">
        <thead>
          <tr style="background:#f5f5f5;">
            <th style="padding:10px;text-align:left;">Produit</th>
            <th style="padding:10px;text-align:center;">Taille</th>
            <th style="padding:10px;text-align:center;">Couleur</th>
            <th style="padding:10px;text-align:center;">Qté</th>
            <th style="padding:10px;text-align:right;">Sous-total</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>

      <div style="text-align:right;padding:10px 0;border-top:2px solid #1a1a1a;">
        <strong style="font-size:18px;">Total : {total:.2f}€</strong>
      </div>

      <div style="background:#f0f9ff;border-radius:6px;padding:15px;margin-top:20px;">
        <p style="margin:0;color:#0369a1;"><strong>Livraison estimée :</strong> 2–3 jours ouvrés en France</p>
        <p style="margin:5px 0 0;color:#0369a1;font-size:14px;">Votre commande est traitée par Gelato EU.</p>
      </div>
    </div>
    <div style="background:#f5f5f5;padding:20px;text-align:center;color:#999;font-size:12px;">
      <p style="margin:0;">© 2026 Demo Shop — T-Shirts personnalisés</p>
    </div>
  </div>
</body>
</html>"""


def build_seller_email_html(buyer_email: str, order_id: str, items: list[dict], total: float) -> str:
    rows = ""
    for item in items:
        rows += f"""
        <tr>
            <td style="padding:8px;border-bottom:1px solid #eee;">{item.get('product_name', 'Produit')}</td>
            <td style="padding:8px;border-bottom:1px solid #eee;text-align:center;">{item.get('size', '')}</td>
            <td style="padding:8px;border-bottom:1px solid #eee;text-align:center;">{item.get('color', '')}</td>
            <td style="padding:8px;border-bottom:1px solid #eee;text-align:center;">{item.get('quantity', 1)}</td>
            <td style="padding:8px;border-bottom:1px solid #eee;text-align:right;">{item.get('subtotal', 0):.2f}€</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><title>Nouvelle commande #{order_id}</title></head>
<body style="font-family:Arial,sans-serif;background:#f9f9f9;margin:0;padding:20px;">
  <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
    <div style="background:#dc2626;padding:30px;text-align:center;">
      <h1 style="color:#fff;margin:0;font-size:24px;">🛍 Nouvelle commande</h1>
    </div>
    <div style="padding:30px;">
      <p style="font-size:16px;color:#333;"><strong>Commande #{order_id}</strong></p>
      <p style="color:#666;"><strong>Client :</strong> {buyer_email}</p>
      <p style="color:#666;"><strong>Montant total :</strong> {total:.2f}€</p>

      <table style="width:100%;border-collapse:collapse;margin:20px 0;">
        <thead>
          <tr style="background:#f5f5f5;">
            <th style="padding:10px;text-align:left;">Produit</th>
            <th style="padding:10px;text-align:center;">Taille</th>
            <th style="padding:10px;text-align:center;">Couleur</th>
            <th style="padding:10px;text-align:center;">Qté</th>
            <th style="padding:10px;text-align:right;">Sous-total</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>

      <div style="text-align:right;padding:10px 0;border-top:2px solid #dc2626;">
        <strong style="font-size:18px;">Total : {total:.2f}€</strong>
      </div>

      <p style="color:#666;font-size:14px;margin-top:20px;">
        Action requise : Transmettez cette commande à Gelato pour la production et livraison.
      </p>
    </div>
  </div>
</body>
</html>"""


def send_order_confirmation(buyer_email: str, order_id: str, items: list[dict], total: float) -> None:
    html = build_buyer_email_html(order_id, items, total)
    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": buyer_email,
            "subject": f"Commande #{order_id} confirmée ✓",
            "html": html,
        })
    except Exception as exc:
        print(f"[email] Failed to send confirmation to {buyer_email}: {exc}")


def send_seller_notification(buyer_email: str, order_id: str, items: list[dict], total: float) -> None:
    html = build_seller_email_html(buyer_email, order_id, items, total)
    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": SELLER_EMAIL,
            "subject": f"🛍 Nouvelle commande #{order_id} — {total:.2f}€",
            "html": html,
        })
    except Exception as exc:
        print(f"[email] Failed to send seller notification: {exc}")
