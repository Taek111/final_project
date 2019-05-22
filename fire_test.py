from firebase import firebase


firebase = firebase.FirebaseApplication("https://test-4ac24.firebaseio.com/", None)
print(firebase.get('/user/test/room1/Light',None))
result = firebase.patch('/user/test/room1/Light', {:Fal)