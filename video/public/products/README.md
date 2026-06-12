# Product images — drop-in folder for carousels

Curated product photos that the carousel compositions can render **without network**
(the cloud sandbox 403s every remote image host, so URL-based images only resolve when
rendered on a network-open machine — local files here always work).

## Convention
- Drop a file named for the product: `video/public/products/<slug>.png` (or `.jpg` / `.webp`).
  Examples: `gatorade-sports-drink.png`, `aquafresh-toothpaste.webp`, `sainsburys-oats.png`.
- Prefer a **clean shot on a white/transparent background** — it sits in a white rounded panel.
- In the props JSON, set the item's `image` to the **local path** (no leading slash):
  `"image": "products/gatorade-sports-drink.png"`. The composition resolves it via `staticFile()`.

## Why local beats the DB `image_url`
The DB has a photo for most products, but they're raw source images (news photos, Reddit
claim uploads) and many hosts 403 in the sandbox. A curated local file: (1) renders in-sandbox
so Claude can deliver a *finished* carousel as files, and (2) is reusable across carousels.

## Fallback
No `image` set → the slide renders a labelled `PRODUCT PHOTO` placeholder marking the reserved
zone. The carousel never breaks; the photo is the last cosmetic layer.
