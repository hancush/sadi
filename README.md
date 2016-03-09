![Sadi in action](http://i.imgur.com/ql8V25y.png)

## SADI: SAM Digest

Sadi is a slash command for SAM Desk users who push updates to Slack. She waits in her Flask app palace on a Heroku cloud until you assign her a story, at which time she retrieves related messages from the SAM bot, then wraps them all up in a shiny digest you can send to the editors who are yelling at you. — Edit

### Dependencies

See [requirements.txt](https://github.com/hancush/sadi/blob/master/requirements.txt).

### Directory

* [classes_web.py](https://github.com/hancush/sadi/blob/master/classes_web.py) is the powerhouse
* [app.py](https://github.com/hancush/sadi/blob/master/app.py) receives pings from Slack and pings Slack back
* [templates/page.html](https://github.com/hancush/sadi/blob/master/templates/page.html) structures the digest

### To use

Fork the repo. 

[Generate a Slack API key](https://api.slack.com/tokens) for your team.

Create a new Heroku app.

[Set the following environment vars](https://devcenter.heroku.com/articles/config-vars):

* username - username of your choice to access digests
* pass - password of your choice to access digests
* ap_key - Slack API key

[Deploy to Heroku](https://devcenter.heroku.com/articles/getting-started-with-python#deploy-the-app).

[Add a new Slash Command](https://slack.com/apps/A0F82E8CA-slash-commands) in Slack.

Set another environment var:

* ap_token - Token from Slash Command setup

/sadi [name of SAM story]

[Here’s an example digest](https://github.com/hancush/sadi/blob/master/examples/taiwan_earthquake_report.pdf).