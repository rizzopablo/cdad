# Copyright 2026 CDAD Contributors
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Idea Log",
    "summary": "Capture ideas, score them and track their status",
    "version": "19.0.1.0.0",
    "category": "Productivity",
    "author": "CDAD Contributors",
    "website": "https://github.com/yourorg/yourrepo",
    "license": "LGPL-3",
    "development_status": "Beta",
    "depends": ["base", "web"],
    "data": [
        "security/idea_log_security.xml",
        "security/ir.model.access.csv",
        "data/idea_sequence.xml",
        "views/idea_log_views.xml",
        "views/idea_log_menus.xml",
    ],
    "demo": [
        "demo/idea_log_demo.xml",
    ],
}
