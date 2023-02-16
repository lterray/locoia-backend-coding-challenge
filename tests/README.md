# Testing GistAPI

## Running the tests

Run the tests!
   ```
   pytest
   ```
   If you're using a Python IDE like Pycharm or VSCode, it should also be able to run the tests.

## Pytest overview

See [Pytest documentation](https://docs.pytest.org/en/latest/) for more details.

### Testing views

Here is an example test that uses a view:

```python
def test_edit_profile(client, student):
    login_as(client, student)

    r = client.get('/profile/edit')
    assert r.status_code == 200

    r = client.post('/profile/edit', data={
        'first_name': 'Editor',
        'last_name': 'McEdit',
    })
    assert r.status_code == 302

    student = refresh(student)
    assert student.first_name == 'Editor'
    assert student.last_name == 'McEdit'
```

You need to use the `client` fixture. It's a Flask/Werkzeug [Client](http://werkzeug.pocoo.org/docs/0.14/test/#werkzeug.test.Client) object that can be used to make requests.

The `login_as` helper method makes sure the client is logged in.

If you need to reload objects from database after you have run some requests, you need to run `obj = refresh(obj)`.

- [Testing Flask](http://flask.pocoo.org/docs/1.0/testing/)
- [Client class](http://werkzeug.pocoo.org/docs/0.14/test/#werkzeug.test.Client)
- [EnvironBuilder class](http://werkzeug.pocoo.org/docs/0.14/test/#werkzeug.test.EnvironBuilder) - actual parameters to `client.get()` and `post()`

### Parsing HTML

You might want to examine the HTML output of a view. For instance. You can use the `lxml` library for that.

```python
from lxml import etree
from .util import html_text

def test_student_list(client, ...):
    ...

    r = client.get('/student/list')
    assert r.status_code == 200

    html = etree.HTML(r.data)
    first_cell = html.cssselect('.user-table tr td')[0]

    assert html_text(first_cell) == 'John Doe'
```

- use `etree.HTML(r.data)` to parse response
- use `.cssselect` to find elements (same as jQuery, or `querySelector`)

Links:
- [CSS Selectors](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors) (MDN)
- [lxml.etree tutorial](https://lxml.de/tutorial.html)
- [lxml.cssselect](https://lxml.de/cssselect.html)
