def system_name(card_num):
    if not card_num:
        return None

    snum = str(card_num)
    if snum.startswith("2"):
        return "MIR"
    elif snum.startswith("30") or snum.startswith("36") or snum.startswith("38"):
        return "DINERSCLUB"
    elif snum.startswith("31") or snum.startswith("35"):
        return "JCB"
    elif snum.startswith("34") or snum.startswith("37"):
        return "AMEX"
    elif snum.startswith("4"):
        return "VISA"
    elif snum.startswith("50") or snum.startswith("56") or snum.startswith("57") or \
            snum.startswith("58"):
        return "MAESTRO"
    elif snum.startswith("51") or snum.startswith("52") or snum.startswith("53") or \
            snum.startswith("54") or snum.startswith("55"):
        return "MASTERCARD"
    elif snum.startswith("60"):
        return "DISCOVER"
    elif snum.startswith("62"):
        return "UNIONPAY"
    elif snum.startswith("63") or snum.startswith("67"):
        return "MAESTRO"
    elif snum.startswith("7"):
        return "UEK"
    return "UNKNOWN"
