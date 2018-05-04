# base url
KEYCLOAK_BASE = 'localhost:8080/auth'

# token url
KEYCLOAK_OPENID = '/realms/{realm_name}/protocol/openid-connect/token'

# admin url
KEYCLOAK_USER = '/admin/realms/{realm_name}/users'
KEYCLOAK_USER_ID = '/admin/realms/{realm_name}/users/{id}'
KEYCLOAK_USER_SESSION = '/admin/realms/{realm_name}/users/{id}/sessions'
KEYCLOAK_REALMS = '/admin/realms/{realm_name}'
KEYCLOAK_ATTACK_DETECTION = '/admin/realms/{realm_name}/attack-detection/brute-force/users/{id}'
KEYCLOAK_CLIENT = '/admin/realms/{realm_name}/clients'
KEYCLOAK_SESSION = '/admin/realms/{realm_name}/sessions/{sessionid}'
KEYCLOAK_RESET_PASSWORD = '/admin/realms/{realm_name}/users/{id}/reset-password'
