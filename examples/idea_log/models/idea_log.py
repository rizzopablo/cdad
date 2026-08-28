# Copyright 2026 CDAD Contributors
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class IdeaLog(models.Model):
    _name = "idea.log"
    _description = "Idea Log"
    _order = "id desc"

    def _default_code(self):
        return self.env["ir.sequence"].next_by_code("idea.log")

    # Fields declaration
    name = fields.Char(required=True, index=True, translate=True)
    code = fields.Char(
        readonly=True, copy=False, default=lambda self: self._default_code()
    )
    description = fields.Text()
    status = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
            ("implemented", "Implemented"),
        ],
        default="draft",
        copy=False,
    )
    score = fields.Integer(help="Score from 1 to 10.")
    effort = fields.Selection(
        selection=[
            ("quick", "Quick"),
            ("medium", "Medium"),
            ("large", "Large"),
        ]
    )
    weighted_value = fields.Integer(compute="_compute_weighted_value", store=True)
    accepted_date = fields.Date(readonly=True, copy=False)
    vote_ids = fields.One2many("idea.vote", "idea_id", string="Votes")
    total_votes = fields.Integer(compute="_compute_total_votes")
    net_score = fields.Integer(compute="_compute_net_score")
    rejected_reason = fields.Char(groups="idea_log.group_reviewer")

    # Compute methods, in the same order of fields declaration
    @api.depends("score", "effort")
    def _compute_weighted_value(self):
        weights = {"quick": 1, "medium": 2, "large": 3}
        for idea in self:
            idea.weighted_value = (idea.score or 0) * weights.get(idea.effort, 1)

    @api.depends("vote_ids")
    def _compute_total_votes(self):
        for idea in self:
            idea.total_votes = len(idea.vote_ids)

    @api.depends("vote_ids.vote_type")
    def _compute_net_score(self):
        for idea in self:
            ups = sum(1 for vote in idea.vote_ids if vote.vote_type == "up")
            idea.net_score = ups - (len(idea.vote_ids) - ups)

    # Constraints
    @api.constrains("score")
    def _check_score(self):
        for idea in self:
            if idea.score is not None and not 1 <= idea.score <= 10:
                raise ValidationError(self.env._("Score must be between 1 and 10."))

    # Action methods
    def action_accept(self):
        self.ensure_one()
        self.write(
            {
                "status": "accepted",
                "accepted_date": fields.Date.context_today(self),
            }
        )

    def action_submit(self):
        self.ensure_one()
        self.write({"status": "submitted"})
