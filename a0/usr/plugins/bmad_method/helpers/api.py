class Request:
    """Request wrapper for plugin API handlers."""

    pass


class Response:
    """Response wrapper for plugin API handlers."""

    pass


class ApiHandler:
    """Base API handler for BMAD plugin endpoints."""

    def requires_auth(self) -> bool:
        return False

    async def process(self, input, request: Request):
        """Process an API request. Override in subclasses."""
        raise NotImplementedError
