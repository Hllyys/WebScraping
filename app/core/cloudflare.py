import time
from DrissionPage import ChromiumPage

class CloudflareBypasser:
    """
    Cloudflare Turnstile doğrulamalarını otomatik aşmak için kullanılan sınıf.
    ChromiumPage nesnesi üzerinde çalışır ve shadow DOM içerisindeki input/iframe öğelerine erişerek
    otomatik checkbox tıklaması yapar.
    """
    def __init__(self, driver: ChromiumPage, max_retries=20, log=True):
        self.driver = driver
        self.max_retries = max_retries
        self.log = log

    def log_message(self, message):
        if self.log:
            print(message)

    def is_bypassed(self):
        """Sayfa başlığına göre Cloudflare ekranının geçilip geçilmediğini kontrol eder."""
        try:
            title = self.driver.title.lower()
            return "just a moment" not in title and "bir dakika" not in title
        except:
            return False

    def search_recursively_shadow_root_with_iframe(self, ele):
        """
        Shadow DOM içinde iframe öğesini bulmak için recursive tarama yapar.
        Cloudflare iframe'i genellikle shadow DOM içinde yer alır.
        """
        if ele.shadow_root:
            if ele.shadow_root.child().tag == "iframe":
                return ele.shadow_root.child()
        else:
            for child in ele.children():
                result = self.search_recursively_shadow_root_with_iframe(child)
                if result:
                    return result
        return None

    def search_recursively_shadow_root_with_cf_input(self, ele):
        """
        Shadow DOM içinde input[type="checkbox"] öğesini bulmak için recursive tarama yapar.
        Bu, genellikle "Ben robot değilim" checkbox'ı olur.
        """
        if ele.shadow_root:
            try:
                return ele.shadow_root.ele("tag:input")
            except:
                return None
        else:
            for child in ele.children():
                result = self.search_recursively_shadow_root_with_cf_input(child)
                if result:
                    return result
        return None

    def locate_cf_button(self):
        """
        CAPTCHA input öğesini locate etmeye çalışır.
        Genellikle iframe içinde yer alır. Shadow DOM içeriği üzerinden bulunur.
        """
        self.log_message("CAPTCHA input aranıyor...")
        try:
            ele = self.driver.ele("tag:body")
            iframe = self.search_recursively_shadow_root_with_iframe(ele)
            if iframe:
                body_inside_iframe = iframe("tag:body")
                return self.search_recursively_shadow_root_with_cf_input(body_inside_iframe)
        except Exception as e:
            self.log_message(f"CAPTCHA bulunamadı: {e}")
        return None

    def click_verification_button(self):
        """
        CAPTCHA input butonunu bulup tıklamaya çalışır.
        Bu, doğrulama checkbox'ı olabilir.
        """
        try:
            button = self.locate_cf_button()
            if button:
                self.log_message("CAPTCHA butonu bulundu, tıklanıyor...")
                button.click()
            else:
                self.log_message("CAPTCHA butonu bulunamadı.")
        except Exception as e:
            self.log_message(f"CAPTCHA tıklama hatası: {e}")

    def bypass(self):
        """
        Ana bypass döngüsüdür. Sayfa tam olarak yüklenene kadar belirli aralıklarla
        CAPTCHA'yı bulup tıklamayı ve durum kontrolü yapmayı tekrarlar.
        """
        self.log_message("Cloudflare kontrolü başlatıldı...")
        try_count = 0
        while not self.is_bypassed():
            if 0 < self.max_retries + 1 <= try_count:
                self.log_message("Max deneme sınırına ulaşıldı.")
                break

            self.log_message(f"Deneme {try_count + 1}")
            self.click_verification_button()
            try_count += 1
            time.sleep(2)

        # Sayfa yüklendi mi kontrolü
        try:
            self.driver.wait.ele_displayed("tag:body", timeout=30)
            time.sleep(2)
        except:
            self.log_message("Sayfa gövdesi yüklenmedi")

        if self.is_bypassed():
            self.log_message("Bypass başarılı")
        else:
            self.log_message("Bypass başarısız")
