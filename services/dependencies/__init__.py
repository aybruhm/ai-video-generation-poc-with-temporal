from .auth import AuthDependencies

auth_deps = AuthDependencies()
get_current_user = auth_deps.get_current_user
