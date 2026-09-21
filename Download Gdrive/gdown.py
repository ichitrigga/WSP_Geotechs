from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch_persistent_context(
        user_data_dir=r"C:\Python\EdgeProfile",
        channel="msedge",
        accept_downloads=True,
        headless=False
    )

    page = browser.new_page()

    page.goto(
        "https://drive.google.com/drive/u/2/folders/1cnNd6hWsZxNNJCRETJ0QgdL6x32cgnrm"
    )

    input("Press Enter after Drive has loaded...")

    browser.close()