app_name = "electronic_tender"
app_title = "Electronic Tender"
app_publisher = "Orient AI"
app_description = "The missing electronic tender system."
app_email = "hcxu0814@gmail.com"
app_license = "agpl-3.0"

# Apps
# ------------------

# required_apps = ["electronic_erp"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "electronic_tender",
# 		"logo": "/assets/electronic_tender/logo.png",
# 		"title": "Electronic Tender",
# 		"route": "/electronic_tender",
# 		"has_permission": "electronic_tender.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/electronic_tender/css/electronic_tender.css"
# app_include_js = "/assets/electronic_tender/js/electronic_tender.js"

# include js, css files in header of web template
# web_include_css = "/assets/electronic_tender/css/electronic_tender.css"
# web_include_js = "/assets/electronic_tender/js/electronic_tender.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "electronic_tender/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "electronic_tender/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "electronic_tender.utils.jinja_methods",
# 	"filters": "electronic_tender.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "electronic_tender.install.before_install"
# after_install = "electronic_tender.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "electronic_tender.uninstall.before_uninstall"
# after_uninstall = "electronic_tender.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "electronic_tender.utils.before_app_install"
# after_app_install = "electronic_tender.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "electronic_tender.utils.before_app_uninstall"
# after_app_uninstall = "electronic_tender.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "electronic_tender.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"electronic_tender.tasks.all"
# 	],
# 	"daily": [
# 		"electronic_tender.tasks.daily"
# 	],
# 	"hourly": [
# 		"electronic_tender.tasks.hourly"
# 	],
# 	"weekly": [
# 		"electronic_tender.tasks.weekly"
# 	],
# 	"monthly": [
# 		"electronic_tender.tasks.monthly"
# 	],
# }

scheduler_events = {
    "cron": {
        "* * * * *": [
            "electronic_tender.controllers.scheduled_tasks.collect_tenders",
            "electronic_tender.controllers.scheduled_tasks.collect_tender_packages",
            "electronic_tender.controllers.scheduled_tasks.collect_tender_lots",
        ]
    }
}

# Testing
# -------

# before_tests = "electronic_tender.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "electronic_tender.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "electronic_tender.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["electronic_tender.utils.before_request"]
# after_request = ["electronic_tender.utils.after_request"]

# Job Events
# ----------
# before_job = ["electronic_tender.utils.before_job"]
# after_job = ["electronic_tender.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"electronic_tender.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

