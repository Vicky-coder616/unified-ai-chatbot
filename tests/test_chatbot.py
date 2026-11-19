from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from src.chatbot import ask
from src.storage import connect, recent, save, save_turn, search


class ChatTests(unittest.TestCase):
    def setUp(self):
        self.db = connect(":memory:")
        self.client = Mock()
        self.client.messages.create.return_value = SimpleNamespace(
            content=[SimpleNamespace(type="text", text="Synthetic answer")]
        )

    def tearDown(self):
        self.db.close()

    def test_api_receives_context_and_persists_complete_turn(self):
        save_turn(self.db, "Earlier question", "Earlier answer")
        self.assertEqual(
            ask(self.db, self.client, "New question", "mock-model"), "Synthetic answer"
        )
        messages = self.client.messages.create.call_args.kwargs["messages"]
        self.assertEqual([m["role"] for m in messages], ["user", "assistant", "user"])
        self.assertEqual(len(recent(self.db)), 4)

    def test_api_failure_or_empty_response_does_not_save_question(self):
        self.client.messages.create.side_effect = RuntimeError("Synthetic failure")
        with self.assertRaises(RuntimeError):
            ask(self.db, self.client, "Question", "mock-model")
        self.assertEqual(recent(self.db), [])
        self.client.messages.create.side_effect = None
        self.client.messages.create.return_value = SimpleNamespace(content=[])
        with self.assertRaises(ValueError):
            ask(self.db, self.client, "Question", "mock-model")
        self.assertEqual(recent(self.db), [])

    def test_context_budget_preserves_user_start(self):
        for i in range(12):
            save_turn(self.db, "Question " + str(i), "Answer " + str(i))
        ask(self.db, self.client, "Next", "mock-model", context_chars=50)
        messages = self.client.messages.create.call_args.kwargs["messages"]
        self.assertEqual(messages[0]["role"], "user")
        self.assertLessEqual(sum(len(m["content"]) for m in messages), 50)

    def test_search_wildcards_and_sql_are_literal(self):
        save(self.db, "user", "100%_complete")
        save(self.db, "assistant", "other")
        self.assertEqual(len(search(self.db, "%_")), 1)
        self.assertEqual(search(self.db, "' OR 1=1 --"), [])

    def test_reject_blank_and_overlong_question(self):
        for value in ("  ", "x" * 8001):
            with self.assertRaises(ValueError):
                ask(self.db, self.client, value, "mock-model")
        self.client.messages.create.assert_not_called()

    def test_turn_insert_rolls_back_on_second_row_failure(self):
        self.db.execute(
            "CREATE TRIGGER fail_assistant BEFORE INSERT ON messages WHEN NEW.role='assistant' BEGIN SELECT RAISE(ABORT,'synthetic failure'); END"
        )
        with self.assertRaises(Exception):
            save_turn(self.db, "question", "answer")
        self.assertEqual(recent(self.db), [])
