## AERPAW Portal Testing
    - The AERPAW Portal uses Djanog's built in testing which subclasses python's unittest module
    - Documentation:
    - unittest: 'https://docs.python.org/3/library/unittest.html#classes-and-functions'
    - Django testing: 'https://docs.djangoproject.com/en/5.1/topics/testing/'
    - Django Rest Framework Testing: 'https://www.django-rest-framework.org/api-guide/testing/'

### unittest

#### unittest Methods
    - setUp()
    - @classmethod and setUpClass(cls)
    - tearDown()
    - TearDownClass()
    - run()

#### unittest Assert Methods
    - assertEqual(a,b)                                  a == b
    - assertNotEqual(a,b)                               a != b
    - assertTrue(x)                                     bool(x) is True
    - assertFalse(x)                                    bool(x) is False
    - assertIs(a,b)                                     a is b
    - assertIsNot(x)                                    a is not b
    - assertIsNone(x)                                   x is None
    - assertIsNotNone(x)                                x is not None
    - assertIn(a,b)                                     a in b
    - assertNotIn(a,b)                                  a not in b
    - assertIsInstance(a,b)                             isinstance(a, b)
    - assertNotIsInstance(a,b)                          not isinstance(a, b)
    - assertRaises(exc, fun, *args, **kwds)             fun(*args, **kwds) raises exc
    - assertRaisesRegex(exc, r, fun, *args, **kwds)     fun(*args, **kwds) raises exc and the message matches regex r
    - assertWarns(warn, fun, *args, **kwds)             fun(*args, **kwds) raises warn
    - assertWarnsRegex(warn, r, fun, *args, **kwds)     fun(*args, **kwds) raises warn and the message matches regex r
    - assertLogs(logger, level)                         The with block logs on logger with minimum level
    - assertNoLogs(logger, level)                       The with block does not log on logger with minimum level
    - assertAlmostEqual(a,b)                            round(a-b, 7) == 0
    - assertNotAlmostEqual(a,b)                         round(a-b, 7) != 0
    - assertGreater(a,b)                                a > b
    - assertGreaterEqual(a,b)                           a >= b
    - assertLess(a,b)                                   a < b
    - assertLessEqual(a,b)                              a <= b
    - assertRegex(s,r)                                  r.search(s)
    - assertNotRegex(s,r)                               not r.search(s)
    - assertCountEqual(a,b)                             a and b have the same elements in the same number, regardless of their order
    - assertMultiLineEqual                              compare strings
    - assertSequenceEqual                               compare sequences
    - assertListEqual                                   compare lists
    - assertTupleEqual                                  compare tuples
    - assertSetEqual                                    compare sets or frozensets
    - assertDictEqual                                   compare dictionaries


### Django Testing
    - assertRaisesMessage(expected_exception, expected_message, callable, *args, **kwargs)
    - assertWarnsMessage(expected_warning, expected_message, callable, *args, **kwargs)
    - assertFieldOutput(fieldclass, valid, invalid, field_args=None, field_kwargs=None, empty_value='')
    - assertFormError(form, field, errors, msg_prefix='')
    - assertFormSetError(formset, form_index, field, errors, msg_prefix='')
    - assertContains(response, text, count=None, status_code=200, msg_prefix='', html=False)
    - assertNotContains(response, text, status_code=200, msg_prefix='', html=False)
    - assertTemplateUsed(response, template_name, msg_prefix='', count=None)
    - assertTemplateNotUsed(response, template_name, msg_prefix='')
    - assertURLEqual(url1, url2, msg_prefix='')
    - assertRedirects(response, expected_url, status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
    - assertHTMLEqual(html1, html2, msg=None)
    - assertHTMLNotEqual(html1, html2, msg=None)
    - assertXMLEqual(xml1, xml2, msg=None)
    - assertXMLNotEqual(xml1, xml2, msg=None)
    - assertInHTML(needle, haystack, count=None, msg_prefix='')
    - assertNotInHTML(needle, haystack, msg_prefix='')
    - assertJSONEqual(raw, expected_data, msg=None)
    - assertJSONNotEqual(raw, expected_data, msg=None)
    - assertQuerySetEqual(qs, values, transform=None, ordered=True, msg=None)
    - assertNumQueries(num, func, *args, **kwargs)