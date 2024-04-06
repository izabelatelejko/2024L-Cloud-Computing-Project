import functions_framework


@functions_framework.http
def run(request):
    return {"test": request.get_json().get("test_input")}, 200
