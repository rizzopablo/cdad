# Copyright 2026 CDAD Contributors
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase, new_test_user


@tagged("idea_log")
class TestIdeaLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.idea_model = cls.env["idea.log"]
        cls.vote_model = cls.env["idea.vote"]
        cls.base_user = new_test_user(
            cls.env, login="idea-user", groups="base.group_user"
        )
        cls.reviewer = new_test_user(
            cls.env, login="idea-reviewer", groups="idea_log.group_reviewer"
        )

    def test_create_defaults(self):
        """Creating an idea sets code and default status."""
        idea = self.idea_model.create({"name": "Test idea"})
        self.assertTrue(idea.code)
        self.assertEqual(idea.status, "draft")
        self.assertEqual(idea.total_votes, 0)
        self.assertEqual(idea.net_score, 0)

    def test_weighted_value(self):
        """Weighted value is score times effort weight and recomputes."""
        idea = self.idea_model.create(
            {"name": "Weighted", "score": 5, "effort": "medium"}
        )
        self.assertEqual(idea.weighted_value, 10)
        idea.write({"score": 8})
        self.assertEqual(idea.weighted_value, 16)
        idea.write({"effort": "large"})
        self.assertEqual(idea.weighted_value, 24)

    def test_score_constraint(self):
        """Score must be within 1..10."""
        with self.assertRaises(ValidationError):
            self.idea_model.create({"name": "Bad", "score": 0})
        with self.assertRaises(ValidationError):
            self.idea_model.create({"name": "Bad", "score": 11})
        idea = self.idea_model.create({"name": "Good", "score": 10})
        self.assertEqual(idea.score, 10)

    def test_action_accept(self):
        """action_accept sets status and accepted date."""
        idea = self.idea_model.create({"name": "Accept me"})
        idea.action_accept()
        self.assertEqual(idea.status, "accepted")
        self.assertEqual(idea.accepted_date, fields.Date.context_today(idea))

    def test_action_submit(self):
        """action_submit moves a draft idea to submitted."""
        idea = self.idea_model.create({"name": "Submit me"})
        idea.action_submit()
        self.assertEqual(idea.status, "submitted")

    def test_votes_aggregate(self):
        """Vote aggregation computes from vote lines."""
        idea = self.idea_model.create({"name": "Votes"})
        self.vote_model.create(
            [
                {"idea_id": idea.id, "voter_name": "Alice", "vote_type": "up"},
                {"idea_id": idea.id, "voter_name": "Bob", "vote_type": "up"},
                {"idea_id": idea.id, "voter_name": "Carol", "vote_type": "down"},
            ]
        )
        self.assertEqual(idea.total_votes, 3)
        self.assertEqual(idea.net_score, 1)

    def test_field_security(self):
        """rejected_reason is only accessible to reviewers."""
        idea = self.idea_model.create({"name": "Security test"})
        with self.assertRaises(AccessError):
            idea.with_user(self.base_user).write({"rejected_reason": "Nope"})
        idea_reviewer = idea.with_user(self.reviewer)
        idea_reviewer.write({"rejected_reason": "Out of scope"})
        self.assertEqual(idea_reviewer.rejected_reason, "Out of scope")

    def test_form_create(self):
        """Creating through the Form helper."""
        form = Form(self.idea_model)
        form.name = "Form idea"
        form.score = 7
        form.effort = "medium"
        with form.vote_ids.new() as vote:
            vote.voter_name = "Alice"
            vote.vote_type = "up"
        idea = form.save()
        self.assertEqual(idea.weighted_value, 14)
        self.assertEqual(idea.total_votes, 1)
