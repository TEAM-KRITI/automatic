# AutoApprove Telegram Bot

- Auto approves every join request
- No reply on /start, but every /start is logged in the logger group
- `/approveall <chat_id>` approves all pending requests (needs SESSION_STRING)

## Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/YOUR_USERNAME/YOUR_REPO)

> Upar link me `YOUR_USERNAME/YOUR_REPO` ko apne GitHub username/repo se badal do.
> Repo public hona chahiye tabhi button kaam karega (secrets repo me mat daalna, wo Heroku form me daalte hain).

After deploy: Resources tab -> worker dyno ON.
