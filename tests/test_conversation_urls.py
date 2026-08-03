import unittest

import erdos_common as C


class ConversationUrlTests(unittest.TestCase):
    def test_accepts_classic_and_changed_project_routes(self):
        self.assertTrue(C.is_conversation_url("https://chatgpt.com/c/abc"))
        self.assertTrue(C.is_conversation_url(
            "https://chatgpt.com/g/project/conversation-1",
            "https://chatgpt.com/g/project",
        ))

    def test_rejects_project_root_and_foreign_hosts(self):
        self.assertFalse(C.is_conversation_url(C.PROJECT_URL))
        self.assertFalse(C.is_conversation_url("https://example.com/c/abc"))


if __name__ == "__main__":
    unittest.main()
