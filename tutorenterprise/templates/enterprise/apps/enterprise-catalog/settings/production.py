from ..production import *

{% include "enterprise/apps/enterprise-catalog/settings/partials/common.py" %}

{{ patch("enterprise-catalog-production-settings") }}
