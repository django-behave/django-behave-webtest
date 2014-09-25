# -*- coding: utf-8 -*-
import re
import json
from os.path import join, abspath, dirname

from behave import when, then, given

from django.contrib.auth.models import User

CURRENT_DIR = dirname(abspath(__file__))


#
# Navigation
#

# en
@when(u"I navigate to: {url:S}")
# fr
@when(u"je navigue à: {url:S}")
def navigate_to(context, url):
    context.response = context.app.get(url)


# en
@when(u'I navigate to "{url:S}" with the code: {status:d}')
# fr
@when(u'je navigue à "{url:S}" avec le code: {status:d}')
def navigate_with_code(context, url, status):
    context.response = context.app.get(url, status=int(status))


# en
@when(u"I open a browser")
@when(u"I launch a browser")
# fr
@when(u"je lance un navigateur")
@when(u"j'ouvre un navigateur")
def launch_the_browser(context):
    context.response.showbrowser()


# en
@then(u'I\'m at the page: {}')
# fr
@then(u'je suis à la page: {}')
def at_page(context, test_url):
    # FIXME urllib2
    url = context.response.request.url
    url = re.sub('http://localhost', '', url)
    url = re.sub('http://testserver', '', url)
    url = re.sub(':80', '', url)

    assert test_url == url, url


# en
@then(u'I\'m redirected to the page:  {}')
# fr
@then(u'je suis redirigé à la page: {}')
def rediricted_to(context, text):
    try:
        url = re.sub('http://localhost', '', context.response['Location'])
        url = re.sub('http://testserver', '', context.response['Location'])
        url = re.sub(':80', '', url)
    except AttributeError:
        context.response.showbrowser()
        raise AssertionError(context.response.status)

    assert url == text, url
    try:
        context.response = context.response.follow()
    except Exception as e:
        assert False, str(e).split("\n")[0]


#
# JSON
#

# en
@then(u"I see the json")
# fr
@then(u"je vois le json")
def got_json(context):
    fixture = json.loads(context.text)
    content = json.loads(context.response.content)

    assert json.dumps(content, sort_keys=True) == json.dumps(fixture, sort_keys=True), \
        json.dumps(content, sort_keys=True)


#
# HTML
#

# FIXME: meta tag title? h* ?
# en
@then(u"I see the title: {}")
# fr
@then(u"je vois le titre: {}")
def got_title(context, text):
    text = text.decode('utf')

    headers = context.response.lxml.cssselect('h1')
    texts = [header.text for header in headers]
    assert text in texts, texts


# en
@then(u"I see a link: {}")
# fr
@then(u"je vois le lien: {}")
def got_link(context, text):
    text = text.decode('utf')

    links = context.response.lxml.cssselect('a')
    hrefs = [link.attrib.get('href') for link in links]
    assert text in hrefs, hrefs


# en
@then(u"I don\'t see the link: {}")
# fr
@then(u"je ne vois pas le lien: {}")
def got_not_link(context, text):
    text = text.decode('utf')

    links = context.response.lxml.cssselect('a')
    hrefs = [link.attrib.get('href') for link in links]
    assert text not in hrefs, hrefs


# en
@then(u'I see the text "{}" in a list')
# fr
@then(u'je vois le texte "{}" dans une liste')
def got_texte_in_list(context, text):
    text = text.decode('utf')

    lists = filter(lambda a: a.text == text, context.response.dom.cssselect('li a'))
    assert lists[0].text == text


# en
@when(u'I click on the link: {}')
# fr
@when(u'je clique sur le lien: {}')
def je_clique_lien(context, text):
    try:
        context.response = context.response.click(description=text)
    except IndexError:
        links = context.response.lxml.cssselect('a')
        texts = [link.text for link in links]
        assert False, texts


# en
@when(u'I click on the button: {}')
# fr
@when(u'je clique sur le bouton: {}')
def click_on_button(context, text):
    context.response = context.response.clickbutton(description=text)


#
# Forms
#


# en
@then(u'I see "{}" in the field "{}" of the form "{}"')
# fr
@then(u'je vois "{}" dans le champ "{}" du formulaire "{}"')
def content_in_field(context, value, field, form_name):
    form = context.response.forms[form_name]
    assert form[field].value == value, form[field]


# en
@then(u'I see the error "{}" in the field "{}" of the form "{}"')
# fr
@then(u'je vois une erreur "{}" pour le champ "{}" du formulaire "{}"')
def error_in_field(context, error, field, form):
    error_msg = context.response.lxml.cssselect('form[id="%s"] div div input[name=%s] + p' % (form, field))
    assert error_msg[0].text == error


# en
@then(u'I see the form "{}" with the fields: {}')
# fr
@then(u'je vois le formulaire "{}" avec les champs: {}')
def fields_in_form(context, form_name, fields):
    assert form_name in context.response.forms.keys(), (form_name, context.response.forms)
    form = context.response.forms[form_name]
    visible_fields = [k for k,v in form.fields.items() if k and v[0].__class__.__name__ is not 'Hidden']
    assert fields == ','.join(visible_fields), (fields, visible_fields)


# en
@then(u'I enter "{}" in the field "{}" of the form "{}"')
# fr
@then(u'je tape "{}" dans le champ "{}" du formulaire "{}"')
def add_content_in_field(context, value, field, form_name):
    form = context.response.forms[form_name]
    form[field] = value


# en
@then(u'I checked the field "{}" of the form "{}"')
# fr
@then(u'je coche le champ "{}" du formulaire "{}"')
def checked(context, field, form_name):
    form = context.response.forms[form_name]
    form[field] = "checked"


# en
@then(u'I unchecked the field "{}" of the form "{}"')
# fr
@then(u'je ne coche pas le champ "{}" du formulaire "{}"')
def unchecked(context, field, form_name):
    form = context.response.forms[form_name]
    form[field] = None


# en
@then(u'I choose "{}" in the field "{}" of the form "{}"')
# fr
@then(u'je choisi "{}" dans le champ "{}" du formulaire "{}"')
def choose_in_dropdown(context, value, field, form_name):
    form = context.response.forms[form_name]
    options = context.response.lxml.cssselect('select[id=id_%s] option' % field)
    for option in options:
        if option.text == value:
            form.select(field, option.attrib['value'])
            return

    raise AssertionError('Option not found in: %s' % str([o.text for o in options]))


# en
@then(u'I choose the file "{}" in the field "{}" of the form "{}"')
# fr
@then(u'je choisi le fichier "{}" dans le champ "{}" du formulaire "{}"')
def choose_file(context, filename, field, form_name):
    form = context.response.forms[form_name]
    form[field] = (field, open(join(CURRENT_DIR, filename), 'r').read())


# en
@when(u'I submit the form: {}')
# fr
@when(u'je soumets le formulaire: {}')
def submit_form(context, form_name):
    context.response = context.response.forms[form_name].submit()


# FIXME check the return code in an other line?
# en
@when(u'I submit the form "{}" with the code: {}')
# fr
@when(u'je soumets le formulaire "{}" avec le code: {}')
def submit_with_code(context, form_name, status):
    context.response = context.response.forms[form_name].submit(status=int(status))


#
# Table
#


# en
@then(u'I see the table "{}"')
# fr
@then(u'je vois la table "{}"')
def got_table(context, table_name):
    soup = context.response.html
    table = soup.find(id=table_name)

    dataset = [[c for c in row.findAll("td")] for row in table.findAll("tr")]
    dataset = filter(lambda x: x != [], dataset)

    new_dataset = []
    for r in range(0, len(dataset)):
        for i in range(0, len(dataset[r])):
            if dataset[r][i] != u'':
                colspan = dataset[r][i].get('colspan', None)
                rowspan = dataset[r][i].get('rowspan', None)
                if colspan:
                    for k in range(1, int(colspan)):
                        dataset[r].insert(i+k, u'')
                if rowspan:
                    for k in range(1, int(rowspan)):
                        dataset[r + k].insert(i, u'')

        new_dataset.append(dataset[r])

    dataset = new_dataset

    for row in dataset:
        for i in range(0, len(row)):
            try:
                row[i] = row[i].get_text().strip().replace('\n', ' ').replace(u'\xa0', ' ')
            except AttributeError:
                continue

    assert len(context.table[:]) == len(dataset), (len(context.table[:]), len(dataset))

    for i in range(0, len(context.table[:])):
        context_row = [v for k, v in context.table[i].items()]
        assert dataset[i] == context_row, (dataset[i], context_row)


#
# Sessions
#


# en
@then(u"I\'m not connected")
# fr
@then(u"je ne suis pas connecté")
def not_connected(context):
    context.response = context.app.get('/')
    user = context.response.context['user']
    assert user.username == 'AnonymousUser', user


# en
@then(u"I\'m connected with the user: {}")
# fr
@then(u"je suis connecté avec l'utilisateur: {}")
def is_connected(context, username):
    user = context.response.context['user']
    assert user.username == username, user


# FIXME use the internal django authentification
# en
@given(u"I log in with the user: {}")
# fr
@given(u"je me connecte avec l'utilisateur: {}")
def login_user(context, username):
    context.response = context.app.get('/admin/', user=username)


# en
@given(u'I create the user "{username}"')
# fr
@given(u'je crée l\'utilisateur "{username}"')
def create_user(context, username):
    user = User.objects.create(username=username)
    user.save()


# en
@given(u"""I create the user "{username}" with the password: {password}""")
# fr
@given(u"""je crée l'utilisateur "{username}" avec le mot de passe: {password}""")
def create_user_with_password(context, username, password):
    user = User.objects.create(username=username, is_staff=True)
    user.set_password(password)
    user.save()


# en
@given(u"""I create the superuser "{username}" with the password: {password}""")
# fr
@given(u"""je crée l'administrateur "{username}" avec le mot de passe: {password}""")
def create_admin_with_password(context, username, password):
    user = User.objects.create(username=username, is_superuser=True, is_staff=True)
    user.set_password(password)
    user.save()


# en
@given(u"""I log in with the superuser "{username}" with the password: {password}""")
# fr
@given(u"""je me connecte avec l'administrateur "{username}" et le mot de passe: {password}""")
def login_admin(context, username, password):
    context.response = context.app.get('/admin/')
    form = context.response.forms['login-form']
    form['username'] = username
    form['password'] = password
    context.response = form.submit()


#
# Emails
#


# en
@then(u'I receive an email "{}" for "{}" with the content')
# fr
@then(u'je reçois un courriel "{}" pour "{}" contenant')
def got_email(context, subject, destination):
    subject = subject.decode('utf8')
    body = context.text

    email = context.last_email = context.mail.pop()
    assert len(context.mail) == 0

    assert subject == email.subject, email.subject
    assert destination == email.to[0], email.to[0]
    assert body == email.body, "expect:\n\n%s\ngot:\n\n%s" % (repr(body), repr(email.body))


# FIXME named the link and use the link checking function declared earlier
# en
@when(u"I navigate to the link in the email")
# fr
@when(u"je navigue au lien du courriel")
def link_in_email(context):
    email = context.last_email
    match = re.search(r'http://[^\s]+', email.body)

    url = match.group(0)

    url = re.sub('http://testserver', '', url)
    url = re.sub('http://example.com', '', url)
    url = re.sub(':80', ':8000', url)

    context.response = context.app.get(url, status=200)

#
# Fixture
#


# en
@given(u"I import the fixture: {}")
# fr
@given(u"j'importe la fixture: {}")
def loaddata_fixture(context, fixture):
    from django.core.management import call_command
    call_command('loaddata', fixture)


#
# Model
#


# en
@then(u'the following "{}" models')
# fr
@then(u'les "{}" suivants')
def models_check(context, model_name):
    from django.db.models import get_model
    from django.forms.models import model_to_dict

    for row in context.table:
        model = get_model(*model_name.split('.', 1))
        model_dict = model_to_dict(model.objects.get(pk=row[0]))

        for k, v in row.items():
            if k == 'pk':
                continue

            if '__' in k:
                rel_name, rel_attr = k.split('__', 1)
                qs = getattr(model, rel_name).get_query_set().all()
                attr = getattr(qs.get(**{rel_attr: v}), rel_attr)
                assert v == attr, (k, v, attr)
            else:
                assert v == str(model_dict[k]), (k, v, str(model_dict[k]))


# en
@then(u'the following "{}" "{}"')
# fr
@then(u'le "{}" "{}" suivant')
def model_check(context, model_name, pk):
    from django.db.models import get_model
    from django.forms.models import model_to_dict

    model = get_model(*model_name.split('.', 1))
    model_dict = model_to_dict(model.objects.get(pk=pk))

    for k, v in dict(context.table).items():
        if '__' in k:
            rel_name, rel_attr = k.split('__', 1)
            qs = getattr(model, rel_name).get_query_set().all()
            attr = getattr(qs.get(**{rel_attr: v}), rel_attr)
            assert v == attr, (k, v, attr)
        else:
            assert v == str(model_dict[k]), (k, v, str(model_dict[k]))


# en
@given(u'the following "{}" model')
# fr
@given(u'le "{}" suivant')
def model_create(context, model_name):
    from django.db.models import get_model

    model = get_model(*model_name.split('.', 1))

    attrs = {}
    rel_attrs = []

    for k, v in dict(context.table).items():
        if v == u'None':
            continue

        if '__' in k:
            rel_name, rel_attr = k.split('__', 1)
            try:
                qs = getattr(model, rel_name).get_query_set().all()
                attrs[rel_name] = qs.get(**{rel_attr: v})
            except AttributeError:
                rel_attrs.append((k, v))
        else:
            attrs[k] = v

    m = model.objects.create(**attrs)

    for k, v in rel_attrs:
        rel_name, rel_attr = k.split('__', 1)
        qs = getattr(m, rel_name).model.objects.filter(**{rel_attr: v})
        getattr(m, rel_name).add(*qs)


# en
@given(u'the following "{} models"')
# fr
@given(u'les "{}" suivants')
def models_create(context, model_name):
    from django.db.models import get_model
    for row in context.table:
        model = get_model(*model_name.split('.', 1))

        attrs = {}
        rel_attrs = []

        for k, v in row.items():
            if v == u'None':
                continue
            if '__' in k:
                rel_name, rel_attr = k.split('__', 1)
                try:
                    qs = getattr(model, rel_name).get_query_set().all()
                    attrs[rel_name] = qs.get(**{rel_attr: v})
                except AttributeError:
                    rel_attrs.append((k, v))
            else:
                attrs[k] = v

        m = model.objects.create(**attrs)
        for k, v in rel_attrs:
            rel_name, rel_attr = k.split('__', 1)
            qs = getattr(m, rel_name).model.objects.filter(**{rel_attr: v})
            getattr(m, rel_name).add(*qs)


# en
@when(u"I open a debugger")
# fr
@when(u"j'ouvre un débuggeur")
def debug(context):
    import pdb
    pdb.set_trace()


# en
@when(u"I call the command: {}")
# fr
@when(u"j'exécute la commande: {}")
def call_django_command(context, cmd):
    from django.core.management import call_command
    call_command(cmd)
