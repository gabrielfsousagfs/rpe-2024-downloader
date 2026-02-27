import asyncio
import os
import zipfile
from playwright.async_api import async_playwright

# =========================
# CONFIGURAÇÃO DO BLOCO
# =========================
START_ID = 0
END_ID = 999  # ajuste conforme quiser expandir
SAVE_FOLDER = "pdfs_rpe_2024"
ZIP_NAME = f"RPE_2024_{START_ID}_{END_ID}.zip"

BASE_URL = "https://sistema-registropublicodeemissoesapi.fgv.br/GenerateReport/GenerateInventoryReport/{}/18/true"

os.makedirs(SAVE_FOLDER, exist_ok=True)

async def main():
    print("Script iniciou.")
    download_count = 0

    print("Iniciando Playwright...")

    async with async_playwright() as p:
        print("Playwright iniciado.")
        print("Abrindo Chromium...")
        browser = await p.chromium.launch(headless=True)
        print("Chromium aberto.")
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        for participant_id in range(START_ID, END_ID + 1):
            formatted_id = f"{participant_id:04d}"
            url = BASE_URL.format(formatted_id)

            try:
                print(f"Tentando {formatted_id}")

                async with page.expect_download(timeout=10000) as download_info:
                    await page.goto(url)

                download = await download_info.value
                path = os.path.join(SAVE_FOLDER, f"{formatted_id}.pdf")
                await download.save_as(path)

                download_count += 1
                print(f"✔ PDF salvo {formatted_id}")

            except Exception:
                print(f"✖ Não encontrado {formatted_id}")

            # pausa para evitar bloqueio
            await asyncio.sleep(0.8)

        await browser.close()

    # Criar ZIP apenas se houver PDFs
    if download_count > 0:
        with zipfile.ZipFile(ZIP_NAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in os.listdir(SAVE_FOLDER):
                zipf.write(os.path.join(SAVE_FOLDER, file), file)

        print(f"ZIP criado: {ZIP_NAME}")
    else:
        print("Nenhum PDF encontrado neste bloco.")

    print("===================================")
    print(f"Total de PDFs baixados: {download_count}")
    print("===================================")

asyncio.run(main())