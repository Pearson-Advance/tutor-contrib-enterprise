import json

# Django settings.
SECRET_KEY = "{{ ENTERPRISE_CATALOG_SECRET_KEY }}"
ALLOWED_HOSTS = [
    "{{ DISCOVERY_HOST }}",
    "{{ ENTERPRISE_CATALOG_HOST }}",
    "{{ LMS_HOST }}",
]
CORS_ORIGIN_WHITELIST = []

# JWT configurations:
{% set jwt_rsa_key | rsa_import_key %}{{ JWT_RSA_PRIVATE_KEY }}{% endset %}
JWT_AUTH["JWT_ISSUER"] = "{{ JWT_COMMON_ISSUER }}"
JWT_AUTH["JWT_AUDIENCE"] = "{{ JWT_COMMON_AUDIENCE }}"
JWT_AUTH["JWT_SECRET_KEY"] = "{{ JWT_COMMON_SECRET_KEY }}"
JWT_AUTH["JWT_PUBLIC_SIGNING_JWK_SET"] = json.dumps(
    {
        "keys": [
            {
                "kid": "openedx",
                "kty": "RSA",
                "e": "{{ jwt_rsa_key.e|long_to_base64 }}",
                "n": "{{ jwt_rsa_key.n|long_to_base64 }}",
            },
        ],
    },
)
JWT_AUTH["JWT_ISSUERS"] = [
    {
        "ISSUER": "{{ JWT_COMMON_ISSUER }}",
        "AUDIENCE": "{{ JWT_COMMON_AUDIENCE }}",
        "SECRET_KEY": "{{ OPENEDX_SECRET_KEY }}"
    },
]

# OAuth configurations for SSO.
SOCIAL_AUTH_EDX_OAUTH2_KEY = "{{ ENTERPRISE_CATALOG_OAUTH2_KEY_SSO }}"
SOCIAL_AUTH_EDX_OAUTH2_SECRET = "{{ ENTERPRISE_CATALOG_OAUTH2_SECRET_KEY_SSO }}"
SOCIAL_AUTH_EDX_OAUTH2_ISSUER = "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ LMS_HOST }}"
SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT = SOCIAL_AUTH_EDX_OAUTH2_ISSUER
SOCIAL_AUTH_EDX_OAUTH2_PUBLIC_URL_ROOT = SOCIAL_AUTH_EDX_OAUTH2_ISSUER
SOCIAL_AUTH_EDX_OAUTH2_LOGOUT_URL = SOCIAL_AUTH_EDX_OAUTH2_ISSUER + "/logout"

# OAuth configurations for backend-to-backend authenticated requests.
BACKEND_SERVICE_EDX_OAUTH2_KEY = "{{ ENTERPRISE_CATALOG_OAUTH2_KEY }}"
BACKEND_SERVICE_EDX_OAUTH2_SECRET = "{{ ENTERPRISE_CATALOG_OAUTH2_SECRET_KEY }}"
BACKEND_SERVICE_EDX_OAUTH2_PROVIDER_URL = SOCIAL_AUTH_EDX_OAUTH2_ISSUER + "/oauth2"

# Storage settings.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "{{ ENTERPRISE_CATALOG_MYSQL_DATABASE }}",
        "USER": "{{ ENTERPRISE_CATALOG_MYSQL_USERNAME }}",
        "PASSWORD": "{{ ENTERPRISE_CATALOG_MYSQL_PASSWORD }}",
        "HOST": "{{ MYSQL_HOST }}",
        "PORT": "{{ MYSQL_PORT }}",
        # The default isolation level for MySQL is REPEATABLE READ, which is a little too aggressive
        # for our needs, particularly around reading celery task state via django-celery-results.
        # https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html#isolevel_read-committed
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            'isolation_level': 'read committed',
        },
    },
}
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "KEY_PREFIX": "enterprise-catalog",
        "LOCATION": "redis://{% if REDIS_USERNAME and REDIS_PASSWORD %}{{ REDIS_USERNAME }}:{{ REDIS_PASSWORD }}{% endif %}@{{ REDIS_HOST }}:{{ REDIS_PORT }}/{{ OPENEDX_CACHE_REDIS_DB }}",
    },
}

# Open edX-related settings.
PLATFORM_NAME = "{{ PLATFORM_NAME }}"
LMS_BASE_URL = "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ LMS_HOST }}"
DISCOVERY_SERVICE_API_URL = "{{ ENTERPRISE_COURSE_CATALOG_API_URL }}"
ENTERPRISE_LEARNER_PORTAL_BASE_URL = ""
ECOMMERCE_BASE_URL = "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ ECOMMERCE_HOST }}"
LICENSE_MANAGER_BASE_URL = ""

# Worker settings.
CELERY_WORKER_HIJACK_ROOT_LOGGER = True
CELERY_TASK_ALWAYS_EAGER = False
CELERY_BROKER_TRANSPORT = "redis"
CELERY_BROKER_HOSTNAME = "{{ REDIS_HOST }}:{{ REDIS_PORT }}"
CELERY_BROKER_VHOST = "{{ OPENEDX_CELERY_REDIS_DB }}"
CELERY_BROKER_USER = "{{ REDIS_USERNAME }}"
CELERY_BROKER_PASSWORD = "{{ REDIS_PASSWORD }}"
CELERY_BROKER_URL = "{}://{}:{}@{}/{}".format(
    CELERY_BROKER_TRANSPORT,
    CELERY_BROKER_USER,
    CELERY_BROKER_PASSWORD,
    CELERY_BROKER_HOSTNAME,
    CELERY_BROKER_VHOST,
)
