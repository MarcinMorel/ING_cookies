import asyncio
from playwright.async_api import async_playwright

#Funkcja podająca wyniki w konsoli, a także zapisująca do pliku
def log_message(message, log_file):
    print(message)
    log_file.write(message + "\n")

async def check_and_log_cookie(cookies, log_file):
    #Funkcja sprawdzająca czy zapisywane są cookies analityczne
    for cookie in cookies:
        if cookie.get('name') == 'cookiePolicyGDPR' and cookie.get('value') == '3':
            log_message("Cookies analityczne zapisywane prawidłowo", log_file)
            break

async def handle_cookie_policy(browser_name, executable_path=None, log_file=None):
    async with async_playwright() as p:
        #Uruchamia wybraną przeglądarkę, z oddzielną ścieżką do MS Edge
        if browser_name == "chromium" and executable_path:
            log_message(f"[{browser_name.upper()}] Launching from path: {executable_path}", log_file)
            browser = await p.chromium.launch(
                headless=False,
                executable_path=executable_path  #Ścieżka do edge'a
            )
        else:
            browser = await getattr(p, browser_name).launch(headless=False)

        context = await browser.new_context()
        page = await context.new_page()

        #Krok 1: Wejście na odpowiednią stronę
        async def navigate_to_url():
            url = "https://www.ing.pl/"
            log_message(f"[{browser_name.upper()}] Visiting {url}", log_file)
            await page.goto(url)

        await navigate_to_url()

        #Krok 2: Kliknięcie przycisku 'Dostosuj' bądź 'Ustawienia plików cookie', jeśli to kolejna wizyta na stronie
        async def click_cookie_buttons():
            try:
                await page.locator("button.js-cookie-policy-main-settings-button.cookie-policy-button.is--primary").click()
                log_message(f"[{browser_name.upper()}] Clicked the 'Dostosuj' button.", log_file)
            except Exception as e:
                log_message(f"[{browser_name.upper()}] 'Dostosuj' button not found: {e}", log_file)
                try:
                    await page.locator("a.cookie-policy-recallBanner-link[role='button']").click()
                    log_message(f"[{browser_name.upper()}] Clicked the fallback 'ustawienia plików cookie' button.", log_file)
                except Exception as fallback_error:
                    log_message(f"[{browser_name.upper()}] Both buttons not found: {fallback_error}", log_file)
                    log_message(f"[{browser_name.upper()}] Clearing cookies and restarting from Step 1.", log_file)
                    
                    #Usuwanie cookies w przypadku, gdy oba przyciski nie zostaną znalezione oraz restart od wejścia na stronę
                    await context.clear_cookies()
                    log_message(f"[{browser_name.upper()}] Cookies cleared.", log_file)
                    await navigate_to_url()
                    await click_cookie_buttons()

        await click_cookie_buttons()

        #Krok 3: Sprawdzenie i wybranie odpowiednich opcji zapisu cookies
        async def adjust_cookie_policies():
            try:
                #Zaznaczenie opcji 'Cookies Analityczne', jeśli nie była zaznaczona
                analytical_selector = "label.cookie-policy-switch-label[for='CpmAnalyticalOption']"
                input_selector = "#CpmAnalyticalOption"
                is_checked = await page.locator(input_selector).is_checked()
                if not is_checked:
                    await page.locator(analytical_selector).click()
                    log_message(f"[{browser_name.upper()}] Enabled the 'Analytical Option'.", log_file)
                else:
                    log_message(f"[{browser_name.upper()}] 'Analytical Option' is already enabled.", log_file)

                #Odznaczenie opcji 'Cookies Marketingowe', jeśli nie była odznaczona
                marketing_selector = "label.cookie-policy-switch-label[for='CpmMarketingOption']"
                marketing_input = "#CpmMarketingOption"
                is_marketing_checked = await page.locator(marketing_input).is_checked()
                if is_marketing_checked:
                    await page.locator(marketing_selector).click()
                    log_message(f"[{browser_name.upper()}] Disabled the 'Marketing Option'.", log_file)
                else:
                    log_message(f"[{browser_name.upper()}] 'Marketing Option' is already disabled.", log_file)
            except Exception as e:
                log_message(f"[{browser_name.upper()}] Error adjusting cookie policies: {e}", log_file)
                await browser.close()
                return

        await adjust_cookie_policies()

        #Krok 4: Kliknięcie przycisku 'Zaakceptuj wybrane'
        try:
            await page.locator("button.js-cookie-policy-settings-decline-button.cookie-policy-button.is--primary").click()
            log_message(f"[{browser_name.upper()}] Clicked the 'Zaakceptuj wybrane' button.", log_file)
        except Exception as e:
            log_message(f"[{browser_name.upper()}] Failed to click 'Zaakceptuj wybrane' button: {e}", log_file)
            await browser.close()
            return

        #Krok 5: Spawdzenie czy odpowiednie cookies zapisują się w pamięci przeglądarki
        try:
            cookies = await context.cookies()
            if cookies:
                log_message(f"[{browser_name.upper()}] Cookies saved in browser memory: {cookies}", log_file)
                await check_and_log_cookie(cookies, log_file)
            else:
                log_message(f"[{browser_name.upper()}] No cookies found in browser memory.", log_file)
        except Exception as e:
            log_message(f"[{browser_name.upper()}] Error verifying cookies: {e}", log_file)

        #Zamknięcie przeglądarki
        await browser.close()
        log_message(f"[{browser_name.upper()}] Test completed.", log_file)

async def main():
    #Ścieżki do plików wykonywalnych przeglądarek opartych na chromium (w celu rozróżnienia i sprawdzenia obu)
    chrome_executable_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"  #Ścieżka do Chrome
    edge_executable_path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"  #Ścieżka do Edge
    
    #Lista przeglądarek do sprawdzenia (włącznie z Firefoxem)
    browsers = [
        ("chromium", chrome_executable_path),
        ("chromium", edge_executable_path),
        ("firefox", None)
    ]
    
    #Zapisanie pliku z wynikami
    with open("results.txt", "w") as log_file:
        tasks = [handle_cookie_policy(browser_name, executable_path, log_file) for browser_name, executable_path in browsers]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
