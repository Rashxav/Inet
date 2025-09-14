import phonenumbers

from phonenumbers import region_code_for_country_code


class PhoneNormalizer:
    def normalize(self, phone: str) -> str:
        try:
            parsed = phonenumbers.parse(phone, None)
            country_code = str(parsed.country_code)
            return "+" + phone[len(country_code) + 1:]
        except Exception:
            return phone
