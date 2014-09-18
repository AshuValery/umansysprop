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

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')
try:
    range = xrange
except NameError:
    pass


import math

import pybel
from wtforms import Form
from wtforms.fields import (
    Field,
    BooleanField,
    FloatField,
    RadioField,
    SelectField,
    SelectMultipleField,
    StringField,
    PasswordField,
    TextAreaField,
    HiddenField,
    FileField,
    FormField,
    SubmitField,
    FormField,
    FieldList,
    )
from wtforms.fields.html5 import (
    SearchField,
    TelField,
    URLField,
    EmailField,
    DateField,
    DateTimeField,
    IntegerField,
    DecimalField,
    )
from wtforms.validators import (
    Optional,
    DataRequired,
    Email,
    EqualTo,
    IPAddress,
    MacAddress,
    Length,
    InputRequired,
    NumberRange,
    Regexp,
    URL,
    UUID,
    AnyOf,
    NoneOf,
    )
from wtforms.widgets import TextInput

from .html import html, literal, content, tag


class SMILESField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return self.data.write(b'smi').decode('ascii')
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = pybel.readstring(b'smi', valuelist[0].encode('ascii'))
        else:
            self.data = None


def frange(start, stop=None, step=1.0):
    """
    Floating point variant of :func:`range`. Note that this variant has several
    inefficiencies compared to the built-in range, notably that reversal of
    the resulting generator relies enumeration of the generator.
    """
    if stop is None:
        stop, start = start, 0.0
    count = int(math.ceil((stop - start) / step))
    return (start + n * step for n in range(count))


class FloatRangeField(FormField):
    def __init__(self, label=None, validators=None, separator='-', **kwargs):
        max_count = kwargs.pop('max_count', 1000)
        validators = validators or []
        self._min = None
        self._max = None
        for v in validators:
            if isinstance(v, NumberRange):
                self._min = v.min
                self._max = v.max
                break

        class RangeForm(Form):
            count = IntegerField(
                'values', default=1,
                validators=
                    [v for v in validators if isinstance(v, InputRequired)] +
                    [NumberRange(min=1, max=max_count)]
                )
            start = FloatField(
                'from', default=kwargs.get('default'),
                validators=validators)
            stop = FloatField(
                'to', default=kwargs.get('default'),
                validators=
                    [v for v in validators if not isinstance(v, InputRequired)]
                )

            def validate(self):
                if not super(RangeForm, self).validate():
                    return False
                if self.stop.data is not None and self.start.data > self.stop.data:
                    self.start.errors.append(
                        'Starting value must be less than ending value')
                    return False
                return True

        super(FloatRangeField, self).__init__(
                RangeForm, label, validators=None, separator=separator,
                **kwargs)

    def __call__(self, **kwargs):
        # XXX The following is specific to the UManSysProp layout
        return literal(''.join((
            tag.div(
                tag.label(
                    tag.input(
                        id='%s-range' % self.name,
                        type='checkbox',
                        value='range'
                        ),
                    ' range'
                    ),
                class_='medium-2 columns'
                ),
            tag.div(
                tag.div(
                    self.form.start(id=self.form.start.id + '-single', min=self._min, max=self._max),
                    self.form.stop(id=self.form.stop.id + '-single', type='hidden'),
                    self.form.count(id=self.form.count.id + '-single', type='hidden', value=1),
                    id='%s-single' % self.name
                    ),
                tag.div(
                    self.form.count(min=1),
                    ' ',
                    self.form.count.label,
                    ' ',
                    self.form.start.label,
                    ' ',
                    self.form.start(min=self._min, max=self._max),
                    ' ',
                    self.form.stop.label,
                    ' ',
                    self.form.stop(min=self._min, max=self._max),
                    id='%s-multi' % self.name,
                    class_='form-inline'
                    ),
                class_='medium-10 columns'
                )
            )))

    @property
    def scripts(self):
        template = """\
$(document).ready(function() {
    if (parseInt($('#%(count)s').val()) > 1) {
        $('#%(name)s-range').prop('checked', true);
        $('#%(name)s-single').hide();
        $('#%(name)s-single input').prop('disabled', true);
    }
    else {
        $('#%(name)s-range').prop('checked', false);
        $('#%(name)s-multi').hide();
        $('#%(name)s-multi input').prop('disabled', true);
    }
});
$('#%(start)s-single').change(function() {
    $('#%(stop)s-single').val($('#%(start)s-single').val());
});
$('#%(name)s-range').change(function() {
    if (this.checked) {
        $('#%(name)s-single').fadeOut('fast', function() {
            $('#%(name)s-single input').prop('disabled', true);
            $('#%(name)s-multi input').prop('disabled', false);
            $('#%(name)s-multi').fadeIn('fast');
        });
    }
    else {
        $('#%(name)s-multi').fadeOut('fast', function() {
            $('#%(name)s-multi input').prop('disabled', true);
            $('#%(name)s-single input').prop('disabled', false);
            $('#%(name)s-single').fadeIn('fast');
        });
    }
});
"""
        return tag.script(literal(template % {
            'name': self.name,
            'start': self.form.start.name,
            'stop': self.form.stop.name,
            'count': self.form.count.name,
            }))

    @property
    def data(self):
        start = self.form.start.data
        stop = self.form.stop.data
        count = self.form.count.data
        if count == 1:
            return [start]
        else:
            step = (stop - start) / (count - 1)
            return frange(start, stop + 1e-15, step)

