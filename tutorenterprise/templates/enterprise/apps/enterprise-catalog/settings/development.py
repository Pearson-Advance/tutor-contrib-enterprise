from ..devstack import *

{% include "enterprise/apps/enterprise-catalog/settings/partials/common.py" %}

DISCOVERY_CATALOG_QUERY_CACHE_TIMEOUT = 0
CELERY_TASK_ALWAYS_EAGER = True

{{ patch("enterprise-catalog-development-settings") }}
