"""
Flask web site with vocabulary matching game
(identify vocabulary words that can be made
from a scrambled string)
"""

import flask
import logging

# Our modules
from src.letterbag import LetterBag
from src.vocab import Vocab
from src.jumble import jumbled
import src.config as config


###
# Globals
###
app = flask.Flask(__name__)

CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY  # Should allow using session variables
# Need to keep global so it can be used in both AJAX handlers
letters_to_use = ""

###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
    return flask.render_template("vocab.html")


@app.route("/success")
def success():
    return flask.render_template('success.html')


###############
# AJAX request handlers
#   These return JSON, rather than rendering pages.
###############

@app.route("/_getinfo")
def getinfo():
    # Set the variables
    WORDS = Vocab(CONFIG.VOCAB)
    target = min(len(WORDS.as_list()), CONFIG.SUCCESS_AT_COUNT)
    global letters_to_use 
    letters_to_use = jumbled(WORDS.as_list(), target)

    # Format them into a dict, and return as json
    info = {}
    info['target'] = target             # Target number of words to find
    info['letters'] = letters_to_use    # Letters they can use
    word_list = WORDS.as_list() 
    info['words'] = word_list           # A list of the words 
    return flask.jsonify(info)


@app.route("/_checkword")
def checkword():
    # Check if the word can be made using the letters and return result
    word = flask.request.args.get("word", type=str)
    rslt = {"uses_letters": LetterBag(letters_to_use).contains(word)}
    return flask.jsonify(result=rslt)


#################
# Functions used within the templates
#################

@app.template_filter('filt')
def format_filt(something):
    """
    Example of a filter that can be used within
    the Jinja2 code
    """
    return "Not what you asked for"

###################
#   Error handlers
###################


@app.errorhandler(404)
def error_404(e):
    app.logger.warning("++ 404 error: {}".format(e))
    return flask.render_template('404.html'), 404


@app.errorhandler(500)
def error_500(e):
    app.logger.warning("++ 500 error: {}".format(e))
    assert not True  # I want to invoke the debugger
    return flask.render_template('500.html'), 500


@app.errorhandler(403)
def error_403(e):
    app.logger.warning("++ 403 error: {}".format(e))
    return flask.render_template('403.html'), 403


#############

if __name__ == "__main__":
    if CONFIG.DEBUG:
        app.debug = True
        app.logger.setLevel(logging.DEBUG)
        app.logger.info(
            "Opening for global access on port {}".format(CONFIG.PORT))
        app.run(port=CONFIG.PORT, host="0.0.0.0")
