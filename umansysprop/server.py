# vim: set et sw=4 sts=4 fileencoding=utf-8:
#
# Copyright 2014 Dave Hughes <dave@waveform.org.uk>.
#
# This file is part of umansysprop.
#
# umansysprop is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# umansysprop is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# umansysprop.  If not, see <http://www.gnu.org/licenses/>.

"""
An online framework for calculating the properties of individual organic
molecules and ensemble mixtures
"""

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')

import re
import pkgutil
import json

from flask import Flask, request, url_for, render_template, make_response, jsonify
from docutils import core

from . import tools
from . import renderers
from . import forms

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

tools = {
    modname.split('.')[-1]: finder.find_module(modname).load_module(modname)
    for (finder, modname, ispkg) in pkgutil.iter_modules(
        tools.__path__, prefix=tools.__name__ + '.')
    if not ispkg and modname != 'template'
    }


@app.route('/')
def index():
    return render_template(
        'index.html',
        title='Welcome',
        tools=tools,
        )


indent_re = re.compile(r'^\s*')
def render_docs(docstring):
    if not isinstance(docstring, str):
        docstring = docstring.decode('utf-8')
    indent = None
    s = ''
    for line in docstring.splitlines():
        if indent is None:
            if line.lstrip():
                indent = indent_re.search(line).group(0)
                s = line[len(indent):] + '\n'
        elif line.startswith(indent):
            s += line[len(indent):] + '\n'
        else:
            s += line + '\n'
    docstring = s
    result = core.publish_parts(
            docstring, writer_name='html', settings_overrides={
                'input_encoding': 'unicode',
                'output_encoding': 'unicode',
                })
    return result['fragment']


@app.route('/api')
def api():
    mimetype = request.accept_mimetypes.best_match([
        'text/html',
        'application/json',
        ])
    if mimetype == 'text/html':
        return render_template(
            'api.html',
            title='JSON API Documentation',
            tools=tools,
            render_docs=render_docs,
            )
    elif mimetype == 'application/json':
        return jsonify(**{
            mod_name: {
                'url': url_for('call', name=mod_name),
                'title': (mod.__doc__ or '').strip(),
                'doc': (mod.handler.__doc__ or '').strip(),
                'params': [
                    field.name for field in mod.HandlerForm()
                    ],
                }
            for mod_name, mod in tools.items()
            })
    else:
        return 'Not acceptable', 406


@app.route('/api/<name>', methods=['POST'])
def call(name):
    # Fail if the RPC call has more than a meg of data
    if request.content_length > 1048576:
        return 'Excessively long request', 413
    mod = tools[name]
    args = json.loads(request.get_data(cache=False, as_text=True))
    args = forms.convert_args(mod.HandlerForm(), args)
    result = mod.handler(**args)
    result = renderers.render_json(result)
    response = make_response(result)
    response.mimetype = 'application/json'
    return response


@app.route('/tool/<name>', methods=['GET', 'POST'])
def tool(name):
    # Present the tool's input form, or execute the tool's handler callable
    # based on whether the HTTP request is a GET or a POST
    mod = tools[name]
    form = mod.HandlerForm(request.form)
    if request.method == 'POST' and form.validate():
        renderer_by_type = {
            'application/json': renderers.render_json,
            'application/xml':  renderers.render_xml,
            'text/html':        renderers.render_html,
            }
        mimetype = request.accept_mimetypes.best_match(renderer_by_type.keys())
        result = mod.handler(**form.data)
        result = renderer_by_type[mimetype](result)
        # If we're generating HTML, wrap the result in a template
        if mimetype == 'text/html':
            result = render_template(
                'result.html',
                title=mod.__doc__,
                result=result)
        response = make_response(result)
        response.mimetype = mimetype
        return response
    return render_template(
        '%s.html' % name,
        title=mod.__doc__,
        form=form,
        )


def main():
    app.run(
        host='0.0.0.0',
        debug=True
        )
