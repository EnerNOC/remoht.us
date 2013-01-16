#!/bin/bash
# Run this before pushing to appengine, assets in _base.html use minified 
# versions.
#
# cssmin can be installed by `easy_install cssmin` or `pip install cssmin`
# closure can be installed by `brew install closure-compiler` on OSX
CSSDIR=static/css
JSDIR=static/js

CSS_FILES="main"
JS_FILES="app remoht"

for F in $CSS_FILES; do
	echo "Writing $CSSDIR/$F.min.css ..."
	cat $CSSDIR/$F.css | cssmin > $CSSDIR/$F.min.css
done

JSMIN="closure-compiler --compilation_level SIMPLE_OPTIMIZATIONS --js"

for F in $JS_FILES; do
	echo "Writing $JSDIR/$F.min.js ..."
	$JSMIN $JSDIR/$F.js > $JSDIR/$F.min.js
done
