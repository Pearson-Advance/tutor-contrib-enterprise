from ..devstack import *

{% include "enterprise/apps/enterprise-catalog/settings/partials/common.py" %}

DISCOVERY_CATALOG_QUERY_CACHE_TIMEOUT = 0

{{ patch("enterprise-catalog-development-settings") }}
