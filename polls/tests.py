from django.test import TestCase
from django.utils import timezone
from .models import Question
from django.urls import reverse
import datetime

def create_question(question_text, days):
    tiempo = timezone.now() + datetime.timedelta(days = days)
    return Question.objects.create(question_text = question_text, pub_date = tiempo)

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days = 30)
        future_question = Question(pub_date = time)
        self.assertIs(future_question.was_published_recently(), False)
    
    def test_was_published_with_old_question(self):
        time = timezone.now() - datetime.timedelta (days = 1, seconds = 1)
        past_question = Question(pub_date = time)
        self.assertIs(past_question.was_published_recently(), False)
        
    def test_was_published_within_one_day(self):
        time = timezone.now() - datetime.timedelta (hours = 23, minutes = 59, seconds = 59)
        correct_question = Question(pub_date = time)
        self.assertIs(correct_question.was_published_recently(), True)
        
class IndexViewTests(TestCase):

    def test_no_questions(self):
        # Manda un mensaje si la pregunta no existe
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])
    
    def test_past_question(self):
        #Las preguntas del pasado se muestran en el indice
        question = create_question(question_text = "Pregunta Pasada", days =-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )
    def test_future_question(self):
        #Las preguntas del futuro no deben mostrarse y display mensaje
        create_question(question_text = "Pregunta Futura", days =30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available")
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [],
        )
    def test_ambas(self):
        #Si hay de ambas, solo mostrar las pasadas
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question])
        
    def dos_pasadas(self):
        #Si hay dos pasadas, mostrar ambas
        question1 = create_question(question_text="Past question1.", days=-30)
        question2 = create_question(question_text="Past question2.", days=5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question1, question2])

class QuestionDetailViewsTests(TestCase):
    def test_future_question(self):
        #Si es futura, manda error 404
        future_question = create_question(question_text="Future", days = 30)
        url = reverse("polls:detail", args = (future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_past_question(self):
        #Si es pasada, muestra el texto de la pregunta
        past_question = create_question(question_text = "Past", days =-5)
        url = reverse("polls:detail", args = (past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)