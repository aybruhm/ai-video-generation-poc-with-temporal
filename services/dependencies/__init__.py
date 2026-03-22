from .auth import AuthDependencies
from .temporal import get_temporal_client

auth_deps = AuthDependencies()
get_current_user = auth_deps.get_current_user
get_temporal_client = get_temporal_client
