async def detect_access_issues(page):
    try:
        captcha_iframe = await page.query_selector('iframe[src*="recaptcha"], iframe[src*="hcaptcha"]')
        captcha_div = await page.query_selector('div[id*="captcha"], div[class*="cf-im-under-attack"]')

        if captcha_iframe and await captcha_iframe.is_visible():
            return "CAPTCHA detectado"
        if captcha_div and await captcha_div.is_visible():
            return "CAPTCHA detectado"

        restricted_phrases = [
            "Get access through your institution", "Institutional Login Required",
            "Please sign in through your institution", "Access Denied", "Get Access",
            "Login Required", "Purchase Short-Term Access",
            "Purchase PDF", "Subscription Required, Log in via an institution"
        ]

        body_text = await page.content()
        for phrase in restricted_phrases:
            if phrase.lower() in body_text.lower():
                return f"Acceso restringido - {phrase}"

    except Exception as e:
        print(f"Error al detectar problemas de acceso: {e}")
    
    return None
