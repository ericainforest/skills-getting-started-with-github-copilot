import copy
import unittest

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


class AppTests(unittest.TestCase):
    def setUp(self):
        self.original = copy.deepcopy(activities)

    def tearDown(self):
        activities.clear()
        activities.update(copy.deepcopy(self.original))

    def test_get_activities_returns_activities(self):
        response = client.get("/activities")

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertIn("Chess Club", payload)
        self.assertIn("Programming Class", payload)
        self.assertIsInstance(payload["Chess Club"], dict)

    def test_signup_for_activity_adds_participant(self):
        email = "test@student.edu"
        activity_name = "Chess Club"

        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], f"Signed up {email} for {activity_name}")
        self.assertIn(email, activities[activity_name]["participants"])

    def test_signup_duplicate_returns_400(self):
        email = activities["Programming Class"]["participants"][0]
        activity_name = "Programming Class"

        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Student already signed up for this activity")

    def test_remove_participant_unregisters_user(self):
        activity_name = "Gym Class"
        email = activities[activity_name]["participants"][0]

        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], f"Removed {email} from {activity_name}")
        self.assertNotIn(email, activities[activity_name]["participants"])

    def test_remove_nonexistent_participant_returns_404(self):
        activity_name = "Chess Club"
        email = "doesnotexist@student.edu"

        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Participant not found")
