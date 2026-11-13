import phonenumbers


def normalize_phone(phone: str, region):
    parsed = phonenumbers.parse(phone, region)

    if not phonenumbers.is_valid_number(parsed):
        raise ValueError("Invalid phone number")

    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
