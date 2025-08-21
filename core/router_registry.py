class RouterRegistry:
    def __init__(self):
        # name -> router instance (router must expose can_handle(text) and get_handler(text))
        self.modules = {}
        self.middlewares = []

    def register_module(self, name: str, router):
        self.modules[name] = router

    def find_handler(self, message_text: str):
        for module_router in self.modules.values():
            if module_router.can_handle(message_text):
                return module_router.get_handler(message_text)
        return None

    def register_middleware(self, middleware):
        """Add a middleware to the registry."""
        self.middlewares.append(middleware)

    async def execute_with_middlewares(self, handler, update, context):
        """Execute a handler with middleware pipeline."""
        _handler = None
        for middleware in self.middlewares:
            if not await middleware.before(update, context):
                return
        _handler = await handler(update, context)
        for middleware in self.middlewares:
            if not await middleware.after(update, context):
                return
        return _handler
