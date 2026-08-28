# Copyright 2026 CDAD Contributors
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class IdeaVote(models.Model):
    _name = "idea.vote"
    _description = "Idea Vote"
    _order = "id desc"

    idea_id = fields.Many2one(
        "idea.log", required=True, ondelete="cascade", index=True
    )
    voter_name = fields.Char()
    vote_type = fields.Selection(
        selection=[("up", "Up"), ("down", "Down")],
        required=True,
        default="up",
    )
