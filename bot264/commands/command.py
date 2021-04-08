from bot264.common.user_response import UserResponse


class UserCommand:

    def __init__(self, message, response: UserResponse):
        self.message = message
        self.response = response

    async def run(self):
        pass
