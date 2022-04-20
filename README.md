Our mail server is Zimbra, and we have policyd enabled in order to avoid problems with spammers if they get our users credentials and they try to send thousand of emails using our mail server.

Policyd itself does not alert admins when some users reach the limits, so you can't react quickly and disable hacked users accounts in these situations.

This python script checks the Policyd database and send alerts (by email and/or telegram) when detects that some user reach the quota percent that you have previously defined.

In our case, we have add a cron job in our Zimbra server to run the script each 5 minutes.
