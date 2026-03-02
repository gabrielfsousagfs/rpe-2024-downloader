import asyncio
import os
import zipfile
from playwright.async_api import async_playwright

# =========================
# CONFIGURAÇÃO GLOBAL
# =========================
START_ID = 0
END_ID = 9999
BATCH_SIZE = 500
SAVE_ROOT = "pdfs_rpe_2024"
BASE_URL = "https://sistema-registropublicodeemissoesapi.fgv.br/GenerateReport/GenerateInventoryReport/{}/18/true"

os.makedirs(SAVE_ROOT, exist_ok=True)


async def process_batch(p, batch_start, batch_end):
    print(f"\n========== PROCESSANDO LOTE {batch_start:04d}-{batch_end:04d} ==========")

    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context(accept_downloads=True)
    page = await context.new_page()

    batch_folder = os.path.join(SAVE_ROOT, f"{batch_start:04d}_{batch_end:04d}")
    os.makedirs(batch_folder, exist_ok=True)

    download_count = 0

    for participant_id in range(batch_start, batch_end + 1):
        formatted_id = f"{participant_id:04d}"
        url = BASE_URL.format(formatted_id)

        try:
            print(f"Tentando {formatted_id}")

            async with page.expect_download(timeout=10000) as download_info:
                await page.goto(url)

            download = await download_info.value
            path = os.path.join(batch_folder, f"{formatted_id}.pdf")
            await download.save_as(path)

            download_count += 1
            print(f"✔ PDF salvo {formatted_id}")

        except Exception:
            print(f"✖ Não encontrado {formatted_id}")

        await asyncio.sleep(1)

    await browser.close()

    if download_count > 0:
        zip_name = f"RPE_2024_{batch_start:04d}_{batch_end:04d}.zip"
        zip_path = os.path.join(SAVE_ROOT, zip_name)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in os.listdir(batch_folder):
                zipf.write(os.path.join(batch_folder, file), file)

        print(f"ZIP criado: {zip_name}")
    else:
        print("Nenhum PDF neste lote.")

    print(f"Total no lote: {download_count}")
    print("====================================================")


async def main():
    print("INICIANDO VARREDURA COMPLETA 0000–9999\n")

    async with async_playwright() as p:
        for batch_start in range(START_ID, END_ID + 1, BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE - 1, END_ID)
            await process_batch(p, batch_start, batch_end)

    print("\nVARREDURA FINALIZADA.")


asyncio.run(main())