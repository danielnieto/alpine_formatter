from unittest import TestCase
from alpine_formatter.formatter import RE_PATTERN, get_indentation_level, format_alpine
import re


class TestPattern(TestCase):
    def test_matches_multiline(self):
        content = """
        <div x-data='
        {"key": "value"}
        '>
        <div x-data="
        {'key': 'value'}
        ">
        <div x-data=
        "
            {'key': 'value'}
        "
        >
        <div x-data=
        "
            {'key': 'value'}">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 4)

    def test_matches_ignoring_case(self):
        content = """
        <div X-dAtA='{"key": "value"}'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_matches_escaped_double_quotes(self):
        content = """
        <div x-data="{\"key\": \"value\"}">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].group("quote"), '"')

    def test_matches_escaped_single_quotes(self):
        content = """
        <div x-data='{\'key\': \'value\'}'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].group("quote"), "'")

    def test_do_not_match_directives_without_spaces(self):
        content = """
        <div x-data="{"key": "value"}"x-data="">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_matches_directives_on_first_line(self):
        content = """<div x-data="{"key": "value"}">"""
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_do_not_match_different_quotes(self):
        content = """
        <div x-data='">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)

    def test_groups_have_expected_content(self):
        content = """
        <div x-data='{"key": "value"}'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)
        match = matches[0]
        self.assertEqual(match.group("directive"), "x-data")
        self.assertEqual(match.group("quote"), "'")
        self.assertEqual(match.group("code"), '{"key": "value"}')


class TestXData(TestCase):
    def test_matches_x_data(self):
        content = """
        <div x-data='{"key": "value"}'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_do_not_match_x_data_with_extra_chars(self):
        content = """
        <div nox-data='{"key": "value"}'>
        <div x-datano='{"key": "value"}'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)

    def test_ignore_x_data_without_content(self):
        content = """
        <div x-data>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)


class TestXInit(TestCase):
    def test_matches_x_init(self):
        content = """
        <div x-init="test=true">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_do_not_match_x_init_with_extra_chars(self):
        content = """
        <div nox-init="test=true">
        <div x-initno="test=true">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)


class TestXShow(TestCase):
    def test_matches_x_show_without_modifiers(self):
        content = """
        <div x-show="open">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_matches_x_show_with_modifiers(self):
        content = """
        <div x-show.important='open'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_matches_x_show_with_unknown_modifiers(self):
        content = """
        <div x-show.not-yet-implemented.modifier.500ms='open'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_do_not_match_x_show_with_extra_chars(self):
        content = """
        <div x-showextrachars='open'>
        <div x-showextrachars.important='open'>
        <div nox-show.important='open'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)

    def test_do_not_match_x_show_with_invalid_modifiers(self):
        content = """
        <div x-show.mo difier='open'>
        <div x-show.invalid_modifier='open'>
        <div x-show.='open'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)


class TestXBind(TestCase):
    def test_matches_x_bind(self):
        content = """
        <div x-bind:placeholder="placeholder">
        <div x-bind:data-attr="value">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 2)

    def test_matches_shorthand_x_bind(self):
        content = """
        <div :placeholder="placeholder">
        <div :data-attr="value">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 2)

    def test_matches_multiple_shorthand_x_bind_in_same_line(self):
        content = """
        <div :data-attr="value" :placeholder="another_value">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 2)

    def test_matches_shorthand_x_bind_class(self):
        content = """
        <div class="opacity-50" :class="hide && 'hidden'">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_do_not_match_x_bind_with_extra_chars(self):
        content = """
        <div x-bindextrachars:class='open'>
        <div nox-bind:class='open'>
        <div no:class="open">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)


class TestXOn(TestCase):
    def test_matches_x_on_without_modifiers(self):
        content = """
        <div x-on:click="alert('Hello World!')">
        <div x-on:custom-event="alert('custom event')">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 2)

    def test_matches_x_on_with_modifiers(self):
        content = """
        <div x-on:keyup.enter="alert('Submitted!')">
        <div x-on:keyup.shift.enter="alert('Submitted!')">
        <div x-on:custom-event="alert('custom event')">
        <div x-on:custom-event.camel="handleCustomEvent">
        <div x-on:keyup.page-down="alert('Submitted!')">
        <div x-on:input.debounce.500ms="fetchResults">
        <div x-on:scroll.window.throttle.750ms="handleScroll">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 7)

    def test_matches_shorthand_x_on_without_modifiers(self):
        content = """
        <div @click="alert('Hello World!')">
        <div @custom-event="alert('custom event')">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 2)

    def test_matches_shorthand_x_on_with_modifiers(self):
        content = """
        <div @keyup.enter="alert('Submitted!')">
        <div @keyup.shift.enter="alert('Submitted!')">
        <div @custom-event="alert('custom event')">
        <div @custom-event.camel="handleCustomEvent">
        <div @keyup.page-down="alert('Submitted!')">
        <div @input.debounce.500ms="fetchResults">
        <div @scroll.window.throttle.750ms="handleScroll">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 7)

    def test_matches_multiple_shorthand_x_on_in_same_line(self):
        content = """
        <div @click="alert('Hello World!')" @custom-event="alert('custom event')">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 2)

    def test_do_not_match_x_on_with_extra_chars(self):
        content = """
        <div x-onextrachars:click='open'>
        <div nox-on:click="open">
        <div no@event="open">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)

    def test_matches_x_on_with_unknown_modifiers(self):
        content = """
        <div x-on:click.not-yet-implemented.modifier.500ms='open'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_do_not_match_x_show_with_invalid_modifiers(self):
        content = """
        <div x-on:event.mo difier='open'>
        <div x-on:event.invalid_modifier='open'>
        <div x-on:event.='open'>
        <div @event.mo difier='open'>
        <div @event.invalid_modifier='open'>
        <div @event.='open'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)


class TestXText(TestCase):
    def test_matches_x_text(self):
        content = """
        <div x-text="username">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_do_not_match_x_text_with_extra_chars(self):
        content = """
        <div nox-text="username">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)


class TestXHtml(TestCase):
    def test_matches_x_html(self):
        content = """
        <div x-html="<div>test</div>">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_do_not_match_x_html_with_extra_chars(self):
        content = """
        <div nox-html="<div>test</div>">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)


class TestXModel(TestCase):
    def test_matches_x_model_without_modifiers(self):
        content = """
        <div x-model="message">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_matches_x_model_with_modifiers(self):
        content = """
        <div x-model.boolean="isActive">
        <div x-model.debounce.500ms="search">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 2)

    def test_matches_x_model_with_unknown_modifiers(self):
        content = """
        <div x-model.not-yet-implemented.modifier.500ms='search'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_do_not_match_x_model_with_extra_chars(self):
        content = """
        <div x-modelextrachars='message'>
        <div x-modelextrachars.boolean='message'>
        <div nox-model.boolean='message'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)

    def test_do_not_match_x_model_with_invalid_modifiers(self):
        content = """
        <div x-model.mo difier='message'>
        <div x-model.invalid_modifier='message'>
        <div x-model.='message'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)


class TestXModelable(TestCase):
    def test_matches_x_modelable(self):
        content = """
        <div x-modelable="count">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_do_not_match_x_modelable_with_extra_chars(self):
        content = """
        <div nox-modelable="count">
        <div x-modelableno="count">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)


class TestXFor(TestCase):
    def test_matches_x_for(self):
        content = """
        <div x-for="color in colors">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_do_not_match_x_for_with_extra_chars(self):
        content = """
        <div nox-for="color in colors">
        <div x-forno="color in colors">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)


class TestXEffect(TestCase):
    def test_matches_x_effect(self):
        content = """
        <div x-effect="console.log(label)">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_do_not_match_x_effect_with_extra_chars(self):
        content = """
        <div nox-effect="console.log(label)">
        <div x-effectno="console.log(label)">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)


class TestXRef(TestCase):
    def test_matches_x_ref(self):
        content = """
        <div x-ref="text">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_do_not_match_x_ref_with_extra_chars(self):
        content = """
        <div nox-ref="text">
        <div x-refno="text">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)


class TestXIf(TestCase):
    def test_matches_x_if(self):
        content = """
        <div x-if="open">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_do_not_match_x_if_with_extra_chars(self):
        content = """
        <div nox-if="open">
        <div x-ifno="open">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)


class TestXId(TestCase):
    def test_matches_x_id(self):
        content = """
        <div x-id="['text-input']">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_do_not_match_x_id_with_extra_chars(self):
        content = """
        <div nox-id="['text-input']">
        <div x-idno="['text-input']">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)


class TestGetIndentationLevel(TestCase):
    def test_no_indentation(self):
        content = "foo"
        match = re.search(r"foo", content)
        self.assertIsNotNone(match)
        self.assertEqual(get_indentation_level(match), 0)

    def test_single_line_indentation(self):
        content = "\n        foo"
        match = re.search(r"foo", content)
        self.assertIsNotNone(match)
        self.assertEqual(get_indentation_level(match), 8)

    def test_multiline_indentation(self):
        content = "foo\n    bar"
        match = re.search(r"bar", content)
        self.assertIsNotNone(match)
        self.assertEqual(get_indentation_level(match), 4)

    def test_indentation_after_newline(self):
        content = "foo\n\n    bar"
        match = re.search(r"bar", content)
        self.assertIsNotNone(match)
        self.assertEqual(get_indentation_level(match), 4)

    def test_no_newline_before_match(self):
        content = "foo bar"
        match = re.search(r"bar", content)
        self.assertIsNotNone(match)
        self.assertEqual(get_indentation_level(match), 0)

    def test_alpine_pattern_indentation(self):
        content = """
        <div>
            <div  x-data='{"hide":false}'>
                foo
            </div
        </div>
        """
        match = re.search(RE_PATTERN, content)
        self.assertIsNotNone(match)
        self.assertEqual(get_indentation_level(match), 18)


class TestFormatAlpine(TestCase):
    def test_single_line_format(self):
        content = """
        <div>
            <div   :class="hide&&'hidden' "   style="border:red">
                foo
            </div
        </div>
        """
        expected_result = """
        <div>
            <div   :class="hide && 'hidden'"   style="border:red">
                foo
            </div
        </div>
        """
        self.assertEqual(format_alpine(content), expected_result)

    def test_multi_line_format(self):
        content = """
        <div>
            <div x-data='{"hide":false}' :class="hide && 'hidden'">
                foo
            </div
        </div>
        """
        expected_result = """
        <div>
            <div x-data='
                 {
                     "hide": false
                 }
                 ' :class="hide && 'hidden'">
                foo
            </div
        </div>
        """
        self.assertEqual(format_alpine(content), expected_result)

    def test_real_example(self):
        content = """
        <div
            {# djlint:off #}
            x-data ="{
             tags: [],
              newTag: '',
             pattern: /[^A-Za-z0-9]/g,
              init: function() { const initialValue = $refs.input.value;
                if (!initialValue) { return; }
                initialValue.split(',').forEach(tag => this.tags.push(tag.trim()));
              },
          addTag : (event) =>{
                if (this.tags.indexOf(this.newTag) > -1 || !this.newTag) {
                  return;
                 }
                this.tags.push(this.newTag);
                 this.newTag = '';
              },
              removeTag:function(tag){
                this.tags.splice(
                    this.tags.indexOf(tag), 1);
              },
              preventInvalid:function(event) {
                if (this.pattern.test(event.key) && event.key.length === 1) {
                  event.preventDefault();
                }
              }, filterInput: function(event) {
                this.newTag = event.target.value.replace(this.pattern, '');
                }}"   {# djlint:on #} >
            <input {% include "django/forms/widgets/attrs.html" %}
                    x-model="  newTag "
                   @keydown.enter.prevent="addTag "
                   @keydown=" preventInvalid"
                   @input="filterInput" placeholder="Add tag...">
        </input>
        <input     x-ref="input"
               x-model="tags"
               type="hidden"
               name="{{ widget.name }}"
               {% if widget.value != None %}value="{{ widget.value|stringformat:'s' }}"{% endif %}>
        </input>
        <div class="flex flex-wrap gap-1 my-2">
            <template x-for =" tag  in tags">
                <div class="badge bg-gray-200">
                    <span class="first-letter:uppercase" x-text="tag"></span>
                    <svg @click="removeTag(tag )"
                         xmlns="http://www.w3.org/2000/svg"
                    </svg>
                </div>
            </template>
        </div>
        """
        expected_result = """
        <div
            {# djlint:off #}
            x-data="
            {
                tags: [],
                newTag: '',
                pattern: /[^A-Za-z0-9]/g,
                init: function() {
                    const initialValue = $refs.input.value;
                    if (!initialValue) {
                        return;
                    }
                    initialValue.split(',').forEach(tag => this.tags.push(tag.trim()));
                },
                addTag: (event) => {
                    if (this.tags.indexOf(this.newTag) > -1 || !this.newTag) {
                        return;
                    }
                    this.tags.push(this.newTag);
                    this.newTag = '';
                },
                removeTag: function(tag) {
                    this.tags.splice(
                        this.tags.indexOf(tag), 1);
                },
                preventInvalid: function(event) {
                    if (this.pattern.test(event.key) && event.key.length === 1) {
                        event.preventDefault();
                    }
                },
                filterInput: function(event) {
                    this.newTag = event.target.value.replace(this.pattern, '');
                }
            }
            "   {# djlint:on #} >
            <input {% include "django/forms/widgets/attrs.html" %}
                    x-model="newTag"
                   @keydown.enter.prevent="addTag"
                   @keydown="preventInvalid"
                   @input="filterInput" placeholder="Add tag...">
        </input>
        <input     x-ref="input"
               x-model="tags"
               type="hidden"
               name="{{ widget.name }}"
               {% if widget.value != None %}value="{{ widget.value|stringformat:'s' }}"{% endif %}>
        </input>
        <div class="flex flex-wrap gap-1 my-2">
            <template x-for="tag in tags">
                <div class="badge bg-gray-200">
                    <span class="first-letter:uppercase" x-text="tag"></span>
                    <svg @click="removeTag(tag)"
                         xmlns="http://www.w3.org/2000/svg"
                    </svg>
                </div>
            </template>
        </div>
        """
        self.maxDiff = None
        self.assertEqual(format_alpine(content), expected_result)
