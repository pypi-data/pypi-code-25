def check_required_roles(required_roles, user_roles):
    # Falls die Liste der required_roles leer oder None ist True zurück geben
    if not required_roles:
        return True

    for required_role in required_roles:
        # Überprüft ob die Aktuelle rolle in den User Rollen vorhanden ist
        if required_role in user_roles:
            # Falls auch nur eine der Rollen vorhanden ist Return True
            return True

    # Falls keine der Rollen vorhanden ist Return false
    return False
