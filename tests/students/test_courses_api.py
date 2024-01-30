import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
# from pytest_django.asserts import assertTemplateUsed
from students.models import Course, Student


# проверка получения первого курса (retrieve-логика)
# - создаем курс через фабрику;
# - строим урл и делаем запрос через тестовый клиент;
# - проверяем, что вернулся именно тот курс, который запрашивали;
@pytest.mark.django_db
def test_first_course(api_client, course_factory, student_factory):
    url = reverse('courses-list')
    students = student_factory(_quantity=5)
    course = course_factory(students=students)
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json[0]
    results = resp_json[0]
    assert results['name'] == course.name

# проверка получения списка курсов (list-логика)
@pytest.mark.django_db
def test_courses_list(api_client, course_factory, student_factory):
    url = reverse('courses-list')
    students = student_factory(_quantity=5)
    courses = course_factory(_quantity=10, students=students)
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert len(data) == len(courses)
    for i, course in enumerate(data):
        assert course['name'] == courses[i].name

# проверка фильтрации списка курсов по id:
# - создаем курсы через фабрику
# - передаем ID одного курса в фильтр
# - проверяем результат запроса с фильтром
@pytest.mark.django_db
def test_courses_filter_by_id(api_client, course_factory):
    url = reverse('courses-list')
    courses = course_factory(_quantity=10)
    course_nom = 5
    resp = api_client.get(url, {'id': courses[course_nom].id})
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data[0]['name'] == courses[course_nom].name

# проверка фильтрации списка курсов по name
@pytest.mark.django_db
def test_courses_filter_by_name(api_client, course_factory):
    url = reverse('courses-list')
    courses = course_factory(_quantity=10)
    course_nom = 5
    resp = api_client.get(url, {'name': courses[course_nom].name})
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data[0]['id'] == courses[course_nom].id

# тест успешного создания курса
@pytest.mark.django_db
def test_course_add(api_client, student_factory):
    students = student_factory(_quantity=5)
    url = reverse('courses-list')
    new_course = {
        'name': 'The best course for ever',
        'students': [student.id for student in students]
    }
    course_num_old = Course.objects.count()
    resp = api_client.post(url, data=new_course)
    assert resp.status_code == status.HTTP_201_CREATED
    assert Course.objects.count() == course_num_old + 1

# тест успешного обновления курса
@pytest.mark.django_db
def test_course_patch(api_client, course_factory):
    course = course_factory()
    url = reverse('courses-detail', kwargs={'pk': course.id})
    patched_course = {
        'name': 'New name for old course'
    }
    resp = api_client.patch(url, data=patched_course)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()['name'] == patched_course['name']
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()['name'] == patched_course['name']

# тест успешного удаления курса
@pytest.mark.django_db
def test_course_patch(api_client, course_factory, student_factory):
    students = student_factory(_quantity=5)
    course = course_factory(students=students)
    url = reverse('courses-detail', kwargs={'pk': course.id})
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp = api_client.delete(url)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
