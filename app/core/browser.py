from DrissionPage import ChromiumOptions, ChromiumPage
from app.core.cloudflare import CloudflareBypasser
from app.core.fetcher import create_browser_fetcher
import time


SUBDOMAIN_PAYLOAD_MAP = {
    "ravensnowshoe": [18085, 18086],
    "verrado": [4977, 24734]
}

# Ana scraping fonksiyonu
def scrape_with_browser(date, start, end, count, subdomain):
    """
    Cloudflare korumasını otomatik olarak aşar, gerekli cookie ve header bilgilerini alır ve 
    JavaScript üzerinden fetch isteği gönderir. Modüler yapıda çalışır ve her subdomain için dinamik olarak işlem yapabilir.
    """
    print("Tarayıcı başlatılıyor...")
    #Tarayıcının bot olduğunu önlemek için
    options = ChromiumOptions()
    options.headless(False)  
    options.set_argument('--disable-blink-features=AutomationControlled')
    options.set_argument('--disable-gpu')
    options.set_argument('--no-sandbox')
    options.set_argument('--disable-dev-shm-usage')
    options.set_argument('--user-data-dir=./chrome_cf_session')  # session klasörü oluşturur

    # Chromium tabanlı tarayıcı başlatılır
    driver = ChromiumPage(addr_or_opts=options)

    # Bot tespiti azaltıcı JavaScript ayarları
    driver.run_js('''Object.defineProperty(navigator, 'webdriver', {get: () => undefined});''')
    driver.run_js('''Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });''')
    driver.run_js('''Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });''')
    driver.run_js('''navigator.permissions.query = () => Promise.resolve({state: "granted"});''')

    base_url = f"https://{subdomain}.ezlinksgolf.com"
    payload_ids = SUBDOMAIN_PAYLOAD_MAP.get(subdomain, [])

    print("Site açılıyor...")
    driver.get(base_url)
    driver.wait.ele_displayed("tag:body", timeout=30)
    time.sleep(2)

    print("Cloudflare kontrolü başlıyor...")
    cf = CloudflareBypasser(driver, max_retries=20)
    cf.bypass()

    # Eğer hâlâ "bir dakika" yazıyorsa Cloudflare geçilememiştir
    print("Sayfa başlığı:", driver.title)
    if "bir dakika" in driver.title.lower():
        return {
            "error": "Cloudflare aşılmadı",
            "title": driver.title,
            "html_snippet": driver.html[:300]
        }

    
    fetch = create_browser_fetcher(driver, base_url)
    payload = {
        "p01": payload_ids,
        "p02": date,
        "p03": start,
        "p04": end,
        "p05": 0,
        "p06": count,
        "p07": False
    }

    result = fetch(f"{base_url}/api/search/search", payload)
    driver.quit()
    return result
