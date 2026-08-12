This file contains instructions for setting up and maintaining the UVI and VN. If you find anything that is missed, please add them to this file.

Last verified: July 2026, against the verbs2 server (verbs.colorado.edu).

About UVI (https://uvi.colorado.edu/):

1.	All codes for UVI website are stored at: https://github.com/cu-clear/UVI . Make sure you are a member of the group.

2.	To set the website on your local machine:

(1)	Clone and cd into the UVI web app repository:

    git clone https://github.com/cu-clear/UVI
    cd UVI

(2)	Create a new conda environment for the UVI project, then activate the environment (production runs Python 3.9, so prefer that over the older 3.6 instructions):

    conda create -n uvi_web python=3.9
    conda activate uvi_web

(3)	With the conda environment active, update pip:

    pip install --upgrade pip

(4)	Install project dependencies from requirements.txt (unfortunately, conda doesn't have all the packages we need so instead of using two package managers we will use the active conda environment's copy of pip to manage our Python packages):

    pip install -r requirements.txt

(5)	Download the Spacy English language model (necessary to generate dependency parse trees on VerbNet) and the NLTK punkt tokenizer:

    python -m spacy download en
    python -c "import nltk; nltk.download('punkt')"

(6)	Set environment variables for mail server:

    [MAIL_SETUP]
    mail_username = uvi.contact@gmail.com
    mail_password = <ask a maintainer — do not write it in this file>
    recipients = uvi.contact@gmail.com, martha.palmer@colorado.edu, brownsw@colorado.edu

(Or inject username and password from configs.ini file. NEVER, NEVER commit or upload this file anywhere.)

(7)	The app needs a local MongoDB instance (it connects to `mongodb://localhost:27017/new_corpora`, see uvi_web/uvi_flask.py). On macOS, install and run it via Homebrew:

    brew tap mongodb/brew
    brew install mongodb-community
    brew services start mongodb-community

This registers MongoDB as a background service (via a LaunchAgent), so it stays running across reboots/logins — you only need to run `brew services start mongodb-community` once. Useful commands:

    brew services info mongodb-community   # check if it's running, show PID
    brew services stop mongodb-community   # stop it
    brew services restart mongodb-community

To verify it's actually reachable:

    mongosh --eval "db.runCommand({ ping: 1 })" --quiet

This should print `{ ok: 1 }`. If `mongosh` isn't installed, `brew install mongosh`.

3.	Now the website has been set on your own local machine. Make sure MongoDB is running first (`brew services info mongodb-community` — start it with `brew services start mongodb-community` if not), then run the server with the commands below:

    cd ./UVI/uvi_web
    conda activate uvi_web
    ./run_local.sh

Copy and paste the localhost address to the browser.
(This is also the way to test the website. Make sure it runs well before you push changes to https://github.com/cu-clear/UVI .)

4.	To deploy code to the production server (verbs.colorado.edu, currently the host "verbs2"):

Prerequisites (one-time): you need an account on verbs.colorado.edu with sudo rights to switch to the verbnet-service user. Contact the Office of Information Technology (oithelp@colorado.edu) to request access.

(1)	First, commit and push your tested changes to GitHub from your local machine:

    cd UVI
    git add <changed files>
    git commit -m "describe your change"
    git push origin master

(2)	SSH to the server and switch to the service account (note: it is `sudo -i -u`, not `sudo -`):

    ssh <your-identikey>@verbs2.colorado.edu
    sudo -i -u verbnet-service

(3)	Go to the deployed checkout. IMPORTANT: the code does NOT live in the service account's home directory — it lives under /data:

    cd /data/verbnet-service/UVI_deployable

(4)	Pull the latest code:

    git remote -v    # confirm the remote is https://github.com/cu-clear/UVI.git
    git status       # confirm there are no local server-side edits that would block the pull
    git pull

(5)	Reload gunicorn so the new code is served. IMPORTANT: the old instruction `sudo service gunicorn_uvi reload` no longer works — that systemd/init unit exists but is inactive (dead). Gunicorn is started manually on this server, so reload it by sending SIGHUP to the gunicorn master process:

    kill -HUP $(pgrep -of 'gunicorn.*uvi_flask')

(`pgrep -of` picks the oldest matching process, which is the gunicorn master; on HUP it gracefully restarts its 4 workers with the new code.)

(6)	Verify the reload worked:

    ps aux | grep -i gunicorn | grep -v grep

The worker processes should show fresh start times, and the master should still be running.

(7)	Test that the site is actually serving. From any machine (your laptop is fine), run:

    curl -sI https://uvi.colorado.edu/ | head -3

You want `HTTP/1.1 200 OK`. A 301/302 to an unexpected host (e.g. https://localhost:4000/) or a 500/502 means the deploy broke the app — see Troubleshooting.

Then smoke-test the main routes (note: the search page is `/uvi_search`, there is NO `/search` route):

    for p in "" uvi_search class_hierarchy references_page verbnet/run-51.3.2 "_process_query?lemma_query_string=run"; do
        curl -s -o /dev/null -w "/$p -> %{http_code}\n" "https://uvi.colorado.edu/$p"
    done

All should print 200. To confirm search returns real results (not an empty page):

    curl -s 'https://uvi.colorado.edu/_process_query?lemma_query_string=run' | grep -c 'run-51'

A nonzero count means search is working. Finally, click through the site in a browser with a hard refresh (Cmd+Shift+R) so you see the newly deployed CSS/JS instead of cached copies.

Main routes for reference (defined in uvi_web/uvi_flask.py): `/` (welcome), `/uvi_search` (search page), `/uvi_search_anywhere`, `/_process_query` (search backend), `/class_hierarchy`, `/references_page`, `/nlp_applications`, `/contact_us`, `/verbnet/<vn_class_id>` (e.g. /verbnet/run-51.3.2), `/download_json`.

For reference, the production setup on verbs2 is:

    App checkout:    /data/verbnet-service/UVI_deployable
    Virtualenv:      /data/verbnet-service/UVI_deployable/uvi_web/env_uvi (Python 3.9)
    App server:      gunicorn, 4 workers, bound to 127.0.0.1:4000, app module uvi_flask:app
    Started:         manually (NOT via systemd; the gunicorn_uvi unit is dead)

Troubleshooting:

- Every page 301-redirects to https://localhost:4000/... — some code in the app is generating absolute redirects (e.g. a Flask-level HTTPS-enforcement `before_request`). TLS terminates at the front-end proxy, so gunicorn only ever sees plain HTTP on localhost:4000 and `request.is_secure` is always False; any such redirect fires on every request and rebuilds the URL with the wrong host. Do NOT add HTTPS redirects in Flask — the proxy already enforces HTTPS and HSTS. (This took the site down in July 2026; fixed by removing the handler from uvi_flask.py.) Note this class of bug is invisible in local testing because run_local.sh runs in debug mode.
- `cd: UVI_deployable: No such file or directory` — you are in the home directory; the checkout is at /data/verbnet-service/UVI_deployable (see step 3).
- `sudo: -: command not found` — you typed `sudo - verbnet-service`; use `sudo -i -u verbnet-service` (or `sudo su - verbnet-service`).
- If gunicorn is not running at all (no processes in `ps aux | grep gunicorn`), start it manually as verbnet-service:

    cd /data/verbnet-service/UVI_deployable/uvi_web
    nohup env_uvi/bin/gunicorn -w 4 -b 127.0.0.1:4000 uvi_flask:app &

- To find the gunicorn master PID explicitly: `pgrep -af 'gunicorn.*uvi_flask'` — the master is the oldest one (state `Ss` in `ps aux`).

More commands about the remote server can be found at: https://docs.google.com/document/d/1p3nc_o7q4VfAD2RFu7OM8Xc9x8zvCPzIHoVur5ojkcM/edit?ts=5f861e3d
It also includes how to see if the database value has been uploaded.

5.	If you have any questions that are not mentioned in this documentation, please contact Lan Sang: lan.sang@colorado.edu


About VerbNet Website (https://verbs.colorado.edu/verbnet/):

1.	Here is the link for codes of VN Website: https://drive.google.com/file/d/1DiJbTxbIa5frby4a5SfbGF8R2N-hN6Wn/view?usp=sharing

2.	Commands to run and test the website on your local machine:

        cd verbnet_webpages_raw
        python -m http.server

	Copy and paste the localhost address to the browser and you can now test the website.

3.	To deploy codes to the remote server: First contact the Office of Information Technology (oithelp@colorado.edu)  to ask for the permission of verbs.colorado.edu server.

        ssh username@verbs.colorado.edu
        sudo su - verbnet-service
        cd /usr/local/apache/htdocs/verbs/verbnet/

(Because rewritting the folder requires additional permission, please contact Kevin Stowe to ask for it.)


it should show a small popup list of "fn_mapping" list when hovered over "Member Verb Lemmas:-topfile" 